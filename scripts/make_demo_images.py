#!/usr/bin/env python3
"""Generate the EXIF-GPS-tagged sample images used by demos/.

Each image is a tiny synthetic placeholder JPEG whose *only* meaningful content is a
real, publicly documented GPS coordinate embedded in EXIF — so the demos can be run
end-to-end offline (`locate <img> --exif-only`) and produce verifiable output without
shipping anyone's real photos. Coordinates are well-known public landmarks / public
infrastructure; no private persons or property.

Run from the repo root:  python scripts/make_demo_images.py
"""
from __future__ import annotations
import sys
from pathlib import Path
from PIL import Image
from PIL.ExifTags import IFD

def _dms(v: float):
    v = abs(v)
    d = int(v); m = int((v - d) * 60); s = round((((v - d) * 60) - m) * 60, 4)
    return (float(d), float(m), float(s))

def write_gps_jpeg(path: Path, lat: float, lon: float, tint=(120, 140, 160)):
    img = Image.new("RGB", (96, 64), tint)
    exif = img.getexif()
    gps = exif.get_ifd(IFD.GPSInfo)
    gps[1] = "N" if lat >= 0 else "S"
    gps[2] = _dms(lat)
    gps[3] = "E" if lon >= 0 else "W"
    gps[4] = _dms(lon)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "JPEG", exif=exif)

def write_plain_jpeg(path: Path, tint=(90, 90, 90)):
    """An image with NO EXIF GPS (visual-clue-only scenario)."""
    img = Image.new("RGB", (96, 64), tint)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, "JPEG")

# (demo dir, filename, lat, lon)  — real public coordinates
GPS_IMAGES = [
    ("02-exif-gps-landmark", "eiffel_tower.jpg", 48.8584, 2.2945),       # Eiffel Tower, Paris
    ("03-batch-folder", "img_0001.jpg", 40.6892, -74.0445),             # Statue of Liberty, NYC
    ("03-batch-folder", "img_0002.jpg", 51.5007, -0.1246),              # Big Ben, London
    ("03-batch-folder", "img_0003.jpg", 35.6586, 139.7454),            # Tokyo Tower, Tokyo
    ("04-geojson-map", "sydney_opera_house.jpg", -33.8568, 151.2153),  # Sydney Opera House (S/E)
    ("05-southern-western", "machu_picchu.jpg", -13.1631, -72.5450),   # Machu Picchu, Peru (S/W)
    ("06-disaster-response", "golden_gate.jpg", 37.8199, -122.4783),   # Golden Gate Bridge, SF
    ("07-maritime-port", "rotterdam_port.jpg", 51.9496, 4.1453),       # Port of Rotterdam (Maasvlakte)
    ("08-evidence-chain", "brandenburg_gate.jpg", 52.5163, 13.3777),   # Brandenburg Gate, Berlin
]

PLAIN_IMAGES = [
    ("09-visual-clues-only", "street_scene.jpg"),   # no GPS → visual-inference path
]

def main():
    root = Path(__file__).resolve().parent.parent / "demos"
    for d, name, lat, lon in GPS_IMAGES:
        write_gps_jpeg(root / d / name, lat, lon)
        print(f"wrote {d}/{name}  ({lat}, {lon})")
    for d, name in PLAIN_IMAGES:
        write_plain_jpeg(root / d / name)
        print(f"wrote {d}/{name}  (no EXIF GPS)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
