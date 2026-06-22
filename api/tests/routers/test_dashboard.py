"""Dashboard endpoint tests (US2)."""
from __future__ import annotations

from datetime import UTC, datetime

from app.models.activity import Activity

from tests.conftest import TEST_USER_ID


def test_dashboard_requires_auth(client):
    assert client.get("/dashboard").status_code == 401


def test_dashboard_returns_payload(app_client, db_session, seed_user):
    db_session.add(
        Activity(
            user_id=TEST_USER_ID,
            garmin_activity_id="g-1",
            activity_type="running",
            start_time=datetime(2026, 6, 20, 7, 0, tzinfo=UTC),
            duration_s=3600,
            avg_hr=150,
            distance_m=10000.0,
        )
    )
    db_session.commit()

    res = app_client.get("/dashboard")
    assert res.status_code == 200
    body = res.json()
    assert set(body) >= {
        "fitness",
        "form",
        "recovery",
        "load_series",
        "totals",
        "latest_activity",
    }
    assert body["totals"]["activity_count"] == 1
    assert body["latest_activity"]["activity_type"] == "running"


def test_dashboard_empty_for_new_user(app_client, seed_user):
    body = app_client.get("/dashboard").json()
    assert body["totals"]["activity_count"] == 0
    assert body["latest_activity"] is None
