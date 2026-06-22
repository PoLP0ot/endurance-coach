"""Activity history + detail endpoint tests (US9)."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.core.deps import get_llm_provider
from app.main import app
from app.models.activity import Activity, ActivityMetric
from app.models.user import User

from tests.conftest import TEST_USER_ID


class _StubLLM:
    def model_for(self, task):  # noqa: ANN001
        return "stub-model"

    def narrate(self, task, facts, instruction):  # noqa: ANN001
        return "Solid aerobic effort — recover and repeat."


def _seed(db, n: int) -> None:
    base = datetime.now(UTC) - timedelta(days=1)
    for i in range(n):
        db.add(
            Activity(
                user_id=TEST_USER_ID,
                garmin_activity_id=f"g-{i}",
                activity_type="running",
                start_time=base - timedelta(hours=i),
            )
        )
    db.commit()


def test_activities_requires_auth(client):
    assert client.get("/activities").status_code == 401


def test_activities_paginates(app_client, db_session, seed_user):
    _seed(db_session, 5)
    body = app_client.get("/activities?limit=2").json()
    assert len(body["items"]) == 2
    assert body["next_cursor"]
    nxt = app_client.get(f"/activities?limit=2&cursor={body['next_cursor']}").json()
    assert {a["id"] for a in body["items"]}.isdisjoint(
        {a["id"] for a in nxt["items"]}
    )


def test_free_tier_is_windowed_flag(app_client, db_session, seed_user):
    _seed(db_session, 1)
    body = app_client.get("/activities").json()
    assert body["windowed"] is True  # seed_user defaults to free


def test_activity_detail_with_streams(app_client, db_session, seed_user):
    a = Activity(
        user_id=TEST_USER_ID,
        garmin_activity_id="g-detail",
        activity_type="running",
        start_time=datetime(2026, 6, 20, 7, tzinfo=UTC),
        duration_s=3600,
    )
    db_session.add(a)
    db_session.commit()
    db_session.add(
        ActivityMetric(activity_id=a.id, kind="stream", data={"hr": [120, 130]})
    )
    db_session.commit()

    body = app_client.get(f"/activities/{a.id}").json()
    assert body["id"] == a.id
    assert body["streams"] == {"hr": [120, 130]}


def test_activity_detail_404_for_other_user(app_client, db_session, seed_user):
    other = Activity(
        user_id="99999999-9999-9999-9999-999999999999",
        garmin_activity_id="g-x",
        activity_type="running",
        start_time=datetime(2026, 6, 20, 7, tzinfo=UTC),
    )
    db_session.add(other)
    db_session.commit()
    assert app_client.get(f"/activities/{other.id}").status_code == 404


def _premium(db) -> None:
    user = db.get(User, TEST_USER_ID)
    user.subscription_status = "premium"
    db.add(user)
    db.commit()


def _make_activity(db) -> Activity:
    a = Activity(
        user_id=TEST_USER_ID,
        garmin_activity_id="g-an",
        activity_type="running",
        start_time=datetime(2026, 6, 20, 7, tzinfo=UTC),
        duration_s=1800,
        distance_m=5000.0,
        avg_hr=150,
    )
    db.add(a)
    db.commit()
    return a


def test_analysis_blocked_for_free_user(app_client, db_session, seed_user):
    a = _make_activity(db_session)
    assert app_client.get(f"/activities/{a.id}/analysis").status_code == 402


def test_analysis_for_premium_user(app_client, db_session, seed_user):
    _premium(db_session)
    a = _make_activity(db_session)
    app.dependency_overrides[get_llm_provider] = lambda: _StubLLM()
    try:
        body = app_client.get(f"/activities/{a.id}/analysis").json()
    finally:
        app.dependency_overrides.pop(get_llm_provider, None)
    assert body["narrative"] == "Solid aerobic effort — recover and repeat."
    assert body["facts"]["tss"] > 0
