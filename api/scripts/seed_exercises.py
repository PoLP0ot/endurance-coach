"""Seed the exercise library from the exercises-dataset JSON.

Usage (from api/, venv active, DATABASE_URL pointing at the target DB):

    python scripts/seed_exercises.py                 # download from GitHub
    python scripts/seed_exercises.py --file path.json  # use a local copy

Idempotent: re-running updates existing rows in place. Deployed environments
seed themselves via the ARQ worker startup (``ensure_seeded``); this script
covers local/dev and manual re-seeds.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.db import SessionLocal  # noqa: E402
from app.services.exercises import fetch_dataset, upsert_exercises  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", help="local exercises.json instead of downloading")
    args = parser.parse_args()

    if args.file:
        records = json.loads(Path(args.file).read_text(encoding="utf-8"))
    else:
        records = fetch_dataset()
    db = SessionLocal()
    try:
        count = upsert_exercises(db, records)
    finally:
        db.close()
    print(f"seeded {count} exercises")


if __name__ == "__main__":
    main()
