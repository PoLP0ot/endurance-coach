"""Coach chat endpoint tests (US4)."""
from __future__ import annotations

from app.core.deps import get_llm_provider
from app.main import app
from app.models.user import User

from tests.conftest import TEST_USER_ID


class _StubLLM:
    def model_for(self, task):  # noqa: ANN001
        return "stub-model"

    def narrate(self, task, facts, instruction):  # noqa: ANN001
        return "Keep today easy and hydrate well."


def _premium(db) -> None:
    user = db.get(User, TEST_USER_ID)
    user.subscription_status = "premium"
    db.add(user)
    db.commit()


def test_chat_requires_auth(client):
    assert client.post("/chat", json={"message": "hi"}).status_code == 401


def test_chat_blocked_for_free_user(app_client, seed_user):
    assert app_client.post("/chat", json={"message": "hi"}).status_code == 402


def test_chat_round_trip(app_client, db_session, seed_user):
    _premium(db_session)
    app.dependency_overrides[get_llm_provider] = lambda: _StubLLM()
    try:
        res = app_client.post("/chat", json={"message": "What now?"})
        assert res.status_code == 200
        assert res.json()["role"] == "assistant"
        assert res.json()["content"] == "Keep today easy and hydrate well."

        msgs = app_client.get("/chat/messages").json()["messages"]
        assert [m["role"] for m in msgs] == ["user", "assistant"]
    finally:
        app.dependency_overrides.pop(get_llm_provider, None)


def test_chat_rejects_empty_message(app_client, db_session, seed_user):
    _premium(db_session)
    assert app_client.post("/chat", json={"message": ""}).status_code == 422


def test_chat_maps_llm_failure_to_clean_status(app_client, db_session, seed_user):
    from app.services.llm import LLMError

    _premium(db_session)

    class _RetryableLLM:
        def model_for(self, task):  # noqa: ANN001
            return "stub"

        def narrate(self, task, facts, instruction):  # noqa: ANN001
            raise LLMError("timeout", retryable=True)

    class _TerminalLLM:
        def model_for(self, task):  # noqa: ANN001
            return "stub"

        def narrate(self, task, facts, instruction):  # noqa: ANN001
            raise LLMError("quota", retryable=False)

    app.dependency_overrides[get_llm_provider] = lambda: _RetryableLLM()
    try:
        res = app_client.post("/chat", json={"message": "hi"})
        assert res.status_code == 503
        assert res.json()["error"]["reason"] == "timeout"
        assert res.json()["error"]["retryable"] is True
    finally:
        app.dependency_overrides.pop(get_llm_provider, None)

    app.dependency_overrides[get_llm_provider] = lambda: _TerminalLLM()
    try:
        res = app_client.post("/chat", json={"message": "hi"})
        assert res.status_code == 502
        assert res.json()["error"]["reason"] == "quota"
    finally:
        app.dependency_overrides.pop(get_llm_provider, None)
