"""Health and identity endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.deps import CurrentUser, get_current_user

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    """Liveness probe."""
    return {"status": "ok"}


@router.get("/me")
async def me(user: CurrentUser = Depends(get_current_user)) -> dict:
    """Return the authenticated user's identity (requires a valid JWT)."""
    return {"id": user.id, "email": user.email, "role": user.role}
