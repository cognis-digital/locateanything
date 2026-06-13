<a name="top"></a>
<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:6b46c1,100:cc0066&height=180&section=header&text=locateanything&fontSize=52&fontColor=ffffff&fontAlignY=42" width="100%"/>

# locateanything

### Drop in a photo → get ranked location guesses. 100% local, powered by an uncensored vision + reasoning model.

[![License: COCL 1.0](https://img.shields.io/badge/License-COCL%201.0-2b6cb0.svg)](LICENSE) ![Local](https://img.shields.io/badge/runs-100%25%20local-111111) ![MCP](https://img.shields.io/badge/MCP-native-black) [![Suite](https://img.shields.io/badge/Cognis-Neural%20Suite-6b46c1.svg)](https://github.com/cognis-digital/cognis-neural-suite)

`#osint` `#geoint` `#geolocation` `#llm` `#vision` `#self-hosted`

</div>

A local **GeoGuessr-for-real-life**: it reads EXIF GPS *and* reasons over visual clues (signage, plates,
architecture, flora, sun position) using a local **uncensored vision-language model** + a **reasoning model** —
no cloud, no API keys, nothing uploaded.

```bash
pip install "cognis-locateanything[img]"
fleet up vision reasoning      # via https://github.com/cognis-digital/uncensored-fleet
locate photo.jpg               # → ranked candidates + rationale
locate photo.jpg --format json
```

## Usage — step by step

1. Install the CLI (console-script: `locate`):
   ```bash
   pipx install "git+https://github.com/cognis-digital/locateanything.git"
   locate --version
   ```
2. Infer where a photo was taken (runs entirely on a local vision + reasoning model):
   ```bash
   locate ./photo.jpg
   ```
3. Get machine-readable output for pipelines or evidence logs:
   ```bash
   locate ./photo.jpg --format json > location.json
   ```
4. Read the result — parse the JSON for the inferred location and rationale:
   ```bash
   jq '.' location.json
   ```
5. In CI/batch, loop over a folder of images and collect findings:
   ```bash
   for f in images/*.jpg; do locate "$f" --format json; done > all_locations.jsonl
   ```

## Architecture

```mermaid
flowchart LR
  IMG[📷 image] --> EXIF[EXIF GPS parse]
  IMG --> VL[Uncensored VL model<br/>visual clues]
  EXIF --> R[Reasoning model<br/>rank candidates]
  VL --> R
  R --> OUT[Ranked locations + rationale<br/>table / JSON / MCP]
```

## Use it from any AI stack
- **MCP server** (`locate mcp`) for Claude Desktop / Cursor / [uncensored-fleet](https://github.com/cognis-digital/uncensored-fleet)
- **JSON** output pipes into any agent · **LangChain/CrewAI** tool in one line · plain **CLI**

## ⚠️ Responsible use
For OSINT, journalism, and research. **Get consent** before geolocating images of people or private
property, and comply with local law. You are responsible for your use.

## Related
[🤖 uncensored-fleet](https://github.com/cognis-digital/uncensored-fleet) · [🧠 engram](https://github.com/cognis-digital/engram) · [🔍 geolens](https://github.com/cognis-digital/geolens) · [🗂️ the suite](https://github.com/cognis-digital/cognis-neural-suite)

> ### ⭐ If this is cool, star it — it helps others find it.

## Interoperability

`{}` composes with the 300+ tool Cognis suite — JSON in/out and a shared
OpenAI-compatible `/v1` backbone. See **[INTEROP.md](INTEROP.md)** for the
suite map, composition patterns, and reference stacks.

## License
COCL v1.0 — see [LICENSE](LICENSE).
