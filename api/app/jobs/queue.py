"""ARQ enqueue helpers. Kept thin so routes stay testable via overrides."""
from __future__ import annotations

from app.core.config import settings


async def enqueue_garmin_import(user_id: str, job_id: str, since_iso: str) -> None:
    """Enqueue the Garmin import job onto ARQ/Redis."""
    from arq import create_pool
    from arq.connections import RedisSettings

    pool = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    try:
        await pool.enqueue_job(
            "import_garmin_activities", user_id, job_id, since_iso
        )
    finally:
        await pool.close()
