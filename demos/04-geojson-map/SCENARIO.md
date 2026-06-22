# 04 · GeoJSON export → drop straight onto a map

`--format geojson` emits an RFC 7946 `FeatureCollection`. Paste it into
[geojson.io](https://geojson.io), load it in QGIS, or feed it to Leaflet/Mapbox.

## Where the data comes from
`sydney_opera_house.jpg` carries the real public coordinate of the **Sydney Opera
House** (-33.8568, 151.2153) — a Southern + Eastern hemisphere fix, which exercises
the negative-latitude / positive-longitude path.

## Run
```bash
locate demos/04-geojson-map/sydney_opera_house.jpg --exif-only --format geojson > opera.geojson
```

## What to expect
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {"type": "Point", "coordinates": [151.2153, -33.8568]},
      "properties": {"source": "exif_gps", "confidence": 0.99, "rationale": "embedded GPS metadata"}
    }
  ]
}
```

Note the coordinate order is **[longitude, latitude]** as required by GeoJSON.

## How to act
Open `opera.geojson` at geojson.io to see the pin land on the harbour. When the VL +
reasoning models add visual-inference candidates (no coordinates), they ride along in
a second feature with `geometry: null` so nothing is lost on the map.
