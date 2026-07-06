"""Subscription status, checkout config, cancel, and Paddle webhook (US8, S3)."""
from __future__ import annotations

import json
from collections.abc import Callable

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
    request_paddle_cancellation,
    verify_paddle_signature,
)

router = APIRouter(prefix="/subscription", tags=["subscription"])

PaddleCanceller = Callable[[str], dict]


def get_paddle_canceller() -> PaddleCanceller:
    """Paddle cancellation call (overridden in tests)."""
    return request_paddle_cancellation


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
        "cancel_at_period_end": bool(sub and sub.cancel_at_period_end),
    }


@router.post("/cancel")
async def cancel_subscription(
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    cancel: PaddleCanceller = Depends(get_paddle_canceller),
) -> dict:
    """Cancel at period end via the Paddle API. Access continues until then."""
    if not settings.paddle_api_key:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, "billing_not_configured"
        )
    sub = db.execute(
        select(Subscription).where(Subscription.user_id == user.id)
    ).scalars().first()
    db_user = db.get(User, user.id)
    if (
        sub is None
        or sub.paddle_subscription_id is None
        or not is_premium(db_user)
    ):
        raise HTTPException(status.HTTP_409_CONFLICT, "no_active_subscription")
    try:
        cancel(sub.paddle_subscription_id)
    except Exception as exc:  # noqa: BLE001 — httpx errors map to a clean 502
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "paddle_error") from exc
    # The webhook will confirm, but reflect the intent immediately so the UI
    # doesn't depend on webhook latency.
    sub.cancel_at_period_end = True
    db.commit()
    return {
        "status": db_user.subscription_status,
        "cancel_at_period_end": True,
        "current_period_end": (
            sub.current_period_end.isoformat() if sub.current_period_end else None
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
