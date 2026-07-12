"""Marathon goal — race-time projection from recent runs (Riegel)."""
from __future__ import annotations

from app.services.goals.base import (
    AHEAD,
    AT_RISK,
    NO_TARGET,
    OFF_TRACK,
    ON_TRACK,
    GoalContext,
    best_recent_pace,
    format_duration_hms,
    format_pace,
    metric,
    riegel_time,
    running_pace_s_per_km,
    session_from_microcycle,
)

MARATHON_M = 42195.0

# Weekday microcycle per phase (Mon..Sun): (kind, prescription).
_MICRO = {
    "base": [
        ("rest", ""),
        ("easy", "Easy run 8 km"),
        ("easy", "Easy run 8 km + strides"),
        ("tempo", "Tempo 3×8 min"),
        ("rest", ""),
        ("long", "Long run 18 km easy"),
        ("recovery", "Recovery jog 5 km"),
    ],
    "build": [
        ("rest", ""),
        ("easy", "Easy run 10 km"),
        ("interval", "Intervals 6×1 km @ threshold"),
        ("easy", "Easy run 8 km"),
        ("threshold", "Threshold 4×2 km"),
        ("long", "Long run 26 km w/ marathon-pace blocks"),
        ("recovery", "Recovery jog 6 km"),
    ],
    "peak": [
        ("rest", ""),
        ("easy", "Easy run 10 km"),
        ("interval", "Race-pace 5×2 km"),
        ("easy", "Easy run 8 km"),
        ("threshold", "Marathon-pace 16 km"),
        ("long", "Long run 30 km"),
        ("recovery", "Recovery jog 6 km"),
    ],
    "taper": [
        ("rest", ""),
        ("easy", "Easy run 8 km"),
        ("interval", "Sharpener 4×1 km @ race pace"),
        ("rest", ""),
        ("easy", "Easy run 6 km + strides"),
        ("long", "Last long run 16 km"),
        ("rest", ""),
    ],
}


class MarathonGoal:
    kind = "marathon"

    def _reference_run(self, ctx: GoalContext) -> dict | None:
        """Longest recent run with a valid pace — the marathon-relevant effort."""
        runs = [
            a
            for a in ctx.recent_activities
            if (a.get("activity_type") or "").startswith("run")
            and running_pace_s_per_km(a) is not None
        ]
        return max(runs, key=lambda a: a.get("distance_m") or 0.0) if runs else None

    def progress(self, ctx: GoalContext) -> dict:
        target_s = ctx.goal_params.get("target_time_s")
        distance_m = ctx.goal_params.get("race_distance_m", MARATHON_M)
        ref = self._reference_run(ctx)
        projection_s = (
            riegel_time(ref["distance_m"], ref["duration_s"], distance_m)
            if ref
            else None
        )
        band = NO_TARGET
        if target_s and projection_s is not None:
            if projection_s <= target_s * 0.98:
                band = AHEAD
            elif projection_s <= target_s * 1.02:
                band = ON_TRACK
            elif projection_s <= target_s * 1.06:
                band = AT_RISK
            else:
                band = OFF_TRACK
        headline = (
            f"Projected finish {format_duration_hms(projection_s)}"
            if projection_s is not None
            else "Log a few runs and I'll project your race time."
        )
        return {
            "kind": self.kind,
            "label": "Race time",
            "current_fitness_ctl": ctx.fitness.get("ctl"),
            "target": format_duration_hms(target_s) if target_s else None,
            "projection": format_duration_hms(projection_s) if projection_s is not None else None,
            "on_track_band": band,
            "headline": headline,
            "eta": ctx.goal_params.get("race_date"),
        }

    def primary_metrics(self, ctx: GoalContext) -> list[dict]:
        pace = best_recent_pace(ctx.recent_activities)
        return [
            metric("Fitness", round(ctx.fitness.get("ctl", 0.0)), "CTL", "42-day load"),
            metric("Form", round(ctx.fitness.get("tsb", 0.0)), "TSB", "balance"),
            metric("Threshold pace", format_pace(pace) if pace else "—", "", "best recent run"),
        ]

    def dashboard_variant(self, ctx: GoalContext) -> dict:
        return {"kind": self.kind, "panels": self.primary_metrics(ctx)}

    def daily_session_template(
        self, week: dict, day_index: int, goal_params: dict | None = None
    ) -> dict | None:
        micro = _MICRO.get(week.get("phase", "base"), _MICRO["base"])
        return session_from_microcycle(week, day_index, micro)
