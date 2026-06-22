"""Activity history service tests — keyset pagination + free-tier window (US9)."""
from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from app.models.activity import Activity
from app.services.activity_history import list_activities


def _seed(db, user_id: str, n: int, *, start: datetime) -> None:
    for i in range(n):
        db.add(
            Activity(
                user_id=user_id,
                garmin_activity_id=f"g-{i}",
                activity_type="running",
                start_time=start + timedelta(days=i),
            )
        )
    db.commit()


def test_pagination_walks_without_overlap(db_session, seed_user):
    _seed(db_session, seed_user.id, 25, start=datetime(2026, 6, 1, 7, tzinfo=UTC))

    page1 = list_activities(db_session, seed_user.id, limit=10, today=date(2026, 7, 1))
    assert len(page1["items"]) == 10
    assert page1["next_cursor"] is not None
    # Newest first.
    assert page1["items"][0]["start_time"] > page1["items"][-1]["start_time"]

    page2 = list_activities(
        db_session,
        seed_user.id,
        limit=10,
        cursor=page1["next_cursor"],
        today=date(2026, 7, 1),
    )
    ids1 = {a["id"] for a in page1["items"]}
    ids2 = {a["id"] for a in page2["items"]}
    assert ids1.isdisjoint(ids2)
    assert len(page2["items"]) == 10


def test_last_page_has_no_cursor(db_session, seed_user):
    _seed(db_session, seed_user.id, 3, start=datetime(2026, 6, 1, 7, tzinfo=UTC))
    page = list_activities(db_session, seed_user.id, limit=10, today=date(2026, 7, 1))
    assert len(page["items"]) == 3
    assert page["next_cursor"] is None


def test_free_tier_limited_to_30_days(db_session, seed_user):
    _seed(db_session, seed_user.id, 60, start=datetime(2026, 5, 1, 7, tzinfo=UTC))
    free = list_activities(
        db_session, seed_user.id, limit=100, today=date(2026, 6, 30), max_age_days=30
    )
    premium = list_activities(
        db_session, seed_user.id, limit=100, today=date(2026, 6, 30)
    )
    assert len(free["items"]) < len(premium["items"])
    cutoff = date(2026, 6, 30) - timedelta(days=30)
    assert all(a["start_time"][:10] >= cutoff.isoformat() for a in free["items"])
