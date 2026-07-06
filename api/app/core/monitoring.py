"""Sentry error tracking (S9). Inert until SENTRY_DSN is configured.

Shared by the API process and the ARQ worker so exceptions from both land in
the same project. PII is never sent by default — this app processes health
data; request bodies and user context stay out of events.
"""
from __future__ import annotations

from app.core.config import settings


def init_sentry() -> bool:
    """Initialise Sentry when a DSN is configured. Returns True when active."""
    if not settings.sentry_dsn:
        return False
    import sentry_sdk

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        send_default_pii=False,
        max_request_body_size="never",
    )
    return True
