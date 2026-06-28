"""'What do I do today' — the daily entry point to the closed loop.

Resolves the athlete's current plan week, today's prescribed session, how the
week is tracking (adherence), and the goal on-track band. Deterministic; the
brief/chat narrate on top of this.
"""
from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.services.adherence import match_week, week_adherence
from app.services.coach_facts import build_coach_facts
from app.services.coach_tools import _recent_activities
from app.services.plans import current_plan
from app.services.workout_push import current_week


def todays_session(db: Session, user_id: str, today: date) -> dict:
    """Today's prescription + week adherence + goal band, or a no-plan status."""
    facts = build_coach_facts(db, user_id, today)
    goal = facts["goal"]

    plan = current_plan(db, user_id)
    if plan is None:
        return {
            "status": "no_plan",
            "date": today.isoformat(),
            "goal_band": goal.get("on_track_band"),
            "headline": goal.get("headline"),
        }
    week = current_week(plan.structure, today)
    if week is None:
        return {
            "status": "no_current_week",
            "date": today.isoformat(),
            "goal_band": goal.get("on_track_band"),
            "headline": goal.get("headline"),
        }

    session = next(
        (s for s in week.get("sessions", []) if s["day_index"] == today.weekday()),
        None,
    )
    activities = _recent_activities(db, user_id, 20)
    adherence = week_adherence(match_week(week, activities, today))
    return {
        "status": "ok",
        "date": today.isoformat(),
        "week": week.get("week"),
        "phase": week.get("phase"),
        "session": session,  # None → rest day
        "is_rest": session is None,
        "adherence": adherence,
        "goal_band": goal.get("on_track_band"),
        "headline": goal.get("headline"),
    }
