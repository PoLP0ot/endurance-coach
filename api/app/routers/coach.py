"""Coach endpoints — today's prescription and the daily brief."""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import CurrentUser, get_current_user
from app.services.today import todays_session

router = APIRouter(prefix="/coach", tags=["coach"])


@router.get("/today")
async def get_today(
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Today's prescribed session, week adherence and goal band."""
    return todays_session(db, user.id, date.today())
