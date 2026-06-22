"""Weekly email preview endpoint (US6, premium)."""
from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_llm_provider, require_premium
from app.models.user import User
from app.services.email import build_weekly_email

router = APIRouter(prefix="/email", tags=["email"])


@router.get("/weekly/preview")
async def preview_weekly_email(
    user: User = Depends(require_premium),
    db: Session = Depends(get_db),
    llm=Depends(get_llm_provider),
) -> dict:
    """Render this week's coaching email without sending it."""
    email = build_weekly_email(db, user, llm, today=date.today())
    return {"subject": email["subject"], "html": email["html"]}
