"""Per-user sliding-window rate limiting, in process memory (S5).

No external dependency and no extra infrastructure: buckets live in the API
process (single-instance assumption, like the pending-MFA store). Guards the
endpoints where abuse costs real money (LLM calls) or third-party standing
(Garmin login attempts).
"""
from __future__ import annotations

import time
from collections import deque

from fastapi import Depends, HTTPException, status

from app.core.config import settings
from app.core.deps import CurrentUser, get_current_user

_buckets: dict[str, deque[float]] = {}


def check(
    key: str, times: int, seconds: float, now: float | None = None
) -> float | None:
    """Record a hit for ``key``; None when allowed, else seconds until retry."""
    current = time.monotonic() if now is None else now
    bucket = _buckets.setdefault(key, deque())
    while bucket and current - bucket[0] > seconds:
        bucket.popleft()
    if len(bucket) >= times:
        return seconds - (current - bucket[0])
    bucket.append(current)
    return None


def clear() -> None:
    """Drop all buckets (tests)."""
    _buckets.clear()


def _limits_for(scope: str) -> tuple[int, float]:
    """(max hits, window seconds) for a scope, read from live settings."""
    return {
        "chat": (settings.rate_limit_chat_per_min, 60.0),
        "garmin_login": (settings.rate_limit_garmin_per_5min, 300.0),
        "plans": (settings.rate_limit_plans_per_hour, 3600.0),
    }[scope]


def rate_limit(scope: str):
    """FastAPI dependency enforcing the scope's per-user limit (429 + Retry-After)."""

    async def dep(user: CurrentUser = Depends(get_current_user)) -> None:
        if not settings.rate_limit_enabled:
            return
        times, seconds = _limits_for(scope)
        retry = check(f"{scope}:{user.id}", times, seconds)
        if retry is not None:
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS,
                "rate_limited",
                headers={"Retry-After": str(int(retry) + 1)},
            )

    return dep
