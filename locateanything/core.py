"""locateanything core — infer where a photo was taken using a local VL model + reasoning model.

Defensive/OSINT/research use only. Get consent before geolocating images of people or private property.
Pure stdlib for transport (urllib); Pillow optional for richer EXIF.
"""
from __future__ import annotations
import base64, json, os, urllib.request
from dataclasses import dataclass, asdict

TOOL_NAME = "locateanything"; TOOL_VERSION = "0.1.0"
VL_ENDPOINT = os.environ.get("LA_VL_ENDPOINT", "http://127.0.0.1:8775/v1/chat/completions")       # fleet 'vision'
REASON_ENDPOINT = os.environ.get("LA_REASON_ENDPOINT", "http://127.0.0.1:8771/v1/chat/completions") # fleet 'reasoning'

@dataclass
class Candidate:
    place: str; confidence: float; rationale: str

def exif_gps(path: str):
    """Return (lat, lon) from EXIF if Pillow is available, else None."""
    try:
        from PIL import Image, ExifTags
        img = Image.open(path); exif = img._getexif() or {}
        gps = {}
        for k, v in exif.items():
            if ExifTags.TAGS.get(k) == "GPSInfo":
                for gk, gv in v.items():
                    gps[ExifTags.GPSTAGS.get(gk, gk)] = gv
        if "GPSLatitude" in gps and "GPSLongitude" in gps:
            def dms(x): return x[0] + x[1] / 60 + x[2] / 3600
            lat = dms(gps["GPSLatitude"]) * (-1 if gps.get("GPSLatitudeRef") == "S" else 1)
            lon = dms(gps["GPSLongitude"]) * (-1 if gps.get("GPSLongitudeRef") == "W" else 1)
            return (float(lat), float(lon))
    except Exception:
        return None
    return None

def _chat(endpoint, messages, max_tokens=700):
    body = json.dumps({"messages": messages, "temperature": 0.4, "max_tokens": max_tokens}).encode()
    req = urllib.request.Request(endpoint, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())["choices"][0]["message"]["content"]

def vl_describe(path: str) -> str:
    """Ask the vision model for location-bearing clues (signs, architecture, flora, plates, sun)."""
    b64 = base64.b64encode(open(path, "rb").read()).decode()
    msg = [{"role": "user", "content": [
        {"type": "text", "text": "List concrete geolocation clues in this image: visible text/signage and language, "
         "license-plate style, architecture, vegetation/climate, road markings, sun position. Be specific."},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]}]
    return _chat(VL_ENDPOINT, msg)

def reason_locate(clues: str, gps=None) -> list:
    """Ask the reasoning model to infer ranked candidate locations from the clues."""
    extra = f"\nEXIF GPS present: {gps}." if gps else ""
    msg = [{"role": "user", "content":
            f"Given these image clues, infer the 3 most likely locations (country/city/landmark) with a "
            f"confidence 0-1 and one-line rationale each. Return JSON list of {{place, confidence, rationale}}.{extra}\n\nCLUES:\n{clues}"}]
    out = _chat(REASON_ENDPOINT, msg)
    try:
        start = out.find("["); data = json.loads(out[start:out.rfind("]") + 1])
        return [Candidate(c.get("place", "?"), float(c.get("confidence", 0)), c.get("rationale", "")) for c in data]
    except Exception:
        return [Candidate("see-model-output", 0.0, out[:300])]

def locate(path: str, exif_only: bool = False) -> dict:
    """Infer where ``path`` was taken.

    Always parses EXIF GPS locally (no network). When ``exif_only`` is False it
    additionally queries the local VL + reasoning models for visual-clue ranking.
    Set ``exif_only=True`` for a deterministic, offline, model-free run that uses
    only embedded metadata — useful in CI, batch triage, or air-gapped review.
    """
    gps = exif_gps(path)
    result = {"tool": TOOL_NAME, "image": path, "exif_gps": gps, "candidates": []}
    if gps:
        result["candidates"].append(asdict(Candidate(f"EXIF GPS {gps[0]:.4f},{gps[1]:.4f}", 0.99, "embedded GPS metadata")))
    if exif_only:
        if not gps:
            result["note"] = "exif-only mode: no EXIF GPS embedded in this image."
        return result
    try:
        clues = vl_describe(path)
        result["clues"] = clues
        result["candidates"] += [asdict(c) for c in reason_locate(clues, gps)]
    except Exception as e:
        result["note"] = f"VL/reasoning models unreachable ({e}). Start uncensored-fleet: `fleet up vision reasoning`."
    return result


def to_geojson(result: dict) -> dict:
    """Render a :func:`locate` result as a standard GeoJSON FeatureCollection.

    Interoperates with QGIS, Leaflet, Mapbox, geojson.io and any GIS pipeline.
    Each EXIF-GPS fix becomes a Point feature; visual-clue candidates (which have
    no coordinates) are carried as properties on a metadata feature so nothing is
    lost when piping into a map. Coordinate order is [lon, lat] per RFC 7946.
    """
    features = []
    gps = result.get("exif_gps")
    if gps:
        lat, lon = gps
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [round(lon, 6), round(lat, 6)]},
            "properties": {
                "source": "exif_gps",
                "tool": result.get("tool", TOOL_NAME),
                "image": result.get("image", ""),
                "confidence": 0.99,
                "rationale": "embedded GPS metadata",
            },
        })
    # carry non-georeferenced visual candidates so the map keeps full context
    inferred = [c for c in result.get("candidates", []) if not str(c.get("place", "")).startswith("EXIF GPS")]
    if inferred or not features:
        features.append({
            "type": "Feature",
            "geometry": None,
            "properties": {
                "source": "visual_inference",
                "tool": result.get("tool", TOOL_NAME),
                "image": result.get("image", ""),
                "candidates": inferred,
                "clues": result.get("clues", ""),
                "note": result.get("note", ""),
            },
        })
    return {"type": "FeatureCollection", "features": features}
