"""Exercise library: seed from the dataset JSON + filtered keyset listing.

Media files stay in the source repo (127 MB of GIFs) and are served through
the jsDelivr CDN; only metadata lives in our database.
"""
from __future__ import annotations

import base64
from collections.abc import Iterable

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.models.exercise import Exercise

CDN_BASE = "https://cdn.jsdelivr.net/gh/hasaneyldrm/exercises-dataset@main/"
DATASET_URL = (
    "https://raw.githubusercontent.com/hasaneyldrm/exercises-dataset/main/"
    "data/exercises.json"
)
DEFAULT_LIMIT = 24
MAX_LIMIT = 100


def _from_raw(record: dict) -> dict:
    """Column values for one entry of data/exercises.json."""
    return {
        "id": record["id"],
        "name": record["name"],
        "body_part": record["body_part"],
        "target": record["target"],
        "muscle_group": record.get("muscle_group"),
        "secondary_muscles": record.get("secondary_muscles") or [],
        "equipment": record["equipment"],
        "instructions": (record.get("instruction_steps") or {}).get("en") or [],
        "image_url": CDN_BASE + record["image"],
        "gif_url": CDN_BASE + record["gif_url"],
        "attribution": record.get("attribution"),
    }


def upsert_exercises(db: Session, records: Iterable[dict]) -> int:
    """Insert or update exercises from raw dataset records. Idempotent.

    Returns the number of records processed.
    """
    count = 0
    for record in records:
        values = _from_raw(record)
        existing = db.get(Exercise, values["id"])
        if existing is None:
            db.add(Exercise(**values))
        else:
            for key, value in values.items():
                setattr(existing, key, value)
        count += 1
    db.commit()
    return count


def fetch_dataset(url: str = DATASET_URL) -> list[dict]:
    """Download the exercises dataset JSON."""
    import httpx

    response = httpx.get(url, timeout=120, follow_redirects=True)
    response.raise_for_status()
    return response.json()


def count_exercises(db: Session) -> int:
    from sqlalchemy import func

    return int(db.execute(select(func.count(Exercise.id))).scalar() or 0)


def ensure_seeded(db: Session) -> int:
    """Seed the library from the dataset when the table is empty.

    Returns the number of records seeded (0 when already populated). Lets any
    download/DB error propagate so callers decide how loudly to fail.
    """
    if count_exercises(db) > 0:
        return 0
    return upsert_exercises(db, fetch_dataset())


def _encode_cursor(name: str, exercise_id: str) -> str:
    return base64.urlsafe_b64encode(f"{name}|{exercise_id}".encode()).decode()


def _decode_cursor(cursor: str) -> tuple[str, str]:
    name, exercise_id = base64.urlsafe_b64decode(cursor.encode()).decode().split("|", 1)
    return name, exercise_id


def serialize_summary(e: Exercise) -> dict:
    return {
        "id": e.id,
        "name": e.name,
        "body_part": e.body_part,
        "target": e.target,
        "equipment": e.equipment,
        "image_url": e.image_url,
        "gif_url": e.gif_url,
    }


def serialize_detail(e: Exercise) -> dict:
    return {
        **serialize_summary(e),
        "muscle_group": e.muscle_group,
        "secondary_muscles": e.secondary_muscles,
        "instructions": e.instructions,
        "attribution": e.attribution,
    }


def list_exercises(
    db: Session,
    *,
    body_part: str | None = None,
    target: str | None = None,
    equipment: str | None = None,
    q: str | None = None,
    limit: int = DEFAULT_LIMIT,
    cursor: str | None = None,
) -> dict:
    """One page of the library ordered by (name, id), with exact filters and
    a case-insensitive name search. Returns ``{"items", "next_cursor"}``.
    """
    limit = max(1, min(limit, MAX_LIMIT))
    query = select(Exercise)
    if body_part is not None:
        query = query.where(Exercise.body_part == body_part)
    if target is not None:
        query = query.where(Exercise.target == target)
    if equipment is not None:
        query = query.where(Exercise.equipment == equipment)
    if q:
        query = query.where(Exercise.name.ilike(f"%{q}%"))
    if cursor is not None:
        c_name, c_id = _decode_cursor(cursor)
        query = query.where(
            or_(
                Exercise.name > c_name,
                and_(Exercise.name == c_name, Exercise.id > c_id),
            )
        )

    query = query.order_by(Exercise.name.asc(), Exercise.id.asc()).limit(limit + 1)
    rows = list(db.execute(query).scalars())

    has_more = len(rows) > limit
    page = rows[:limit]
    next_cursor = (
        _encode_cursor(page[-1].name, page[-1].id) if has_more and page else None
    )
    return {"items": [serialize_summary(e) for e in page], "next_cursor": next_cursor}
