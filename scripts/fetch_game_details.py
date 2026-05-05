#!/usr/bin/env python3
"""Fetch high-value game details that make the site useful day to day."""

from collections import defaultdict

from lib.io import now_iso, read_json, write_json
from lib.mlb_api import MlbApiError, get_json
from lib.paths import GENERATED_DIR, RAW_DIR, ensure_dirs
from lib.run_context import as_of_date


def latest_completed_game(games):
    completed = [game for game in games if game.get("result") in {"W", "L", "T"}]
    return completed[-1] if completed else None


def batting_rows(team_box):
    rows = []
    for player_id in team_box.get("batters", []):
        player = team_box.get("players", {}).get(f"ID{player_id}", {})
        stats = player.get("stats", {}).get("batting", {})
        if not stats or stats.get("plateAppearances", 0) == 0:
            continue
        rows.append(
            {
                "player": player.get("person", {}).get("fullName", "Player"),
                "summary": stats.get("summary", ""),
                "ab": stats.get("atBats", 0),
                "r": stats.get("runs", 0),
                "h": stats.get("hits", 0),
                "rbi": stats.get("rbi", 0),
                "bb": stats.get("baseOnBalls", 0),
                "so": stats.get("strikeOuts", 0),
            }
        )
    return rows


def pitching_rows(team_box):
    rows = []
    for player_id in team_box.get("pitchers", []):
        player = team_box.get("players", {}).get(f"ID{player_id}", {})
        stats = player.get("stats", {}).get("pitching", {})
        if not stats or stats.get("battersFaced", 0) == 0:
            continue
        rows.append(
            {
                "player": player.get("person", {}).get("fullName", "Player"),
                "summary": stats.get("summary", ""),
                "ip": stats.get("inningsPitched", "0.0"),
                "h": stats.get("hits", 0),
                "r": stats.get("runs", 0),
                "er": stats.get("earnedRuns", 0),
                "bb": stats.get("baseOnBalls", 0),
                "so": stats.get("strikeOuts", 0),
                "pitches": stats.get("numberOfPitches", 0),
            }
        )
    return rows


def batted_balls(play_by_play):
    balls = []
    by_batter = defaultdict(lambda: {"count": 0, "hard_hit": 0, "max_ev": 0, "total_ev": 0})
    for play in play_by_play.get("allPlays", []):
        batter = play.get("matchup", {}).get("batter", {}).get("fullName", "Batter")
        for event in play.get("playEvents", []):
            hit_data = event.get("hitData")
            ev = hit_data.get("launchSpeed") if hit_data else None
            if ev is None:
                continue
            launch_angle = hit_data.get("launchAngle")
            distance = hit_data.get("totalDistance")
            row = {
                "batter": batter,
                "event": play.get("result", {}).get("event", ""),
                "exit_velocity": ev,
                "launch_angle": launch_angle,
                "distance": distance,
                "trajectory": hit_data.get("trajectory"),
                "hardness": hit_data.get("hardness"),
            }
            balls.append(row)
            summary = by_batter[batter]
            summary["count"] += 1
            summary["hard_hit"] += 1 if ev >= 95 else 0
            summary["max_ev"] = max(summary["max_ev"], ev)
            summary["total_ev"] += ev

    balls.sort(key=lambda row: row["exit_velocity"], reverse=True)
    batter_summary = []
    for batter, summary in by_batter.items():
        count = summary["count"]
        batter_summary.append(
            {
                "batter": batter,
                "batted_balls": count,
                "max_exit_velocity": round(summary["max_ev"], 1),
                "avg_exit_velocity": round(summary["total_ev"] / count, 1) if count else 0,
                "hard_hit_pct": round((summary["hard_hit"] / count) * 100, 1) if count else 0,
            }
        )
    batter_summary.sort(key=lambda row: (row["max_exit_velocity"], row["hard_hit_pct"]), reverse=True)
    return balls, batter_summary


def playback_url(item):
    preferred = ["mp4Avc", "HTTP_CLOUD_WIRED", "HTTP_CLOUD_WIRED_60", "hlsCloud"]
    playbacks = item.get("playbacks", [])
    for name in preferred:
        for playback in playbacks:
            if playback.get("name") == name and playback.get("url"):
                return playback["url"], name
    for playback in playbacks:
        if playback.get("url"):
            return playback["url"], playback.get("name")
    return None, None


def is_short_play_highlight(item):
    text = f"{item.get('title', '')} {item.get('description', '')}".lower()
    blocked = [
        "condensed game",
        "game recap",
        "full game",
        "extended highlights",
        "strong outing leads",
    ]
    if any(term in text for term in blocked):
        return False
    wanted = [
        "home run",
        "homer",
        "rbi",
        "double",
        "triple",
        "single",
        "strikeout",
        "strikes out",
        "k's",
        "catch",
        "diving",
        "rob",
        "throw",
        "steal",
        "scores",
    ]
    return any(term in text for term in wanted)


def normalize_highlights(content, limit=6):
    items = (
        content.get("highlights", {})
        .get("highlights", {})
        .get("items", [])
    )
    highlights = []
    for item in items:
        if not is_short_play_highlight(item):
            continue
        url, playback_type = playback_url(item)
        if not url:
            continue
        highlights.append(
            {
                "id": item.get("id") or item.get("guid") or item.get("slug"),
                "title": item.get("title", "Highlight"),
                "description": item.get("description") or "",
                "date": item.get("date"),
                "duration": item.get("duration"),
                "playback_url": url,
                "playback_type": playback_type,
                "mlb_url": item.get("url"),
                "image_url": item.get("image", {}).get("cuts", [{}])[0].get("src")
                if item.get("image", {}).get("cuts")
                else None,
            }
        )
    return highlights[:limit]


def fetch_latest_game_details():
    game_log = read_json(GENERATED_DIR / "game-log.json", {"games": []})
    latest = latest_completed_game(game_log.get("games", []))
    if not latest:
        raise MlbApiError("No completed Royals game available for details")

    boxscore = get_json(f"/game/{latest['game_pk']}/boxscore")
    play_by_play = get_json(f"/game/{latest['game_pk']}/playByPlay")
    write_json(RAW_DIR / f"boxscore-{latest['game_pk']}.json", boxscore)
    write_json(RAW_DIR / f"play-by-play-{latest['game_pk']}.json", play_by_play)

    royals_side = "home" if latest.get("home_away") == "home" else "away"
    opponent_side = "away" if royals_side == "home" else "home"
    hardest_balls, batter_summary = batted_balls(play_by_play)

    return {
        "source": "mlb-stats-api",
        "generated_at": now_iso(),
        "game": latest,
        "royals_boxscore": {
            "batting": batting_rows(boxscore.get("teams", {}).get(royals_side, {})),
            "pitching": pitching_rows(boxscore.get("teams", {}).get(royals_side, {})),
        },
        "opponent_boxscore": {
            "batting": batting_rows(boxscore.get("teams", {}).get(opponent_side, {})),
            "pitching": pitching_rows(boxscore.get("teams", {}).get(opponent_side, {})),
        },
        "batted_balls": {
            "hardest": hardest_balls[:12],
            "by_batter": batter_summary[:12],
        },
    }


def fetch_latest_game_highlights():
    game_log = read_json(GENERATED_DIR / "game-log.json", {"games": []})
    latest = latest_completed_game(game_log.get("games", []))
    if not latest:
        raise MlbApiError("No completed Royals game available for highlights")
    content = get_json(f"/game/{latest['game_pk']}/content", {"highlightLimit": 20})
    write_json(RAW_DIR / f"game-content-{latest['game_pk']}.json", content)
    return {
        "source": "mlb-stats-api",
        "generated_at": now_iso(),
        "game": latest,
        "filter": "Short play clips only; condensed games and full-game recaps excluded.",
        "highlights": normalize_highlights(content),
    }


def fetch_scoreboard():
    raw = get_json(
        "/schedule",
        {
            "sportId": 1,
            "date": as_of_date().isoformat(),
            "hydrate": "team,linescore,probablePitcher",
        },
    )
    write_json(RAW_DIR / "mlb-scoreboard-today.json", raw)
    games = []
    for day in raw.get("dates", []):
        for game in day.get("games", []):
            teams = game.get("teams", {})
            away = teams.get("away", {})
            home = teams.get("home", {})
            linescore = game.get("linescore", {})
            games.append(
                {
                    "game_pk": game.get("gamePk"),
                    "status": game.get("status", {}).get("detailedState", "Scheduled"),
                    "abstract_state": game.get("status", {}).get("abstractGameState", "Preview"),
                    "away_team": away.get("team", {}).get("name", "Away"),
                    "home_team": home.get("team", {}).get("name", "Home"),
                    "away_score": away.get("score"),
                    "home_score": home.get("score"),
                    "inning": linescore.get("currentInningOrdinal"),
                    "inning_state": linescore.get("inningState"),
                    "game_datetime": game.get("gameDate"),
                }
            )
    return {"source": "mlb-stats-api", "generated_at": now_iso(), "date": as_of_date().isoformat(), "games": games}


def main():
    ensure_dirs()
    try:
        write_json(GENERATED_DIR / "latest-game-details.json", fetch_latest_game_details())
    except MlbApiError as exc:
        write_json(
            GENERATED_DIR / "latest-game-details.json",
            {"source": "fallback", "generated_at": now_iso(), "fallback_reason": str(exc)},
        )
    try:
        write_json(GENERATED_DIR / "latest-game-highlights.json", fetch_latest_game_highlights())
    except MlbApiError as exc:
        write_json(
            GENERATED_DIR / "latest-game-highlights.json",
            {"source": "fallback", "generated_at": now_iso(), "fallback_reason": str(exc), "highlights": []},
        )
    write_json(GENERATED_DIR / "scoreboard.json", fetch_scoreboard())


if __name__ == "__main__":
    main()
