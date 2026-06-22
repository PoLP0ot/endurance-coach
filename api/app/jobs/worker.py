"""ARQ worker settings and async background jobs.

Run with: arq app.jobs.worker.WorkerSettings
"""
from __future__ import annotations

from datetime import date

from app.core.config import settings
from app.core.db import SessionLocal
from app.core.security import decrypt
from app.models.garmin import GarminConnection
from app.models.import_job import ImportJob
from app.services.garmin import GarminConnectProvider
from app.services.garmin_import import run_import


async def import_garmin_activities(
    ctx: dict, user_id: str, job_id: str, since_iso: str
) -> dict:
    """Background Garmin import: decrypt token, fetch + upsert, update job.

    Runs the deterministic import pipeline in a worker. The heavy Garmin
    library stays behind GarminConnectProvider.
    """
    db = SessionLocal()
    try:
        connection = (
            db.query(GarminConnection).filter_by(user_id=user_id).one_or_none()
        )
        job = db.get(ImportJob, job_id)
        if connection is None or job is None:
            return {"user_id": user_id, "imported": 0, "error": "missing_state"}

        token = decrypt(connection.encrypted_tokens)
        result = run_import(
            db,
            GarminConnectProvider(),
            user_id=user_id,
            token=token,
            since=date.fromisoformat(since_iso),
            job=job,
        )
        connection.last_sync_at = job.updated_at
        db.add(connection)
        db.commit()
        return {"user_id": user_id, **result}
    finally:
        db.close()


class WorkerSettings:
    """ARQ worker configuration."""

    functions = [import_garmin_activities]
    redis_settings = settings.redis_url
