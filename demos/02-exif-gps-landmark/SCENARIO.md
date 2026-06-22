# 02 · EXIF GPS fix, offline (no models needed)

Many photos already carry a GPS fix in EXIF. `--exif-only` reads it locally with
zero network calls and zero models — deterministic, air-gap friendly, CI-safe.

## Where the data comes from
`eiffel_tower.jpg` is a synthetic placeholder image carrying the real, public
coordinate of the **Eiffel Tower, Paris** (48.8584, 2.2945) in its EXIF GPS tags.
No real photo of anyone is shipped — only the metadata matters for this path.

## Run
```bash
locate demos/02-exif-gps-landmark/eiffel_tower.jpg --exif-only --format json
```

## What to expect
```json
{
  "tool": "locateanything",
  "image": "demos/02-exif-gps-landmark/eiffel_tower.jpg",
  "exif_gps": [48.8584, 2.2945],
  "candidates": [
    {"place": "EXIF GPS 48.8584,2.2945", "confidence": 0.99, "rationale": "embedded GPS metadata"}
  ]
}
```

## How to act
A 0.99-confidence EXIF fix is the strongest signal this tool emits — but EXIF can be
edited or stripped, so still confirm provenance. Paste `48.8584,2.2945` into any map
to confirm. Use `--format geojson` (demo 04) to drop the point straight onto a map.
