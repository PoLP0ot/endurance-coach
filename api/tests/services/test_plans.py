"""Training plan generator tests — deterministic periodization (US5)."""
from __future__ import annotations

from datetime import date

from app.services.plans import build_plan_structure


def _weeks(goal: str, weeks: int, start: date, base_ctl: float) -> list[dict]:
    return build_plan_structure(goal, weeks, start, base_ctl)["weeks"]


def test_plan_has_requested_number_of_weeks():
    plan = build_plan_structure("marathon", 12, date(2026, 7, 1), 40)
    assert len(plan["weeks"]) == 12
    assert plan["goal"] == "marathon"


def test_phases_progress_base_to_taper():
    weeks = _weeks("marathon", 16, date(2026, 7, 1), 40)
    phases = [w["phase"] for w in weeks]
    assert phases[0] == "base"
    assert phases[-1] == "taper"
    # Phases never go backwards.
    order = {"base": 0, "build": 1, "peak": 2, "taper": 3}
    assert all(order[a] <= order[b] for a, b in zip(phases, phases[1:], strict=False))


def test_recovery_weeks_reduce_load():
    weeks = _weeks("marathon", 12, date(2026, 7, 1), 50)
    recovery = [w for w in weeks if w["is_recovery"]]
    assert recovery  # at least one down week
    for w in recovery:
        assert w["target_tss"] > 0


def test_taper_sheds_load_into_race_week():
    weeks = _weeks("marathon", 12, date(2026, 7, 1), 50)
    taper = [w for w in weeks if w["phase"] == "taper"]
    assert taper[-1]["target_tss"] < taper[0]["target_tss"]


def test_weeks_carry_dates_and_goal_focus():
    weeks = _weeks("hyrox", 8, date(2026, 7, 6), 30)
    assert weeks[0]["start_date"] == "2026-07-06"
    assert weeks[1]["start_date"] == "2026-07-13"
    assert all(w["focus"] for w in weeks)
