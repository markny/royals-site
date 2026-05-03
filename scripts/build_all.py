#!/usr/bin/env python3
"""Run the local update pipeline in the same order a nightly job will use."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(script):
    subprocess.run([sys.executable, str(ROOT / "scripts" / script)], cwd=ROOT, check=True)


def main():
    run("fetch_mlb.py")
    run("generate_content.py")


if __name__ == "__main__":
    main()
