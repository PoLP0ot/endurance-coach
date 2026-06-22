"""GDPR export + delete service tests (US11b)."""
from __future__ import annotations

from datetime import UTC, datetime

from app.models.activity import Activity
from app.models.audit import GDPR_DELETE, GDPR_EXPORT, GdprAuditLog
from app.models.chat import ChatMessage
from app.models.health import DailyHealth
from app.models.user import User
from app.services.gdpr import build_export, delete_user_data

from tests.conftest import TEST_USER_ID


def _seed(db) -> None:
    db.add(
        Activity(
            user_id=TEST_USER_ID,
            garmin_activity_id="g-1",
            activity_type="running",
            start_time=datetime(2026, 6, 20, 7, tzinfo=UTC),
            duration_s=3600,
            distance_m=10000.0,
        )
    )
    db.add(DailyHealth(user_id=TEST_USER_ID, day=datetime(2026, 6, 20).date(), steps=8000))
    db.add(ChatMessage(user_id=TEST_USER_ID, role="user", content="hi"))
    db.commit()


def test_export_bundles_all_user_data(db_session, seed_user):
    _seed(db_session)
    bundle = build_export(db_session, TEST_USER_ID)

    assert bundle["json"]["profile"]["id"] == TEST_USER_ID
    assert len(bundle["json"]["activities"]) == 1
    assert len(bundle["json"]["daily_health"]) == 1
    assert len(bundle["json"]["chat_messages"]) == 1
    # CSV export of activities has a header + one row.
    assert "garmin_activity_id" in bundle["csv"]["activities"]
    assert bundle["csv"]["activities"].strip().count("\n") == 1

    audit = db_session.query(GdprAuditLog).filter_by(action=GDPR_EXPORT).all()
    assert len(audit) == 1


def test_delete_purges_everything_and_audits(db_session, seed_user):
    _seed(db_session)
    delete_user_data(db_session, TEST_USER_ID)

    assert db_session.get(User, TEST_USER_ID) is None
    assert db_session.query(Activity).filter_by(user_id=TEST_USER_ID).count() == 0
    assert db_session.query(DailyHealth).filter_by(user_id=TEST_USER_ID).count() == 0
    assert db_session.query(ChatMessage).filter_by(user_id=TEST_USER_ID).count() == 0
    # Audit record survives the deletion.
    audit = db_session.query(GdprAuditLog).filter_by(action=GDPR_DELETE).all()
    assert len(audit) == 1
    assert audit[0].user_id == TEST_USER_ID
