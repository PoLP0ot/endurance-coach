"""Sentry wiring (S9): inert without a DSN, PII-safe when active."""
from __future__ import annotations

from app.core.config import settings
from app.core.monitoring import init_sentry


def test_no_dsn_means_no_init(monkeypatch):
    monkeypatch.setattr(settings, "sentry_dsn", "")
    assert init_sentry() is False


def test_dsn_initialises_without_pii(monkeypatch):
    captured: dict = {}

    def fake_init(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(settings, "sentry_dsn", "https://key@sentry.example/1")
    monkeypatch.setattr("sentry_sdk.init", fake_init)
    assert init_sentry() is True
    assert captured["dsn"] == "https://key@sentry.example/1"
    # Health-data app: PII and request bodies must never leave the box.
    assert captured["send_default_pii"] is False
    assert captured["max_request_body_size"] == "never"
