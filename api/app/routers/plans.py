"""Training plan endpoints (US5, premium)."""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_llm_provider, require_premium
from app.core.ratelimit import rate_limit
from app.models.plan import TrainingPlan
from app.models.user import User
from app.routers.garmin import get_garmin_provider
from app.services.dashboard import build_dashboard
from app.services.garmin import GarminProvider
from app.services.plans import create_plan, current_plan
from app.services.workout_push import push_current_week

router = APIRouter(prefix="/plans", tags=["plans"])

VALID_GOALS = {"marathon", "weight_loss", "hyrox", "triathlon", "health"}


class PlanRequest(BaseModel):
    goal: str | None = None
    weeks: int = Field(default=12, ge=4, le=24)


def _serialize(plan: TrainingPlan) -> dict:
    return {
        "id": plan.id,
        "goal": plan.goal,
        "weeks": plan.weeks,
        "start_date": plan.start_date.isoformat(),
        "status": plan.status,
        "structure": plan.structure,
        "narrative": plan.narrative,
        "model": plan.model,
    }


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit("plans"))],
)
async def generate_plan(
    body: PlanRequest,
    user: User = Depends(require_premium),
    db: Session = Depends(get_db),
    llm=Depends(get_llm_provider),
) -> dict:
    """Generate a periodized plan for the user's goal, grounded in current CTL."""
    goal = body.goal or user.primary_goal or "marathon"
    if goal not in VALID_GOALS:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "invalid_goal")
    base_ctl = build_dashboard(db, user.id, today=date.today())["fitness"]["ctl"]
    plan = create_plan(
        db,
        user.id,
        goal=goal,
        weeks=body.weeks,
        start_date=date.today(),
        base_ctl=base_ctl,
        llm=llm,
        goal_params=user.goal_params if goal == (user.primary_goal or goal) else None,
    )
    return _serialize(plan)


@router.get("/current")
async def get_current_plan(
    user: User = Depends(require_premium),
    db: Session = Depends(get_db),
) -> dict:
    """Return the user's active plan, or null when none exists."""
    plan = current_plan(db, user.id)
    return {"plan": _serialize(plan) if plan is not None else None}


_PUSH_ERRORS = {
    "garmin_not_connected": status.HTTP_409_CONFLICT,
    "no_active_plan": status.HTTP_409_CONFLICT,
    "no_current_week": status.HTTP_409_CONFLICT,
}


@router.post("/push", status_code=status.HTTP_202_ACCEPTED)
async def push_to_watch(
    user: User = Depends(require_premium),
    db: Session = Depends(get_db),
    provider: GarminProvider = Depends(get_garmin_provider),
) -> dict:
    """Send this week's structured workout to the user's Garmin watch (A14)."""
    try:
        result = push_current_week(db, user.id, provider, date.today())
    except ValueError as exc:
        code = _PUSH_ERRORS.get(str(exc), status.HTTP_400_BAD_REQUEST)
        raise HTTPException(code, str(exc)) from exc
    return result
