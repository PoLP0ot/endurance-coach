"""Pending-MFA store: stash/pop semantics and TTL expiry (S2)."""
from __future__ import annotations

from app.services import garmin_mfa


def setup_function() -> None:
    garmin_mfa.clear()


def test_pop_returns_stashed_challenge_once():
    garmin_mfa.stash("user-1", "u@example.com", {"k": 1}, now=1000.0)
    assert garmin_mfa.pop("user-1", now=1001.0) == ("u@example.com", {"k": 1})
    assert garmin_mfa.pop("user-1", now=1002.0) is None


def test_pop_expires_after_ttl():
    garmin_mfa.stash("user-1", "u@example.com", {"k": 1}, now=1000.0)
    assert garmin_mfa.pop("user-1", now=1000.0 + garmin_mfa.MFA_TTL_S + 1) is None


def test_pop_unknown_user_is_none():
    assert garmin_mfa.pop("nobody", now=0.0) is None
