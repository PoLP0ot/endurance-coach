"""Triathlon goal — per-discipline (swim/bike/run) load balance."""
from __future__ import annotations

from app.services.goals.base import (
    AT_RISK,
    ON_TRACK,
    GoalContext,
    session_from_microcycle,
)

_SPORT_MAP = {
    "swimming": "swim",
    "lap_swimming": "swim",
    "open_water_swimming": "swim",
    "cycling": "bike",
    "road_biking": "bike",
    "indoor_cycling": "bike",
    "virtual_ride": "bike",
}

_MICRO = [
    ("swim", "Swim technique 2 km"),
    ("bike", "Bike endurance 60 min"),
    ("easy", "Run easy 8 km"),
    ("swim", "Swim intervals 1.8 km"),
    ("interval", "Bike intervals 5×4 min"),
    ("long", "Brick: bike 50 km + run 5 km"),
    ("rest", ""),
]


def _sport_of(activity_type: str) -> str:
    if activity_type.startswith("run"):
        return "run"
    return _SPORT_MAP.get(activity_type, "other")


class TriathlonGoal:
    kind = "triathlon"

    def _by_sport(self, ctx: GoalContext) -> dict[str, float]:
        totals = {"swim": 0.0, "bike": 0.0, "run": 0.0}
        for a in ctx.recent_activities:
            sport = _sport_of(a.get("activity_type") or "")
            if sport in totals:
                totals[sport] += a.get("tss") or 0.0
        return {k: round(v, 1) for k, v in totals.items()}

    def progress(self, ctx: GoalContext) -> dict:
        by_sport = self._by_sport(ctx)
        active = [v for v in by_sport.values() if v > 0]
        neglected = [s for s, v in by_sport.items() if v == 0]
        balanced = len(active) == 3
        band = ON_TRACK if balanced else AT_RISK
        if not active:
            headline = "Log swim, bike and run sessions and I'll balance the three."
        elif balanced:
            headline = "All three disciplines are getting load — well balanced."
        else:
            headline = f"Neglecting: {', '.join(neglected)}. Add a session to balance the three."
        return {
            "kind": self.kind,
            "label": "Three-sport balance",
            "by_sport": by_sport,
            "on_track_band": band,
            "headline": headline,
            "eta": ctx.goal_params.get("race_date"),
        }

    def primary_metrics(self, ctx: GoalContext) -> list[dict]:
        by_sport = self._by_sport(ctx)
        return [
            {"label": "Swim", "value": by_sport["swim"], "unit": "TSS", "hint": "recent"},
            {"label": "Bike", "value": by_sport["bike"], "unit": "TSS", "hint": "recent"},
            {"label": "Run", "value": by_sport["run"], "unit": "TSS", "hint": "recent"},
        ]

    def dashboard_variant(self, ctx: GoalContext) -> dict:
        return {"kind": self.kind, "panels": self.primary_metrics(ctx)}

    def daily_session_template(
        self, week: dict, day_index: int, goal_params: dict | None = None
    ) -> dict | None:
        return session_from_microcycle(week, day_index, _MICRO)
