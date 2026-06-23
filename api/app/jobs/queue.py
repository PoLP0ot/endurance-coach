"""ARQ enqueue helpers. Kept thin so routes stay testable via overrides."""
from __future__ import annotations

import asyncio
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


async def enqueue_garmin_import(user_id: str, job_id: str, since_iso: str) -> None:
    """Enqueue the Garmin import job onto ARQ/Redis.

    If Redis is unreachable (e.g. local dev without a worker), fall back to
    running the import inline so the flow still completes.
    """
    from arq import create_pool
    from arq.connections import RedisSettings

    try:
        pool = await asyncio.wait_for(
            create_pool(RedisSettings.from_dsn(settings.redis_url)), timeout=3
        )
    except Exception:  # noqa: BLE001 — any Redis/connection failure → inline fallback
        logger.warning(
            "redis_unavailable_inline_import",
            extra={"job_id": job_id, "user_id": user_id},
        )
        from app.jobs.worker import import_garmin_activities

        await import_garmin_activities({}, user_id, job_id, since_iso)
        return

    try:
        await pool.enqueue_job(
            "import_garmin_activities", user_id, job_id, since_iso
        )
        logger.info("garmin_import_enqueued", extra={"job_id": job_id})
    finally:
        await pool.close()
