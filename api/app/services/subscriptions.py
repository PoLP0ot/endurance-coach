"""Subscription helpers + Paddle webhook handling (US8)."""
from __future__ import annotations

import hashlib
import hmac
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.subscription import Subscription
from app.models.user import User

# Subscription statuses that unlock premium features.
PREMIUM_STATUSES = frozenset({"premium", "active", "trialing"})
# Free-tier history window (days).
FREE_HISTORY_DAYS = 30
# Paddle statuses we treat as no-longer-premium.
INACTIVE_STATUSES = frozenset({"canceled", "paused", "past_due"})


def is_premium(user: User | None) -> bool:
    """True when the user's subscription unlocks premium features."""
    return user is not None and user.subscription_status in PREMIUM_STATUSES


def verify_paddle_signature(secret: str, raw_body: bytes, header: str | None) -> bool:
    """Verify a Paddle ``Paddle-Signature`` header (ts + HMAC-SHA256).

    The signed payload is ``f"{ts}:{body}"``. Returns False on any malformed
    header or mismatch. Constant-time comparison.
    """
    if not secret or not header:
        return False
    parts = dict(
        p.split("=", 1) for p in header.split(";") if "=" in p
    )
    ts, h1 = parts.get("ts"), parts.get("h1")
    if not ts or not h1:
        return False
    signed = f"{ts}:{raw_body.decode()}".encode()
    expected = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, h1)


def _status_from_event(paddle_status: str) -> str:
    """Map a Paddle subscription status to our stored status."""
    if paddle_status in INACTIVE_STATUSES:
        return "free"
    return paddle_status  # active / trialing pass through (premium)


def _parse_period_end(data: dict) -> datetime | None:
    period = data.get("current_billing_period") or {}
    ends_at = period.get("ends_at")
    if not ends_at:
        return None
    try:
        return datetime.fromisoformat(ends_at.replace("Z", "+00:00"))
    except ValueError:
        return None


def apply_webhook_event(db: Session, event: dict) -> Subscription | None:
    """Apply a Paddle subscription webhook, upserting state and user status.

    The athlete's ``user_id`` is carried in ``data.custom_data.user_id`` (set at
    checkout). Returns the upserted Subscription, or None when not actionable.
    """
    event_type = event.get("event_type", "")
    if not event_type.startswith("subscription."):
        return None
    data = event.get("data", {})
    user_id = (data.get("custom_data") or {}).get("user_id")
    if not user_id:
        return None

    status = _status_from_event(data.get("status", "free"))
    sub = db.execute(
        select(Subscription).where(Subscription.user_id == user_id)
    ).scalars().first()
    if sub is None:
        sub = Subscription(user_id=user_id)
        db.add(sub)

    sub.paddle_subscription_id = data.get("id")
    sub.paddle_customer_id = data.get("customer_id")
    sub.status = status
    items = data.get("items") or []
    if items:
        sub.price_id = (items[0].get("price") or {}).get("id")
    sub.current_period_end = _parse_period_end(data)

    user = db.get(User, user_id)
    if user is not None:
        user.subscription_status = status
        db.add(user)

    db.commit()
    db.refresh(sub)
    return sub
