"""Training plan endpoint tests (US5)."""
from __future__ import annotations

from app.core.deps import get_llm_provider
from app.main import app
from app.models.user import User

from tests.conftest import TEST_USER_ID


class _StubLLM:
    def model_for(self, task):  # noqa: ANN001
        return "stub-plan-model"

    def narrate(self, task, facts, instruction):  # noqa: ANN001
        return "Build your base, then sharpen into race week."


def _premium(db, goal: str = "marathon") -> None:
    user = db.get(User, TEST_USER_ID)
    user.subscription_status = "premium"
    user.primary_goal = goal
    db.add(user)
    db.commit()


def test_plans_require_premium(app_client, seed_user):
    assert app_client.post("/plans", json={}).status_code == 402


def test_generate_and_fetch_current_plan(app_client, db_session, seed_user):
    _premium(db_session)
    app.dependency_overrides[get_llm_provider] = lambda: _StubLLM()
    try:
        res = app_client.post("/plans", json={"weeks": 12})
        assert res.status_code == 201
        body = res.json()
        assert body["goal"] == "marathon"
        assert len(body["structure"]["weeks"]) == 12
        assert body["narrative"].startswith("Build your base")

        current = app_client.get("/plans/current").json()["plan"]
        assert current["id"] == body["id"]
        assert current["status"] == "active"
    finally:
        app.dependency_overrides.pop(get_llm_provider, None)


def test_regenerating_archives_previous(app_client, db_session, seed_user):
    _premium(db_session)
    app.dependency_overrides[get_llm_provider] = lambda: _StubLLM()
    try:
        first = app_client.post("/plans", json={"weeks": 8}).json()
        second = app_client.post("/plans", json={"weeks": 16}).json()
        current = app_client.get("/plans/current").json()["plan"]
        assert current["id"] == second["id"]
        assert current["id"] != first["id"]
    finally:
        app.dependency_overrides.pop(get_llm_provider, None)


def test_current_plan_null_when_none(app_client, db_session, seed_user):
    _premium(db_session)
    assert app_client.get("/plans/current").json()["plan"] is None
