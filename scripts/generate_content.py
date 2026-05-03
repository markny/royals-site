#!/usr/bin/env python3
"""Generate local narrative-ready content from deterministic data.

Future Gemma/MLX work should plug in after this script has assembled facts.
Keep facts and prose separated: facts come from data/generated, prose is written
to content/recaps and indexed as JSON for the static frontend.
"""

from datetime import date, datetime
from zoneinfo import ZoneInfo

from lib.io import now_iso, read_json, write_json
from lib.paths import GENERATED_DIR, RECAP_DIR, ensure_dirs


def latest_completed_game(games):
    completed = [game for game in games if game.get("result") in {"W", "L"}]
    return completed[-1] if completed else None


def next_scheduled_game(games):
    today = date.today().isoformat()
    for game in games:
        if game.get("result") == "TBD" and (game.get("date") or "") >= today:
            return game
    return {"date": date.today().isoformat(), "opponent": "TBD", "time_local": "TBD"}


def build_season_summary(game_log, standings, hitting, pitching, prospects):
    royals_entry = standings.get("royals_entry") or next(
        (team for team in standings.get("al_central", []) if team.get("team") == "Kansas City Royals"),
        {"wins": 0, "losses": 0, "pct": 0, "games_back": "-", "streak": "-"},
    )
    record = {
        "wins": royals_entry.get("wins", 0),
        "losses": royals_entry.get("losses", 0),
        "games_played": royals_entry.get("wins", 0) + royals_entry.get("losses", 0),
        "win_pct": royals_entry.get("pct", 0),
    }
    last_game = latest_completed_game(game_log.get("games", [])) or {}
    next_game = next_scheduled_game(game_log.get("games", []))
    hitters = hitting.get("players", [])
    qualified_hitters = [row for row in hitters if row.get("ab", 0) >= 40] or hitters
    best_hitter = max(qualified_hitters, key=lambda row: row.get("ops", 0), default={"player": "TBD", "ops": 0})
    best_pitcher = max(pitching.get("players", []), key=lambda row: row.get("so", 0), default={"player": "TBD", "so": 0})
    hot_prospect = prospects.get("hot_prospects", [{"name": "TBD", "note": "Prospect tracker awaiting updates."}])[0]

    next_time = "TBD"
    if next_game.get("game_datetime"):
        next_time = (
            datetime.fromisoformat(next_game["game_datetime"].replace("Z", "+00:00"))
            .astimezone(ZoneInfo("America/New_York"))
            .strftime("%-I:%M %p ET")
        )

    return {
        "generated_at": now_iso(),
        "headline": "A compact command center for the Royals season",
        "record": record,
        "division_rank": f"{royals_entry.get('games_back', '-')} GB in the AL Central",
        "last_game": {
            "date": last_game.get("date"),
            "opponent": last_game.get("opponent", "TBD"),
            "score": last_game.get("score", "TBD"),
            "short_result": f"{last_game.get('result', 'TBD')} {last_game.get('score', '')}".strip(),
        },
        "next_game": {
            "date": next_game.get("date"),
            "opponent": next_game.get("opponent", "TBD"),
            "site": next_game.get("site", "TBD"),
            "home_away": next_game.get("home_away", "TBD"),
            "venue": next_game.get("venue", "TBD"),
            "matchup": next_game.get("matchup", "Royals schedule"),
            "probable_pitchers": next_game.get(
                "probable_pitchers",
                {
                    "royals": {"id": None, "name": "TBD"},
                    "opponent": {"id": None, "name": "TBD"},
                },
            ),
            "time_local": next_time,
        },
        "nightly_recap": (
            "The local pipeline has refreshed the structured baseball facts and prepared the recap layer. "
            "Future Gemma summaries can replace this deterministic placeholder without changing the frontend."
        ),
        "player_of_game": {
            "name": best_hitter.get("player", "TBD"),
            "reason": f"Current OPS leader at {best_hitter.get('ops', 0)}; pair this with nightly game context later.",
        },
        "pitcher_watch": {
            "name": best_pitcher.get("player", "TBD"),
            "reason": f"Strikeout leader with {best_pitcher.get('so', 0)} punchouts.",
        },
        "latest_prospect_update": hot_prospect,
    }


def write_recap_markdown(recap):
    path = RECAP_DIR / f"{recap['slug']}.md"
    body = f"""---
title: "{recap['title']}"
date: "{recap['date']}"
source: "deterministic-template"
llm_ready: true
---

{recap['summary']}

## Key Performers

{chr(10).join(f"- {player}" for player in recap['key_performers'])}

## Statcast Notes

{recap['statcast_observation']}

## Standings Implication

{recap['standings_implication']}
"""
    path.write_text(body, encoding="utf-8")


def build_recap_index(game_log, season_summary, statcast):
    latest = latest_completed_game(game_log.get("games", []))
    if not latest:
        latest = {
            "date": date.today().isoformat(),
            "score": "No completed game",
            "matchup": "Royals schedule",
            "recap_slug": "sample-royals-recap",
        }
    slug = latest.get("recap_slug") or f"{latest.get('date')}-royals-recap"
    statcast_note = statcast.get("players", [{}])[0].get(
        "note",
        "Statcast observations will be generated after Baseball Savant ingestion is added.",
    )
    recap = {
        "slug": slug,
        "date": latest.get("date"),
        "title": f"{latest.get('matchup', 'Royals')} Recap",
        "summary": (
            f"{latest.get('score')} is indexed as the latest completed Royals result. "
            "This template keeps the recap factual until a local LLM adds nightly color."
        ),
        "key_performers": [
            season_summary.get("player_of_game", {}).get("name", "TBD"),
            season_summary.get("pitcher_watch", {}).get("name", "TBD"),
        ],
        "statcast_observation": statcast_note,
        "standings_implication": season_summary.get("division_rank", "Standings context pending."),
        "standings_delta": 0,
    }
    write_recap_markdown(recap)
    return {"generated_at": now_iso(), "items": [recap]}


def main():
    ensure_dirs()
    game_log = read_json(GENERATED_DIR / "game-log.json", {"games": []})
    standings = read_json(GENERATED_DIR / "standings.json", {"al_central": []})
    hitting = read_json(GENERATED_DIR / "hitting-stats.json", {"players": []})
    pitching = read_json(GENERATED_DIR / "pitching-stats.json", {"players": []})
    prospects = read_json(GENERATED_DIR / "prospects.json", {"hot_prospects": []})
    statcast = read_json(GENERATED_DIR / "statcast-metrics.json", {"players": []})

    season_summary = build_season_summary(game_log, standings, hitting, pitching, prospects)
    write_json(GENERATED_DIR / "season-summary.json", season_summary)
    write_json(RECAP_DIR / "index.json", build_recap_index(game_log, season_summary, statcast))


if __name__ == "__main__":
    main()
