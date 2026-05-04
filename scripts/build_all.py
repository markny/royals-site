#!/usr/bin/env python3
"""Run the local update pipeline in the same order a nightly job will use."""

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(script):
    subprocess.run([sys.executable, str(ROOT / "scripts" / script)], cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--date",
        help="As-of date in YYYY-MM-DD form. Use this for deterministic nightly runs.",
    )
    args = parser.parse_args()
    if args.date:
        os.environ["TRACKER_AS_OF_DATE"] = args.date

    run("fetch_mlb.py")
    run("fetch_game_details.py")
    run("fetch_prospects.py")
    run("generate_content.py")


if __name__ == "__main__":
    main()
