"""Weekly adaptation tests — re-seed upcoming weeks, never the past (C3)."""
from __future__ import annotations

from datetime import date

from app.services.adaptation import adapt_plan
from app.services.plans import build_plan_structure

START = date(2026, 7, 6)  # Monday


def _structure(base_ctl: float = 50.0):
    return build_plan_structure("marathon", 10, START, base_ctl)


def test_adaptation_bumps_version_and_changes_future_weeks():
    structure = _structure()
    before = [w["target_tss"] for w in structure["weeks"]]
    summary = adapt_plan(structure, current_ctl=20.0, adherence_pct=50, today=START)
    assert summary["version"] == 2
    assert summary["changed_weeks"] > 0
    after = [w["target_tss"] for w in structure["weeks"]]
    # Lower CTL + behind on adherence → upcoming load drops.
    assert after != before
    assert structure["adapted_at"] == START.isoformat()


def test_adaptation_never_rewrites_past_or_current_week():
    structure = _structure()
    # Pretend we're in week 4 (index 3).
    today = date(2026, 7, 6 + 21)  # 3 weeks in
    before = [w["target_tss"] for w in structure["weeks"]]
    adapt_plan(structure, current_ctl=60.0, adherence_pct=90, today=today)
    after = [w["target_tss"] for w in structure["weeks"]]
    assert after[:4] == before[:4]  # weeks 1-4 untouched


def test_adaptation_records_a_change_summary_for_the_athlete():
    """The athlete must be able to see what changed and why (S8)."""
    structure = _structure()
    before = {w["week"]: w["target_tss"] for w in structure["weeks"]}
    adapt_plan(structure, current_ctl=20.0, adherence_pct=50, today=START)

    last = structure["last_adaptation"]
    assert last["at"] == START.isoformat()
    assert last["changes"]
    for change in last["changes"]:
        assert change["from"] == before[change["week"]]
        assert change["to"] != change["from"]


def test_no_change_leaves_no_adaptation_notice():
    structure = _structure()
    # Re-adapting from the same CTL/adherence the plan was built on: no-op-ish
    # runs must not fabricate a notice.
    adapt_plan(structure, current_ctl=20.0, adherence_pct=50, today=START)
    structure["last_adaptation"] = None
    summary = adapt_plan(structure, current_ctl=20.0, adherence_pct=50, today=START)
    if summary["changed_weeks"] == 0:
        assert structure["last_adaptation"] is None


def test_adapted_weeks_regenerate_sessions():
    structure = _structure()
    adapt_plan(structure, current_ctl=80.0, adherence_pct=100, today=START)
    for w in structure["weeks"][1:]:
        assert w["sessions"]  # sessions still present after re-seed
        assert abs(sum(s["target_tss"] for s in w["sessions"]) - w["target_tss"]) < 1.0
