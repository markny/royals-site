#!/usr/bin/env python3
"""Build a curated Royals prospect performance feed.

The watchlist is intentionally editorial. The API supplies performance; the
watchlist explains why the player matters to this specific Royals tracker.
"""

from lib.io import now_iso, read_json, write_json
from lib.mlb_api import MlbApiError, get_json
from lib.paths import DATA_DIR, GENERATED_DIR, RAW_DIR, ensure_dirs
from lib.run_context import season

WATCHLIST_PATH = DATA_DIR / "prospects" / "watchlist.json"
SEASON = season()


def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0


def safe_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def fetch_player_stats(player, stat_type):
    params = {
        "stats": stat_type,
        "group": player["group"],
        "season": SEASON,
        "sportId": player.get("sport_id"),
        "hydrate": "team",
    }
    if stat_type == "lastXGames":
        params["limit"] = 7
    raw = get_json(f"/people/{player['mlbam_id']}/stats", params)
    write_json(RAW_DIR / f"prospect-{player['mlbam_id']}-{stat_type}.json", raw)
    stats = raw.get("stats", [])
    splits = stats[0].get("splits", []) if stats else []
    return splits[0] if splits else {}


def hitter_line(stat):
    avg = stat.get("avg", ".---")
    obp = stat.get("obp", ".---")
    slg = stat.get("slg", ".---")
    return f"{avg} / {obp} / {slg}"


def pitcher_line(stat):
    return f"{stat.get('era', '-.--')} ERA, {stat.get('strikeOuts', 0)} K, {stat.get('whip', '-.--')} WHIP"


def hitter_metrics(stat):
    pa = safe_int(stat.get("plateAppearances"))
    bb = safe_int(stat.get("baseOnBalls"))
    so = safe_int(stat.get("strikeOuts"))
    return {
        "avg": stat.get("avg", ".---"),
        "obp": stat.get("obp", ".---"),
        "slg": stat.get("slg", ".---"),
        "ops": stat.get("ops", ".---"),
        "hr": safe_int(stat.get("homeRuns")),
        "rbi": safe_int(stat.get("rbi")),
        "sb": safe_int(stat.get("stolenBases")),
        "pa": pa,
        "bb_pct": round((bb / pa) * 100, 1) if pa else 0,
        "k_pct": round((so / pa) * 100, 1) if pa else 0,
    }


def pitcher_metrics(stat):
    batters = safe_int(stat.get("battersFaced"))
    bb = safe_int(stat.get("baseOnBalls"))
    so = safe_int(stat.get("strikeOuts"))
    return {
        "era": stat.get("era", "-.--"),
        "whip": stat.get("whip", "-.--"),
        "ip": stat.get("inningsPitched", "0.0"),
        "so": so,
        "bb": bb,
        "k_pct": round((so / batters) * 100, 1) if batters else 0,
        "bb_pct": round((bb / batters) * 100, 1) if batters else 0,
    }


def trend_label(player, season_stat, recent_stat):
    if not recent_stat:
        return "Status Watch"
    if player["group"] == "hitting":
        recent_ops = safe_float(recent_stat.get("ops"))
        if recent_ops >= 0.9:
            return "Heating Up"
        if recent_ops <= 0.6:
            return "Cold Week"
        return "Steady"
    era = safe_float(recent_stat.get("era"))
    if era and era <= 3:
        return "Strong Run"
    if era >= 5:
        return "Rough Stretch"
    return "Steady"


def build_player(player):
    season_split = fetch_player_stats(player, "season")
    recent_split = fetch_player_stats(player, "lastXGames")
    season_stat = season_split.get("stat", {})
    recent_stat = recent_split.get("stat", {})
    team = season_split.get("team", {}) or recent_split.get("team", {})
    level = recent_split.get("sport", {}).get("abbreviation") or season_split.get("sport", {}).get("abbreviation")

    if player["group"] == "hitting":
        line = hitter_line(season_stat)
        metrics = hitter_metrics(season_stat)
        recent_metrics = hitter_metrics(recent_stat) if recent_stat else {}
        recent_line = hitter_line(recent_stat) if recent_stat else "No recent game data"
    else:
        line = pitcher_line(season_stat)
        metrics = pitcher_metrics(season_stat)
        recent_metrics = pitcher_metrics(recent_stat) if recent_stat else {}
        recent_line = pitcher_line(recent_stat) if recent_stat else "No recent game data"

    return {
        "rank": None,
        "name": player["name"],
        "mlbam_id": player["mlbam_id"],
        "position": player["position"],
        "level": player["level"],
        "affiliate": team.get("name", player["affiliate"]),
        "api_level": level,
        "priority": player["priority"],
        "rank_label": player["rank_label"],
        "watch_reason": player["watch_reason"],
        "status_note": player["status_note"],
        "tags": player["tags"],
        "line": line,
        "recent_line": recent_line,
        "metrics": metrics,
        "recent_metrics": recent_metrics,
        "trend_label": trend_label(player, season_stat, recent_stat),
        "trend_note": f"{player['watch_reason']} Recent line: {recent_line}.",
    }


def build_feed():
    watchlist = read_json(WATCHLIST_PATH, {"players": []})
    players = []
    for player in watchlist.get("players", []):
        try:
            players.append(build_player(player))
        except MlbApiError as exc:
            fallback = dict(player)
            fallback.update(
                {
                    "line": "Stats unavailable",
                    "recent_line": "Stats unavailable",
                    "trend_label": "Fetch Issue",
                    "trend_note": f"{player['watch_reason']} Stats fetch failed: {exc}",
                    "metrics": {},
                    "recent_metrics": {},
                }
            )
            players.append(fallback)

    hot = [
        {"name": player["name"], "note": f"{player['trend_label']}: {player['recent_line']}"}
        for player in players
        if player.get("trend_label") in {"Heating Up", "Strong Run"}
    ]
    if not hot:
        hot = [{"name": players[0]["name"], "note": players[0]["trend_note"]}] if players else []

    return {
        "source": "curated-watchlist+mlb-stats-api",
        "generated_at": now_iso(),
        "watchlist_notes": watchlist.get("notes"),
        "hot_prospects": hot[:3],
        "prospects": players,
    }


def main():
    ensure_dirs()
    write_json(GENERATED_DIR / "prospects.json", build_feed())


if __name__ == "__main__":
    main()
