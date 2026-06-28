"""Coach tools — deterministic data the agentic coach can pull on demand.

Each tool returns already-computed facts (from analytics / the goal engine /
adherence). The LLM calls them and narrates the result; it never computes a
number itself. ``TOOL_SPECS`` are OpenAI function-calling schemas.
"""
from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.services.adherence import match_week, week_adherence
from app.services.coach_facts import build_coach_facts
from app.services.plans import current_plan
from app.services.workout_push import current_week

TOOL_SPECS = [
    {
        "type": "function",
        "function": {
            "name": "get_goal_progress",
            "description": "The athlete's goal, projection, on-track band and race countdown.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_recent_activities",
            "description": "The athlete's most recent activities (date, type, distance, load).",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "minimum": 1, "maximum": 20}
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_health_trend",
            "description": "7-day body snapshot (HRV, sleep, steps, stress) and CTL/TSB trend.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_adherence",
            "description": "How the athlete is tracking against this week's prescribed sessions.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


def _recent_activities(db: Session, user_id: str, limit: int) -> list[dict]:
    rows = db.execute(
        select(Activity)
        .where(Activity.user_id == user_id)
        .order_by(Activity.start_time.desc())
        .limit(limit)
    ).scalars()
    return [
        {
            "date": a.start_time.isoformat(),
            "activity_type": a.activity_type,
            "distance_km": round((a.distance_m or 0.0) / 1000.0, 2),
            "duration_s": a.duration_s,
            "avg_hr": a.avg_hr,
            "tss": a.tss,
        }
        for a in rows
    ]


def _adherence(db: Session, user_id: str, today: date) -> dict:
    plan = current_plan(db, user_id)
    if plan is None:
        return {"status": "no_plan"}
    week = current_week(plan.structure, today)
    if week is None:
        return {"status": "no_current_week"}
    activities = _recent_activities(db, user_id, 20)
    match = match_week(week, activities, today)
    return {"status": "ok", "week": week.get("week"), **week_adherence(match)}


def run_tool(
    db: Session, user_id: str, today: date, name: str, args: dict
) -> dict:
    """Dispatch a tool call to its deterministic service. Pure data, no LLM."""
    if name == "get_goal_progress":
        facts = build_coach_facts(db, user_id, today)
        return {"goal": facts["goal"], "race": facts["race"]}
    if name == "get_recent_activities":
        limit = int(args.get("limit", 5))
        return {"activities": _recent_activities(db, user_id, max(1, min(limit, 20)))}
    if name == "get_health_trend":
        facts = build_coach_facts(db, user_id, today)
        return {"health": facts["health"], "trend": facts["trend"]}
    if name == "get_adherence":
        return _adherence(db, user_id, today)
    return {"error": f"unknown_tool:{name}"}
