"""GDPR endpoint tests (US11b)."""
from __future__ import annotations

from datetime import UTC, datetime

from app.models.activity import Activity
from app.models.user import User

from tests.conftest import TEST_USER_ID


def test_export_requires_auth(client):
    assert client.get("/gdpr/export").status_code == 401


def test_export_returns_bundle(app_client, db_session, seed_user):
    db_session.add(
        Activity(
            user_id=TEST_USER_ID,
            garmin_activity_id="g-1",
            activity_type="running",
            start_time=datetime(2026, 6, 20, 7, tzinfo=UTC),
            duration_s=3600,
        )
    )
    db_session.commit()
    body = app_client.get("/gdpr/export").json()
    assert body["json"]["profile"]["id"] == TEST_USER_ID
    assert len(body["json"]["activities"]) == 1
    assert "activities" in body["csv"]


def test_delete_account_purges(app_client, db_session, seed_user):
    res = app_client.request("DELETE", "/gdpr/account")
    assert res.status_code == 200
    assert res.json()["deleted"] is True
    assert db_session.get(User, TEST_USER_ID) is None
