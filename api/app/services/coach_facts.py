"""Single source of deterministic, goal-aware facts for every AI surface.

Chat, signals, the weekly email and the daily brief all narrate the SAME fact
sheet so the coach is consistently aware of the athlete's goal, projection,
recovery and recent trend. Every number here comes from ``build_dashboard``
(i.e. ``analytics.py`` + the goal engine) — the LLM only narrates it.
"""
from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.services.dashboard import build_dashboard
from app.services.strength_progress import strength_facts

# How many recent days of the load curve to expose as a trend hint.
TREND_DAYS = 14


def build_coach_facts(db: Session, user_id: str, today: date) -> dict:
    """Compact, goal-aware fact sheet shared by all coaching surfaces."""
    data = build_dashboard(db, user_id, today=today)
    tail = data["load_series"][-TREND_DAYS:]
    return {
        "goal": data["goal_structured"],
        "race": data["goal"],
        "goal_metrics": data["goal_variant"]["panels"],
        "fitness": data["fitness"],
        "form": data["form"],
        "recovery": data["recovery"],
        "health": data["health"],
        "this_week": data["this_week"],
        "totals": data["totals"],
        "trend": [{"date": p["date"], "ctl": p["ctl"], "tsb": p["tsb"]} for p in tail],
        "strength": strength_facts(db, user_id, today),
    }
