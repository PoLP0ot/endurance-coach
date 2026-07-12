"""Weight-loss goal — weight trajectory to target from the trend line."""
from __future__ import annotations

from datetime import date, timedelta

from app.services.goals.base import (
    AHEAD,
    AT_RISK,
    NO_TARGET,
    OFF_TRACK,
    ON_TRACK,
    GoalContext,
    linear_trend,
    metric,
    session_from_microcycle,
)

# Healthy weekly loss window (kg/week).
_MIN_RATE = 0.25
_MAX_RATE = 1.0

_E40 = ("easy", "Easy aerobic 40 min")
_E45 = ("easy", "Easy aerobic 45 min")
_TEMPO = ("tempo", "Tempo 25 min to lift the burn")
_LONG = ("long", "Long easy session 60 min")
_STRENGTH = ("strength", "Strength session — follow your strength program")
_REST = ("rest", "")

# Default cadence mixes cardio and strength; muscle preserved in a deficit.
_DEFAULT_MICRO = [_E40, _STRENGTH, _E45, _TEMPO, _STRENGTH, _LONG, _REST]

# Availability-shaped microcycles (weekly_activity_target → 7-day layout).
_MICRO_BY_DAYS: dict[int, list[tuple[str, str]]] = {
    3: [_E45, _REST, _STRENGTH, _REST, _REST, _LONG, _REST],
    4: [_E40, _STRENGTH, _REST, _STRENGTH, _REST, _LONG, _REST],
    5: [_E40, _STRENGTH, _TEMPO, _REST, _STRENGTH, _LONG, _REST],
}


class WeightLossGoal:
    kind = "weight_loss"

    def _trend(self, ctx: GoalContext):
        """(slope_kg_per_day, intercept) over the weight series, or None."""
        series = ctx.weight_series
        if len(series) < 2:
            return None
        x0 = date.fromisoformat(series[0]["day"]).toordinal()
        pts = [
            (float(date.fromisoformat(p["day"]).toordinal() - x0), float(p["kg"]))
            for p in series
        ]
        return linear_trend(pts)

    def progress(self, ctx: GoalContext) -> dict:
        target = ctx.goal_params.get("target_weight_kg")
        deadline_iso = ctx.goal_params.get("target_date")
        deadline = date.fromisoformat(deadline_iso) if deadline_iso else None
        series = ctx.weight_series
        current = series[-1]["kg"] if series else None
        baseline = series[0]["kg"] if series else None
        trend = self._trend(ctx)
        rate_per_week = round(trend[0] * 7, 2) if trend else None  # negative = losing

        # Deterministic pace demanded by the deadline, if one is set.
        required_rate = None
        if target is not None and current is not None and deadline is not None:
            days_left = (deadline - ctx.today).days
            if days_left > 0 and current > target:
                required_rate = round((current - target) / (days_left / 7.0), 2)

        band = NO_TARGET
        eta = None
        headline = "Step on the scale a few times and I'll track your trajectory."
        if target is not None and current is not None:
            to_lose = current - target
            losing_per_week = -rate_per_week if rate_per_week is not None else None
            if to_lose <= 0:
                band, headline = AHEAD, "You've reached your target weight — nice work."
            elif losing_per_week is None or losing_per_week <= 0:
                band = OFF_TRACK
                headline = "Weight isn't trending down yet — let's tighten consistency."
            else:
                days = to_lose / (losing_per_week / 7)
                eta_date = ctx.today + timedelta(days=round(days))
                eta = eta_date.isoformat()
                if losing_per_week > _MAX_RATE:
                    band, headline = AT_RISK, "Dropping fast — ease off to protect muscle."
                elif deadline is not None:
                    if eta_date <= deadline:
                        band = ON_TRACK
                        headline = (
                            f"On track — losing {losing_per_week:.2f} kg/week, "
                            f"on pace for your {deadline_iso} deadline."
                        )
                    else:
                        band = AT_RISK
                        headline = (
                            f"At this rate you'll hit {target:g} kg around {eta} — "
                            f"past your deadline ({deadline_iso})."
                        )
                        if required_rate is not None:
                            headline += f" You need {required_rate:.2f} kg/week."
                elif losing_per_week < _MIN_RATE:
                    band, headline = AT_RISK, "Losing slowly — a touch more volume would help."
                else:
                    band = ON_TRACK
                    headline = f"On track — losing {losing_per_week:.2f} kg/week."

        return {
            "kind": self.kind,
            "label": "Weight",
            "baseline": baseline,
            "current": current,
            "target": target,
            "target_date": deadline_iso,
            "rate_kg_per_week": rate_per_week,
            "required_rate_kg_per_week": required_rate,
            "on_track_band": band,
            "headline": headline,
            "eta": eta,
        }

    def primary_metrics(self, ctx: GoalContext) -> list[dict]:
        series = ctx.weight_series
        current = series[-1]["kg"] if series else None
        steps = (ctx.health or {}).get("steps")
        prog = self.progress(ctx)
        rate = prog["rate_kg_per_week"]
        return [
            metric("Weight", current if current is not None else "—", "kg", "latest"),
            metric("Trend", rate if rate is not None else "—", "kg/wk", "trajectory"),
            metric("Steps", round(steps) if steps else "—", "/day", "7-day avg"),
        ]

    def dashboard_variant(self, ctx: GoalContext) -> dict:
        return {"kind": self.kind, "panels": self.primary_metrics(ctx)}

    def daily_session_template(
        self, week: dict, day_index: int, goal_params: dict | None = None
    ) -> dict | None:
        target = (goal_params or {}).get("weekly_activity_target")
        micro = _MICRO_BY_DAYS.get(target, _DEFAULT_MICRO)
        return session_from_microcycle(week, day_index, micro)
