"""Coach today-endpoint tests (C4)."""
from __future__ import annotations

from datetime import UTC, date, datetime

from app.core.deps import get_llm_provider
from app.main import app
from app.models.activity import Activity
from app.models.plan import PLAN_ACTIVE, TrainingPlan
from app.models.user import User
from app.services.plans import build_plan_structure

from tests.conftest import TEST_USER_ID


class _StubLLM:
    def model_for(self, task):  # noqa: ANN001
        return "stub"

    def narrate(self, task, facts, instruction):  # noqa: ANN001
        return "Today: easy run. You're tracking well."


def test_today_no_plan_status(app_client, seed_user):
    body = app_client.get("/coach/today").json()
    assert body["status"] == "no_plan"
    assert "goal_band" in body


def test_today_returns_session_and_adherence(app_client, db_session, seed_user):
    # Active plan whose week 1 contains today.
    start = date.today()
    start = start.fromordinal(start.toordinal() - start.weekday())  # this Monday
    structure = build_plan_structure("marathon", 8, start, 50.0)
    db_session.add(
        TrainingPlan(
            user_id=TEST_USER_ID,
            goal="marathon",
            weeks=8,
            start_date=start,
            structure=structure,
            narrative="",
            model="test",
            status=PLAN_ACTIVE,
        )
    )
    db_session.add(
        Activity(
            user_id=TEST_USER_ID,
            garmin_activity_id="g-today",
            activity_type="running",
            start_time=datetime.now(UTC),
            duration_s=3600,
            distance_m=12000.0,
            tss=70.0,
        )
    )
    db_session.commit()

    body = app_client.get("/coach/today").json()
    assert body["status"] == "ok"
    assert body["week"] == 1
    assert "adherence" in body
    assert "is_rest" in body


def test_brief_requires_premium(app_client, seed_user):
    assert app_client.get("/coach/brief").status_code == 402


def test_brief_returns_narrated_body_for_premium(app_client, db_session, seed_user):
    user = db_session.get(User, TEST_USER_ID)
    user.subscription_status = "premium"
    db_session.add(
        Activity(
            user_id=TEST_USER_ID,
            garmin_activity_id="g-brief",
            activity_type="running",
            start_time=datetime.now(UTC),
            duration_s=3600,
            distance_m=10000.0,
            tss=55.0,
        )
    )
    db_session.commit()

    app.dependency_overrides[get_llm_provider] = lambda: _StubLLM()
    try:
        res = app_client.get("/coach/brief")
        assert res.status_code == 200
        assert res.json()["body"] == "Today: easy run. You're tracking well."
    finally:
        app.dependency_overrides.pop(get_llm_provider, None)
