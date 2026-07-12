"""Exercise library endpoints (epic MUSCU, M1)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import CurrentUser, get_current_user
from app.models.exercise import Exercise
from app.services.exercises import (
    DEFAULT_LIMIT,
    MAX_LIMIT,
    list_exercises,
    serialize_detail,
)

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("")
async def get_exercises(
    body_part: str | None = Query(None),
    target: str | None = Query(None),
    equipment: str | None = Query(None),
    q: str | None = Query(None, max_length=100),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    cursor: str | None = Query(None),
    _user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Paginated exercise library with exact filters and name search."""
    return list_exercises(
        db,
        body_part=body_part,
        target=target,
        equipment=equipment,
        q=q,
        limit=limit,
        cursor=cursor,
    )


@router.get("/{exercise_id}")
async def get_exercise(
    exercise_id: str,
    _user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Full exercise sheet: muscles, instruction steps, media."""
    exercise = db.get(Exercise, exercise_id)
    if exercise is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "exercise_not_found")
    return serialize_detail(exercise)
