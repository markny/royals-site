# Nightly Prose Contract

This tells OpenClaw or a future local Gemma step which public-facing copy it may rewrite.

## Inputs

Use only generated fact files:

- `data/generated/season-summary.json`
- `data/generated/latest-game-details.json`
- `data/generated/latest-game-highlights.json`
- `data/generated/standings.json`
- `data/generated/prospects.json`
- `content/recaps/index.json`

## Fields OpenClaw May Improve

- `data/generated/season-summary.json`
  - `nightly_recap`
  - `player_of_game.reason`
- `content/recaps/index.json`
  - `items[0].summary`
  - `items[0].statcast_observation`
- The matching recap Markdown file in `content/recaps/*.md`

## Style

- Keep it short and factual.
- Write like a useful Royals fan notebook, not a newspaper beat story.
- Mention the final score, opponent, one or two key performers, and one concrete batted-ball or box-score detail.
- Prefer specific facts over flourish.
- Do not mention pipelines, templates, local LLMs, Gemma, OpenClaw, generated content, or placeholders in public site copy.

## Example Shape

```text
The Royals beat the Guardians, KC 6, CLE 2. Michael Wacha set the tone with seven efficient innings, while Bobby Witt Jr. and Jac Caglianone both homered. Witt also produced the loudest Royals contact at 107.1 mph.
```

## Safety Rules

- Do not invent injuries, transactions, quotes, or roster moves.
- If a fact is not in generated data, leave it out.
- If no completed game exists, write a neutral schedule-focused update.
- Preserve JSON structure exactly.
