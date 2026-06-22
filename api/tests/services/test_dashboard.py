"""Dashboard service tests — deterministic coach-first summary (US2)."""
from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from app.models.activity import Activity
from app.models.health import DailyHealth
from app.services.analytics import form_assessment
from app.services.dashboard import build_dashboard


def test_form_assessment_bands():
    assert form_assessment(20.0)["band"] == "peaked"
    assert form_assessment(8.0)["band"] == "fresh"
    assert form_assessment(0.0)["band"] == "neutral"
    assert form_assessment(-20.0)["band"] == "productive"
    assert form_assessment(-40.0)["band"] == "overreached"
    # Every band carries a human-facing headline.
    assert form_assessment(-20.0)["headline"]


def _activity(user_id: str, when: datetime, *, hr: int = 150, dur: int = 3600) -> Activity:
    return Activity(
        user_id=user_id,
        garmin_activity_id=f"g-{when.isoformat()}",
        activity_type="running",
        start_time=when,
        duration_s=dur,
        avg_hr=hr,
    )


def test_build_dashboard_empty(db_session, seed_user):
    data = build_dashboard(db_session, seed_user.id, today=date(2026, 6, 1))
    assert data["totals"]["activity_count"] == 0
    assert data["fitness"]["ctl"] == 0.0
    assert data["latest_activity"] is None
    assert data["load_series"]  # one point per day in the window


def test_build_dashboard_reflects_load(db_session, seed_user):
    today = date(2026, 6, 22)
    base = datetime(2026, 6, 1, 7, 0, tzinfo=UTC)
    for i in range(20):
        db_session.add(_activity(seed_user.id, base + timedelta(days=i)))
    db_session.add(
        DailyHealth(
            user_id=seed_user.id,
            day=today,
            resting_hr=48,
            sleep_score=82,
        )
    )
    db_session.commit()

    data = build_dashboard(db_session, seed_user.id, today=today)
    assert data["totals"]["activity_count"] == 20
    assert data["fitness"]["ctl"] > 0
    assert data["fitness"]["atl"] > 0
    assert data["latest_activity"]["activity_type"] == "running"
    assert 0 <= data["recovery"] <= 100
    assert data["form"]["band"] in {
        "peaked",
        "fresh",
        "neutral",
        "productive",
        "overreached",
    }


def test_build_dashboard_isolates_users(db_session, seed_user):
    today = date(2026, 6, 22)
    when = datetime(2026, 6, 20, 7, 0, tzinfo=UTC)
    db_session.add(_activity("99999999-9999-9999-9999-999999999999", when))
    db_session.commit()
    data = build_dashboard(db_session, seed_user.id, today=today)
    assert data["totals"]["activity_count"] == 0
