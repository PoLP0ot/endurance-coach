"""AnalyticsEngine — deterministic, pure-Python training metrics.

CORE PRINCIPLE (see .claude/memory/architecture.md): the AI NEVER computes
numbers. Everything here is pure and fully unit-testable. The LLM only narrates
the facts these functions produce.
"""
from __future__ import annotations

from dataclasses import dataclass


def training_stress_score(
    duration_s: float, normalized_power: float, ftp: float
) -> float:
    """Power-based TSS.

    TSS = (duration_s * NP * IF) / (FTP * 3600) * 100, where IF = NP / FTP.

    Raises ValueError if ftp <= 0.
    """
    if ftp <= 0:
        raise ValueError("FTP must be positive")
    if duration_s < 0:
        raise ValueError("duration must be non-negative")
    intensity_factor = normalized_power / ftp
    return (duration_s * normalized_power * intensity_factor) / (ftp * 3600) * 100.0


def hr_training_stress_score(
    duration_s: float, avg_hr: float, threshold_hr: float
) -> float:
    """Heart-rate based TSS (hrTSS) fallback when power is unavailable.

    Uses HR intensity ratio as a proxy for IF.
    """
    if threshold_hr <= 0:
        raise ValueError("threshold_hr must be positive")
    if duration_s < 0:
        raise ValueError("duration must be non-negative")
    intensity_factor = avg_hr / threshold_hr
    return (duration_s / 3600.0) * (intensity_factor**2) * 100.0


def _ema_step(prev: float, today: float, time_constant_days: int) -> float:
    """One step of an exponentially-weighted moving average."""
    alpha = 1.0 - pow(2.718281828459045, -1.0 / time_constant_days)
    return prev + alpha * (today - prev)


@dataclass(frozen=True)
class FitnessState:
    """Fitness snapshot for one day."""

    ctl: float  # Chronic Training Load (fitness), 42-day EMA
    atl: float  # Acute Training Load (fatigue), 7-day EMA
    tsb: float  # Training Stress Balance (form) = CTL - ATL


def fitness_series(
    daily_tss: list[float],
    ctl_tc: int = 42,
    atl_tc: int = 7,
    initial_ctl: float = 0.0,
    initial_atl: float = 0.0,
) -> list[FitnessState]:
    """Compute CTL/ATL/TSB for each day from a daily TSS series.

    daily_tss[i] is the total TSS on day i (0 for rest days).
    """
    states: list[FitnessState] = []
    ctl, atl = initial_ctl, initial_atl
    for tss in daily_tss:
        ctl = _ema_step(ctl, tss, ctl_tc)
        atl = _ema_step(atl, tss, atl_tc)
        states.append(FitnessState(ctl=ctl, atl=atl, tsb=ctl - atl))
    return states


def recovery_score(tsb: float, resting_hr_delta: float = 0.0, sleep_score: float = 75.0) -> int:
    """Composite 0-100 recovery score.

    Higher TSB (more form), lower resting-HR elevation, and better sleep all
    raise recovery. Clamped to [0, 100]. Deterministic and explainable.
    """
    base = 50.0 + tsb * 1.5
    base -= resting_hr_delta * 3.0
    base += (sleep_score - 75.0) * 0.4
    return int(max(0.0, min(100.0, round(base))))


def activity_tss(
    duration_s: int | None, avg_hr: int | None, threshold_hr: float = 170.0
) -> float:
    """Best-effort TSS for a single activity from HR, 0.0 when data is missing.

    Power-based TSS is preferred upstream; this HR fallback keeps the daily load
    series populated for runners without a power meter. Deterministic.
    """
    if duration_s is None or avg_hr is None or duration_s <= 0:
        return 0.0
    return hr_training_stress_score(float(duration_s), float(avg_hr), threshold_hr)


# Training Stress Balance bands → coach-facing form assessment.
def form_assessment(tsb: float) -> dict[str, str]:
    """Map TSB (form) to a band and a human-facing coaching headline.

    Bands follow the standard CTL/ATL/TSB model: positive form means fresh,
    the -10..-30 window is the productive training zone, and deeply negative
    form signals overreaching. Returns ``{"band", "headline", "detail"}``.
    """
    if tsb >= 15.0:
        band, headline = "peaked", "You're peaked and race-ready."
        detail = "Form is high — a great window to perform. Avoid adding big load."
    elif tsb >= 5.0:
        band, headline = "fresh", "You're fresh."
        detail = "Fatigue has cleared. Good day for quality or a hard session."
    elif tsb >= -10.0:
        band, headline = "neutral", "You're balanced."
        detail = "Load and recovery are roughly even. Keep building steadily."
    elif tsb >= -30.0:
        band, headline = "productive", "You're in the productive training zone."
        detail = "Fatigue is elevated but this is where fitness is built. Recover well."
    else:
        band, headline = "overreached", "You're carrying heavy fatigue."
        detail = "Form is deeply negative. Prioritise recovery before more hard work."
    return {"band": band, "headline": headline, "detail": detail}


def intensity_distribution(
    hr_samples: list[int], zone_bounds: list[int]
) -> dict[str, float]:
    """Fraction of time spent in each HR zone (polarized-training analysis).

    zone_bounds are the upper bounds of zones 1..n-1; anything above the last
    bound is the top zone. Returns fractions that sum to ~1.0.
    """
    if not hr_samples:
        return {}
    n_zones = len(zone_bounds) + 1
    counts = [0] * n_zones
    for hr in hr_samples:
        placed = False
        for i, bound in enumerate(zone_bounds):
            if hr <= bound:
                counts[i] += 1
                placed = True
                break
        if not placed:
            counts[-1] += 1
    total = len(hr_samples)
    return {f"z{i + 1}": counts[i] / total for i in range(n_zones)}
