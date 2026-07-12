"""Seed the exercise library from the exercises-dataset JSON.

Usage (from api/, venv active, DATABASE_URL pointing at the target DB):

    python scripts/seed_exercises.py                 # download from GitHub
    python scripts/seed_exercises.py --file path.json  # use a local copy

Idempotent: re-running updates existing rows in place.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.db import SessionLocal  # noqa: E402
from app.services.exercises import upsert_exercises  # noqa: E402

DATASET_URL = (
    "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/"
    "data/exercises.json"
)


def load_records(file: str | None) -> list[dict]:
    if file:
        return json.loads(Path(file).read_text(encoding="utf-8"))
    response = httpx.get(DATASET_URL, timeout=120, follow_redirects=True)
    response.raise_for_status()
    return response.json()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", help="local exercises.json instead of downloading")
    args = parser.parse_args()

    records = load_records(args.file)
    db = SessionLocal()
    try:
        count = upsert_exercises(db, records)
    finally:
        db.close()
    print(f"seeded {count} exercises")


if __name__ == "__main__":
    main()
