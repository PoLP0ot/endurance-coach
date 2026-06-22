"""Garmin import service tests (US1.5–1.8, 1.10) against in-memory SQLite."""
from __future__ import annotations

from datetime import UTC, date, datetime

import pytest
from app.models.activity import Activity, ActivityMetric
from app.models.garmin import GarminConnection
from app.models.health import DailyHealth
from app.models.import_job import JOB_DONE, ImportJob
from app.services.garmin import GarminActivity, GarminDailyHealth
from app.services.garmin_import import (
    downsample,
    resolve_since,
    run_import,
    store_streams,
    upsert_activities,
    upsert_daily_health,
)

from tests.conftest import TEST_USER_ID


def _activity(gid: str) -> GarminActivity:
    return GarminActivity(
        garmin_activity_id=gid,
        activity_type="running",
        name=f"Run {gid}",
        start_time="2026-06-01 10:00:00",
        duration_s=3600,
        distance_m=10000.0,
        avg_hr=150,
        max_hr=175,
        elevation_gain_m=120.0,
        avg_power_w=None,
    )


def _health(day: str) -> GarminDailyHealth:
    return GarminDailyHealth(
        day=day,
        resting_hr=48,
        hrv=65.0,
        sleep_score=82,
        steps=9000,
        body_battery=70,
        stress_avg=30,
        weight_kg=72.0,
    )


class _FakeProvider:
    def __init__(self, activities, health, streams):
        self._activities = activities
        self._health = health
        self._streams = streams

    def login(self, username, password):  # pragma: no cover - unused here
        return "token"

    def list_activities(self, token, since):
        return self._activities

    def list_daily_health(self, token, since):
        return self._health

    def get_activity_streams(self, token, garmin_activity_id):
        return self._streams


def test_downsample_keeps_short_sequences():
    assert downsample([1, 2, 3], 10) == [1, 2, 3]


def test_downsample_caps_long_sequences():
    result = downsample(list(range(10_000)), 500)
    assert len(result) == 500
    assert result[0] == 0


def test_downsample_rejects_nonpositive_cap():
    with pytest.raises(ValueError):
        downsample([1, 2, 3], 0)


def test_upsert_activities_is_idempotent(db_session, seed_user):
    activities = [_activity("100"), _activity("101")]
    assert upsert_activities(db_session, TEST_USER_ID, activities) == 2
    upsert_activities(db_session, TEST_USER_ID, activities)
    assert db_session.query(Activity).count() == 2


def test_upsert_daily_health_is_idempotent(db_session, seed_user):
    days = [_health("2026-06-01"), _health("2026-06-02")]
    assert upsert_daily_health(db_session, TEST_USER_ID, days) == 2
    upsert_daily_health(db_session, TEST_USER_ID, days)
    assert db_session.query(DailyHealth).count() == 2


def test_store_streams_downsamples_and_replaces(db_session, seed_user):
    activity = Activity(
        user_id=TEST_USER_ID,
        garmin_activity_id="100",
        activity_type="running",
        start_time=datetime(2026, 6, 1, 10, tzinfo=UTC),
    )
    db_session.add(activity)
    db_session.commit()

    streams = {"heart_rate": list(range(5000)), "altitude": list(range(5000))}
    store_streams(db_session, activity.id, streams, cap=1000)
    store_streams(db_session, activity.id, streams, cap=1000)  # re-import

    rows = db_session.query(ActivityMetric).filter_by(activity_id=activity.id).all()
    assert len(rows) == 1  # replaced, not duplicated
    assert len(rows[0].data["heart_rate"]) == 1000


def test_run_import_reports_progress_and_completes(db_session, seed_user):
    provider = _FakeProvider(
        activities=[_activity("100")],
        health=[_health("2026-06-01")],
        streams={"heart_rate": [1, 2, 3]},
    )
    job = ImportJob(user_id=TEST_USER_ID)
    db_session.add(job)
    db_session.commit()

    labels: list[str] = []
    result = run_import(
        db_session,
        provider,
        user_id=TEST_USER_ID,
        token="token",
        since=date(2026, 1, 1),
        job=job,
        on_progress=labels.append,
    )

    assert "Fetching activities…" in labels[0]
    assert any("Analyzing" in label for label in labels)
    assert any("Building" in label for label in labels)
    assert result == {"activities": 1, "health_days": 1}
    assert job.status == JOB_DONE
    assert job.activities_imported == 1


def test_resolve_since_uses_last_sync_when_present():
    conn = GarminConnection(
        user_id=TEST_USER_ID,
        encrypted_tokens="x",
        last_sync_at=datetime(2026, 5, 10, 8, tzinfo=UTC),
    )
    assert resolve_since(conn, date(2026, 6, 1)) == date(2026, 5, 10)


def test_resolve_since_falls_back_to_lookback_window():
    assert resolve_since(None, date(2026, 6, 1), default_lookback_days=30) == date(
        2026, 5, 2
    )
