"""In-session set logging against a strength program (epic MUSCU, M4).

Sets are keyed by (plan, week, day, exercise, set_index): re-logging the same
index corrects the entry. Volume and completion are computed here; the LLM
never touches these numbers.
"""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.strength_log import StrengthSessionDone, StrengthSetLog
from app.models.strength_plan import StrengthPlan


def find_session(plan: StrengthPlan, week: int, day: int) -> dict:
    """The prescribed session at (week, day), or ``ValueError`` if absent."""
    for plan_week in plan.structure["weeks"]:
        if plan_week["week"] != week:
            continue
        for session in plan_week["sessions"]:
            if session["day"] == day:
                return session
    raise ValueError("unknown_session")


def log_set(
    db: Session,
    user_id: str,
    plan: StrengthPlan,
    *,
    week: int,
    day: int,
    exercise_id: str,
    set_index: int,
    weight_kg: float | None,
    reps: int,
    rpe: float | None = None,
) -> dict:
    """Record (or correct) one performed set of a prescribed session."""
    session = find_session(plan, week, day)
    if exercise_id not in {item["exercise_id"] for item in session["items"]}:
        raise ValueError("unknown_exercise")

    existing = db.execute(
        select(StrengthSetLog).where(
            StrengthSetLog.plan_id == plan.id,
            StrengthSetLog.week == week,
            StrengthSetLog.day == day,
            StrengthSetLog.exercise_id == exercise_id,
            StrengthSetLog.set_index == set_index,
        )
    ).scalars().first()

    if existing is None:
        existing = StrengthSetLog(
            user_id=user_id,
            plan_id=plan.id,
            week=week,
            day=day,
            exercise_id=exercise_id,
            set_index=set_index,
        )
    existing.weight_kg = weight_kg
    existing.reps = reps
    existing.rpe = rpe
    db.add(existing)
    db.commit()
    db.refresh(existing)
    return _serialize(existing)


def _serialize(log: StrengthSetLog) -> dict:
    return {
        "exercise_id": log.exercise_id,
        "set_index": log.set_index,
        "weight_kg": log.weight_kg,
        "reps": log.reps,
        "rpe": log.rpe,
    }


def session_logs(
    db: Session, user_id: str, plan_id: str, *, week: int, day: int
) -> list[dict]:
    """All sets logged for one session, ordered by exercise then set."""
    rows = db.execute(
        select(StrengthSetLog)
        .where(
            StrengthSetLog.user_id == user_id,
            StrengthSetLog.plan_id == plan_id,
            StrengthSetLog.week == week,
            StrengthSetLog.day == day,
        )
        .order_by(StrengthSetLog.exercise_id.asc(), StrengthSetLog.set_index.asc())
    ).scalars()
    return [_serialize(log) for log in rows]


def _is_completed(db: Session, plan_id: str, week: int, day: int) -> bool:
    return (
        db.execute(
            select(StrengthSessionDone).where(
                StrengthSessionDone.plan_id == plan_id,
                StrengthSessionDone.week == week,
                StrengthSessionDone.day == day,
            )
        ).scalars().first()
        is not None
    )


def session_summary(
    db: Session, user_id: str, plan: StrengthPlan, *, week: int, day: int
) -> dict:
    """Prescribed vs performed for one session: sets, volume, completion."""
    session = find_session(plan, week, day)
    logs = session_logs(db, user_id, plan.id, week=week, day=day)
    volume = sum((log["weight_kg"] or 0.0) * log["reps"] for log in logs)
    return {
        "week": week,
        "day": day,
        "title": session["title"],
        "sets_prescribed": sum(item["sets"] for item in session["items"]),
        "sets_logged": len(logs),
        "volume_kg": round(volume, 1),
        "completed": _is_completed(db, plan.id, week, day),
    }


def complete_session(
    db: Session, user_id: str, plan: StrengthPlan, *, week: int, day: int
) -> dict:
    """Mark a session done (idempotent) and return its summary."""
    find_session(plan, week, day)
    if not _is_completed(db, plan.id, week, day):
        db.add(
            StrengthSessionDone(
                user_id=user_id, plan_id=plan.id, week=week, day=day
            )
        )
        db.commit()
    return session_summary(db, user_id, plan, week=week, day=day)
