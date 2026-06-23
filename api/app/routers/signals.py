"""Signals / Explore endpoint (US2 lens).

Available on the free tier with deterministic templated answers. Premium users
get the same facts narrated by the LLM.
"""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import CurrentUser, get_current_user, get_llm_provider
from app.models.user import User
from app.services.signals import build_signals
from app.services.subscriptions import is_premium

router = APIRouter(prefix="/signals", tags=["signals"])


@router.get("")
async def get_signals(
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    llm=Depends(get_llm_provider),
) -> dict:
    """Return coach-answered signal cards grounded in the user's real metrics."""
    db_user = db.get(User, user.id)
    narrator = llm if (db_user is not None and is_premium(db_user)) else None
    return build_signals(db, user.id, today=date.today(), llm=narrator)
