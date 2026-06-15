"""locateanything core — infer where a photo was taken using a local VL model + reasoning model.

Defensive/OSINT/research use only. Get consent before geolocating images of people or private property.
Pure stdlib for transport (urllib); Pillow optional for richer EXIF.
"""
from __future__ import annotations

import base64
import json
import os
import urllib.request
from dataclasses import asdict, dataclass

TOOL_NAME = "locateanything"
TOOL_VERSION = "0.1.0"
VL_ENDPOINT = os.environ.get(
    "LA_VL_ENDPOINT", "http://127.0.0.1:8775/v1/chat/completions"
)  # fleet 'vision'
REASON_ENDPOINT = os.environ.get(
    "LA_REASON_ENDPOINT", "http://127.0.0.1:8771/v1/chat/completions"
)  # fleet 'reasoning'

# Default timeout for individual HTTP calls (seconds).
_HTTP_TIMEOUT = int(os.environ.get("LA_HTTP_TIMEOUT", "120"))


@dataclass
class Candidate:
    place: str
    confidence: float
    rationale: str


def _validate_image_path(path: str) -> None:
    """Raise ValueError with a human-readable message if *path* is unusable."""
    if not path or not path.strip():
        raise ValueError("image path must not be empty")
    if not os.path.exists(path):
        raise FileNotFoundError(f"image not found: {path!r}")
    if not os.path.isfile(path):
        raise ValueError(f"not a file: {path!r}")
    if os.path.getsize(path) == 0:
        raise ValueError(f"image file is empty: {path!r}")


def exif_gps(path: str):
    """Return (lat, lon) from EXIF if Pillow is available, else None."""
    try:
        from PIL import ExifTags, Image  # type: ignore[import]

        img = Image.open(path)
        raw_exif = img._getexif() or {}
        gps: dict = {}
        for k, v in raw_exif.items():
            if ExifTags.TAGS.get(k) == "GPSInfo":
                for gk, gv in v.items():
                    gps[ExifTags.GPSTAGS.get(gk, gk)] = gv
        if "GPSLatitude" not in gps or "GPSLongitude" not in gps:
            return None

        def dms(x) -> float:
            deg, minutes, seconds = x[0], x[1], x[2]
            # IFDRational / Fraction objects — handle zero denominator safely
            try:
                deg = float(deg)
                minutes = float(minutes)
                seconds = float(seconds)
            except (ZeroDivisionError, Exception):
                return 0.0
            return deg + minutes / 60.0 + seconds / 3600.0

        lat = dms(gps["GPSLatitude"]) * (-1 if gps.get("GPSLatitudeRef") == "S" else 1)
        lon = dms(gps["GPSLongitude"]) * (-1 if gps.get("GPSLongitudeRef") == "W" else 1)
        return (float(lat), float(lon))
    except Exception:
        return None


def _chat(endpoint: str, messages: list, max_tokens: int = 700) -> str:
    """POST a chat-completion request and return the assistant message text."""
    body = json.dumps(
        {"messages": messages, "temperature": 0.4, "max_tokens": max_tokens}
    ).encode()
    req = urllib.request.Request(
        endpoint, data=body, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=_HTTP_TIMEOUT) as r:
        data = json.loads(r.read())
        return data["choices"][0]["message"]["content"]


def vl_describe(path: str) -> str:
    """Ask the vision model for location-bearing clues (signs, architecture, flora, plates, sun)."""
    with open(path, "rb") as fh:
        b64 = base64.b64encode(fh.read()).decode()
    msg = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "List concrete geolocation clues in this image: visible text/signage and language, "
                        "license-plate style, architecture, vegetation/climate, road markings, sun position. Be specific."
                    ),
                },
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
            ],
        }
    ]
    return _chat(VL_ENDPOINT, msg)


def reason_locate(clues: str, gps=None) -> list:
    """Ask the reasoning model to infer ranked candidate locations from the clues."""
    if not clues or not clues.strip():
        return [Candidate("unknown", 0.0, "no clues provided")]
    extra = f"\nEXIF GPS present: {gps}." if gps else ""
    msg = [
        {
            "role": "user",
            "content": (
                f"Given these image clues, infer the 3 most likely locations (country/city/landmark) with a "
                f"confidence 0-1 and one-line rationale each. "
                f"Return JSON list of {{place, confidence, rationale}}.{extra}\n\nCLUES:\n{clues}"
            ),
        }
    ]
    out = _chat(REASON_ENDPOINT, msg)
    try:
        start = out.find("[")
        end = out.rfind("]")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("no JSON array found in model output")
        data = json.loads(out[start : end + 1])
        if not isinstance(data, list):
            raise ValueError("model output is not a JSON list")
        candidates = []
        for c in data:
            if not isinstance(c, dict):
                continue
            confidence = max(0.0, min(1.0, float(c.get("confidence", 0))))
            candidates.append(
                Candidate(
                    str(c.get("place", "?")),
                    confidence,
                    str(c.get("rationale", "")),
                )
            )
        return candidates or [Candidate("see-model-output", 0.0, out[:300])]
    except Exception:
        return [Candidate("see-model-output", 0.0, out[:300])]


def locate(path: str) -> dict:
    """Infer where a photo was taken.

    Raises
    ------
    FileNotFoundError
        If *path* does not exist.
    ValueError
        If *path* is not a usable image file (empty, not a file, etc.).
    """
    _validate_image_path(path)
    gps = exif_gps(path)
    result: dict = {"tool": TOOL_NAME, "image": path, "exif_gps": gps, "candidates": []}
    if gps:
        result["candidates"].append(
            asdict(Candidate(f"EXIF GPS {gps[0]:.4f},{gps[1]:.4f}", 0.99, "embedded GPS metadata"))
        )
    try:
        clues = vl_describe(path)
        result["clues"] = clues
        result["candidates"] += [asdict(c) for c in reason_locate(clues, gps)]
    except Exception as e:
        result["note"] = (
            f"VL/reasoning models unreachable ({e}). "
            "Start uncensored-fleet: `fleet up vision reasoning`."
        )
    return result
