"""Activity history + detail endpoints (US9)."""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import CurrentUser, get_current_user
from app.models.activity import Activity, ActivityMetric
from app.models.user import User
from app.services.activity_history import (
    DEFAULT_LIMIT,
    MAX_LIMIT,
    list_activities,
)
from app.services.subscriptions import FREE_HISTORY_DAYS, is_premium

router = APIRouter(prefix="/activities", tags=["activities"])


@router.get("")
async def get_activities(
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    cursor: str | None = Query(None),
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Paginated activity history, newest first. Free tier is windowed."""
    db_user = db.get(User, user.id)
    max_age = None if is_premium(db_user) else FREE_HISTORY_DAYS
    page = list_activities(
        db,
        user.id,
        limit=limit,
        cursor=cursor,
        today=date.today(),
        max_age_days=max_age,
    )
    return {**page, "windowed": max_age is not None}


@router.get("/{activity_id}")
async def get_activity(
    activity_id: str,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Single activity with its stored stream samples. Ownership enforced."""
    activity = db.get(Activity, activity_id)
    if activity is None or activity.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "activity_not_found")
    streams = db.execute(
        select(ActivityMetric).where(
            ActivityMetric.activity_id == activity_id,
            ActivityMetric.kind == "stream",
        )
    ).scalars().first()
    return {
        "id": activity.id,
        "activity_type": activity.activity_type,
        "name": activity.name,
        "start_time": activity.start_time.isoformat(),
        "distance_m": activity.distance_m,
        "duration_s": activity.duration_s,
        "avg_hr": activity.avg_hr,
        "max_hr": activity.max_hr,
        "elevation_gain_m": activity.elevation_gain_m,
        "avg_power_w": activity.avg_power_w,
        "tss": activity.tss,
        "streams": streams.data if streams is not None else None,
    }
