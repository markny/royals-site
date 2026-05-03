from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
GENERATED_DIR = DATA_DIR / "generated"
CONTENT_DIR = ROOT / "content"
RECAP_DIR = CONTENT_DIR / "recaps"


def ensure_dirs():
    for directory in [RAW_DIR, GENERATED_DIR, CONTENT_DIR, RECAP_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
