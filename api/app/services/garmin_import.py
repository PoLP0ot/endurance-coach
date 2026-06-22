"""Garmin import orchestration — idempotent upserts and stream downsampling.

Pure-ish functions operating on a SQLAlchemy Session so they are unit-testable
against an in-memory database. The unofficial Garmin library stays behind
GarminProvider; nothing here imports it directly.
"""
from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from datetime import date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import Activity, ActivityMetric
from app.models.garmin import GarminConnection
from app.models.health import DailyHealth
from app.models.import_job import (
    JOB_DONE,
    JOB_ERROR,
    JOB_RUNNING,
    ImportJob,
)
from app.services.garmin import (
    GarminActivity,
    GarminDailyHealth,
    GarminProvider,
)

# Default look-back when a connection has never been synced.
DEFAULT_LOOKBACK_DAYS = 365
# Cap on stored stream samples per array (keeps JSON rows bounded).
DEFAULT_STREAM_CAP = 1000

ProgressFn = Callable[[str], None]


def downsample(samples: Sequence, cap: int) -> list:
    """Evenly reduce a sequence to at most `cap` items, preserving order.

    Returns the input unchanged (as a list) when it already fits. Raises
    ValueError for a non-positive cap.
    """
    if cap <= 0:
        raise ValueError("cap must be positive")
    n = len(samples)
    if n <= cap:
        return list(samples)
    step = n / cap
    return [samples[int(i * step)] for i in range(cap)]


def _parse_dt(value: str) -> datetime:
    """Parse a Garmin ISO timestamp ('YYYY-MM-DD HH:MM:SS' or with 'T'/'Z')."""
    text = value.strip().replace("Z", "+00:00")
    if "T" not in text and " " in text:
        text = text.replace(" ", "T", 1)
    return datetime.fromisoformat(text)


def upsert_activities(
    db: Session, user_id: str, activities: Iterable[GarminActivity]
) -> int:
    """Insert or update activities, keyed on (user_id, garmin_activity_id).

    Running the same import twice produces no duplicates. Returns the number of
    activities processed.
    """
    count = 0
    for a in activities:
        existing = db.execute(
            select(Activity).where(
                Activity.user_id == user_id,
                Activity.garmin_activity_id == a.garmin_activity_id,
            )
        ).scalar_one_or_none()
        fields = {
            "activity_type": a.activity_type,
            "name": a.name,
            "start_time": _parse_dt(a.start_time),
            "duration_s": a.duration_s,
            "distance_m": a.distance_m,
            "avg_hr": a.avg_hr,
            "max_hr": a.max_hr,
            "elevation_gain_m": a.elevation_gain_m,
            "avg_power_w": a.avg_power_w,
        }
        if existing is None:
            db.add(
                Activity(
                    user_id=user_id,
                    garmin_activity_id=a.garmin_activity_id,
                    **fields,
                )
            )
        else:
            for key, val in fields.items():
                setattr(existing, key, val)
        count += 1
    db.commit()
    return count


def upsert_daily_health(
    db: Session, user_id: str, days: Iterable[GarminDailyHealth]
) -> int:
    """Insert or update daily health rows, idempotent on (user_id, day)."""
    count = 0
    for h in days:
        day = date.fromisoformat(h.day)
        existing = db.execute(
            select(DailyHealth).where(
                DailyHealth.user_id == user_id,
                DailyHealth.day == day,
            )
        ).scalar_one_or_none()
        fields = {
            "resting_hr": h.resting_hr,
            "hrv": h.hrv,
            "sleep_score": h.sleep_score,
            "steps": h.steps,
            "body_battery": h.body_battery,
            "stress_avg": h.stress_avg,
            "weight_kg": h.weight_kg,
        }
        if existing is None:
            db.add(DailyHealth(user_id=user_id, day=day, **fields))
        else:
            for key, val in fields.items():
                setattr(existing, key, val)
        count += 1
    db.commit()
    return count


def store_streams(
    db: Session,
    activity_id: str,
    streams: dict,
    cap: int = DEFAULT_STREAM_CAP,
) -> ActivityMetric:
    """Downsample each stream array and store one 'stream' metric row.

    Replaces any existing stream row for the activity so re-import is idempotent.
    """
    for row in db.execute(
        select(ActivityMetric).where(
            ActivityMetric.activity_id == activity_id,
            ActivityMetric.kind == "stream",
        )
    ).scalars():
        db.delete(row)

    capped = {
        key: downsample(value, cap) if isinstance(value, list) else value
        for key, value in streams.items()
    }
    metric = ActivityMetric(activity_id=activity_id, kind="stream", data=capped)
    db.add(metric)
    db.commit()
    return metric


def resolve_since(
    connection: GarminConnection | None,
    today: date,
    default_lookback_days: int = DEFAULT_LOOKBACK_DAYS,
) -> date:
    """Pick the incremental import start date.

    Syncs only activities after the last successful sync; falls back to a
    look-back window for a first-time import.
    """
    if connection is not None and connection.last_sync_at is not None:
        return connection.last_sync_at.date()
    return today - timedelta(days=default_lookback_days)


def _activity_id(db: Session, user_id: str, garmin_activity_id: str) -> str | None:
    return db.execute(
        select(Activity.id).where(
            Activity.user_id == user_id,
            Activity.garmin_activity_id == garmin_activity_id,
        )
    ).scalar_one_or_none()


def run_import(
    db: Session,
    provider: GarminProvider,
    *,
    user_id: str,
    token: str,
    since: date,
    job: ImportJob | None = None,
    on_progress: ProgressFn | None = None,
    stream_cap: int = DEFAULT_STREAM_CAP,
    fetch_streams: bool = True,
) -> dict:
    """Run a full import: activities → health → streams, with progress labels.

    Updates `job` (status + progress_label + counts) as it advances so the
    polling endpoint can report progress. Marks the job errored and re-raises on
    failure.
    """

    def progress(label: str) -> None:
        if job is not None:
            job.status = JOB_RUNNING
            job.progress_label = label
            db.add(job)
            db.commit()
        if on_progress is not None:
            on_progress(label)

    try:
        progress("Fetching activities…")
        activities = provider.list_activities(token, since)
        n_act = upsert_activities(db, user_id, activities)

        progress("Fetching health data…")
        health = provider.list_daily_health(token, since)
        n_health = upsert_daily_health(db, user_id, health)

        progress("Analyzing metrics…")
        if fetch_streams:
            for a in activities:
                aid = _activity_id(db, user_id, a.garmin_activity_id)
                if aid is None:
                    continue
                streams = provider.get_activity_streams(token, a.garmin_activity_id)
                store_streams(db, aid, streams, cap=stream_cap)

        progress("Building your dashboard…")
        if job is not None:
            job.status = JOB_DONE
            job.activities_imported = n_act
            job.health_days_imported = n_health
            db.add(job)
            db.commit()
        return {"activities": n_act, "health_days": n_health}
    except Exception as exc:  # noqa: BLE001 — record then re-raise
        if job is not None:
            job.status = JOB_ERROR
            job.error = str(exc)
            db.add(job)
            db.commit()
        raise
