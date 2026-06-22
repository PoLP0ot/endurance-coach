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
from app.models.user import User
from app.services.email import EmailProvider, build_weekly_email
from app.services.garmin import GarminConnectProvider
from app.services.garmin_import import run_import
from app.services.llm import LLMProvider
from app.services.subscriptions import is_premium


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


async def send_weekly_email(ctx: dict, user_id: str) -> dict:
    """Build and send one athlete's weekly coaching email."""
    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        if user is None or not is_premium(user) or not user.weekly_email_opt_in:
            return {"user_id": user_id, "sent": False, "reason": "skipped"}
        if not user.email:
            return {"user_id": user_id, "sent": False, "reason": "no_email"}
        email = build_weekly_email(db, user, LLMProvider(), today=date.today())
        message_id = EmailProvider().send(user.email, email["subject"], email["html"])
        return {"user_id": user_id, "sent": True, "message_id": message_id}
    finally:
        db.close()


async def send_weekly_emails(ctx: dict) -> dict:
    """Fan out weekly emails to all opted-in premium users (scheduled)."""
    db = SessionLocal()
    try:
        users = db.query(User).filter(User.weekly_email_opt_in.is_(True)).all()
        queued = 0
        for user in users:
            if is_premium(user) and user.email:
                await ctx["redis"].enqueue_job("send_weekly_email", user.id)
                queued += 1
        return {"queued": queued}
    finally:
        db.close()


class WorkerSettings:
    """ARQ worker configuration."""

    functions = [import_garmin_activities, send_weekly_email, send_weekly_emails]
    redis_settings = settings.redis_url
