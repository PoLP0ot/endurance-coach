"""Training plan endpoints (US5, premium)."""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_llm_provider, require_premium
from app.models.plan import TrainingPlan
from app.models.user import User
from app.services.dashboard import build_dashboard
from app.services.plans import create_plan, current_plan

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


@router.post("", status_code=status.HTTP_201_CREATED)
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
