"""ARQ worker settings and async background jobs.

Run with: arq app.jobs.worker.WorkerSettings
"""
from __future__ import annotations

from app.core.config import settings


async def import_garmin_activities(ctx: dict, user_id: str, since_iso: str) -> dict:
    """Placeholder import job. Real logic added in the Garmin import story.

    Returns a small summary so the job result is inspectable.
    """
    return {"user_id": user_id, "since": since_iso, "imported": 0}


class WorkerSettings:
    """ARQ worker configuration."""

    functions = [import_garmin_activities]
    redis_settings = settings.redis_url
