"""Subscription endpoint tests (US8, S3 cancel)."""
from __future__ import annotations

import hashlib
import hmac
import json

from app.core.config import settings
from app.main import app
from app.models.subscription import Subscription
from app.models.user import User
from app.routers.subscriptions import get_paddle_canceller

from tests.conftest import TEST_USER_ID


def _seed_active_subscription(db_session):
    db_session.add(
        Subscription(
            user_id=TEST_USER_ID,
            paddle_subscription_id="sub_live",
            status="active",
        )
    )
    user = db_session.get(User, TEST_USER_ID)
    user.subscription_status = "active"
    db_session.commit()


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


def test_checkout_annual_uses_annual_price(app_client, seed_user, monkeypatch):
    monkeypatch.setattr(settings, "paddle_price_id", "pri_month")
    monkeypatch.setattr(settings, "paddle_price_id_annual", "pri_year")
    body = app_client.post(
        "/subscription/checkout", json={"interval": "year"}
    ).json()
    assert body["price_id"] == "pri_year"
    assert body["interval"] == "year"


def test_checkout_defaults_to_monthly(app_client, seed_user, monkeypatch):
    monkeypatch.setattr(settings, "paddle_price_id", "pri_month")
    body = app_client.post("/subscription/checkout").json()
    assert body["price_id"] == "pri_month"
    assert body["interval"] == "month"


def test_checkout_annual_503_when_not_configured(
    app_client, seed_user, monkeypatch
):
    monkeypatch.setattr(settings, "paddle_price_id", "pri_month")
    monkeypatch.setattr(settings, "paddle_price_id_annual", "")
    res = app_client.post("/subscription/checkout", json={"interval": "year"})
    assert res.status_code == 503
    assert res.json()["error"]["message"] == "annual_price_not_configured"


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


def test_cancel_flags_period_end_and_calls_paddle(
    app_client, db_session, seed_user, monkeypatch
):
    monkeypatch.setattr(settings, "paddle_api_key", "key")
    _seed_active_subscription(db_session)
    calls: list[str] = []
    app.dependency_overrides[get_paddle_canceller] = lambda: (
        lambda sub_id: calls.append(sub_id) or {}
    )

    res = app_client.post("/subscription/cancel")
    assert res.status_code == 200
    assert res.json()["cancel_at_period_end"] is True
    assert calls == ["sub_live"]

    status = app_client.get("/subscription/status").json()
    assert status["cancel_at_period_end"] is True
    assert status["is_premium"] is True  # access kept until period end


def test_cancel_409_without_active_subscription(
    app_client, seed_user, monkeypatch
):
    monkeypatch.setattr(settings, "paddle_api_key", "key")
    res = app_client.post("/subscription/cancel")
    assert res.status_code == 409
    assert res.json()["error"]["message"] == "no_active_subscription"


def test_cancel_503_when_unconfigured(app_client, db_session, seed_user, monkeypatch):
    monkeypatch.setattr(settings, "paddle_api_key", "")
    _seed_active_subscription(db_session)
    assert app_client.post("/subscription/cancel").status_code == 503
