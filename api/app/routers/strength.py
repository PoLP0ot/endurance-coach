"""Strength program endpoints (epic MUSCU, M3 — premium)."""
from __future__ import annotations

from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import require_premium
from app.core.ratelimit import rate_limit
from app.models.strength_plan import StrengthPlan
from app.models.user import User
from app.services.strength import (
    MAX_FREQUENCY,
    MAX_WEEKS,
    MIN_FREQUENCY,
    MIN_WEEKS,
    create_strength_plan,
    current_strength_plan,
)

router = APIRouter(prefix="/strength", tags=["strength"])


class StrengthPlanRequest(BaseModel):
    frequency: int = Field(default=3, ge=MIN_FREQUENCY, le=MAX_FREQUENCY)
    weeks: int = Field(default=12, ge=MIN_WEEKS, le=MAX_WEEKS)
    level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    equipment: list[str] = Field(min_length=1)


def _serialize(plan: StrengthPlan) -> dict:
    return {
        "id": plan.id,
        "goal_kind": plan.goal_kind,
        "weeks": plan.weeks,
        "frequency": plan.frequency,
        "level": plan.level,
        "equipment": plan.equipment,
        "start_date": plan.start_date.isoformat(),
        "status": plan.status,
        "structure": plan.structure,
        "narrative": plan.narrative,
    }


@router.post(
    "/plans",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit("plans"))],
)
async def generate_strength_plan(
    body: StrengthPlanRequest,
    user: User = Depends(require_premium),
    db: Session = Depends(get_db),
) -> dict:
    """Compose a periodized strength program from the exercise library."""
    try:
        plan = create_strength_plan(
            db,
            user.id,
            frequency=body.frequency,
            weeks=body.weeks,
            level=body.level,
            equipment=body.equipment,
            start_date=date.today(),
            goal_kind=user.primary_goal,
        )
    except ValueError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
    return _serialize(plan)


@router.get("/plans/current")
async def get_current_strength_plan(
    user: User = Depends(require_premium),
    db: Session = Depends(get_db),
) -> dict:
    """Return the user's active strength program, or null when none exists."""
    plan = current_strength_plan(db, user.id)
    return {"plan": _serialize(plan) if plan is not None else None}
