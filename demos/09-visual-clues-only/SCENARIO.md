# 09 · No EXIF → visual-clue inference

The realistic hard case: screenshots, re-shared social media, and stripped images carry
**no** GPS metadata. Here the EXIF path returns nothing and the VL + reasoning models
do the work from visible clues.

## Where the data comes from
`street_scene.jpg` is a placeholder image deliberately saved **without** any EXIF GPS,
standing in for a re-shared photo whose metadata was stripped.

## Run
```bash
# Offline EXIF probe first — confirms there is no embedded fix
locate demos/09-visual-clues-only/street_scene.jpg --exif-only --format json

# Then the full inference path (needs the fleet)
fleet up vision reasoning
locate demos/09-visual-clues-only/street_scene.jpg --format json
```

## What to expect
- `--exif-only` returns `exif_gps: null`, empty `candidates`, and the note
  `"exif-only mode: no EXIF GPS embedded in this image."`
- The full path returns visual-inference candidates (country/city/landmark) with
  confidences and rationales drawn from signage, plates, architecture, flora and sun
  position. In `--format geojson` these come back as a `geometry: null` feature so they
  still ride into your map pipeline as context.

## How to act
When EXIF is absent, treat the visual candidates as investigative leads only and
corroborate (street-level imagery, known landmarks, language of signage) before relying
on any single guess.
