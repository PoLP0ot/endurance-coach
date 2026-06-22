"""Adaptive training plan generation (US5).

The periodized STRUCTURE — phases, weekly TSS targets, recovery and taper — is
computed deterministically here. The LLM only narrates the rationale (see the
plans router). Numbers never come from the model.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.plan import PLAN_ACTIVE, PLAN_ARCHIVED, TrainingPlan

# Weekly load ≈ CTL × 7; we ramp from this baseline.
WEEKLY_TSS_PER_CTL = 7.0
PROGRESSION_RATE = 0.08  # +8% build weeks
RECOVERY_FACTOR = 0.6  # down weeks at 60% load
RECOVERY_EVERY = 4  # every 4th week is a recovery week

# Goal-specific weekly focus by phase (see business-logic.md).
GOAL_FOCUS: dict[str, dict[str, str]] = {
    "marathon": {
        "base": "Aerobic base + easy mileage",
        "build": "Threshold + marathon-pace work",
        "peak": "Race-pace long runs + sharpening",
        "taper": "Freshen up, hold intensity, drop volume",
    },
    "weight_loss": {
        "base": "Consistent easy volume + steps",
        "build": "Add tempo to raise energy burn",
        "peak": "Hardest sustainable training block",
        "taper": "Maintain habit, ease intensity",
    },
    "hyrox": {
        "base": "Aerobic base + foundational strength",
        "build": "Compromised running + strength volume",
        "peak": "Race simulations + transitions",
        "taper": "Sharpen, rest, stay explosive",
    },
    "triathlon": {
        "base": "Swim/bike/run aerobic base",
        "build": "Discipline-specific thresholds + bricks",
        "peak": "Race-specific bricks + open water",
        "taper": "Reduce volume, keep frequency",
    },
    "health": {
        "base": "Build a consistent weekly routine",
        "build": "Gently raise activity minutes",
        "peak": "Most active sustainable weeks",
        "taper": "Recover and consolidate",
    },
}
DEFAULT_FOCUS = GOAL_FOCUS["marathon"]


class _Narrator(Protocol):
    def model_for(self, task) -> str: ...  # noqa: ANN001
    def narrate(self, task, facts: dict, instruction: str) -> str: ...  # noqa: ANN001


def _allocate_phases(weeks: int) -> list[str]:
    """Lay out base → build → peak → taper across the given number of weeks."""
    taper = 2 if weeks >= 8 else 1
    peak = max(1, round(weeks * 0.15))
    base = max(1, round(weeks * 0.40))
    build = weeks - base - peak - taper
    while build < 1 and base > 1:
        base -= 1
        build += 1
    return ["base"] * base + ["build"] * build + ["peak"] * peak + ["taper"] * taper


def build_plan_structure(
    goal: str,
    weeks: int,
    start_date: date,
    base_ctl: float,
) -> dict:
    """Build a periodized plan: phases, weekly TSS targets, recovery and taper.

    Load ramps progressively through base/build, dips on recovery weeks, peaks,
    then sheds volume across the taper into race week. Deterministic.
    """
    weekly_base = max(base_ctl, 10.0) * WEEKLY_TSS_PER_CTL
    focus = GOAL_FOCUS.get(goal, DEFAULT_FOCUS)
    phases = _allocate_phases(weeks)
    taper_start = len(phases) - phases.count("taper")
    plan_weeks: list[dict] = []
    progressive = weekly_base

    for i in range(weeks):
        phase = phases[i]
        is_recovery = phase in {"base", "build"} and (i + 1) % RECOVERY_EVERY == 0

        if phase in {"base", "build"}:
            if not is_recovery:
                progressive *= 1.0 + PROGRESSION_RATE
            target = progressive * (RECOVERY_FACTOR if is_recovery else 1.0)
        elif phase == "peak":
            target = progressive * 1.05
        else:  # taper: linear shed toward race week
            target = progressive * (0.7 - 0.15 * (i - taper_start))

        plan_weeks.append(
            {
                "week": i + 1,
                "start_date": (start_date + timedelta(days=7 * i)).isoformat(),
                "phase": phase,
                "is_recovery": is_recovery,
                "target_tss": round(max(target, 0.0), 1),
                "focus": focus[phase],
            }
        )

    return {"goal": goal, "weeks": plan_weeks}


PLAN_INSTRUCTION = (
    "Narrate the rationale of this periodized plan for the athlete's goal: why "
    "the phases progress this way and how to approach each block. Do not restate "
    "the numbers — explain the strategy. A few short paragraphs."
)


def current_plan(db: Session, user_id: str) -> TrainingPlan | None:
    """Return the user's active plan, if any."""
    return db.execute(
        select(TrainingPlan)
        .where(
            TrainingPlan.user_id == user_id,
            TrainingPlan.status == PLAN_ACTIVE,
        )
        .order_by(TrainingPlan.created_at.desc())
    ).scalars().first()


def create_plan(
    db: Session,
    user_id: str,
    *,
    goal: str,
    weeks: int,
    start_date: date,
    base_ctl: float,
    llm: _Narrator,
) -> TrainingPlan:
    """Generate, narrate and persist a plan, archiving any previous active one."""
    from app.services.llm import Task

    structure = build_plan_structure(goal, weeks, start_date, base_ctl)
    narrative = llm.narrate(
        Task.PLAN,
        {"goal": goal, "weeks": weeks, "phases": [w["phase"] for w in structure["weeks"]]},
        PLAN_INSTRUCTION,
    )

    for existing in db.execute(
        select(TrainingPlan).where(
            TrainingPlan.user_id == user_id,
            TrainingPlan.status == PLAN_ACTIVE,
        )
    ).scalars():
        existing.status = PLAN_ARCHIVED
        db.add(existing)

    plan = TrainingPlan(
        user_id=user_id,
        goal=goal,
        weeks=weeks,
        start_date=start_date,
        structure=structure,
        narrative=narrative,
        model=llm.model_for(Task.PLAN),
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan
