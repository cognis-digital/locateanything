"""Tests for the offline EXIF path, --exif-only mode, and GeoJSON export."""
from __future__ import annotations

import json

import pytest

from locateanything.core import exif_gps, locate, to_geojson, TOOL_NAME
from locateanything import cli

Image = pytest.importorskip("PIL.Image", reason="Pillow [img] extra not installed")
from PIL.ExifTags import IFD  # noqa: E402


def _dms(v):
    v = abs(v)
    d = int(v); m = int((v - d) * 60); s = round((((v - d) * 60) - m) * 60, 4)
    return (float(d), float(m), float(s))


def _make_gps_jpeg(path, lat, lon):
    img = Image.new("RGB", (32, 24), (120, 140, 160))
    exif = img.getexif()
    gps = exif.get_ifd(IFD.GPSInfo)
    gps[1] = "N" if lat >= 0 else "S"; gps[2] = _dms(lat)
    gps[3] = "E" if lon >= 0 else "W"; gps[4] = _dms(lon)
    img.save(str(path), "JPEG", exif=exif)


def _make_plain_jpeg(path):
    Image.new("RGB", (32, 24), (90, 90, 90)).save(str(path), "JPEG")


@pytest.mark.parametrize("lat,lon", [
    (48.8584, 2.2945),     # N/E  Paris
    (40.6892, -74.0445),   # N/W  New York
    (-33.8568, 151.2153),  # S/E  Sydney
    (-13.1631, -72.5450),  # S/W  Machu Picchu
])
def test_exif_roundtrip_all_quadrants(tmp_path, lat, lon):
    p = tmp_path / "g.jpg"
    _make_gps_jpeg(p, lat, lon)
    got = exif_gps(str(p))
    assert got is not None
    assert got[0] == pytest.approx(lat, abs=1e-3)
    assert got[1] == pytest.approx(lon, abs=1e-3)


def test_exif_only_skips_models_and_returns_candidate(tmp_path):
    p = tmp_path / "g.jpg"
    _make_gps_jpeg(p, 52.5163, 13.3777)
    res = locate(str(p), exif_only=True)
    assert res["tool"] == TOOL_NAME
    assert res["exif_gps"][0] == pytest.approx(52.5163, abs=1e-3)
    assert res["candidates"] and res["candidates"][0]["confidence"] == 0.99
    assert "clues" not in res  # models were not consulted


def test_exif_only_no_gps_notes_cleanly(tmp_path):
    p = tmp_path / "plain.jpg"
    _make_plain_jpeg(p)
    res = locate(str(p), exif_only=True)
    assert res["exif_gps"] is None
    assert res["candidates"] == []
    assert "exif-only" in res["note"]


def test_geojson_point_uses_lon_lat_order(tmp_path):
    p = tmp_path / "g.jpg"
    _make_gps_jpeg(p, -33.8568, 151.2153)
    fc = to_geojson(locate(str(p), exif_only=True))
    assert fc["type"] == "FeatureCollection"
    pt = [f for f in fc["features"] if f["geometry"]][0]
    assert pt["geometry"]["type"] == "Point"
    lon, lat = pt["geometry"]["coordinates"]
    assert lon == pytest.approx(151.2153, abs=1e-3)   # longitude first
    assert lat == pytest.approx(-33.8568, abs=1e-3)


def test_geojson_no_gps_emits_metadata_feature(tmp_path):
    p = tmp_path / "plain.jpg"
    _make_plain_jpeg(p)
    fc = to_geojson(locate(str(p), exif_only=True))
    assert fc["features"] and fc["features"][0]["geometry"] is None
    assert fc["features"][0]["properties"]["source"] == "visual_inference"


def test_cli_geojson_format(tmp_path, capsys):
    p = tmp_path / "g.jpg"
    _make_gps_jpeg(p, 48.8584, 2.2945)
    rc = cli.main([str(p), "--exif-only", "--format", "geojson"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["type"] == "FeatureCollection"
