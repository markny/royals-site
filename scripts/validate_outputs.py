#!/usr/bin/env python3
"""Validate generated files before an automated commit."""

import sys
from datetime import date

from lib.io import read_json
from lib.paths import GENERATED_DIR, RECAP_DIR
from lib.run_context import as_of_date


def fail(message):
    print(f"Validation failed: {message}", file=sys.stderr)
    sys.exit(1)


def require(path):
    data = read_json(path)
    if data is None:
        fail(f"missing {path}")
    return data


def main():
    season = require(GENERATED_DIR / "season-summary.json")
    require(GENERATED_DIR / "game-log.json")
    require(GENERATED_DIR / "standings.json")
    require(GENERATED_DIR / "hitting-stats.json")
    require(GENERATED_DIR / "hitting-sabermetrics.json")
    require(GENERATED_DIR / "pitching-stats.json")
    require(GENERATED_DIR / "latest-game-details.json")
    require(GENERATED_DIR / "latest-game-highlights.json")
    require(GENERATED_DIR / "scoreboard.json")
    prospects = require(GENERATED_DIR / "prospects.json")
    recaps = require(RECAP_DIR / "index.json")

    next_game = season.get("next_game", {})
    next_date = next_game.get("date")
    if not next_date:
        fail("season-summary next_game.date is empty")
    if date.fromisoformat(next_date) < as_of_date():
        fail(f"next_game.date {next_date} is before as-of date {as_of_date().isoformat()}")
    if not next_game.get("opponent") or next_game.get("opponent") == "TBD":
        fail("next_game opponent is missing")

    if not prospects.get("prospects"):
        fail("prospect list is empty")
    if not recaps.get("items"):
        fail("recap index is empty")

    forbidden_public_phrases = ["local pipeline", "local LLM", "Gemma", "OpenClaw", "placeholder", "template"]
    public_text = " ".join(
        [
            season.get("nightly_recap", ""),
            season.get("player_of_game", {}).get("reason", ""),
            recaps.get("items", [{}])[0].get("summary", ""),
            recaps.get("items", [{}])[0].get("statcast_observation", ""),
        ]
    )
    for phrase in forbidden_public_phrases:
        if phrase.lower() in public_text.lower():
            fail(f"public copy contains forbidden phrase: {phrase}")

    print("Generated data validation passed.")


if __name__ == "__main__":
    main()
