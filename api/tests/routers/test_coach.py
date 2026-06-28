"""Coach today-endpoint tests (C4)."""
from __future__ import annotations

from datetime import UTC, date, datetime

from app.models.activity import Activity
from app.models.plan import PLAN_ACTIVE, TrainingPlan
from app.services.plans import build_plan_structure

from tests.conftest import TEST_USER_ID


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
