# 06 · Disaster-response / situational awareness

During an incident, responders and OSINT analysts triage inbound photos to map where
each was taken. The offline EXIF path gives an instant, network-free fix you can drop
on a coordination map.

## Where the data comes from
`golden_gate.jpg` carries the real public coordinate of the **Golden Gate Bridge,
San Francisco** (37.8199, -122.4783), standing in for a geotagged photo of critical
infrastructure submitted to an incident desk.

## Run
```bash
# fix + GeoJSON in one step, ready for the situation map
locate demos/06-disaster-response/golden_gate.jpg --exif-only --format geojson
```

## What to expect
A single Point feature at `[-122.4783, 37.8199]` with `source: "exif_gps"`.

## How to act
Pin it on the common operating picture. For images **without** EXIF (the usual case
for screenshots and re-shared media), fall back to the VL + reasoning path (demo 01)
to get visual-clue candidates, and corroborate before tasking resources.

> Authorized response and force-protection use only. Get consent before geolocating
> images of identifiable people or private property, and comply with local law.
