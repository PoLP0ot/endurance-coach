"""Garmin router tests (US1.3, 1.4, 1.9, 1.11) with overridden deps."""
from __future__ import annotations

from app.core.security import decrypt
from app.main import app
from app.models.garmin import GarminConnection
from app.models.import_job import ImportJob
from app.routers.garmin import get_garmin_provider
from app.services.garmin import GarminMFARequired

from tests.conftest import TEST_USER_ID


class _FakeProvider:
    def __init__(self, token="TOKEN_BLOB", raises=None):
        self._token = token
        self._raises = raises

    def login(self, username, password):
        if self._raises is not None:
            raise self._raises
        return self._token


def _use_provider(provider):
    app.dependency_overrides[get_garmin_provider] = lambda: provider


def test_connect_stores_encrypted_token_and_enqueues(
    app_client, db_session, enqueue_spy
):
    _use_provider(_FakeProvider(token="SECRET_TOKEN"))
    resp = app_client.post(
        "/garmin/connect", json={"username": "u@example.com", "password": "pw"}
    )
    assert resp.status_code == 202
    job_id = resp.json()["job_id"]

    conn = db_session.query(GarminConnection).filter_by(user_id=TEST_USER_ID).one()
    assert conn.encrypted_tokens != "SECRET_TOKEN"
    assert decrypt(conn.encrypted_tokens) == "SECRET_TOKEN"
    assert conn.status == "connected"

    assert db_session.get(ImportJob, job_id) is not None
    assert len(enqueue_spy.calls) == 1
    assert enqueue_spy.calls[0][0] == TEST_USER_ID
    assert enqueue_spy.calls[0][1] == job_id


def test_connect_mfa_returns_typed_error(app_client):
    _use_provider(_FakeProvider(raises=GarminMFARequired("need mfa")))
    resp = app_client.post(
        "/garmin/connect", json={"username": "u", "password": "pw"}
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["message"] == "garmin_mfa_required"


def test_status_reports_disconnected_without_connection(app_client):
    resp = app_client.get("/garmin/status")
    assert resp.status_code == 200
    assert resp.json()["status"] == "disconnected"


def test_import_status_returns_job(app_client, db_session):
    job = ImportJob(user_id=TEST_USER_ID, status="running", progress_label="Fetching…")
    db_session.add(job)
    db_session.commit()
    resp = app_client.get(f"/garmin/import-status/{job.id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "running"
    assert body["progress_label"] == "Fetching…"


def test_import_status_enforces_ownership(app_client, db_session):
    other = ImportJob(user_id="22222222-2222-2222-2222-222222222222")
    db_session.add(other)
    db_session.commit()
    resp = app_client.get(f"/garmin/import-status/{other.id}")
    assert resp.status_code == 404


def test_disconnect_keeps_data(app_client, db_session, seed_user):
    conn = GarminConnection(
        user_id=TEST_USER_ID, encrypted_tokens="x", status="connected"
    )
    db_session.add(conn)
    db_session.commit()

    resp = app_client.post("/garmin/disconnect")
    assert resp.status_code == 200
    db_session.refresh(conn)
    assert conn.status == "disconnected"
    # row is kept, not deleted
    assert db_session.query(GarminConnection).count() == 1


def test_sync_enqueues_incremental_job(app_client, db_session, seed_user, enqueue_spy):
    conn = GarminConnection(
        user_id=TEST_USER_ID, encrypted_tokens="x", status="connected"
    )
    db_session.add(conn)
    db_session.commit()

    resp = app_client.post("/garmin/sync")
    assert resp.status_code == 202
    assert len(enqueue_spy.calls) == 1
