"""User profile endpoint tests (US11a)."""
from __future__ import annotations

from app.models.user import User

from tests.conftest import TEST_USER_ID


def test_me_requires_auth(client):
    assert client.get("/profile").status_code == 401


def test_me_returns_profile(app_client, seed_user):
    body = app_client.get("/profile").json()
    assert body["id"] == TEST_USER_ID
    assert body["units"] == "metric"
    assert body["weekly_email_opt_in"] is True
    assert body["subscription_status"] == "free"


def test_me_autoprovisions_when_missing(app_client):
    body = app_client.get("/profile").json()
    assert body["id"] == TEST_USER_ID


def test_patch_me_updates_fields(app_client, db_session, seed_user):
    res = app_client.patch(
        "/profile",
        json={
            "display_name": "Sam Runner",
            "primary_goal": "marathon",
            "units": "imperial",
            "weekly_email_opt_in": False,
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["display_name"] == "Sam Runner"
    assert body["primary_goal"] == "marathon"
    assert body["units"] == "imperial"
    assert body["weekly_email_opt_in"] is False

    user = db_session.get(User, TEST_USER_ID)
    assert user.display_name == "Sam Runner"


def test_patch_me_rejects_invalid_goal(app_client, seed_user):
    assert app_client.patch("/profile", json={"primary_goal": "nope"}).status_code == 422


def test_patch_me_rejects_invalid_units(app_client, seed_user):
    assert app_client.patch("/profile", json={"units": "furlongs"}).status_code == 422


def test_patch_me_stores_goal_params(app_client, db_session, seed_user):
    res = app_client.patch(
        "/profile",
        json={
            "primary_goal": "weight_loss",
            "goal_params": {"target_weight_kg": 74.5, "weekly_activity_target": 4},
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["goal_params"]["target_weight_kg"] == 74.5
    user = db_session.get(User, TEST_USER_ID)
    assert user.goal_params["weekly_activity_target"] == 4


def test_patch_me_rejects_goal_params_wrong_shape(app_client, seed_user):
    # weight key is invalid for a health goal → 422.
    res = app_client.patch(
        "/profile",
        json={"primary_goal": "health", "goal_params": {"target_weight_kg": 74.0}},
    )
    assert res.status_code == 422


def test_log_weight_upserts_todays_entry(app_client, db_session, seed_user):
    res = app_client.post("/profile/weight", json={"weight_kg": 88.5})
    assert res.status_code == 200
    assert res.json()["weight_kg"] == 88.5

    res = app_client.post("/profile/weight", json={"weight_kg": 88.1})
    assert res.status_code == 200
    from app.models.health import DailyHealth

    rows = db_session.query(DailyHealth).filter_by(user_id=seed_user.id).all()
    assert len(rows) == 1 and rows[0].weight_kg == 88.1


def test_log_weight_rejects_absurd_values(app_client, seed_user):
    assert app_client.post("/profile/weight", json={"weight_kg": 10}).status_code == 422
    assert app_client.post("/profile/weight", json={"weight_kg": 500}).status_code == 422
