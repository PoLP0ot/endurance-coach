"""Current-user profile endpoints (US11a)."""
from __future__ import annotations

from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from sqlalchemy import select

from app.core.db import get_db
from app.core.deps import CurrentUser, get_current_user
from app.models.health import DailyHealth
from app.models.user import User
from app.schemas.goal_params import validate_goal_params

router = APIRouter(tags=["users"])

Goal = Literal["marathon", "weight_loss", "hyrox", "triathlon", "health"]
Units = Literal["metric", "imperial"]


class ProfileUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=120)
    primary_goal: Goal | None = None
    race_name: str | None = Field(default=None, max_length=120)
    race_date: date | None = None
    goal_params: dict | None = None
    units: Units | None = None
    weekly_email_opt_in: bool | None = None


def _get_or_create(db: Session, current: CurrentUser) -> User:
    user = db.get(User, current.id)
    if user is None:
        user = User(id=current.id, email=current.email)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def _serialize(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "primary_goal": user.primary_goal,
        "race_name": user.race_name,
        "race_date": user.race_date.isoformat() if user.race_date else None,
        "goal_params": user.goal_params,
        "units": user.units,
        "weekly_email_opt_in": user.weekly_email_opt_in,
        "onboarding_complete": user.onboarding_complete,
        "subscription_status": user.subscription_status,
    }


@router.get("/profile")
async def get_me(
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Return the caller's profile, creating the row on first access."""
    return _serialize(_get_or_create(db, user))


@router.patch("/profile")
async def update_me(
    body: ProfileUpdate,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Update profile fields. Only provided fields change.

    ``goal_params`` is validated against the resulting goal kind (the new
    ``primary_goal`` if provided, else the stored one) → 422 on a bad shape.
    """
    db_user = _get_or_create(db, user)
    fields = body.model_dump(exclude_unset=True)

    if "goal_params" in fields and fields["goal_params"] is not None:
        goal_kind = fields.get("primary_goal") or db_user.primary_goal
        try:
            fields["goal_params"] = validate_goal_params(goal_kind, fields["goal_params"])
        except ValueError as exc:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY, f"invalid_goal_params: {exc}"
            ) from exc

    for field, value in fields.items():
        setattr(db_user, field, value)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return _serialize(db_user)


class WeightEntry(BaseModel):
    weight_kg: float = Field(gt=20, lt=400)
    day: date | None = None


@router.post("/profile/weight")
async def log_weight(
    body: WeightEntry,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Manually log a body weight (defaults to today). Upserts the day's row.

    This is the weight-loss loop's input for athletes without a connected
    scale; Garmin imports never overwrite a manual entry with an empty value.
    """
    _get_or_create(db, user)
    day = body.day or date.today()
    row = db.execute(
        select(DailyHealth).where(
            DailyHealth.user_id == user.id, DailyHealth.day == day
        )
    ).scalar_one_or_none()
    if row is None:
        row = DailyHealth(user_id=user.id, day=day)
    row.weight_kg = body.weight_kg
    db.add(row)
    db.commit()
    return {"day": day.isoformat(), "weight_kg": body.weight_kg}
