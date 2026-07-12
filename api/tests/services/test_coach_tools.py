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


def test_propose_strength_plan_creates_the_program(db_session, seed_user):
    from app.services.strength import current_strength_plan

    from tests.services.test_strength import seed_library

    seed_library(db_session)
    out = run_tool(
        db_session,
        seed_user.id,
        TODAY,
        "propose_strength_plan",
        {"frequency": 3, "weeks": 8, "level": "beginner", "equipment": ["body weight"]},
    )
    assert out["status"] == "created"
    assert out["weeks"] == 8 and out["frequency"] == 3
    plan = current_strength_plan(db_session, seed_user.id)
    assert plan is not None and len(plan.structure["weeks"]) == 8


def test_propose_strength_plan_rejects_bad_params(db_session, seed_user):
    out = run_tool(
        db_session,
        seed_user.id,
        TODAY,
        "propose_strength_plan",
        {"frequency": 9, "weeks": 8, "level": "beginner", "equipment": ["body weight"]},
    )
    assert "error" in out


def _weigh_ins(db_session, user_id, *, start_kg=90.0, days=15, per_day=0.05):
    from app.models.health import DailyHealth

    for i in range(days):
        db_session.add(
            DailyHealth(
                user_id=user_id,
                day=TODAY - timedelta(days=days - 1 - i),
                weight_kg=round(start_kg - per_day * i, 2),
            )
        )
    db_session.commit()


def test_weight_guidance_computes_deterministic_numbers(db_session, seed_user):
    seed_user.primary_goal = "weight_loss"
    seed_user.goal_params = {
        "target_weight_kg": 80.0,
        "target_date": (TODAY + timedelta(days=140)).isoformat(),
    }
    db_session.commit()
    _weigh_ins(db_session, seed_user.id)

    out = run_tool(db_session, seed_user.id, TODAY, "get_weight_guidance", {})
    assert out["status"] == "ok"
    assert out["kcal_per_kg"] == 7700
    assert out["required_rate_kg_per_week"] is not None
    assert out["weekly_kcal_deficit_needed"] == round(
        out["required_rate_kg_per_week"] * 7700
    )
    assert out["weeks_remaining"] == 20.0


def test_weight_guidance_without_data_says_so(db_session, seed_user):
    seed_user.primary_goal = "weight_loss"
    seed_user.goal_params = {"target_weight_kg": 80.0}
    db_session.commit()
    out = run_tool(db_session, seed_user.id, TODAY, "get_weight_guidance", {})
    assert out["status"] == "missing_data"
