"""Activity history with keyset (cursor) pagination (US9).

Ordered newest-first by (start_time, id). Cursors are opaque base64 tokens so
the API stays stable; the free tier is bounded to a recent window server-side.
"""
from __future__ import annotations

import base64
from datetime import date, datetime, timedelta

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.models.activity import Activity

DEFAULT_LIMIT = 20
MAX_LIMIT = 100


def _encode_cursor(start_time: datetime, activity_id: str) -> str:
    raw = f"{start_time.isoformat()}|{activity_id}"
    return base64.urlsafe_b64encode(raw.encode()).decode()


def _decode_cursor(cursor: str) -> tuple[datetime, str]:
    raw = base64.urlsafe_b64decode(cursor.encode()).decode()
    start_iso, activity_id = raw.split("|", 1)
    return datetime.fromisoformat(start_iso), activity_id


def _serialize(a: Activity) -> dict:
    return {
        "id": a.id,
        "activity_type": a.activity_type,
        "name": a.name,
        "start_time": a.start_time.isoformat(),
        "distance_m": a.distance_m,
        "duration_s": a.duration_s,
        "avg_hr": a.avg_hr,
        "tss": a.tss,
    }


def list_activities(
    db: Session,
    user_id: str,
    *,
    limit: int = DEFAULT_LIMIT,
    cursor: str | None = None,
    today: date,
    max_age_days: int | None = None,
) -> dict:
    """Return one page of the user's activities, newest first.

    ``max_age_days`` bounds the window (free tier = 30). ``cursor`` is the
    ``next_cursor`` from a previous page. The result is
    ``{"items": [...], "next_cursor": str | None}``.
    """
    limit = max(1, min(limit, MAX_LIMIT))
    query = select(Activity).where(Activity.user_id == user_id)

    if max_age_days is not None:
        floor = datetime.combine(
            today - timedelta(days=max_age_days), datetime.min.time()
        )
        query = query.where(Activity.start_time >= floor)

    if cursor is not None:
        c_time, c_id = _decode_cursor(cursor)
        query = query.where(
            or_(
                Activity.start_time < c_time,
                and_(Activity.start_time == c_time, Activity.id < c_id),
            )
        )

    query = query.order_by(Activity.start_time.desc(), Activity.id.desc()).limit(
        limit + 1
    )
    rows = list(db.execute(query).scalars())

    has_more = len(rows) > limit
    page = rows[:limit]
    next_cursor = (
        _encode_cursor(page[-1].start_time, page[-1].id) if has_more and page else None
    )
    return {"items": [_serialize(a) for a in page], "next_cursor": next_cursor}
