"""Goal engine — strategy contract + shared deterministic helpers.

Each goal kind (marathon, weight_loss, hyrox, triathlon, health) implements
``GoalDefinition`` over a ``GoalContext`` built from already-computed dashboard
facts. Definitions are PURE (no DB, no LLM) and only ever read numbers that came
from ``analytics.py`` or the database — they never let a model invent a number.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol

# On-track bands (deterministic classification of progress vs target).
AHEAD = "ahead"
ON_TRACK = "on_track"
AT_RISK = "at_risk"
OFF_TRACK = "off_track"
NO_TARGET = "no_target"


@dataclass(frozen=True)
class GoalContext:
    """Everything a goal definition needs, pre-computed and DB-free.

    ``recent_activities`` is newest-first, each ``{date, activity_type,
    distance_m, duration_s, avg_hr, tss}``. ``weight_series`` is ascending,
    each ``{day, kg}``. ``health`` is the 7-day snapshot (or None).
    """

    today: date
    goal_params: dict
    fitness: dict  # {ctl, atl, tsb}
    recovery: int
    health: dict | None
    recent_activities: list[dict]
    weight_series: list[dict]


class GoalDefinition(Protocol):
    """Contract every goal kind satisfies."""

    kind: str

    def primary_metrics(self, ctx: GoalContext) -> list[dict]:
        """The 2-4 metrics this goal cares about most (label/value/unit/hint)."""
        ...

    def progress(self, ctx: GoalContext) -> dict:
        """Where the athlete is vs the target, with a deterministic projection."""
        ...

    def dashboard_variant(self, ctx: GoalContext) -> dict:
        """Goal-specific dashboard payload: ``{kind, panels: [...]}``."""
        ...

    def daily_session_template(
        self, week: dict, day_index: int, goal_params: dict | None = None
    ) -> dict | None:
        """A prescribed session for ``day_index`` (0=Mon) of a plan week, or None
        for a rest day. ``goal_params`` lets a goal shape the microcycle around
        the athlete's declared constraints. Used by the plan builder (Phase C)."""
        ...


# --- Shared pure helpers -------------------------------------------------


def metric(label: str, value, unit: str = "", hint: str = "") -> dict:
    """Build a dashboard metric tile."""
    return {"label": label, "value": value, "unit": unit, "hint": hint}


def running_pace_s_per_km(activity: dict) -> float | None:
    """Average pace (seconds/km) for one activity, or None when uncomputable."""
    dist = activity.get("distance_m") or 0.0
    dur = activity.get("duration_s") or 0
    if dist <= 0 or dur <= 0:
        return None
    return dur / (dist / 1000.0)


def best_recent_pace(
    activities: list[dict], min_distance_m: float = 3000.0
) -> float | None:
    """Fastest average pace (s/km) over runs of at least ``min_distance_m``.

    A rough threshold-pace proxy: the quickest sustained recent effort.
    """
    paces = [
        p
        for a in activities
        if (a.get("activity_type") or "").startswith("run")
        and (a.get("distance_m") or 0.0) >= min_distance_m
        and (p := running_pace_s_per_km(a)) is not None
    ]
    return min(paces) if paces else None


def riegel_time(known_distance_m: float, known_time_s: float, target_distance_m: float) -> float:
    """Riegel race-time prediction: T2 = T1 * (D2/D1)^1.06."""
    return known_time_s * (target_distance_m / known_distance_m) ** 1.06


def linear_trend(points: list[tuple[float, float]]) -> tuple[float, float] | None:
    """Least-squares slope+intercept for ``(x, y)`` points, or None if < 2.

    Returns ``(slope, intercept)`` so ``y ≈ slope*x + intercept``.
    """
    n = len(points)
    if n < 2:
        return None
    sx = sum(x for x, _ in points)
    sy = sum(y for _, y in points)
    sxx = sum(x * x for x, _ in points)
    sxy = sum(x * y for x, y in points)
    denom = n * sxx - sx * sx
    if denom == 0:
        return None
    slope = (n * sxy - sx * sy) / denom
    intercept = (sy - slope * sx) / n
    return slope, intercept


def format_duration_hms(total_s: float) -> str:
    """Seconds → 'H:MM:SS' (or 'M:SS' under an hour)."""
    total = int(round(total_s))
    h, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def format_pace(s_per_km: float) -> str:
    """Seconds/km → 'M:SS/km'."""
    m, s = divmod(int(round(s_per_km)), 60)
    return f"{m}:{s:02d}/km"


def session_from_microcycle(
    week: dict, day_index: int, microcycle: list[tuple[str, str]]
) -> dict | None:
    """Build a day's session from a 7-entry weekday ``microcycle``.

    Each entry is ``(kind, prescription)``; ``("rest", ...)`` yields None. The
    week's ``target_tss`` is split evenly across the non-rest days so daily load
    sums back to the deterministic weekly target.
    """
    if not 0 <= day_index < len(microcycle):
        return None
    kind, prescription = microcycle[day_index]
    if kind == "rest":
        return None
    active = sum(1 for k, _ in microcycle if k != "rest") or 1
    target_tss = round((week.get("target_tss", 0.0) or 0.0) / active, 1)
    return {
        "day_index": day_index,
        "kind": kind,
        "prescription": prescription,
        "target_tss": target_tss,
    }
