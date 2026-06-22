# 08 · Evidence chain + forward to STIX/MISP/Slack

For investigations you want (a) a stable hash of the source image for chain-of-custody
and (b) the location finding forwarded to your platform of record.

## Where the data comes from
`brandenburg_gate.jpg` carries the real public coordinate of the **Brandenburg Gate,
Berlin** (52.5163, 13.3777).

## Run
```bash
# 1. Record a content hash of the exact bytes you analyzed (stdlib only)
python -c "import hashlib;print(hashlib.sha256(open('demos/08-evidence-chain/brandenburg_gate.jpg','rb').read()).hexdigest())"

# 2. Get the location finding
locate demos/08-evidence-chain/brandenburg_gate.jpg --exif-only --format json > finding.json

# 3. Forward it to a platform via cognis-connect (optional [connect] extra)
pip install "git+https://github.com/cognis-digital/cognis-connect.git"
locateanything-emit --to stix  < finding.json      # STIX 2.1 bundle
locateanything-emit --to slack --url "$WEBHOOK" --dry-run < finding.json
```

## What to expect
- Step 1 prints `sha256=b1311b041a9550445901b260c509d7ea53473c5b7700c39ae3ee3b14a5133f8d`
  for the shipped file — record it alongside the case.
- Step 2 yields the JSON finding with `exif_gps: [52.5163, 13.3777]`.
- Step 3 maps the finding to STIX/MISP/Sigma/Splunk/Elastic/Slack/Discord/webhook.
  Without the `[connect]` extra it prints a one-line install hint and exits cleanly.

## How to act
Store the hash + the GeoJSON (demo 04) in your case file. The `--dry-run` flag lets you
inspect exactly what would be posted before sending anything to a live channel.
