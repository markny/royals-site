# Royals Season Tracker

A lightweight static website and local update pipeline for a personal Kansas City Royals season tracker. The project is built to become a small automated sports newsroom later: deterministic data first, generated prose second, static build last.

## Stack

- Vite + React for a static frontend
- Tailwind CSS for styling
- Python scripts for repeatable data fetching and content generation
- JSON in `data/generated` as the frontend data contract
- Markdown in `content/recaps` for daily recap artifacts

## Project Layout

```text
src/                  React app and UI components
scripts/              Local update pipeline
scripts/lib/          Shared Python helpers
data/raw/             Source snapshots from APIs
data/generated/       Normalized JSON consumed by the site
content/recaps/       Generated daily recap Markdown and index JSON
content/notes/        Future automation notes
public/               Static assets
```

## Local Setup

Install JavaScript dependencies:

```sh
npm install
```

Refresh baseball data and generated content:

```sh
npm run update:data
```

Run the local site:

```sh
npm run dev
```

Build static output:

```sh
npm run build
```

The static site is emitted to `dist/`, which is suitable for Cloudflare Pages, GitHub Pages, or any simple static host.

## Data Pipeline

The update flow is intentionally split:

1. `scripts/fetch_mlb.py`
   Fetches structured facts from the MLB Stats API and writes normalized JSON. This step should stay deterministic and non-creative.

2. `scripts/generate_content.py`
   Reads normalized facts and writes the site summary plus recap Markdown/index files. Today this uses deterministic templates.

3. Future Gemma MLX integration
   A local LLM can later replace or enrich the prose fields after the fact layer is generated.

4. Future OpenClaw orchestration
   OpenClaw can later run the update, validate the build, commit changes, push to GitHub, and rely on the static host to deploy.

## Current Data Sources

- MLB schedule, standings, hitting, and pitching stats use the public MLB Stats API.
- Statcast/Baseball Savant data is represented by a placeholder JSON layer for now.
- Prospect tracking is represented by curated placeholder data for now.

Both placeholder areas are deliberately isolated so they can be replaced without touching the frontend.

## Future TODOs

See `content/notes/openclaw-gemma-todo.md`.

Recommended next additions:

- Add Baseball Savant CSV or API ingestion for exit velocity, hard-hit rate, barrels, and pitcher quality-of-contact metrics.
- Add a prospect source or curated YAML/JSON file with nightly minor league stat refreshes.
- Add a Gemma MLX client that consumes `data/generated/*.json` and writes recap prose only.
- Add a validation script that checks JSON shape, required recap fields, and a successful static build.
- Add OpenClaw nightly orchestration, then automated commits and pushes.
