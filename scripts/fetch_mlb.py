#!/usr/bin/env python3
"""Fetch deterministic baseball data for the static site.

This script is intentionally prose-free. It gathers structured facts from public
sources and writes normalized JSON files that the site and later LLM steps can
consume.
"""

from datetime import date

from lib.io import now_iso, write_json
from lib.mlb_api import MlbApiError, ROYALS_TEAM_ID, get_json
from lib.paths import GENERATED_DIR, RAW_DIR, ensure_dirs
from lib.samples import (
    SAMPLE_GAME_LOG,
    SAMPLE_HITTING,
    SAMPLE_PITCHING,
    SAMPLE_PROSPECTS,
    SAMPLE_STATCAST,
    SAMPLE_STANDINGS,
)

SEASON = date.today().year
ROYALS_NAME = "Kansas City Royals"


def team_name(team):
    return team.get("teamName") or team.get("name") or team.get("abbreviation") or "Opponent"


def normalize_record(raw_record):
    wins = int(raw_record.get("wins", 0))
    losses = int(raw_record.get("losses", 0))
    games = wins + losses
    win_pct = round(wins / games, 3) if games else 0
    return {"wins": wins, "losses": losses, "games_played": games, "win_pct": win_pct}


def fetch_schedule():
    raw = get_json(
        "/schedule",
        {
            "sportId": 1,
            "teamId": ROYALS_TEAM_ID,
            "season": SEASON,
            "gameTypes": "R",
            "hydrate": "team,venue,linescore,probablePitcher",
        },
    )
    write_json(RAW_DIR / "mlb-schedule.json", raw)
    games = []
    for day in raw.get("dates", []):
        for game in day.get("games", []):
            teams = game.get("teams", {})
            home = teams.get("home", {})
            away = teams.get("away", {})
            is_home = home.get("team", {}).get("id") == ROYALS_TEAM_ID
            royals_side = home if is_home else away
            opponent_side = away if is_home else home
            royals_probable = royals_side.get("probablePitcher", {})
            opponent_probable = opponent_side.get("probablePitcher", {})
            status = game.get("status", {}).get("abstractGameState")
            royals_score = royals_side.get("score")
            opponent_score = opponent_side.get("score")
            result = "TBD"
            score = "Scheduled"
            if status == "Final" and royals_score is not None and opponent_score is not None:
                result = "W" if royals_score > opponent_score else "L" if royals_score < opponent_score else "T"
                score = f"KC {royals_score}, {opponent_side.get('team', {}).get('abbreviation', 'OPP')} {opponent_score}"
            slug_date = game.get("officialDate", day.get("date", "game"))
            opponent = opponent_side.get("team", {})
            games.append(
                {
                    "game_pk": game.get("gamePk"),
                    "date": game.get("officialDate", day.get("date")),
                    "matchup": f"Royals {'vs' if is_home else 'at'} {team_name(opponent)}",
                    "opponent": opponent.get("name", "Opponent"),
                    "home_away": "home" if is_home else "away",
                    "site": "Home" if is_home else "Away",
                    "venue": game.get("venue", {}).get("name", "TBD"),
                    "result": result,
                    "score": score,
                    "probable_pitchers": {
                        "royals": {
                            "id": royals_probable.get("id"),
                            "name": royals_probable.get("fullName", "TBD"),
                        },
                        "opponent": {
                            "id": opponent_probable.get("id"),
                            "name": opponent_probable.get("fullName", "TBD"),
                        },
                    },
                    "recap_slug": f"{slug_date}-royals-{'vs' if is_home else 'at'}-{team_name(opponent).lower().replace(' ', '-')}"
                    if status == "Final"
                    else None,
                    "game_datetime": game.get("gameDate"),
                }
            )
    return {"source": "mlb-stats-api", "season": SEASON, "generated_at": now_iso(), "games": games}


def fetch_standings():
    raw = get_json(
        "/standings",
        {
            "leagueId": 103,
            "season": SEASON,
            "standingsTypes": "regularSeason,wildCard",
            "hydrate": "team",
        },
    )
    write_json(RAW_DIR / "mlb-standings.json", raw)

    al_central = []
    wild_card = []
    for record_group in raw.get("records", []):
        group = []
        for team_record in record_group.get("teamRecords", []):
            group.append(
                {
                    "team": team_record.get("team", {}).get("name", "Team"),
                    "wins": int(team_record.get("wins", 0)),
                    "losses": int(team_record.get("losses", 0)),
                    "pct": float(team_record.get("winningPercentage", 0)),
                    "games_back": team_record.get("gamesBack", "-"),
                    "streak": team_record.get("streak", {}).get("streakCode", "-"),
                }
            )
        if record_group.get("standingsType") == "regularSeason" and any(
            team["team"] == ROYALS_NAME for team in group
        ):
            al_central = group
        if record_group.get("standingsType") == "wildCard":
            wild_card = group[:8]

    if not al_central:
        raise MlbApiError("AL Central standings missing from MLB response")
    royals_entry = next((team for team in al_central if team["team"] == ROYALS_NAME), al_central[0])
    return {
        "source": "mlb-stats-api",
        "season": SEASON,
        "generated_at": now_iso(),
        "al_central": al_central,
        "wild_card": wild_card or SAMPLE_STANDINGS["wild_card"],
        "royals_entry": royals_entry,
    }


def split_stat_line(group, category):
    rows = []
    for split in group.get("splits", []):
        stat = split.get("stat", {})
        player = split.get("player", {})
        rows.append(
            {
                "id": player.get("id"),
                "player": player.get("fullName", "Player"),
                "avg": safe_float(stat.get("avg")),
                "ops": safe_float(stat.get("ops")),
                "hr": int(stat.get("homeRuns", 0) or 0),
                "rbi": int(stat.get("rbi", 0) or 0),
                "ab": int(stat.get("atBats", 0) or 0),
            }
            if category == "hitting"
            else {
                "id": player.get("id"),
                "player": player.get("fullName", "Player"),
                "era": safe_float(stat.get("era")),
                "whip": safe_float(stat.get("whip")),
                "so": int(stat.get("strikeOuts", 0) or 0),
                "ip": stat.get("inningsPitched", "0.0"),
            }
        )
    return rows


def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0


def fetch_team_stats(group, category):
    raw = get_json(
        "/stats",
        {
            "season": SEASON,
            "stats": "season",
            "group": group,
            "playerPool": "all",
            "teamId": ROYALS_TEAM_ID,
            "limit": 12,
            "hydrate": "person",
        },
    )
    write_json(RAW_DIR / f"mlb-{category}-stats.json", raw)
    stats = raw.get("stats", [])
    if not stats:
        raise MlbApiError(f"No {category} stats returned")
    players = split_stat_line(stats[0], category)
    if not players:
        raise MlbApiError(f"No {category} player rows returned")
    return {
        "source": "mlb-stats-api",
        "season": SEASON,
        "generated_at": now_iso(),
        "players": players,
    }


def add_fallback_metadata(data, reason):
    output = dict(data)
    output["generated_at"] = now_iso()
    output["fallback_reason"] = reason
    return output


def main():
    ensure_dirs()
    fetchers = [
        ("game-log.json", fetch_schedule, SAMPLE_GAME_LOG),
        ("standings.json", fetch_standings, SAMPLE_STANDINGS),
        ("hitting-stats.json", lambda: fetch_team_stats("hitting", "hitting"), SAMPLE_HITTING),
        ("pitching-stats.json", lambda: fetch_team_stats("pitching", "pitching"), SAMPLE_PITCHING),
    ]
    for filename, fetcher, fallback in fetchers:
        try:
            payload = fetcher()
        except MlbApiError as exc:
            payload = add_fallback_metadata(fallback, str(exc))
        write_json(GENERATED_DIR / filename, payload)

    write_json(GENERATED_DIR / "statcast-metrics.json", add_fallback_metadata(SAMPLE_STATCAST, "Savant ingestion TODO"))
    write_json(GENERATED_DIR / "prospects.json", add_fallback_metadata(SAMPLE_PROSPECTS, "Prospect feed TODO"))


if __name__ == "__main__":
    main()
