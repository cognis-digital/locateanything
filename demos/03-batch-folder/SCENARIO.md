# 03 · Batch a folder into JSONL

A common OSINT/triage task: you have a folder of images and want one machine-readable
line per image to feed a pipeline, a spreadsheet, or a SIEM.

## Where the data comes from
Three synthetic placeholder images, each carrying a real public landmark coordinate
in EXIF:
- `img_0001.jpg` → Statue of Liberty, New York (40.6892, -74.0445)
- `img_0002.jpg` → Big Ben / Palace of Westminster, London (51.5007, -0.1246)
- `img_0003.jpg` → Tokyo Tower, Tokyo (35.6586, 139.7454)

## Run
```bash
for f in demos/03-batch-folder/*.jpg; do
  locate "$f" --exif-only --format json
done > all_locations.jsonl
```

(Drop `--exif-only` to also run the VL + reasoning models when the fleet is up.)

## What to expect
Three JSON objects — one per image — each with the correct `exif_gps` pair and a
0.99 EXIF candidate. Notice the mixed hemispheres: New York is West, London is on the
prime meridian (negative longitude), Tokyo is far East.

## How to act
Load `all_locations.jsonl` into your pipeline. To convert any single line to a map
feature, pipe it through `--format geojson` (demo 04), or forward the whole batch to
STIX/MISP/Slack/Splunk with `locateanything-emit` (demo 08).
