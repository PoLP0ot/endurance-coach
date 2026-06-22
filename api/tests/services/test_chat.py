"""Coach chat service tests (US4) — LLM stubbed."""
from __future__ import annotations

from datetime import UTC, date, datetime

from app.models.activity import Activity
from app.models.chat import ROLE_ASSISTANT, ROLE_USER
from app.services.chat import answer, history


class _StubLLM:
    def __init__(self) -> None:
        self.last_facts = None

    def model_for(self, task):  # noqa: ANN001
        return "stub-model"

    def narrate(self, task, facts, instruction):  # noqa: ANN001
        self.last_facts = facts
        return "Based on your form, take it easy today."


def test_answer_persists_pair_and_returns_reply(db_session, seed_user):
    db_session.add(
        Activity(
            user_id=seed_user.id,
            garmin_activity_id="g-1",
            activity_type="running",
            start_time=datetime(2026, 6, 20, 7, tzinfo=UTC),
            duration_s=3600,
            avg_hr=150,
        )
    )
    db_session.commit()

    llm = _StubLLM()
    reply = answer(
        db_session, seed_user.id, "How should I train today?", llm, today=date(2026, 6, 22)
    )

    assert reply.role == ROLE_ASSISTANT
    assert reply.content == "Based on your form, take it easy today."
    # Coach is grounded in deterministic facts.
    assert "fitness" in llm.last_facts

    msgs = history(db_session, seed_user.id)
    assert [m.role for m in msgs] == [ROLE_USER, ROLE_ASSISTANT]
    assert msgs[0].content == "How should I train today?"


def test_history_is_per_user(db_session, seed_user):
    llm = _StubLLM()
    answer(db_session, seed_user.id, "hi", llm, today=date(2026, 6, 22))
    answer(db_session, "99999999-9999-9999-9999-999999999999", "hello", llm,
           today=date(2026, 6, 22))
    assert len(history(db_session, seed_user.id)) == 2
