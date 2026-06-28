"""General-health goal — consistency + recovery. The fallback definition."""
from __future__ import annotations

from datetime import date, timedelta

from app.services.goals.base import (
    AHEAD,
    AT_RISK,
    OFF_TRACK,
    ON_TRACK,
    GoalContext,
    metric,
    session_from_microcycle,
)

# Default weekly active-day target when the user hasn't set one.
_DEFAULT_TARGET_DAYS = 4

_MICRO = [
    ("easy", "Easy movement 30 min"),
    ("steps", "Active day · 8k steps"),
    ("easy", "Easy cardio 35 min"),
    ("rest", ""),
    ("steps", "Active day · 8k steps"),
    ("long", "Longer easy session 50 min"),
    ("rest", ""),
]


class HealthGoal:
    kind = "health"

    def _active_days(self, ctx: GoalContext) -> int:
        start = ctx.today - timedelta(days=6)
        days = {
            a["date"]
            for a in ctx.recent_activities
            if a.get("date") and start <= date.fromisoformat(a["date"][:10]) <= ctx.today
        }
        return len(days)

    def progress(self, ctx: GoalContext) -> dict:
        target = ctx.goal_params.get("weekly_activity_target", _DEFAULT_TARGET_DAYS)
        active = self._active_days(ctx)
        if active >= target + 1:
            band, headline = AHEAD, f"{active} active days this week — excellent consistency."
        elif active >= target:
            band, headline = ON_TRACK, f"{active}/{target} active days — right on target."
        elif active >= max(target - 1, 1):
            band, headline = AT_RISK, f"{active}/{target} active days — one more would do it."
        else:
            band, headline = OFF_TRACK, f"{active}/{target} active days — let's rebuild the habit."
        return {
            "kind": self.kind,
            "label": "Consistency",
            "current": active,
            "target": target,
            "on_track_band": band,
            "headline": headline,
            "eta": None,
        }

    def primary_metrics(self, ctx: GoalContext) -> list[dict]:
        h = ctx.health or {}
        dash = "—"
        sleep = round(h["sleep_score"]) if h.get("sleep_score") else dash
        steps = round(h["steps"]) if h.get("steps") else dash
        stress = round(h["stress_avg"]) if h.get("stress_avg") else dash
        return [
            metric("Active days", self._active_days(ctx), "/wk", "last 7 days"),
            metric("Sleep", sleep, "score", "7-day avg"),
            metric("Steps", steps, "/day", "7-day avg"),
            metric("Stress", stress, "", "7-day avg"),
        ]

    def dashboard_variant(self, ctx: GoalContext) -> dict:
        return {"kind": self.kind, "panels": self.primary_metrics(ctx)}

    def daily_session_template(self, week: dict, day_index: int) -> dict | None:
        return session_from_microcycle(week, day_index, _MICRO)
