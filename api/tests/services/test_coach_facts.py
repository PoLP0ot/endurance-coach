"""coach_facts tests — the AI now sees the goal, projection and trend (B1)."""
from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from app.models.activity import Activity
from app.services.coach_facts import build_coach_facts


def _run(user_id: str, when: datetime) -> Activity:
    return Activity(
        user_id=user_id,
        garmin_activity_id=f"g-{when.isoformat()}",
        activity_type="running",
        start_time=when,
        duration_s=3600,
        distance_m=14000.0,
        avg_hr=150,
    )


def test_coach_facts_include_goal_and_trend(db_session, seed_user):
    today = date(2026, 6, 22)
    base = datetime(2026, 6, 1, 7, tzinfo=UTC)
    for i in range(8):
        db_session.add(_run(seed_user.id, base + timedelta(days=i)))
    seed_user.primary_goal = "marathon"
    seed_user.goal_params = {"target_time_s": 12600}
    db_session.commit()

    facts = build_coach_facts(db_session, seed_user.id, today)
    assert facts["goal"]["kind"] == "marathon"
    assert facts["goal"]["projection"] is not None
    assert facts["trend"]  # recent CTL/TSB direction is exposed
    assert "fitness" in facts and "recovery" in facts
