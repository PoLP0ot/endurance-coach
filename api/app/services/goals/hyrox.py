"""Hyrox goal — balance of compromised running and strength load."""
from __future__ import annotations

from app.services.goals.base import (
    AT_RISK,
    ON_TRACK,
    GoalContext,
    metric,
    session_from_microcycle,
)

_STRENGTH_TYPES = ("strength", "training", "cardio", "fitness_equipment", "hiit")

_MICRO = [
    ("strength", "Strength endurance circuit"),
    ("easy", "Compromised run 6 km"),
    ("rest", ""),
    ("interval", "Run + strength stations 5 rounds"),
    ("strength", "Heavy carries + sled work"),
    ("long", "Long run 12 km"),
    ("rest", ""),
]


class HyroxGoal:
    kind = "hyrox"

    def _split(self, ctx: GoalContext) -> tuple[float, float]:
        run = sum(
            a.get("tss") or 0.0
            for a in ctx.recent_activities
            if (a.get("activity_type") or "").startswith("run")
        )
        strength = sum(
            a.get("tss") or 0.0
            for a in ctx.recent_activities
            if (a.get("activity_type") or "") in _STRENGTH_TYPES
        )
        return round(run, 1), round(strength, 1)

    def progress(self, ctx: GoalContext) -> dict:
        run, strength = self._split(ctx)
        total = run + strength
        balanced = total > 0 and 0.35 <= run / total <= 0.65
        band = ON_TRACK if balanced else AT_RISK
        if total == 0:
            headline = "Log runs and strength sessions and I'll balance the two."
        elif balanced:
            headline = "Run and strength load are well balanced for Hyrox."
        elif run / total > 0.65:
            headline = "Heavy on running — add strength endurance to balance it."
        else:
            headline = "Heavy on strength — add compromised running to balance it."
        return {
            "kind": self.kind,
            "label": "Run / strength balance",
            "run_load": run,
            "strength_load": strength,
            "on_track_band": band,
            "headline": headline,
            "eta": ctx.goal_params.get("race_date"),
        }

    def primary_metrics(self, ctx: GoalContext) -> list[dict]:
        run, strength = self._split(ctx)
        battery = (ctx.health or {}).get("body_battery") or "—"
        return [
            metric("Run load", run, "TSS", "recent"),
            metric("Strength load", strength, "TSS", "recent"),
            metric("Body Battery", battery, "", "latest"),
        ]

    def dashboard_variant(self, ctx: GoalContext) -> dict:
        return {"kind": self.kind, "panels": self.primary_metrics(ctx)}

    def daily_session_template(self, week: dict, day_index: int) -> dict | None:
        return session_from_microcycle(week, day_index, _MICRO)
