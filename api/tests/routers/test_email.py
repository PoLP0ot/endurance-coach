"""Weekly email preview endpoint tests (US6)."""
from __future__ import annotations

from app.core.deps import get_llm_provider
from app.main import app
from app.models.user import User

from tests.conftest import TEST_USER_ID


class _StubLLM:
    def model_for(self, task):  # noqa: ANN001
        return "stub"

    def narrate(self, task, facts, instruction):  # noqa: ANN001
        return "You stacked a strong week of aerobic work."


def test_preview_requires_premium(app_client, seed_user):
    assert app_client.get("/email/weekly/preview").status_code == 402


def test_preview_renders_email(app_client, db_session, seed_user):
    user = db_session.get(User, TEST_USER_ID)
    user.subscription_status = "premium"
    db_session.add(user)
    db_session.commit()
    app.dependency_overrides[get_llm_provider] = lambda: _StubLLM()
    try:
        body = app_client.get("/email/weekly/preview").json()
    finally:
        app.dependency_overrides.pop(get_llm_provider, None)
    assert body["subject"]
    assert "strong week of aerobic work" in body["html"]
