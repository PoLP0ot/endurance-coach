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
    {
        "type": "function",
        "function": {
            "name": "get_weight_guidance",
            "description": (
                "Deterministic weight-loss pacing: required kg/week for the "
                "athlete's deadline, weekly calorie deficit equivalents, healthy "
                "rate window. ALWAYS use this for any calorie or pacing question."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_strength_progress",
            "description": (
                "The athlete's strength program status: current week, sessions "
                "and volume this week, personal records."
            ),
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "propose_strength_plan",
            "description": (
                "Compose and activate a periodized strength program from the "
                "exercise library. Ask the athlete for their weekly frequency, "
                "program length, level and available equipment first."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "frequency": {"type": "integer", "minimum": 2, "maximum": 4},
                    "weeks": {"type": "integer", "minimum": 8, "maximum": 16},
                    "level": {
                        "type": "string",
                        "enum": ["beginner", "intermediate", "advanced"],
                    },
                    "equipment": {
                        "type": "array",
                        "items": {"type": "string"},
                        "minItems": 1,
                        "description": "e.g. body weight, dumbbell, barbell, cable",
                    },
                },
                "required": ["frequency", "weeks", "level", "equipment"],
            },
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
    from app.services.strength_progress import strength_completions_as_activities

    activities = _recent_activities(db, user_id, 20) + strength_completions_as_activities(
        db, user_id
    )
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
    if name == "propose_strength_plan":
        return _propose_strength_plan(db, user_id, today, args)
    if name == "get_strength_progress":
        from app.services.strength_progress import strength_facts

        return strength_facts(db, user_id, today)
    if name == "get_weight_guidance":
        return _weight_guidance(db, user_id, today)
    return {"error": f"unknown_tool:{name}"}


# Energy density of body fat — the ONLY calorie constant the coach may cite.
KCAL_PER_KG_FAT = 7700


def _weight_guidance(db: Session, user_id: str, today: date) -> dict:
    """Deterministic weight-loss pacing derived from the goal engine."""
    goal = build_coach_facts(db, user_id, today)["goal"]
    if goal.get("kind") != "weight_loss":
        return {"status": "not_weight_loss_goal", "goal_kind": goal.get("kind")}
    current, target = goal.get("current"), goal.get("target")
    if current is None or target is None:
        return {
            "status": "missing_data",
            "hint": "needs a target weight and at least two weigh-ins",
            "current_weight_kg": current,
            "target_weight_kg": target,
        }

    out = {
        "status": "ok",
        "current_weight_kg": current,
        "target_weight_kg": target,
        "to_lose_kg": round(current - target, 1),
        "target_date": goal.get("target_date"),
        "eta": goal.get("eta"),
        "on_track_band": goal.get("on_track_band"),
        "current_rate_kg_per_week": goal.get("rate_kg_per_week"),
        "required_rate_kg_per_week": goal.get("required_rate_kg_per_week"),
        "kcal_per_kg": KCAL_PER_KG_FAT,
        "healthy_rate_kg_per_week": [0.25, 1.0],
    }
    required = goal.get("required_rate_kg_per_week")
    if required is not None:
        out["weekly_kcal_deficit_needed"] = round(required * KCAL_PER_KG_FAT)
    rate = goal.get("rate_kg_per_week")
    if rate is not None and rate < 0:
        out["weekly_kcal_deficit_at_current_rate"] = round(-rate * KCAL_PER_KG_FAT)
    if goal.get("target_date"):
        days = (date.fromisoformat(goal["target_date"]) - today).days
        out["weeks_remaining"] = round(days / 7, 1)
    return out


def _propose_strength_plan(
    db: Session, user_id: str, today: date, args: dict
) -> dict:
    from app.services.strength import create_strength_plan

    try:
        plan = create_strength_plan(
            db,
            user_id,
            frequency=int(args["frequency"]),
            weeks=int(args["weeks"]),
            level=str(args["level"]),
            equipment=list(args["equipment"]),
            start_date=today,
        )
    except (KeyError, TypeError, ValueError) as exc:
        return {"error": f"invalid_params:{exc}"}
    first_week = plan.structure["weeks"][0]
    return {
        "status": "created",
        "weeks": plan.weeks,
        "frequency": plan.frequency,
        "level": plan.level,
        "equipment": plan.equipment,
        "blocks": plan.structure["blocks"],
        "first_week_sessions": [
            {
                "day": s["day"],
                "title": s["title"],
                "exercises": [i["name"] for i in s["items"]],
            }
            for s in first_week["sessions"]
        ],
    }
