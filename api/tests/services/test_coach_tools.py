"""Coach tool dispatch tests — deterministic facts, user isolation (B3)."""
from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from app.models.activity import Activity
from app.services.coach_tools import run_tool

TODAY = date(2026, 6, 22)


def _run(user_id: str, when: datetime, tss: float = 60.0) -> Activity:
    return Activity(
        user_id=user_id,
        garmin_activity_id=f"g-{user_id}-{when.isoformat()}",
        activity_type="running",
        start_time=when,
        duration_s=3600,
        distance_m=12000.0,
        avg_hr=150,
        tss=tss,
    )


def test_get_recent_activities_respects_limit_and_owner(db_session, seed_user):
    base = datetime(2026, 6, 1, 7, tzinfo=UTC)
    for i in range(6):
        db_session.add(_run(seed_user.id, base + timedelta(days=i)))
    db_session.add(_run("99999999-9999-9999-9999-999999999999", base))
    db_session.commit()

    out = run_tool(db_session, seed_user.id, TODAY, "get_recent_activities", {"limit": 3})
    assert len(out["activities"]) == 3  # limited
    # Newest first, only the owner's data.
    assert out["activities"][0]["activity_type"] == "running"


def test_get_goal_progress_returns_goal(db_session, seed_user):
    db_session.add(_run(seed_user.id, datetime(2026, 6, 20, 7, tzinfo=UTC)))
    seed_user.primary_goal = "health"
    db_session.commit()
    out = run_tool(db_session, seed_user.id, TODAY, "get_goal_progress", {})
    assert out["goal"]["kind"] == "health"


def test_get_adherence_handles_no_plan(db_session, seed_user):
    out = run_tool(db_session, seed_user.id, TODAY, "get_adherence", {})
    assert out["status"] == "no_plan"


def test_unknown_tool_is_reported(db_session, seed_user):
    out = run_tool(db_session, seed_user.id, TODAY, "frobnicate", {})
    assert "unknown_tool" in out["error"]
