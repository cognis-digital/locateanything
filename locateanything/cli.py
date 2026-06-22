"""locateanything CLI."""
import argparse, json, sys
from locateanything.core import locate, to_geojson, TOOL_NAME, TOOL_VERSION
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="locate", description="Infer where a photo was taken (local VL + reasoning model).")
    ap.add_argument("--version", action="version", version=f"{TOOL_NAME} {TOOL_VERSION}")
    ap.add_argument("image", help="path to an image")
    ap.add_argument("--format", choices=["table", "json", "geojson"], default="table")
    ap.add_argument("--exif-only", action="store_true",
                    help="offline, deterministic: use only embedded EXIF GPS, skip the VL/reasoning models")
    a = ap.parse_args(argv)
    res = locate(a.image, exif_only=a.exif_only)
    if a.format == "json":
        print(json.dumps(res, indent=2)); return 0
    if a.format == "geojson":
        print(json.dumps(to_geojson(res), indent=2)); return 0
    print(f"[{TOOL_NAME}] {a.image}  exif_gps={res.get('exif_gps')}")
    for c in res.get("candidates", []):
        print(f"  {c['confidence']:.2f}  {c['place']}  — {c['rationale']}")
    if res.get("note"): print("  ! " + res["note"])
    return 0
if __name__ == "__main__":
    sys.exit(main())
