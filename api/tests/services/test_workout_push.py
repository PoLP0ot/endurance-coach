"""Push-to-watch tests — plan week → Garmin workout payload (A14)."""
from __future__ import annotations

from datetime import date

import pytest
from app.core.security import encrypt
from app.models.garmin import GarminConnection
from app.models.plan import PLAN_ACTIVE, TrainingPlan
from app.services.workout_push import (
    build_garmin_workout,
    current_week,
    push_current_week,
)

STRUCTURE = {
    "goal": "marathon",
    "weeks": [
        {"week": 1, "start_date": "2026-06-01", "phase": "base", "focus": "Easy base"},
        {"week": 2, "start_date": "2026-06-08", "phase": "build", "focus": "Threshold"},
        {"week": 3, "start_date": "2026-06-15", "phase": "peak", "focus": "Race pace"},
    ],
}


def test_build_garmin_workout_has_valid_shape():
    workout = build_garmin_workout(STRUCTURE["weeks"][1])
    assert workout["sportType"]["sportTypeKey"] == "running"
    step = workout["workoutSegments"][0]["workoutSteps"][0]
    assert step["endCondition"]["conditionTypeKey"] == "time"
    assert step["endConditionValue"] == 60 * 60  # build phase
    assert "Threshold" in workout["workoutName"]


def test_current_week_picks_latest_started_week():
    assert current_week(STRUCTURE, date(2026, 6, 10))["week"] == 2
    assert current_week(STRUCTURE, date(2026, 6, 20))["week"] == 3
    assert current_week(STRUCTURE, date(2026, 5, 1)) is None


class _Pusher:
    def __init__(self) -> None:
        self.received: list[dict] = []

    def push_workouts(self, token: str, workouts: list[dict]) -> int:
        self.received.extend(workouts)
        return len(workouts)


def _connect(db, user_id: str) -> None:
    db.add(
        GarminConnection(
            user_id=user_id,
            encrypted_tokens=encrypt("tok"),
            garmin_username="marc@example.com",
            status="connected",
        )
    )
    db.commit()


def _plan(db, user_id: str) -> None:
    db.add(
        TrainingPlan(
            user_id=user_id,
            goal="marathon",
            weeks=3,
            start_date=date(2026, 6, 1),
            structure=STRUCTURE,
            narrative="",
            model="test",
            status=PLAN_ACTIVE,
        )
    )
    db.commit()


def test_push_current_week_sends_workout(db_session, seed_user):
    _connect(db_session, seed_user.id)
    _plan(db_session, seed_user.id)
    pusher = _Pusher()

    result = push_current_week(db_session, seed_user.id, pusher, date(2026, 6, 10))
    assert result == {"pushed": 1, "week": 2}
    assert pusher.received[0]["sportType"]["sportTypeKey"] == "running"


def test_push_requires_connected_garmin(db_session, seed_user):
    _plan(db_session, seed_user.id)
    with pytest.raises(ValueError, match="garmin_not_connected"):
        push_current_week(db_session, seed_user.id, _Pusher(), date(2026, 6, 10))


def test_push_requires_active_plan(db_session, seed_user):
    _connect(db_session, seed_user.id)
    with pytest.raises(ValueError, match="no_active_plan"):
        push_current_week(db_session, seed_user.id, _Pusher(), date(2026, 6, 10))
