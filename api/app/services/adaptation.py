"""Weekly plan adaptation — re-seed upcoming load from the athlete's real fitness.

When the worker runs this each week (or on demand), upcoming weeks are recomputed
from the *actual* current CTL and recent adherence, so the plan stays realistic
when sessions are missed or fitness diverges from the original projection. Past
and current weeks are never rewritten. Deterministic; the LLM only narrates why.
"""
from __future__ import annotations

from datetime import date

from app.services.goals import get_goal_definition
from app.services.plans import (
    PROGRESSION_RATE,
    RECOVERY_FACTOR,
    WEEKLY_TSS_PER_CTL,
)

# Below this weekly adherence we ramp more conservatively (athlete is behind).
_BEHIND_THRESHOLD = 70


def _current_week_index(weeks: list[dict], today: date) -> int:
    """Index of the latest week that has started, or 0 before the plan begins."""
    idx = 0
    for i, w in enumerate(weeks):
        if date.fromisoformat(w["start_date"]) <= today:
            idx = i
    return idx


def adapt_plan(
    structure: dict, current_ctl: float, adherence_pct: int | None, today: date
) -> dict:
    """Recompute upcoming weeks in place from current CTL + adherence.

    Returns a summary ``{changed_weeks, version}``. Only weeks after the current
    one change; taper weeks are preserved. Sessions are regenerated for any week
    whose target load moved.
    """
    weeks = structure["weeks"]
    definition = get_goal_definition(structure.get("goal"))
    cur_idx = _current_week_index(weeks, today)

    # Ramp from where the athlete actually is, conservatively if behind.
    progressive = max(current_ctl, 10.0) * WEEKLY_TSS_PER_CTL
    ramp = (
        PROGRESSION_RATE
        if adherence_pct is None or adherence_pct >= _BEHIND_THRESHOLD
        else PROGRESSION_RATE / 2
    )

    changed = 0
    changes: list[dict] = []
    for i, week in enumerate(weeks):
        if i <= cur_idx:
            continue
        phase = week["phase"]
        if phase in {"base", "build"}:
            if not week["is_recovery"]:
                progressive *= 1.0 + ramp
            target = progressive * (RECOVERY_FACTOR if week["is_recovery"] else 1.0)
        elif phase == "peak":
            target = progressive * 1.05
        else:  # taper: keep the original shed
            continue
        new_target = round(max(target, 0.0), 1)
        if abs(new_target - week["target_tss"]) > 0.1:
            changes.append(
                {"week": week["week"], "from": week["target_tss"], "to": new_target}
            )
            week["target_tss"] = new_target
            week["sessions"] = [
                s
                for d in range(7)
                if (s := definition.daily_session_template(week, d)) is not None
            ]
            changed += 1

    structure["version"] = structure.get("version", 1) + 1
    structure["adapted_at"] = today.isoformat()
    if changed:
        # What the athlete sees on the plan page: which upcoming weeks moved.
        structure["last_adaptation"] = {
            "at": today.isoformat(),
            "adherence_pct": adherence_pct,
            "changes": changes,
        }
    return {"changed_weeks": changed, "version": structure["version"]}
