"""GDPR data export + account deletion endpoints (US11b)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import CurrentUser, get_current_user
from app.services.gdpr import build_export, delete_user_data

router = APIRouter(prefix="/gdpr", tags=["gdpr"])


@router.get("/export")
async def export_data(
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Return a full data-portability bundle (JSON + CSV) for the caller."""
    return build_export(db, user.id)


@router.delete("/account")
async def delete_account(
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Right to erasure: purge all of the caller's data and audit the request."""
    delete_user_data(db, user.id)
    return {"deleted": True}
