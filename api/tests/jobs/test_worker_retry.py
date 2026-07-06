"""Import job retry semantics (S10): transient failures retry, auth doesn't."""
from __future__ import annotations

import pytest
from app.core.security import encrypt
from app.jobs import worker
from app.models.garmin import GarminConnection
from app.models.import_job import ImportJob
from arq.worker import Retry

from tests.conftest import TEST_USER_ID


def _seed(db_session):
    conn = GarminConnection(
        user_id=TEST_USER_ID, encrypted_tokens=encrypt("t"), status="connected"
    )
    job = ImportJob(user_id=TEST_USER_ID)
    db_session.add_all([conn, job])
    db_session.commit()
    return job


@pytest.fixture()
def worker_db(monkeypatch, db_session):
    monkeypatch.setattr(worker, "SessionLocal", lambda: db_session)
    monkeypatch.setattr(db_session, "close", lambda: None)
    return db_session


@pytest.mark.asyncio
async def test_transient_failure_requeues_and_retries(
    monkeypatch, worker_db, seed_user
):
    job = _seed(worker_db)

    def boom(*_a, **_k):
        raise RuntimeError("connection reset by peer")

    monkeypatch.setattr(worker, "run_import", boom)
    with pytest.raises(Retry):
        await worker.import_garmin_activities(
            {"job_try": 1}, TEST_USER_ID, job.id, "2026-06-01"
        )
    assert job.status == "queued"
    assert "retry" in (job.progress_label or "").lower()


@pytest.mark.asyncio
async def test_auth_failure_does_not_retry(monkeypatch, worker_db, seed_user):
    job = _seed(worker_db)

    def boom(*_a, **_k):
        raise RuntimeError("401 Client Error: Unauthorized")

    monkeypatch.setattr(worker, "run_import", boom)
    with pytest.raises(RuntimeError):
        await worker.import_garmin_activities(
            {"job_try": 1}, TEST_USER_ID, job.id, "2026-06-01"
        )


@pytest.mark.asyncio
async def test_last_attempt_does_not_retry(monkeypatch, worker_db, seed_user):
    job = _seed(worker_db)

    def boom(*_a, **_k):
        raise RuntimeError("connection reset by peer")

    monkeypatch.setattr(worker, "run_import", boom)
    with pytest.raises(RuntimeError):
        await worker.import_garmin_activities(
            {"job_try": worker.MAX_IMPORT_TRIES}, TEST_USER_ID, job.id, "2026-06-01"
        )
