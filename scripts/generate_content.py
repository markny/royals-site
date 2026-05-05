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
from lib.run_context import as_of_date


def latest_completed_game(games):
    completed = [game for game in games if game.get("result") in {"W", "L"}]
    return completed[-1] if completed else None


def next_scheduled_game(games):
    today = as_of_date().isoformat()
    for game in games:
        if game.get("result") == "TBD" and (game.get("date") or "") >= today:
            return game
    return {"date": as_of_date().isoformat(), "opponent": "TBD", "time_local": "TBD"}


def parse_ip(value):
    if not value:
        return 0
    whole, _, partial = str(value).partition(".")
    outs = int(whole or 0) * 3 + int(partial or 0)
    return outs / 3


def latest_royals_hard_contact(game_details):
    royals = {row.get("player") for row in game_details.get("royals_boxscore", {}).get("batting", [])}
    for ball in game_details.get("batted_balls", {}).get("hardest", []):
        if ball.get("batter") in royals:
            return ball
    return None


def player_of_game(game_details):
    candidates = []
    for row in game_details.get("royals_boxscore", {}).get("batting", []):
        summary = row.get("summary", "")
        score = row.get("h", 0) + row.get("rbi", 0) * 1.4 + row.get("r", 0) * 0.7 + row.get("bb", 0) * 0.5
        if "HR" in summary:
            score += 4
        if "2B" in summary:
            score += 1
        if "3B" in summary:
            score += 2
        candidates.append(
            {
                "name": row.get("player", "TBD"),
                "score": score,
                "reason": f"{summary} in the latest Royals game.",
            }
        )

    for row in game_details.get("royals_boxscore", {}).get("pitching", []):
        ip = parse_ip(row.get("ip"))
        er = row.get("er", 0)
        score = ip * 2 + row.get("so", 0) * 0.5 - er * 2 - row.get("h", 0) * 0.3 - row.get("bb", 0) * 0.5
        if ip >= 6 and er <= 2:
            score += 4
        walk_text = "walk" if row.get("bb", 0) == 1 else "walks"
        candidates.append(
            {
                "name": row.get("player", "TBD"),
                "score": score,
                "reason": (
                    f"worked {row.get('ip', '0.0')} innings with {row.get('er', 0)} earned runs, "
                    f"{row.get('so', 0)} strikeouts and {row.get('bb', 0)} {walk_text}."
                ),
            }
        )

    if not candidates:
        return {"name": "TBD", "reason": "No latest-game box score is available yet."}
    winner = max(candidates, key=lambda item: item["score"])
    return {"name": winner["name"], "reason": winner["reason"]}


def deterministic_recap(latest, player, hard_contact):
    if not latest:
        return "No completed Royals game is available yet."
    contact = ""
    if hard_contact:
        contact = (
            f" {hard_contact['batter']} supplied the loudest Royals contact at "
            f"{hard_contact['exit_velocity']} mph."
        )
    result_word = {"W": "beat", "L": "lost to", "T": "tied"}.get(latest.get("result"), "played")
    reason = player["reason"]
    if reason.startswith("worked "):
        reason = f"working {reason.removeprefix('worked ')}"
    return (
        f"The Royals {result_word} the {latest.get('opponent', 'opponent')}, "
        f"{latest.get('score', 'latest score')}. {player['name']} led the night, "
        f"{reason}{contact}"
    )


def build_season_summary(game_log, standings, hitting, pitching, prospects, game_details):
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
    best_pitcher = max(pitching.get("players", []), key=lambda row: row.get("so", 0), default={"player": "TBD", "so": 0})
    hot_prospect = prospects.get("hot_prospects", [{"name": "TBD", "note": "Prospect tracker awaiting updates."}])[0]
    game_player = player_of_game(game_details)
    hard_contact = latest_royals_hard_contact(game_details)

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
        "nightly_recap": deterministic_recap(last_game, game_player, hard_contact),
        "player_of_game": game_player,
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


def build_recap_index(game_log, season_summary, game_details):
    latest = latest_completed_game(game_log.get("games", []))
    if not latest:
        latest = {
            "date": as_of_date().isoformat(),
            "score": "No completed game",
            "matchup": "Royals schedule",
            "recap_slug": "sample-royals-recap",
        }
    slug = latest.get("recap_slug") or f"{latest.get('date')}-royals-recap"
    hard_contact = latest_royals_hard_contact(game_details)
    statcast_note = "No batted-ball detail is available yet."
    if hard_contact:
        statcast_note = (
            f"{hard_contact['batter']} produced the hardest tracked Royals contact: "
            f"{hard_contact['exit_velocity']} mph at a {hard_contact['launch_angle']} degree launch angle."
        )
    recap = {
        "slug": slug,
        "date": latest.get("date"),
        "title": f"{latest.get('matchup', 'Royals')} Recap",
        "summary": season_summary.get("nightly_recap", f"{latest.get('score')} was the latest completed Royals result."),
        "key_performers": [
            name
            for name in dict.fromkeys(
                [
                    season_summary.get("player_of_game", {}).get("name", "TBD"),
                    hard_contact.get("batter") if hard_contact else None,
                ]
            )
            if name
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
    game_details = read_json(GENERATED_DIR / "latest-game-details.json", {})

    season_summary = build_season_summary(game_log, standings, hitting, pitching, prospects, game_details)
    write_json(GENERATED_DIR / "season-summary.json", season_summary)
    write_json(RECAP_DIR / "index.json", build_recap_index(game_log, season_summary, game_details))


if __name__ == "__main__":
    main()
