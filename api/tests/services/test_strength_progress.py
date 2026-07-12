"""Perf-driven progression and strength facts (epic MUSCU, M5)."""
from __future__ import annotations

from datetime import date

import pytest
from app.services.strength import create_strength_plan
from app.services.strength_logs import complete_session, log_set
from app.services.strength_progress import (
    exercise_history,
    strength_completions_as_activities,
    strength_facts,
    suggest_weights,
)

from tests.services.test_strength import seed_library

START = date(2026, 7, 6)


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


def _first_exercise(plan) -> tuple[str, int]:
    item = plan.structure["weeks"][0]["sessions"][0]["items"][0]
    return item["exercise_id"], item["sets"]


def _log_full_session(db, user_id, plan, *, week, day, exercise_id, sets,
                      weight, reps):
    for index in range(1, sets + 1):
        log_set(db, user_id, plan, week=week, day=day, exercise_id=exercise_id,
                set_index=index, weight_kg=weight, reps=reps)


def test_suggests_nothing_without_history(db_session, seed_user, plan):
    out = suggest_weights(db_session, seed_user.id, plan, week=1, day=0)
    exercise_id, _ = _first_exercise(plan)
    assert out[exercise_id]["weight_kg"] is None
    assert out[exercise_id]["last"] is None


def test_double_progression_adds_2point5_on_success(db_session, seed_user, plan):
    exercise_id, sets = _first_exercise(plan)
    prescribed_reps = plan.structure["weeks"][0]["sessions"][0]["items"][0]["reps"]
    # Same exercise appears in week 1 session A (day 0); log all sets at target.
    _log_full_session(
        db_session, seed_user.id, plan,
        week=1, day=0, exercise_id=exercise_id, sets=sets,
        weight=40.0, reps=prescribed_reps,
    )

    out = suggest_weights(db_session, seed_user.id, plan, week=2, day=0)
    assert out[exercise_id]["weight_kg"] == 42.5
    assert out[exercise_id]["last"] == {"weight_kg": 40.0, "reps": prescribed_reps}


def test_holds_weight_when_reps_were_missed(db_session, seed_user, plan):
    exercise_id, sets = _first_exercise(plan)
    prescribed_reps = plan.structure["weeks"][0]["sessions"][0]["items"][0]["reps"]
    _log_full_session(
        db_session, seed_user.id, plan,
        week=1, day=0, exercise_id=exercise_id, sets=sets,
        weight=40.0, reps=prescribed_reps - 2,
    )

    out = suggest_weights(db_session, seed_user.id, plan, week=2, day=0)
    assert out[exercise_id]["weight_kg"] == 40.0


def test_exercise_history_reports_pr_and_last(db_session, seed_user, plan):
    exercise_id, sets = _first_exercise(plan)
    _log_full_session(db_session, seed_user.id, plan, week=1, day=0,
                      exercise_id=exercise_id, sets=sets, weight=40.0, reps=10)
    _log_full_session(db_session, seed_user.id, plan, week=2, day=0,
                      exercise_id=exercise_id, sets=sets, weight=45.0, reps=8)

    history = exercise_history(db_session, seed_user.id, plan)
    entry = next(e for e in history if e["exercise_id"] == exercise_id)
    assert entry["pr_weight_kg"] == 45.0
    assert entry["last_weight_kg"] == 45.0
    assert entry["name"]


def test_strength_facts_summarise_program_and_week(db_session, seed_user, plan):
    exercise_id, sets = _first_exercise(plan)
    _log_full_session(db_session, seed_user.id, plan, week=1, day=0,
                      exercise_id=exercise_id, sets=sets, weight=40.0, reps=10)
    complete_session(db_session, seed_user.id, plan, week=1, day=0)

    facts = strength_facts(db_session, seed_user.id, date.today())
    assert facts["program"]["weeks"] == 8
    assert facts["sessions_7d"] == 1
    assert facts["volume_7d_kg"] == 40.0 * 10 * sets


def test_strength_facts_without_plan(db_session, seed_user):
    facts = strength_facts(db_session, seed_user.id, date.today())
    assert facts["program"] is None and facts["sessions_7d"] == 0


def test_completions_become_pseudo_activities(db_session, seed_user, plan):
    complete_session(db_session, seed_user.id, plan, week=1, day=0)
    acts = strength_completions_as_activities(db_session, seed_user.id)
    assert len(acts) == 1
    assert acts[0]["activity_type"] == "strength"
    assert acts[0]["tss"] is None
