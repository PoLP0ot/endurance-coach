"""In-process store for pending Garmin MFA challenges (S2).

The garth ``client_state`` holds a live HTTP client and cookies, so it cannot
be serialized to the database. Pending challenges therefore live in process
memory with a short TTL. This assumes a single API instance — true for the
current deployment; with several instances the MFA request could land on
another process and receive a clean 410, in which case the user simply
restarts the connect flow.
"""
from __future__ import annotations

import time

# How long a Garmin MFA challenge stays resumable (seconds).
MFA_TTL_S = 300

_pending: dict[str, tuple[float, str, dict]] = {}


def stash(
    user_id: str, username: str, client_state: dict, now: float | None = None
) -> None:
    """Hold ``client_state`` for ``user_id`` until the code arrives or TTL passes."""
    ts = time.monotonic() if now is None else now
    _pending[user_id] = (ts, username, client_state)


def pop(user_id: str, now: float | None = None) -> tuple[str, dict] | None:
    """Return (username, client_state) and consume it; None if absent/expired."""
    entry = _pending.pop(user_id, None)
    if entry is None:
        return None
    ts, username, client_state = entry
    current = time.monotonic() if now is None else now
    if current - ts > MFA_TTL_S:
        return None
    return username, client_state


def clear() -> None:
    """Drop all pending challenges (tests)."""
    _pending.clear()
