# Nightly Update Runbook

This is the intended contract for a future OpenClaw nightly job.

## Goal

Refresh deterministic baseball data, generate local recap-ready content, validate the output, build the static site, then commit and push only if everything passes.

## Required Inputs

- Repository checkout with dependencies installed.
- Network access to public MLB Stats API endpoints.
- `TRACKER_AS_OF_DATE` set to the intended update date in `YYYY-MM-DD` format.

Use an explicit date instead of trusting the host clock. This prevents stale next-game selection if the runner clock is wrong.

## Command Sequence

For Monday, May 4, 2026:

```sh
python3 scripts/build_all.py --date 2026-05-04
TRACKER_AS_OF_DATE=2026-05-04 python3 scripts/validate_outputs.py
npm run test:dates
npm run build
```

For a normal nightly run, OpenClaw should compute the local Eastern date and pass it explicitly:

```sh
python3 scripts/build_all.py --date "$RUN_DATE"
TRACKER_AS_OF_DATE="$RUN_DATE" python3 scripts/validate_outputs.py
npm run test:dates
npm run build
```

## Generated Files

- `data/generated/season-summary.json`
- `data/generated/game-log.json`
- `data/generated/standings.json`
- `data/generated/hitting-stats.json`
- `data/generated/hitting-sabermetrics.json`
- `data/generated/pitching-stats.json`
- `data/generated/latest-game-details.json`
- `data/generated/latest-game-highlights.json`
- `data/generated/scoreboard.json`
- `data/generated/prospects.json`
- `content/recaps/index.json`
- `content/recaps/*.md`
- `data/raw/*.json` source snapshots

## Commit Policy

Only commit after all validation and build steps pass.

Suggested commit message:

```text
Update Royals tracker data for YYYY-MM-DD
```

## Failure Policy

- If MLB API fetches fail, do not commit broken or partial output.
- If validation fails, leave the workspace dirty for inspection and report the failed check.
- If the static build fails, do not push.
- Future enhancement: preserve previous known-good generated files when a source fetch fails.

## Future Gemma Step

When the local Gemma MLX server is added, insert it after deterministic data generation and before validation:

```sh
python3 scripts/build_all.py --date "$RUN_DATE"
python3 scripts/generate_llm_recaps.py --date "$RUN_DATE"
TRACKER_AS_OF_DATE="$RUN_DATE" python3 scripts/validate_outputs.py
npm run test:dates
npm run build
```

The LLM should write prose only to `content/recaps` and approved summary fields in `data/generated/season-summary.json`.

Use `docs/nightly-prose-contract.md` for field ownership, style, and safety rules.
