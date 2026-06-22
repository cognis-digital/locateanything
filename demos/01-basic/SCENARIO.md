# 01 · Basic run (full VL + reasoning)

The headline use case: drop in a photo, get ranked location guesses with rationale.
This path uses the local vision and reasoning models, so it needs the
[uncensored-fleet](https://github.com/cognis-digital/uncensored-fleet) `vision` and
`reasoning` slots running.

## Where the data comes from
Any photo you want to geolocate — a field photo, an open-source image you are
authorized to analyze, a frame from footage you have rights to.

## Run
```bash
fleet up vision reasoning          # start the local models
locate sample.jpg                  # ranked candidates + rationale
locate sample.jpg --format json    # machine-readable
```

## What to expect
A table (or JSON) with `exif_gps` (if the photo carries GPS metadata) plus 1–3
inferred candidates, each with a confidence and a one-line rationale drawn from
visible signage, plate styles, architecture, vegetation, road markings and sun
position.

## How to act
Treat candidates as leads, not proof. Corroborate with a second source before you
rely on a location. If you only need the metadata fix and want a deterministic,
offline run, see **demo 02** (`--exif-only`).
