"""Deterministic strength-program composer (epic MUSCU, M3).

Builds a periodized multi-week program — adaptation → hypertrophy → strength,
with a deload every 4th week — from the exercise library. Exercise choice,
sets, reps, RPE and rest are all computed here; the LLM only narrates.

Body-weight work is always considered available on top of the athlete's
declared equipment. Loads (kg) start unset: they come from logged sets (M5).
"""
from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.exercise import Exercise
from app.models.strength_plan import (
    STRENGTH_PLAN_ACTIVE,
    STRENGTH_PLAN_ARCHIVED,
    StrengthPlan,
)

LEVELS = ("beginner", "intermediate", "advanced")
MIN_WEEKS, MAX_WEEKS = 8, 16
MIN_FREQUENCY, MAX_FREQUENCY = 2, 4

DELOAD_EVERY = 4
ADAPTATION_WEEKS = 2

# Per-block prescription; level shifts set counts by ±1 (min 2).
BLOCKS = {
    "adaptation": {"sets": 3, "reps": 12, "rpe": 6, "rest_sec": 60},
    "hypertrophy": {"sets": 4, "reps": 10, "rpe": 8, "rest_sec": 90},
    "strength": {"sets": 4, "reps": 5, "rpe": 8, "rest_sec": 150},
}
BLOCK_FOCUS = {
    "adaptation": "Groove the movements, build work capacity",
    "hypertrophy": "Build muscle — volume at controlled effort",
    "strength": "Get strong — heavier, fewer reps, full rest",
}
DELOAD_RPE = 6
LEVEL_SET_DELTA = {"beginner": -1, "intermediate": 0, "advanced": 1}

# A slot is (label, target-muscle priority list). Ordered big-to-small.
_SLOT_SQUAT = ("squat", ["quads"])
_SLOT_PUSH = ("push", ["pectorals"])
_SLOT_PULL = ("pull", ["lats", "upper back"])
_SLOT_HINGE = ("hinge", ["hamstrings", "glutes"])
_SLOT_SHOULDERS = ("shoulders", ["delts"])
_SLOT_CORE = ("core", ["abs"])
_SLOT_BICEPS = ("biceps", ["biceps"])
_SLOT_TRICEPS = ("triceps", ["triceps"])
_SLOT_GLUTES = ("glutes", ["glutes"])
_SLOT_CALVES = ("calves", ["calves"])

FOCUS_SLOTS = {
    "full": [_SLOT_SQUAT, _SLOT_PUSH, _SLOT_PULL, _SLOT_HINGE, _SLOT_SHOULDERS, _SLOT_CORE],
    "upper": [_SLOT_PUSH, _SLOT_PULL, _SLOT_SHOULDERS, _SLOT_BICEPS, _SLOT_TRICEPS, _SLOT_CORE],
    "lower": [_SLOT_SQUAT, _SLOT_HINGE, _SLOT_GLUTES, _SLOT_CALVES, _SLOT_CORE],
}

# Weekly session layout per frequency: (day 0 = Monday, focus).
FREQUENCY_LAYOUT = {
    2: [(0, "full"), (3, "full")],
    3: [(0, "full"), (2, "upper"), (4, "lower")],
    4: [(0, "upper"), (1, "lower"), (3, "upper"), (4, "lower")],
}
SESSION_TITLES = {"full": "Full body", "upper": "Upper body", "lower": "Lower body"}


def _allocate_blocks(weeks: int) -> list[str]:
    """adaptation → hypertrophy → strength across the program."""
    strength = max(2, weeks // 4)
    hypertrophy = weeks - ADAPTATION_WEEKS - strength
    return (
        ["adaptation"] * ADAPTATION_WEEKS
        + ["hypertrophy"] * hypertrophy
        + ["strength"] * strength
    )


def _library_by_target(db: Session, equipment: list[str]) -> dict[str, list[Exercise]]:
    """Usable exercises grouped by target muscle, in stable id order."""
    allowed = set(equipment) | {"body weight"}
    rows = db.execute(
        select(Exercise)
        .where(Exercise.equipment.in_(sorted(allowed)))
        .order_by(Exercise.id.asc())
    ).scalars()
    by_target: dict[str, list[Exercise]] = {}
    for exercise in rows:
        by_target.setdefault(exercise.target, []).append(exercise)
    return by_target


def _pick(
    by_target: dict[str, list[Exercise]], targets: list[str], variant: int
) -> Exercise | None:
    """Nth candidate for a slot; the variant differentiates A/B sessions."""
    for target in targets:
        candidates = by_target.get(target)
        if candidates:
            return candidates[variant % len(candidates)]
    return None


def _prescription(block: str, level: str, is_deload: bool) -> dict:
    base = BLOCKS[block]
    sets = max(2, base["sets"] + LEVEL_SET_DELTA[level])
    if is_deload:
        return {
            "sets": max(2, sets - 1),
            "reps": base["reps"],
            "rpe": DELOAD_RPE,
            "rest_sec": base["rest_sec"],
        }
    return {"sets": sets, "reps": base["reps"], "rpe": base["rpe"], "rest_sec": base["rest_sec"]}


def build_strength_structure(
    db: Session,
    *,
    frequency: int,
    weeks: int,
    level: str,
    equipment: list[str],
    start_date: date,
) -> dict:
    """Compose the full periodized program. Deterministic for given inputs.

    Returns ``{"frequency", "level", "equipment", "blocks", "weeks": [...]}``
    where each week carries its block, deload flag and fully prescribed
    sessions (day, focus, items with exercise, sets×reps, RPE, rest).
    """
    if not MIN_FREQUENCY <= frequency <= MAX_FREQUENCY:
        raise ValueError("invalid_frequency")
    if not MIN_WEEKS <= weeks <= MAX_WEEKS:
        raise ValueError("invalid_weeks")
    if level not in LEVELS:
        raise ValueError("invalid_level")
    if not equipment:
        raise ValueError("invalid_equipment")

    by_target = _library_by_target(db, equipment)
    blocks = _allocate_blocks(weeks)
    layout = FREQUENCY_LAYOUT[frequency]
    focus_counts: dict[str, int] = {}
    for _, focus in layout:
        focus_counts[focus] = focus_counts.get(focus, 0) + 1

    plan_weeks: list[dict] = []
    for i in range(weeks):
        block = blocks[i]
        is_deload = (i + 1) % DELOAD_EVERY == 0
        prescription = _prescription(block, level, is_deload)

        # A/B variation: sessions sharing a focus rotate through candidates.
        focus_seen: dict[str, int] = {}
        sessions = []
        for day, focus in layout:
            variant = focus_seen.get(focus, 0)
            focus_seen[focus] = variant + 1
            items = []
            for label, targets in FOCUS_SLOTS[focus]:
                exercise = _pick(by_target, targets, variant)
                if exercise is None:
                    continue
                items.append(
                    {
                        "slot": label,
                        "exercise_id": exercise.id,
                        "name": exercise.name,
                        "equipment": exercise.equipment,
                        "gif_url": exercise.gif_url,
                        "target_weight_kg": None,
                        **prescription,
                    }
                )
            title = SESSION_TITLES[focus]
            if focus_counts[focus] > 1:
                title = f"{title} {'AB'[variant % 2]}"
            sessions.append({"day": day, "focus": focus, "title": title, "items": items})

        plan_weeks.append(
            {
                "week": i + 1,
                "start_date": (start_date + timedelta(days=7 * i)).isoformat(),
                "block": block,
                "is_deload": is_deload,
                "focus": BLOCK_FOCUS[block],
                "sessions": sessions,
            }
        )

    return {
        "frequency": frequency,
        "level": level,
        "equipment": sorted(set(equipment)),
        "blocks": [
            {"block": name, "weeks": blocks.count(name)}
            for name in ("adaptation", "hypertrophy", "strength")
        ],
        "weeks": plan_weeks,
    }


def current_strength_plan(db: Session, user_id: str) -> StrengthPlan | None:
    """Return the user's active strength program, if any."""
    return db.execute(
        select(StrengthPlan)
        .where(
            StrengthPlan.user_id == user_id,
            StrengthPlan.status == STRENGTH_PLAN_ACTIVE,
        )
        .order_by(StrengthPlan.created_at.desc())
    ).scalars().first()


def create_strength_plan(
    db: Session,
    user_id: str,
    *,
    frequency: int,
    weeks: int,
    level: str,
    equipment: list[str],
    start_date: date,
    goal_kind: str | None = None,
) -> StrengthPlan:
    """Compose and persist a program, archiving any previous active one."""
    structure = build_strength_structure(
        db,
        frequency=frequency,
        weeks=weeks,
        level=level,
        equipment=equipment,
        start_date=start_date,
    )

    for existing in db.execute(
        select(StrengthPlan).where(
            StrengthPlan.user_id == user_id,
            StrengthPlan.status == STRENGTH_PLAN_ACTIVE,
        )
    ).scalars():
        existing.status = STRENGTH_PLAN_ARCHIVED
        db.add(existing)

    plan = StrengthPlan(
        user_id=user_id,
        goal_kind=goal_kind,
        weeks=weeks,
        frequency=frequency,
        level=level,
        equipment=sorted(set(equipment)),
        start_date=start_date,
        structure=structure,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan
