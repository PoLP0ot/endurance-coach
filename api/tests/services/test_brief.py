"""Daily brief tests — cached, deterministic facts narrated once (B4)."""
from __future__ import annotations

from datetime import UTC, date, datetime

from app.models.activity import Activity
from app.services.brief import build_daily_brief, get_or_create_brief

from tests.conftest import TEST_USER_ID


class _StubLLM:
    def __init__(self) -> None:
        self.calls = 0
        self.last_facts: dict | None = None

    def model_for(self, task) -> str:  # noqa: ANN001
        return "stub"

    def narrate(self, task, facts, instruction) -> str:  # noqa: ANN001
        self.calls += 1
        self.last_facts = facts
        return "Easy run today — your form is fresh, so make it count."


def _seed_activity(db, user_id):
    db.add(
        Activity(
            user_id=user_id,
            garmin_activity_id="g-b",
            activity_type="running",
            start_time=datetime(2026, 6, 20, 7, tzinfo=UTC),
            duration_s=3600,
            distance_m=12000.0,
            tss=60.0,
        )
    )
    db.commit()


def test_build_brief_passes_goal_and_today_to_llm(db_session, seed_user):
    _seed_activity(db_session, seed_user.id)
    seed_user.primary_goal = "health"
    db_session.commit()
    llm = _StubLLM()
    out = build_daily_brief(db_session, seed_user.id, llm, date(2026, 6, 22))
    assert out["body"]
    assert "goal" in llm.last_facts
    assert "today" in llm.last_facts


def test_brief_is_cached_per_day(db_session, seed_user):
    _seed_activity(db_session, seed_user.id)
    llm = _StubLLM()
    first = get_or_create_brief(db_session, TEST_USER_ID, llm, date(2026, 6, 22))
    second = get_or_create_brief(db_session, TEST_USER_ID, llm, date(2026, 6, 22))
    assert first.id == second.id
    assert llm.calls == 1  # generated once, then served from cache
