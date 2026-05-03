from datetime import date

SAMPLE_SEASON = 2026
TODAY = date.today().isoformat()

SAMPLE_GAME_LOG = {
    "source": "sample",
    "games": [
        {
            "game_pk": 1001,
            "date": "2026-04-28",
            "matchup": "Royals at Twins",
            "opponent": "Minnesota Twins",
            "home_away": "away",
            "site": "Away",
            "venue": "Target Field",
            "result": "W",
            "score": "KC 5, MIN 3",
            "probable_pitchers": {
                "royals": {"id": None, "name": "TBD"},
                "opponent": {"id": None, "name": "TBD"},
            },
            "recap_slug": "2026-04-28-royals-at-twins",
        },
        {
            "game_pk": 1002,
            "date": "2026-04-29",
            "matchup": "Royals at Twins",
            "opponent": "Minnesota Twins",
            "home_away": "away",
            "site": "Away",
            "venue": "Target Field",
            "result": "L",
            "score": "MIN 4, KC 2",
            "probable_pitchers": {
                "royals": {"id": None, "name": "TBD"},
                "opponent": {"id": None, "name": "TBD"},
            },
            "recap_slug": "2026-04-29-royals-at-twins",
        },
        {
            "game_pk": 1003,
            "date": "2026-05-01",
            "matchup": "Royals vs Tigers",
            "opponent": "Detroit Tigers",
            "home_away": "home",
            "site": "Home",
            "venue": "Kauffman Stadium",
            "result": "W",
            "score": "KC 6, DET 1",
            "probable_pitchers": {
                "royals": {"id": None, "name": "TBD"},
                "opponent": {"id": None, "name": "TBD"},
            },
            "recap_slug": "2026-05-01-royals-vs-tigers",
        },
    ],
}

SAMPLE_STANDINGS = {
    "source": "sample",
    "al_central": [
        {"team": "Cleveland Guardians", "wins": 19, "losses": 13, "pct": 0.594, "games_back": "-", "streak": "W2"},
        {"team": "Kansas City Royals", "wins": 18, "losses": 14, "pct": 0.563, "games_back": "1.0", "streak": "W1"},
        {"team": "Detroit Tigers", "wins": 17, "losses": 15, "pct": 0.531, "games_back": "2.0", "streak": "L1"},
        {"team": "Minnesota Twins", "wins": 15, "losses": 17, "pct": 0.469, "games_back": "4.0", "streak": "L2"},
        {"team": "Chicago White Sox", "wins": 10, "losses": 22, "pct": 0.313, "games_back": "9.0", "streak": "W1"},
    ],
    "wild_card": [
        {"team": "Seattle Mariners", "wins": 19, "losses": 13, "pct": 0.594, "games_back": "+1.0", "streak": "W3"},
        {"team": "Kansas City Royals", "wins": 18, "losses": 14, "pct": 0.563, "games_back": "-", "streak": "W1"},
        {"team": "Boston Red Sox", "wins": 17, "losses": 15, "pct": 0.531, "games_back": "-", "streak": "L1"},
    ],
}

SAMPLE_HITTING = {
    "source": "sample",
    "players": [
        {"id": 1, "player": "Bobby Witt Jr.", "avg": 0.318, "ops": 0.942, "hr": 8, "rbi": 25},
        {"id": 2, "player": "Vinnie Pasquantino", "avg": 0.287, "ops": 0.846, "hr": 6, "rbi": 22},
        {"id": 3, "player": "Salvador Perez", "avg": 0.271, "ops": 0.801, "hr": 5, "rbi": 19},
        {"id": 4, "player": "Maikel Garcia", "avg": 0.296, "ops": 0.773, "hr": 2, "rbi": 13},
    ],
}

SAMPLE_PITCHING = {
    "source": "sample",
    "players": [
        {"id": 11, "player": "Cole Ragans", "era": 2.71, "whip": 1.04, "so": 48, "ip": "39.2"},
        {"id": 12, "player": "Seth Lugo", "era": 3.08, "whip": 1.12, "so": 34, "ip": "38.0"},
        {"id": 13, "player": "Michael Wacha", "era": 3.52, "whip": 1.2, "so": 29, "ip": "35.2"},
        {"id": 14, "player": "Kris Bubic", "era": 2.95, "whip": 1.15, "so": 31, "ip": "36.2"},
    ],
}

SAMPLE_STATCAST = {
    "source": "placeholder",
    "players": [
        {
            "player": "Bobby Witt Jr.",
            "avg_exit_velocity": 92.1,
            "hard_hit_pct": 51.4,
            "barrel_pct": 12.7,
            "note": "Placeholder until Savant ingestion is wired.",
        },
        {
            "player": "Vinnie Pasquantino",
            "avg_exit_velocity": 90.3,
            "hard_hit_pct": 47.9,
            "barrel_pct": 10.8,
            "note": "Good future target for swing-quality trend notes.",
        },
        {
            "player": "Salvador Perez",
            "avg_exit_velocity": 89.6,
            "hard_hit_pct": 45.1,
            "barrel_pct": 9.9,
            "note": "Use nightly deltas once Baseball Savant export is added.",
        },
    ],
}

SAMPLE_PROSPECTS = {
    "source": "curated-placeholder",
    "hot_prospects": [
        {"name": "Blake Mitchell", "note": "Power and patience profile remains the nightly watch item."},
        {"name": "Jac Caglianone", "note": "Track contact quality, strikeout rate, and defensive usage."},
    ],
    "prospects": [
        {
            "rank": 1,
            "name": "Blake Mitchell",
            "position": "C",
            "affiliate": "Quad Cities River Bandits",
            "level": "High-A",
            "line": ".282 / .390 / .512",
            "trend_note": "Strong walk rate keeps the floor stable even when the power comes in streaks.",
        },
        {
            "rank": 2,
            "name": "Jac Caglianone",
            "position": "1B/LHP",
            "affiliate": "Northwest Arkansas Naturals",
            "level": "Double-A",
            "line": ".268 / .331 / .511",
            "trend_note": "Loud contact is the draw; nightly system should flag chase-rate movement.",
        },
        {
            "rank": 3,
            "name": "Ben Kudrna",
            "position": "RHP",
            "affiliate": "Omaha Storm Chasers",
            "level": "Triple-A",
            "line": "3.48 ERA, 27 K",
            "trend_note": "Fastball command is the lead indicator before any MLB-role projection changes.",
        },
    ],
}
