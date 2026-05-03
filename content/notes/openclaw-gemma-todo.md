# Future OpenClaw + Gemma Integration Notes

- Add an OpenClaw nightly job that runs `npm run update:data`, then `npm run build`.
- Add a local Gemma MLX client after deterministic JSON generation and before recap Markdown indexing.
- Keep LLM output constrained to `/content/recaps` and optional short summary fields in `/data/generated/season-summary.json`.
- Commit only generated data/content/buildable source changes after validation passes.
- Push to GitHub and let Cloudflare Pages or GitHub Pages deploy from the static build.
- Add failure policy: if MLB or Savant APIs fail, keep the previous valid data and write a run report.
- Add source snapshots under `/data/raw` for debugging nightly changes.
