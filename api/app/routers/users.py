"""Current-user profile endpoints (US11a)."""
from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import CurrentUser, get_current_user
from app.models.user import User

router = APIRouter(tags=["users"])

Goal = Literal["marathon", "weight_loss", "hyrox", "triathlon", "health"]
Units = Literal["metric", "imperial"]


class ProfileUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=120)
    primary_goal: Goal | None = None
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
    """Update profile fields. Only provided fields change."""
    db_user = _get_or_create(db, user)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(db_user, field, value)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return _serialize(db_user)
