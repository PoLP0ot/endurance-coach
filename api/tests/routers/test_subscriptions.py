"""Subscription endpoint tests (US8)."""
from __future__ import annotations

import hashlib
import hmac
import json

from app.core.config import settings

from tests.conftest import TEST_USER_ID


def test_status_defaults_to_free(app_client, seed_user):
    body = app_client.get("/subscription/status").json()
    assert body["status"] == "free"
    assert body["is_premium"] is False


def test_checkout_returns_config(app_client, seed_user, monkeypatch):
    monkeypatch.setattr(settings, "paddle_price_id", "pri_abc")
    monkeypatch.setattr(settings, "paddle_client_token", "tok")
    body = app_client.post("/subscription/checkout").json()
    assert body["price_id"] == "pri_abc"
    assert body["custom_data"]["user_id"] == TEST_USER_ID


def test_checkout_503_when_unconfigured(app_client, seed_user, monkeypatch):
    monkeypatch.setattr(settings, "paddle_price_id", "")
    assert app_client.post("/subscription/checkout").status_code == 503


def test_webhook_rejects_bad_signature(app_client, seed_user, monkeypatch):
    monkeypatch.setattr(settings, "paddle_webhook_secret", "shh")
    res = app_client.post(
        "/subscription/webhook",
        content=b"{}",
        headers={"Paddle-Signature": "ts=1;h1=bad"},
    )
    assert res.status_code == 401


def test_webhook_applies_valid_event(app_client, db_session, seed_user, monkeypatch):
    monkeypatch.setattr(settings, "paddle_webhook_secret", "shh")
    event = {
        "event_type": "subscription.activated",
        "data": {
            "id": "sub_1",
            "status": "active",
            "items": [{"price": {"id": "pri_1"}}],
            "custom_data": {"user_id": TEST_USER_ID},
        },
    }
    raw = json.dumps(event).encode()
    ts = "1700000000"
    mac = hmac.new(b"shh", f"{ts}:{raw.decode()}".encode(), hashlib.sha256).hexdigest()
    res = app_client.post(
        "/subscription/webhook",
        content=raw,
        headers={"Paddle-Signature": f"ts={ts};h1={mac}"},
    )
    assert res.status_code == 200
    assert app_client.get("/subscription/status").json()["is_premium"] is True
