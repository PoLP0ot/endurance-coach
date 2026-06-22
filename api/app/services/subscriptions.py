"""Subscription helpers shared across feature gates (US8 extends this)."""
from __future__ import annotations

from app.models.user import User

# Subscription statuses that unlock premium features.
PREMIUM_STATUSES = frozenset({"premium", "active", "trialing"})
# Free-tier history window (days).
FREE_HISTORY_DAYS = 30


def is_premium(user: User | None) -> bool:
    """True when the user's subscription unlocks premium features."""
    return user is not None and user.subscription_status in PREMIUM_STATUSES
