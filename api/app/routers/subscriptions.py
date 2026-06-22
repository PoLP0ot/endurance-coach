"""Subscription status, checkout config, and Paddle webhook (US8)."""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.deps import CurrentUser, get_current_user
from app.models.subscription import Subscription
from app.models.user import User
from app.services.subscriptions import (
    apply_webhook_event,
    is_premium,
    verify_paddle_signature,
)

router = APIRouter(prefix="/subscription", tags=["subscription"])


@router.get("/status")
async def subscription_status(
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Report the caller's subscription state and premium entitlement."""
    db_user = db.get(User, user.id)
    sub = db.execute(
        select(Subscription).where(Subscription.user_id == user.id)
    ).scalars().first()
    return {
        "status": db_user.subscription_status if db_user else "free",
        "is_premium": is_premium(db_user),
        "current_period_end": (
            sub.current_period_end.isoformat()
            if sub and sub.current_period_end
            else None
        ),
    }


@router.post("/checkout")
async def create_checkout(
    user: CurrentUser = Depends(get_current_user),
) -> dict:
    """Return the config the frontend needs to open Paddle checkout."""
    if not settings.paddle_price_id:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, "billing_not_configured"
        )
    return {
        "client_token": settings.paddle_client_token,
        "price_id": settings.paddle_price_id,
        "environment": settings.paddle_environment,
        "customer_email": user.email,
        "custom_data": {"user_id": user.id},
    }


@router.post("/webhook")
async def paddle_webhook(
    request: Request,
    db: Session = Depends(get_db),
    paddle_signature: str | None = Header(default=None),
) -> dict:
    """Receive Paddle subscription events. Verifies the signature, then applies."""
    raw = await request.body()
    if not verify_paddle_signature(
        settings.paddle_webhook_secret, raw, paddle_signature
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid_signature")
    try:
        event = json.loads(raw.decode())
    except json.JSONDecodeError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "invalid_payload") from exc
    apply_webhook_event(db, event)
    return {"received": True}
