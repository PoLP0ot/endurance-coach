"""Strength set-log endpoints (epic MUSCU, M4 — premium)."""
from __future__ import annotations

from app.models.user import User

from tests.conftest import TEST_USER_ID
from tests.services.test_strength import seed_library

BODY = {
    "frequency": 2,
    "weeks": 8,
    "level": "intermediate",
    "equipment": ["dumbbell"],
}


def _premium(db) -> None:
    user = db.get(User, TEST_USER_ID)
    user.subscription_status = "premium"
    db.add(user)
    db.commit()


def _make_plan(app_client, db_session) -> dict:
    _premium(db_session)
    seed_library(db_session)
    return app_client.post("/strength/plans", json=BODY).json()


def test_log_and_fetch_session_sets(app_client, db_session, seed_user):
    plan = _make_plan(app_client, db_session)
    exercise_id = plan["structure"]["weeks"][0]["sessions"][0]["items"][0]["exercise_id"]

    res = app_client.post(
        "/strength/logs",
        json={
            "week": 1,
            "day": 0,
            "exercise_id": exercise_id,
            "set_index": 1,
            "weight_kg": 40,
            "reps": 10,
            "rpe": 8,
        },
    )
    assert res.status_code == 201

    logs = app_client.get("/strength/logs", params={"week": 1, "day": 0}).json()
    assert len(logs["sets"]) == 1
    assert logs["sets"][0]["weight_kg"] == 40
    assert logs["summary"]["sets_logged"] == 1


def test_log_unknown_session_is_404(app_client, db_session, seed_user):
    plan = _make_plan(app_client, db_session)
    exercise_id = plan["structure"]["weeks"][0]["sessions"][0]["items"][0]["exercise_id"]
    res = app_client.post(
        "/strength/logs",
        json={"week": 1, "day": 6, "exercise_id": exercise_id, "set_index": 1, "reps": 10},
    )
    assert res.status_code == 404


def test_complete_session(app_client, db_session, seed_user):
    plan = _make_plan(app_client, db_session)
    exercise_id = plan["structure"]["weeks"][0]["sessions"][0]["items"][0]["exercise_id"]
    app_client.post(
        "/strength/logs",
        json={"week": 1, "day": 0, "exercise_id": exercise_id, "set_index": 1,
              "weight_kg": 40, "reps": 10},
    )

    res = app_client.post("/strength/sessions/complete", json={"week": 1, "day": 0})
    assert res.status_code == 200
    assert res.json()["completed"] is True
    assert res.json()["volume_kg"] == 400


def test_logs_require_premium_and_a_plan(app_client, db_session, seed_user):
    assert app_client.get("/strength/logs", params={"week": 1, "day": 0}).status_code == 402
    _premium(db_session)
    assert app_client.get("/strength/logs", params={"week": 1, "day": 0}).status_code == 409
