# 07 · Maritime / port geolocation (suite interop)

Geolocating a dockside or port photo and handing the fix to a maritime-intelligence
workflow. Pairs naturally with
[maritimeint](https://github.com/cognis-digital/maritimeint) and the shared
`Finding` contract.

## Where the data comes from
`rotterdam_port.jpg` carries the real public coordinate of the **Maasvlakte deep-sea
terminals at the Port of Rotterdam** (51.9496, 4.1453), Europe's largest port.

## Run
```bash
locate demos/07-maritime-port/rotterdam_port.jpg --exif-only --format json
```

## What to expect
`exif_gps: [51.9496, 4.1453]` with a 0.99 EXIF candidate.

## How to act
Cross-reference the fix against AIS port-call data to confirm which berth/terminal,
then enrich vessel context in your maritime tooling. To forward the location as a
canonical finding (Slack, Splunk, STIX, …) see demo 08.
