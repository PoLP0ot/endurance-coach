"""429 behaviour on abuse-sensitive endpoints (S5)."""
from __future__ import annotations

import pytest
from app.core import ratelimit
from app.core.config import settings
from app.main import app
from app.routers.garmin import get_garmin_provider


class _Provider:
    def login(self, username, password):
        return "TOKEN"


@pytest.fixture()
def limited(monkeypatch):
    monkeypatch.setattr(settings, "rate_limit_enabled", True)
    monkeypatch.setattr(settings, "rate_limit_garmin_per_5min", 2)
    ratelimit.clear()
    yield
    ratelimit.clear()


def test_garmin_connect_429_after_limit(app_client, limited):
    app.dependency_overrides[get_garmin_provider] = lambda: _Provider()
    payload = {"username": "u@example.com", "password": "pw"}
    assert app_client.post("/garmin/connect", json=payload).status_code == 202
    assert app_client.post("/garmin/connect", json=payload).status_code == 202

    resp = app_client.post("/garmin/connect", json=payload)
    assert resp.status_code == 429
    assert resp.json()["error"]["message"] == "rate_limited"
    assert "Retry-After" in resp.headers
