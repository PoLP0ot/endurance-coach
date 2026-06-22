"""Subscription service tests — Paddle signature + webhook application (US8)."""
from __future__ import annotations

import hashlib
import hmac

from app.models.subscription import Subscription
from app.services.subscriptions import (
    apply_webhook_event,
    is_premium,
    verify_paddle_signature,
)

from tests.conftest import TEST_USER_ID


def _sign(secret: str, ts: str, body: bytes) -> str:
    mac = hmac.new(secret.encode(), f"{ts}:{body.decode()}".encode(), hashlib.sha256)
    return f"ts={ts};h1={mac.hexdigest()}"


def test_signature_roundtrip():
    body = b'{"event_type":"subscription.activated"}'
    header = _sign("shh", "1700000000", body)
    assert verify_paddle_signature("shh", body, header) is True
    assert verify_paddle_signature("wrong", body, header) is False
    assert verify_paddle_signature("shh", body, None) is False


def _event(status: str) -> dict:
    return {
        "event_type": "subscription.activated",
        "data": {
            "id": "sub_123",
            "customer_id": "ctm_1",
            "status": status,
            "items": [{"price": {"id": "pri_1"}}],
            "current_billing_period": {"ends_at": "2026-12-31T00:00:00Z"},
            "custom_data": {"user_id": TEST_USER_ID},
        },
    }


def test_webhook_activates_premium(db_session, seed_user):
    sub = apply_webhook_event(db_session, _event("active"))
    assert sub is not None
    assert sub.status == "active"
    assert sub.paddle_subscription_id == "sub_123"
    user = db_session.get(type(seed_user), TEST_USER_ID)
    assert user.subscription_status == "active"
    assert is_premium(user)


def test_webhook_cancel_downgrades(db_session, seed_user):
    apply_webhook_event(db_session, _event("active"))
    cancel = _event("canceled")
    cancel["event_type"] = "subscription.canceled"
    apply_webhook_event(db_session, cancel)
    user = db_session.get(type(seed_user), TEST_USER_ID)
    assert user.subscription_status == "free"
    assert not is_premium(user)
    # Single subscription row reused.
    assert db_session.query(Subscription).count() == 1


def test_webhook_ignores_non_subscription_events(db_session, seed_user):
    assert apply_webhook_event(db_session, {"event_type": "transaction.completed"}) is None
