# 05 · Southern + Western hemisphere (sign handling)

A correctness demo: EXIF stores latitude/longitude as positive DMS plus a N/S/E/W
reference. Getting the sign wrong silently flips a location to the wrong hemisphere.

## Where the data comes from
`machu_picchu.jpg` carries the real public coordinate of **Machu Picchu, Peru**
(-13.1631, -72.5450) — South latitude AND West longitude, the case most likely to
expose a sign bug.

## Run
```bash
locate demos/05-southern-western/machu_picchu.jpg --exif-only --format json
```

## What to expect
```json
"exif_gps": [-13.1631, -72.545]
```
Both values negative. If you ever see `[13.16, 72.54]` (which lands in the Arabian
Sea), the S/W reference handling is broken.

## How to act
Use this image as a regression check after touching `exif_gps()` in `core.py`. Any
geolocation tool must round-trip all four hemisphere quadrants correctly.
