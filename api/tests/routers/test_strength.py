"""Strength program endpoints (epic MUSCU, M3 — premium)."""
from __future__ import annotations

from app.models.user import User

from tests.conftest import TEST_USER_ID
from tests.services.test_strength import seed_library

BODY = {
    "frequency": 3,
    "weeks": 8,
    "level": "intermediate",
    "equipment": ["dumbbell"],
}


def _premium(db) -> None:
    user = db.get(User, TEST_USER_ID)
    user.subscription_status = "premium"
    db.add(user)
    db.commit()


def test_strength_plans_require_premium(app_client, seed_user):
    assert app_client.post("/strength/plans", json=BODY).status_code == 402


def test_create_and_fetch_current_program(app_client, db_session, seed_user):
    _premium(db_session)
    seed_library(db_session)

    res = app_client.post("/strength/plans", json=BODY)
    assert res.status_code == 201
    body = res.json()
    assert body["frequency"] == 3
    assert len(body["structure"]["weeks"]) == 8

    current = app_client.get("/strength/plans/current").json()["plan"]
    assert current["id"] == body["id"]
    assert current["status"] == "active"


def test_regenerating_archives_previous(app_client, db_session, seed_user):
    _premium(db_session)
    seed_library(db_session)

    first = app_client.post("/strength/plans", json=BODY).json()
    second = app_client.post("/strength/plans", json={**BODY, "weeks": 12}).json()
    current = app_client.get("/strength/plans/current").json()["plan"]
    assert current["id"] == second["id"]
    assert first["id"] != second["id"]


def test_validation_rejects_out_of_range_params(app_client, db_session, seed_user):
    _premium(db_session)
    seed_library(db_session)
    assert app_client.post("/strength/plans", json={**BODY, "weeks": 30}).status_code == 422
    assert app_client.post("/strength/plans", json={**BODY, "frequency": 5}).status_code == 422
    assert app_client.post("/strength/plans", json={**BODY, "level": "pro"}).status_code == 422
    assert app_client.post("/strength/plans", json={**BODY, "equipment": []}).status_code == 422


def test_current_without_plan_is_null(app_client, db_session, seed_user):
    _premium(db_session)
    assert app_client.get("/strength/plans/current").json()["plan"] is None
