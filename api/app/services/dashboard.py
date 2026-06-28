"""Coach-first dashboard assembly (US2).

Deterministic: every number here comes from AnalyticsEngine or the database.
The LLM is never involved — the dashboard must work on the free tier and be
fully testable. The narrative ``form`` assessment is a templated mapping of the
computed TSB, not generated text.
"""
from __future__ import annotations

import math
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.models.health import DailyHealth
from app.models.user import User
from app.services.analytics import (
    activity_tss,
    fitness_series,
    form_assessment,
    recovery_score,
)
from app.services.goals import GoalContext, get_goal_definition

# How far back the goal engine looks for recent activities and the weight trend.
GOAL_ACTIVITY_WINDOW = 30
WEIGHT_TREND_DAYS = 28

# Window of the fitness curve shown on the dashboard.
DEFAULT_WINDOW_DAYS = 42
# Reference resting HR used to derive a daily elevation delta for recovery.
RESTING_HR_BASELINE = 50


def _activity_tss(a: Activity) -> float:
    """TSS for one activity, preferring the stored value over the HR fallback."""
    return a.tss if a.tss is not None else activity_tss(a.duration_s, a.avg_hr)


def _week_summary(activities: list[Activity], start: date, end: date) -> dict:
    """Aggregate distance/TSS/duration/count for activities in [start, end]."""
    in_week = [a for a in activities if start <= a.start_time.date() <= end]
    return {
        "activity_count": len(in_week),
        "distance_m": round(sum(a.distance_m or 0.0 for a in in_week), 1),
        "tss": round(sum(_activity_tss(a) for a in in_week), 1),
        "duration_s": sum(a.duration_s or 0 for a in in_week),
    }


def _build_goal(user: User | None, today: date, first_activity: date | None) -> dict | None:
    """North-star race banner: countdown + progress from training start to race."""
    if user is None or user.race_date is None:
        return None
    days_to_go = (user.race_date - today).days
    weeks_to_go = max(math.ceil(days_to_go / 7), 0)
    start = first_activity or today
    total_days = max((user.race_date - start).days, 1)
    done_days = min(max((today - start).days, 0), total_days)
    progress_pct = round(done_days / total_days * 100)
    return {
        "race_name": user.race_name,
        "race_date": user.race_date.isoformat(),
        "days_to_go": days_to_go,
        "weeks_to_go": weeks_to_go,
        "progress_pct": progress_pct,
        "is_past": days_to_go < 0,
    }


# Metric the goal "lens" features first in the body snapshot (A13).
GOAL_FEATURE = {
    "marathon": "hrv",
    "triathlon": "hrv",
    "hyrox": "body_battery",
    "weight_loss": "weight_kg",
    "health": "steps",
}


def _avg(values: list[float | int | None]) -> float | None:
    """Average of the non-null values, or None when there are none."""
    present = [v for v in values if v is not None]
    return round(sum(present) / len(present), 1) if present else None


def _build_health(db: Session, user_id: str, today: date, goal: str | None) -> dict | None:
    """7-day body snapshot (latest + averages) from imported daily health."""
    start = today - timedelta(days=6)
    rows = list(
        db.execute(
            select(DailyHealth)
            .where(
                DailyHealth.user_id == user_id,
                DailyHealth.day >= start,
                DailyHealth.day <= today,
            )
            .order_by(DailyHealth.day)
        ).scalars()
    )
    if not rows:
        return None
    latest = rows[-1]
    return {
        "resting_hr": latest.resting_hr,
        "hrv": _avg([r.hrv for r in rows]),
        "sleep_score": _avg([r.sleep_score for r in rows]),
        "steps": _avg([r.steps for r in rows]),
        "body_battery": latest.body_battery,
        "stress_avg": _avg([r.stress_avg for r in rows]),
        "weight_kg": next((r.weight_kg for r in reversed(rows) if r.weight_kg), None),
        "days": len(rows),
        "feature": GOAL_FEATURE.get(goal or "", "hrv"),
    }


def _build_this_week(activities: list[Activity], today: date) -> dict:
    """This-week vs last-week aggregate (ISO weeks, Monday-anchored)."""
    monday = today - timedelta(days=today.weekday())
    last_monday = monday - timedelta(days=7)
    return {
        "this_week": _week_summary(activities, monday, today),
        "last_week": _week_summary(activities, last_monday, monday - timedelta(days=1)),
        "week_start": monday.isoformat(),
    }


def _build_goal_context(
    db: Session,
    user: User | None,
    activities: list[Activity],
    fitness: dict,
    recovery: int,
    health: dict | None,
    today: date,
) -> GoalContext:
    """Assemble the DB-free context the goal definitions read."""
    recent = [
        {
            "date": a.start_time.isoformat(),
            "activity_type": a.activity_type,
            "distance_m": a.distance_m,
            "duration_s": a.duration_s,
            "avg_hr": a.avg_hr,
            "tss": round(_activity_tss(a), 1),
        }
        for a in reversed(activities[-GOAL_ACTIVITY_WINDOW:])
    ]
    weight_start = today - timedelta(days=WEIGHT_TREND_DAYS)
    weight_rows = db.execute(
        select(DailyHealth)
        .where(
            DailyHealth.user_id == (user.id if user else ""),
            DailyHealth.day >= weight_start,
            DailyHealth.day <= today,
        )
        .order_by(DailyHealth.day)
    ).scalars()
    weight_series = [
        {"day": r.day.isoformat(), "kg": r.weight_kg}
        for r in weight_rows
        if r.weight_kg is not None
    ]
    return GoalContext(
        today=today,
        goal_params=(user.goal_params or {}) if user else {},
        fitness=fitness,
        recovery=recovery,
        health=health,
        recent_activities=recent,
        weight_series=weight_series,
    )


def _daily_tss(activities: list[Activity]) -> dict[date, float]:
    """Sum each activity's TSS into its calendar day."""
    by_day: dict[date, float] = {}
    for a in activities:
        day = a.start_time.date()
        by_day[day] = by_day.get(day, 0.0) + _activity_tss(a)
    return by_day


def build_dashboard(
    db: Session,
    user_id: str,
    today: date,
    window_days: int = DEFAULT_WINDOW_DAYS,
) -> dict:
    """Assemble the dashboard payload for one user.

    Builds a continuous daily TSS series across the window, runs the CTL/ATL/TSB
    recurrence, derives the form band and recovery score, and summarises totals
    and the latest activity. Only the given user's data is read.
    """
    start = today - timedelta(days=window_days - 1)
    activities = list(
        db.execute(
            select(Activity)
            .where(Activity.user_id == user_id)
            .order_by(Activity.start_time)
        ).scalars()
    )
    by_day = _daily_tss(activities)
    series = [by_day.get(start + timedelta(days=i), 0.0) for i in range(window_days)]
    states = fitness_series(series)

    load_series = [
        {
            "date": (start + timedelta(days=i)).isoformat(),
            "ctl": round(s.ctl, 1),
            "atl": round(s.atl, 1),
            "tsb": round(s.tsb, 1),
        }
        for i, s in enumerate(states)
    ]
    current = states[-1]

    latest_health = db.execute(
        select(DailyHealth)
        .where(DailyHealth.user_id == user_id)
        .order_by(DailyHealth.day.desc())
    ).scalars().first()
    resting_delta = 0.0
    sleep = 75.0
    if latest_health is not None:
        if latest_health.resting_hr is not None:
            resting_delta = float(latest_health.resting_hr - RESTING_HR_BASELINE)
        if latest_health.sleep_score is not None:
            sleep = float(latest_health.sleep_score)
    recovery = recovery_score(current.tsb, resting_delta, sleep)

    user = db.get(User, user_id)
    first_activity = activities[0].start_time.date() if activities else None
    goal = _build_goal(user, today, first_activity)
    this_week = _build_this_week(activities, today)
    health = _build_health(db, user_id, today, user.primary_goal if user else None)

    fitness = {
        "ctl": round(current.ctl, 1),
        "atl": round(current.atl, 1),
        "tsb": round(current.tsb, 1),
    }
    goal_ctx = _build_goal_context(db, user, activities, fitness, recovery, health, today)
    definition = get_goal_definition(user.primary_goal if user else None)
    goal_structured = definition.progress(goal_ctx)
    goal_variant = definition.dashboard_variant(goal_ctx)

    window_activities = [a for a in activities if a.start_time.date() >= start]
    total_distance = sum(a.distance_m or 0.0 for a in window_activities)
    latest = activities[-1] if activities else None
    latest_activity = (
        None
        if latest is None
        else {
            "id": latest.id,
            "activity_type": latest.activity_type,
            "name": latest.name,
            "start_time": latest.start_time.isoformat(),
            "distance_m": latest.distance_m,
            "duration_s": latest.duration_s,
            "avg_hr": latest.avg_hr,
        }
    )

    return {
        "goal": goal,
        "goal_structured": goal_structured,
        "goal_variant": goal_variant,
        "this_week": this_week,
        "health": health,
        "fitness": fitness,
        "form": form_assessment(current.tsb),
        "recovery": recovery,
        "load_series": load_series,
        "totals": {
            "activity_count": len(window_activities),
            "total_distance_m": round(total_distance, 1),
            "window_days": window_days,
        },
        "latest_activity": latest_activity,
    }
