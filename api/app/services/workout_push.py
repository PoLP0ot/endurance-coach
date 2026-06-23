"""Push the current plan week to a Garmin watch (A14).

Builds a Garmin-Connect structured workout from the deterministic plan week and
hands it to the GarminProvider. The workout shape is data; the provider does the
network upload. Numbers come from the plan, never from a model.
"""
from __future__ import annotations

from datetime import date
from typing import Protocol

from sqlalchemy.orm import Session

from app.models.garmin import GarminConnection
from app.services.plans import current_plan

# Garmin sport identifiers (running) for the workout payload.
_RUN_SPORT = {"sportTypeId": 1, "sportTypeKey": "running"}
# Default session length per week phase, in seconds.
_PHASE_DURATION_S = {
    "base": 45 * 60,
    "build": 60 * 60,
    "peak": 75 * 60,
    "taper": 40 * 60,
}
_DEFAULT_DURATION_S = 50 * 60


class _Pusher(Protocol):
    def push_workouts(self, token: str, workouts: list[dict]) -> int: ...


def build_garmin_workout(week: dict) -> dict:
    """Build one Garmin workout JSON from a plan week.

    A single time-based run step carries the week's coaching focus. This is the
    minimal valid shape Garmin Connect accepts for a structured workout.
    """
    phase = week.get("phase", "base")
    duration_s = _PHASE_DURATION_S.get(phase, _DEFAULT_DURATION_S)
    focus = week.get("focus", "Endurance session")
    name = f"Week {week.get('week', '?')} · {focus}"
    return {
        "workoutName": name[:80],
        "sportType": _RUN_SPORT,
        "workoutSegments": [
            {
                "segmentOrder": 1,
                "sportType": _RUN_SPORT,
                "workoutSteps": [
                    {
                        "type": "ExecutableStepDTO",
                        "stepOrder": 1,
                        "stepType": {"stepTypeId": 3, "stepTypeKey": "interval"},
                        "endCondition": {
                            "conditionTypeId": 2,
                            "conditionTypeKey": "time",
                        },
                        "endConditionValue": duration_s,
                        "description": focus,
                    }
                ],
            }
        ],
    }


def current_week(structure: dict, today: date) -> dict | None:
    """Return the plan week containing ``today``, or None when out of range."""
    weeks = structure.get("weeks", [])
    chosen = None
    for week in weeks:
        start = date.fromisoformat(week["start_date"])
        if start <= today:
            chosen = week
    return chosen


def push_current_week(
    db: Session,
    user_id: str,
    provider: _Pusher,
    today: date,
) -> dict:
    """Push the active plan's current-week workout to the user's Garmin watch.

    Returns ``{"pushed": n, "week": int}``. Raises ValueError when there is no
    connected Garmin account or no active plan week to send.
    """
    conn = (
        db.query(GarminConnection).filter_by(user_id=user_id).one_or_none()
    )
    if conn is None or conn.status != "connected" or not conn.encrypted_tokens:
        raise ValueError("garmin_not_connected")

    plan = current_plan(db, user_id)
    if plan is None:
        raise ValueError("no_active_plan")
    week = current_week(plan.structure, today)
    if week is None:
        raise ValueError("no_current_week")

    from app.core.security import decrypt

    token = decrypt(conn.encrypted_tokens)
    workout = build_garmin_workout(week)
    pushed = provider.push_workouts(token, [workout])
    return {"pushed": pushed, "week": week.get("week")}
