"""Coach endpoints — today's prescription and the daily brief."""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import (
    CurrentUser,
    get_current_user,
    get_llm_provider,
    require_premium,
)
from app.models.user import User
from app.services.brief import get_or_create_brief
from app.services.today import todays_session

router = APIRouter(prefix="/coach", tags=["coach"])


@router.get("/today")
async def get_today(
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Today's prescribed session, week adherence and goal band."""
    return todays_session(db, user.id, date.today())


@router.get("/brief")
async def get_brief(
    user: User = Depends(require_premium),
    db: Session = Depends(get_db),
    llm=Depends(get_llm_provider),
) -> dict:
    """The proactive daily coaching brief (premium). Cached per day."""
    brief = get_or_create_brief(db, user.id, llm, date.today())
    return {
        "day": brief.day.isoformat(),
        "headline": brief.headline,
        "body": brief.body,
        "prescription": brief.prescription,
        "model": brief.model,
    }
