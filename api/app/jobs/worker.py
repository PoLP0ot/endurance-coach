"""ARQ worker settings and async background jobs.

Run with: arq app.jobs.worker.WorkerSettings
"""
from __future__ import annotations

from datetime import date

from arq import cron
from arq.worker import Retry
from sqlalchemy.orm.attributes import flag_modified

from app.core.config import settings
from app.core.db import SessionLocal
from app.core.security import decrypt
from app.models.garmin import GarminConnection
from app.models.import_job import JOB_QUEUED, ImportJob
from app.models.plan import PLAN_ACTIVE, TrainingPlan
from app.models.user import User
from app.services.adaptation import adapt_plan
from app.services.brief import get_or_create_brief
from app.services.coach_facts import build_coach_facts
from app.services.email import EmailProvider, build_weekly_email
from app.services.garmin import GarminConnectProvider
from app.services.garmin_import import is_auth_failure, resolve_since, run_import
from app.services.llm import LLMProvider
from app.services.subscriptions import is_premium
from app.services.today import todays_session

# Transient import failures are retried with linear backoff; auth failures
# aren't (retrying a dead token only worsens Garmin rate limiting).
MAX_IMPORT_TRIES = 3


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
        try:
            result = run_import(
                db,
                GarminConnectProvider(),
                user_id=user_id,
                token=token,
                since=date.fromisoformat(since_iso),
                job=job,
            )
        except Exception as exc:  # noqa: BLE001 — classify for retry
            job_try = ctx.get("job_try") or 1
            if not is_auth_failure(exc) and job_try < MAX_IMPORT_TRIES:
                job.status = JOB_QUEUED
                job.progress_label = "Import hit a snag — retrying shortly…"
                db.add(job)
                db.commit()
                raise Retry(defer=60 * job_try) from exc
            raise
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


async def sync_all_garmin(ctx: dict) -> dict:
    """Scheduled fan-out: queue an incremental import for every connected user."""
    db = SessionLocal()
    try:
        conns = (
            db.query(GarminConnection).filter_by(status="connected").all()
        )
        queued = 0
        for conn in conns:
            job = ImportJob(user_id=conn.user_id, status=JOB_QUEUED)
            db.add(job)
            db.commit()
            db.refresh(job)
            since = resolve_since(conn, date.today())
            await ctx["redis"].enqueue_job(
                "import_garmin_activities", conn.user_id, job.id, since.isoformat()
            )
            queued += 1
        return {"queued": queued}
    finally:
        db.close()


async def adapt_all_plans(ctx: dict) -> dict:
    """Scheduled: re-seed every active plan's upcoming weeks from real fitness."""
    db = SessionLocal()
    try:
        plans = db.query(TrainingPlan).filter_by(status=PLAN_ACTIVE).all()
        adapted = 0
        for plan in plans:
            facts = build_coach_facts(db, plan.user_id, date.today())
            today_info = todays_session(db, plan.user_id, date.today())
            adherence_pct = (today_info.get("adherence") or {}).get("adherence_pct")
            summary = adapt_plan(
                plan.structure, facts["fitness"]["ctl"], adherence_pct, date.today()
            )
            flag_modified(plan, "structure")
            db.add(plan)
            db.commit()
            if summary["changed_weeks"]:
                adapted += 1
        return {"plans": len(plans), "adapted": adapted}
    finally:
        db.close()


async def generate_daily_brief(ctx: dict, user_id: str) -> dict:
    """Generate (and cache) one premium user's daily brief."""
    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        if user is None or not is_premium(user):
            return {"user_id": user_id, "generated": False, "reason": "skipped"}
        brief = get_or_create_brief(db, user_id, LLMProvider(), date.today())
        return {"user_id": user_id, "generated": True, "brief_id": brief.id}
    finally:
        db.close()


async def generate_daily_briefs(ctx: dict) -> dict:
    """Fan out daily-brief generation to all premium users (scheduled)."""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        queued = 0
        for user in users:
            if is_premium(user):
                await ctx["redis"].enqueue_job("generate_daily_brief", user.id)
                queued += 1
        return {"queued": queued}
    finally:
        db.close()


class WorkerSettings:
    """ARQ worker configuration. Run with: arq app.jobs.worker.WorkerSettings"""

    functions = [
        import_garmin_activities,
        send_weekly_email,
        send_weekly_emails,
        sync_all_garmin,
        adapt_all_plans,
        generate_daily_brief,
        generate_daily_briefs,
    ]
    cron_jobs = [
        cron(sync_all_garmin, hour=3, minute=0),  # daily Garmin re-sync 03:00
        cron(generate_daily_briefs, hour=5, minute=30),  # daily brief 05:30
        cron(send_weekly_emails, weekday="mon", hour=7, minute=0),  # Mon 07:00
        cron(adapt_all_plans, weekday="sun", hour=18, minute=0),  # weekly adaptation
    ]
    redis_settings = settings.redis_url
