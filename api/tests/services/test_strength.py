"""Deterministic strength-program composer (epic MUSCU, M3)."""
from __future__ import annotations

from datetime import date

from app.services.exercises import upsert_exercises
from app.services.strength import (
    build_strength_structure,
    create_strength_plan,
    current_strength_plan,
)

from tests.services.test_exercises import make_raw

START = date(2026, 7, 13)

_TARGETS = [
    ("quads", "upper legs"),
    ("pectorals", "chest"),
    ("lats", "back"),
    ("upper back", "back"),
    ("hamstrings", "upper legs"),
    ("glutes", "upper legs"),
    ("delts", "shoulders"),
    ("abs", "waist"),
    ("biceps", "upper arms"),
    ("triceps", "upper arms"),
    ("calves", "lower legs"),
]


def seed_library(db) -> None:
    """Two exercises per target: one body-weight, one dumbbell."""
    records = []
    i = 1
    for target, body_part in _TARGETS:
        for equipment in ("body weight", "dumbbell"):
            records.append(
                make_raw(
                    f"{i:04d}",
                    f"{equipment} {target} drill",
                    body_part=body_part,
                    target=target,
                    equipment=equipment,
                )
            )
            i += 1
    upsert_exercises(db, records)


def build(db, **overrides) -> dict:
    params = {
        "frequency": 3,
        "weeks": 8,
        "level": "intermediate",
        "equipment": ["dumbbell"],
        "start_date": START,
    }
    params.update(overrides)
    return build_strength_structure(db, **params)


def test_structure_shape_blocks_and_deload(db_session):
    seed_library(db_session)
    structure = build(db_session)

    weeks = structure["weeks"]
    assert len(weeks) == 8
    assert weeks[0]["block"] == "adaptation"
    assert weeks[-1]["block"] == "strength"
    assert any(w["block"] == "hypertrophy" for w in weeks)
    assert [w["is_deload"] for w in weeks].count(True) == 2  # weeks 4 and 8
    assert weeks[3]["is_deload"] and weeks[7]["is_deload"]

    for week in weeks:
        assert len(week["sessions"]) == 3
        days = [s["day"] for s in week["sessions"]]
        assert days == sorted(days) and all(0 <= d <= 6 for d in days)
        for session in week["sessions"]:
            assert session["items"], "every session prescribes exercises"
            for item in session["items"]:
                assert item["sets"] >= 2 and item["reps"] >= 4
                assert item["rest_sec"] > 0 and 5 <= item["rpe"] <= 9


def test_equipment_profile_is_respected(db_session):
    seed_library(db_session)
    structure = build(db_session, equipment=["dumbbell"])
    for week in structure["weeks"]:
        for session in week["sessions"]:
            for item in session["items"]:
                assert item["equipment"] in {"dumbbell", "body weight"}


def test_composition_is_deterministic(db_session):
    seed_library(db_session)
    assert build(db_session) == build(db_session)


def test_twice_weekly_full_body_sessions_vary(db_session):
    seed_library(db_session)
    structure = build(db_session, frequency=2)
    a, b = structure["weeks"][0]["sessions"]
    assert a["focus"] == "full" and b["focus"] == "full"
    assert a["items"][0]["exercise_id"] != b["items"][0]["exercise_id"]


def test_deload_eases_the_week(db_session):
    seed_library(db_session)
    structure = build(db_session)
    normal = structure["weeks"][4]["sessions"][0]["items"][0]  # week 5, hypertrophy
    deload = structure["weeks"][3]["sessions"][0]["items"][0]  # week 4 deload
    assert deload["rpe"] < normal["rpe"]
    assert deload["sets"] <= normal["sets"]


def test_create_archives_previous_and_current_returns_latest(db_session, seed_user):
    seed_library(db_session)
    first = create_strength_plan(
        db_session,
        seed_user.id,
        frequency=2,
        weeks=8,
        level="beginner",
        equipment=["body weight"],
        start_date=START,
    )
    second = create_strength_plan(
        db_session,
        seed_user.id,
        frequency=3,
        weeks=12,
        level="intermediate",
        equipment=["dumbbell"],
        start_date=START,
    )
    db_session.refresh(first)
    assert first.status == "archived"
    current = current_strength_plan(db_session, seed_user.id)
    assert current is not None and current.id == second.id
    assert current.weeks == 12
