"""Sliding-window rate limiter unit tests (S5)."""
from __future__ import annotations

from app.core import ratelimit


def setup_function() -> None:
    ratelimit.clear()


def test_allows_up_to_limit_then_blocks():
    assert ratelimit.check("k", times=2, seconds=60.0, now=0.0) is None
    assert ratelimit.check("k", times=2, seconds=60.0, now=1.0) is None
    retry = ratelimit.check("k", times=2, seconds=60.0, now=2.0)
    assert retry is not None and retry > 0


def test_window_slides():
    assert ratelimit.check("k", times=1, seconds=10.0, now=0.0) is None
    assert ratelimit.check("k", times=1, seconds=10.0, now=5.0) is not None
    assert ratelimit.check("k", times=1, seconds=10.0, now=11.0) is None


def test_keys_are_independent():
    assert ratelimit.check("a", times=1, seconds=60.0, now=0.0) is None
    assert ratelimit.check("b", times=1, seconds=60.0, now=0.0) is None
