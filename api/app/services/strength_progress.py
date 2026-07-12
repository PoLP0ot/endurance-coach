"""Perf-driven strength progression and coaching facts (epic MUSCU, M5).

Double progression: when the athlete logged every prescribed set of an
exercise at (or above) the prescribed reps, the next suggestion adds 2.5 kg;
otherwise it holds the last weight. Deload weeks are already planned by the
composer. All numbers are computed here — the LLM only narrates them.
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exercise import Exercise
from app.models.strength_log import StrengthSessionDone, StrengthSetLog
from app.models.strength_plan import StrengthPlan
from app.services.strength import current_strength_plan
from app.services.strength_logs import find_session

PROGRESSION_INCREMENT_KG = 2.5
FACTS_WINDOW_DAYS = 7
TOP_PRS = 3


def _plan_logs(db: Session, user_id: str, plan_id: str) -> list[StrengthSetLog]:
    return list(
        db.execute(
            select(StrengthSetLog)
            .where(
                StrengthSetLog.user_id == user_id,
                StrengthSetLog.plan_id == plan_id,
            )
            .order_by(
                StrengthSetLog.week.asc(),
                StrengthSetLog.day.asc(),
                StrengthSetLog.set_index.asc(),
            )
        ).scalars()
    )


def _last_session_group(
    logs: list[StrengthSetLog], exercise_id: str, before: tuple[int, int]
) -> list[StrengthSetLog]:
    """Sets of the most recent earlier session where the exercise was logged."""
    groups: dict[tuple[int, int], list[StrengthSetLog]] = {}
    for log in logs:
        if log.exercise_id != exercise_id or (log.week, log.day) >= before:
            continue
        groups.setdefault((log.week, log.day), []).append(log)
    if not groups:
        return []
    return groups[max(groups)]


def _top_set(sets: list[StrengthSetLog]) -> StrengthSetLog:
    return max(sets, key=lambda log: (log.weight_kg is not None, log.weight_kg or 0.0))


def _prescription(plan: StrengthPlan, week: int, day: int, exercise_id: str) -> dict | None:
    try:
        session = find_session(plan, week, day)
    except ValueError:
        return None
    for item in session["items"]:
        if item["exercise_id"] == exercise_id:
            return item
    return None


def suggest_weights(
    db: Session, user_id: str, plan: StrengthPlan, *, week: int, day: int
) -> dict:
    """Suggested load per exercise of one session, from prior logged sets."""
    session = find_session(plan, week, day)
    logs = _plan_logs(db, user_id, plan.id)

    suggestions: dict[str, dict] = {}
    for item in session["items"]:
        group = _last_session_group(logs, item["exercise_id"], (week, day))
        if not group:
            suggestions[item["exercise_id"]] = {"weight_kg": None, "last": None}
            continue
        top = _top_set(group)
        last = {"weight_kg": top.weight_kg, "reps": top.reps}
        prescribed = _prescription(plan, group[0].week, group[0].day, item["exercise_id"])
        success = (
            prescribed is not None
            and len(group) >= prescribed["sets"]
            and all(log.reps >= prescribed["reps"] for log in group)
        )
        weight = top.weight_kg
        if success and weight is not None:
            weight = round(weight + PROGRESSION_INCREMENT_KG, 1)
        suggestions[item["exercise_id"]] = {"weight_kg": weight, "last": last}
    return suggestions


def exercise_history(db: Session, user_id: str, plan: StrengthPlan) -> list[dict]:
    """Per-exercise PR and latest performance across the program."""
    logs = _plan_logs(db, user_id, plan.id)
    by_exercise: dict[str, list[StrengthSetLog]] = {}
    for log in logs:
        by_exercise.setdefault(log.exercise_id, []).append(log)

    history = []
    for exercise_id, entries in by_exercise.items():
        weights = [log.weight_kg for log in entries if log.weight_kg is not None]
        last_key = max((log.week, log.day) for log in entries)
        last_group = [log for log in entries if (log.week, log.day) == last_key]
        top = _top_set(last_group)
        exercise = db.get(Exercise, exercise_id)
        history.append(
            {
                "exercise_id": exercise_id,
                "name": exercise.name if exercise is not None else exercise_id,
                "pr_weight_kg": max(weights) if weights else None,
                "last_weight_kg": top.weight_kg,
                "last_reps": top.reps,
                "sets_logged": len(entries),
            }
        )
    history.sort(key=lambda entry: entry["name"])
    return history


def strength_completions_as_activities(db: Session, user_id: str) -> list[dict]:
    """Completed strength sessions shaped like activities for adherence."""
    rows = db.execute(
        select(StrengthSessionDone)
        .where(StrengthSessionDone.user_id == user_id)
        .order_by(StrengthSessionDone.completed_at.desc())
    ).scalars()
    return [
        {
            "date": done.completed_at.isoformat(),
            "tss": None,
            "activity_type": "strength",
        }
        for done in rows
    ]


def strength_facts(db: Session, user_id: str, today: date) -> dict:
    """Deterministic strength summary for the coaching fact sheet."""
    plan = current_strength_plan(db, user_id)
    if plan is None:
        return {"program": None, "sessions_7d": 0, "volume_7d_kg": 0.0, "prs": []}

    cutoff = datetime.combine(today - timedelta(days=FACTS_WINDOW_DAYS), time.min)
    completions = db.execute(
        select(StrengthSessionDone).where(
            StrengthSessionDone.user_id == user_id,
            StrengthSessionDone.plan_id == plan.id,
            StrengthSessionDone.completed_at >= cutoff,
        )
    ).scalars().all()
    recent_logs = db.execute(
        select(StrengthSetLog).where(
            StrengthSetLog.user_id == user_id,
            StrengthSetLog.plan_id == plan.id,
            StrengthSetLog.created_at >= cutoff,
        )
    ).scalars().all()
    volume = sum((log.weight_kg or 0.0) * log.reps for log in recent_logs)

    current_week = min(
        max((today - plan.start_date).days // 7 + 1, 1), plan.weeks
    )
    prs = [
        {"name": entry["name"], "weight_kg": entry["pr_weight_kg"]}
        for entry in exercise_history(db, user_id, plan)
        if entry["pr_weight_kg"] is not None
    ]
    prs.sort(key=lambda entry: entry["weight_kg"], reverse=True)

    return {
        "program": {
            "weeks": plan.weeks,
            "frequency": plan.frequency,
            "level": plan.level,
            "current_week": current_week,
        },
        "sessions_7d": len(completions),
        "volume_7d_kg": round(volume, 1),
        "prs": prs[:TOP_PRS],
    }
