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
from app.services.strength_logs import (
    complete_session,
    log_set,
    session_logs,
    session_summary,
)
from app.services.strength_progress import exercise_history, suggest_weights

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


class SetLogRequest(BaseModel):
    week: int = Field(ge=1)
    day: int = Field(ge=0, le=6)
    exercise_id: str = Field(max_length=8)
    set_index: int = Field(ge=1, le=20)
    weight_kg: float | None = Field(default=None, ge=0, le=500)
    reps: int = Field(ge=1, le=100)
    rpe: float | None = Field(default=None, ge=1, le=10)


class CompleteSessionRequest(BaseModel):
    week: int = Field(ge=1)
    day: int = Field(ge=0, le=6)


def _require_plan(db: Session, user_id: str):
    plan = current_strength_plan(db, user_id)
    if plan is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "no_active_plan")
    return plan


@router.post("/logs", status_code=status.HTTP_201_CREATED)
async def log_strength_set(
    body: SetLogRequest,
    user: User = Depends(require_premium),
    db: Session = Depends(get_db),
) -> dict:
    """Record (or correct) one performed set of the active program."""
    plan = _require_plan(db, user.id)
    try:
        return log_set(
            db,
            user.id,
            plan,
            week=body.week,
            day=body.day,
            exercise_id=body.exercise_id,
            set_index=body.set_index,
            weight_kg=body.weight_kg,
            reps=body.reps,
            rpe=body.rpe,
        )
    except ValueError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc


@router.get("/logs")
async def get_session_logs(
    week: int,
    day: int,
    user: User = Depends(require_premium),
    db: Session = Depends(get_db),
) -> dict:
    """Sets already logged for one session, with its live summary."""
    plan = _require_plan(db, user.id)
    try:
        summary = session_summary(db, user.id, plan, week=week, day=day)
    except ValueError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
    return {
        "sets": session_logs(db, user.id, plan.id, week=week, day=day),
        "summary": summary,
        "suggestions": suggest_weights(db, user.id, plan, week=week, day=day),
    }


@router.get("/history")
async def get_exercise_history(
    user: User = Depends(require_premium),
    db: Session = Depends(get_db),
) -> dict:
    """Per-exercise PR and latest performance across the active program."""
    plan = _require_plan(db, user.id)
    return {"exercises": exercise_history(db, user.id, plan)}


@router.post("/sessions/complete")
async def complete_strength_session(
    body: CompleteSessionRequest,
    user: User = Depends(require_premium),
    db: Session = Depends(get_db),
) -> dict:
    """Mark today's session done and return prescribed-vs-performed."""
    plan = _require_plan(db, user.id)
    try:
        return complete_session(db, user.id, plan, week=body.week, day=body.day)
    except ValueError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(exc)) from exc
