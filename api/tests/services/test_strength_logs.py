"""In-session set logging and session completion (epic MUSCU, M4)."""
from __future__ import annotations

from datetime import date

import pytest
from app.services.strength import create_strength_plan
from app.services.strength_logs import (
    complete_session,
    log_set,
    session_logs,
    session_summary,
)

from tests.services.test_strength import seed_library

START = date(2026, 7, 13)


@pytest.fixture()
def plan(db_session, seed_user):
    seed_library(db_session)
    return create_strength_plan(
        db_session,
        seed_user.id,
        frequency=2,
        weeks=8,
        level="intermediate",
        equipment=["dumbbell"],
        start_date=START,
    )


def test_log_set_upserts_on_same_index(db_session, seed_user, plan):
    exercise_id = plan.structure["weeks"][0]["sessions"][0]["items"][0]["exercise_id"]

    log_set(
        db_session, seed_user.id, plan,
        week=1, day=0, exercise_id=exercise_id, set_index=1,
        weight_kg=40.0, reps=10, rpe=8.0,
    )
    log_set(
        db_session, seed_user.id, plan,
        week=1, day=0, exercise_id=exercise_id, set_index=1,
        weight_kg=42.5, reps=9, rpe=8.5,
    )

    logs = session_logs(db_session, seed_user.id, plan.id, week=1, day=0)
    assert len(logs) == 1
    assert logs[0]["weight_kg"] == 42.5 and logs[0]["reps"] == 9


def test_log_set_rejects_unknown_session_or_exercise(db_session, seed_user, plan):
    exercise_id = plan.structure["weeks"][0]["sessions"][0]["items"][0]["exercise_id"]
    with pytest.raises(ValueError, match="unknown_session"):
        log_set(
            db_session, seed_user.id, plan,
            week=1, day=6, exercise_id=exercise_id, set_index=1,
            weight_kg=40.0, reps=10,
        )
    with pytest.raises(ValueError, match="unknown_exercise"):
        log_set(
            db_session, seed_user.id, plan,
            week=1, day=0, exercise_id="9999", set_index=1,
            weight_kg=40.0, reps=10,
        )


def test_complete_session_returns_summary(db_session, seed_user, plan):
    session = plan.structure["weeks"][0]["sessions"][0]
    first, second = session["items"][0], session["items"][1]
    log_set(db_session, seed_user.id, plan, week=1, day=0,
            exercise_id=first["exercise_id"], set_index=1, weight_kg=40.0, reps=10)
    log_set(db_session, seed_user.id, plan, week=1, day=0,
            exercise_id=first["exercise_id"], set_index=2, weight_kg=40.0, reps=8)
    log_set(db_session, seed_user.id, plan, week=1, day=0,
            exercise_id=second["exercise_id"], set_index=1, weight_kg=None, reps=12)

    out = complete_session(db_session, seed_user.id, plan, week=1, day=0)
    assert out["completed"] is True
    assert out["sets_logged"] == 3
    assert out["volume_kg"] == 40.0 * 10 + 40.0 * 8
    # Completing twice stays idempotent.
    again = complete_session(db_session, seed_user.id, plan, week=1, day=0)
    assert again["completed"] is True and again["sets_logged"] == 3


def test_session_summary_reports_prescribed_vs_done(db_session, seed_user, plan):
    session = plan.structure["weeks"][0]["sessions"][0]
    prescribed = sum(i["sets"] for i in session["items"])
    out = session_summary(db_session, seed_user.id, plan, week=1, day=0)
    assert out["sets_prescribed"] == prescribed
    assert out["sets_logged"] == 0 and out["completed"] is False
