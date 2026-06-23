"""Signals service tests — question cards grounded in real facts (US2 lens)."""
from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from app.models.activity import Activity
from app.services.llm import Task
from app.services.signals import build_signals


def _activity(user_id: str, when: datetime) -> Activity:
    return Activity(
        user_id=user_id,
        garmin_activity_id=f"g-{when.isoformat()}",
        activity_type="running",
        start_time=when,
        duration_s=3600,
        avg_hr=150,
    )


def test_build_signals_empty_when_no_activities(db_session, seed_user):
    out = build_signals(db_session, seed_user.id, today=date(2026, 6, 1))
    assert out["signals"] == []


def test_build_signals_returns_three_cards_from_facts(db_session, seed_user):
    today = date(2026, 6, 22)
    base = datetime(2026, 6, 1, 7, 0, tzinfo=UTC)
    for i in range(15):
        db_session.add(_activity(seed_user.id, base + timedelta(days=i)))
    db_session.commit()

    out = build_signals(db_session, seed_user.id, today=today)
    keys = [s["key"] for s in out["signals"]]
    assert keys == ["fitness", "form", "recovery"]
    # Deterministic interpretation, real CTL series on the fitness card.
    fitness = out["signals"][0]
    assert fitness["interpretation"]
    assert fitness["points"] and len(fitness["points"]) > 0
    assert out["signals"][2]["points"] is None  # recovery card has no series


def test_build_signals_uses_llm_when_provided(db_session, seed_user):
    today = date(2026, 6, 22)
    db_session.add(_activity(seed_user.id, datetime(2026, 6, 20, 7, 0, tzinfo=UTC)))
    db_session.commit()

    class _Stub:
        def model_for(self, task: Task) -> str:
            return "stub"

        def narrate(self, task: Task, facts: dict, instruction: str) -> str:
            return "Narrated coaching answer."

    out = build_signals(db_session, seed_user.id, today=today, llm=_Stub())
    assert all(s["interpretation"] == "Narrated coaching answer." for s in out["signals"])


def test_build_signals_falls_back_when_llm_raises(db_session, seed_user):
    today = date(2026, 6, 22)
    db_session.add(_activity(seed_user.id, datetime(2026, 6, 20, 7, 0, tzinfo=UTC)))
    db_session.commit()

    class _Boom:
        def model_for(self, task: Task) -> str:
            return "stub"

        def narrate(self, task: Task, facts: dict, instruction: str) -> str:
            raise RuntimeError("quota exceeded")

    out = build_signals(db_session, seed_user.id, today=today, llm=_Boom())
    # Best-effort narration: a model failure degrades to the deterministic text.
    assert all(s["interpretation"] for s in out["signals"])
