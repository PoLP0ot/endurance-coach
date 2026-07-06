"""GarminConnectProvider login/resume tests against mocked garth (US1.1, S2)."""
from __future__ import annotations

import pytest
from app.services.garmin import (
    GarminAccountLocked,
    GarminAuthError,
    GarminConnectProvider,
    GarminMFARequired,
)


class _FakeGarthClient:
    def __init__(self, **kwargs):
        self.oauth1_token = None
        self.oauth2_token = None

    def dumps(self):
        return "TOKEN_BLOB"


def test_login_returns_serialized_session_token(monkeypatch):
    monkeypatch.setattr("garth.Client", _FakeGarthClient)
    monkeypatch.setattr(
        "garth.sso.login", lambda u, p, client=None, return_on_mfa=False: ("o1", "o2")
    )
    assert GarminConnectProvider().login("user", "pass") == "TOKEN_BLOB"


def test_login_surfaces_mfa_with_resumable_state(monkeypatch):
    monkeypatch.setattr("garth.Client", _FakeGarthClient)
    monkeypatch.setattr(
        "garth.sso.login",
        lambda *a, **k: {"needs_mfa": True, "client_state": {"csrf": "x"}},
    )
    with pytest.raises(GarminMFARequired) as exc_info:
        GarminConnectProvider().login("user", "pass")
    assert exc_info.value.client_state == {"csrf": "x"}


def test_login_maps_auth_error(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("401 Client Error: Unauthorized for url: sso")

    monkeypatch.setattr("garth.Client", _FakeGarthClient)
    monkeypatch.setattr("garth.sso.login", boom)
    with pytest.raises(GarminAuthError):
        GarminConnectProvider().login("user", "pass")


def test_login_maps_rate_limit_to_locked(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("429 Too Many Requests")

    monkeypatch.setattr("garth.Client", _FakeGarthClient)
    monkeypatch.setattr("garth.sso.login", boom)
    with pytest.raises(GarminAccountLocked):
        GarminConnectProvider().login("user", "pass")


def test_resume_login_returns_serialized_token(monkeypatch):
    monkeypatch.setattr("garth.sso.resume_login", lambda state, code: ("o1", "o2"))
    state = {"client": _FakeGarthClient()}
    assert GarminConnectProvider().resume_login(state, "123456") == "TOKEN_BLOB"


def test_resume_login_maps_bad_code_to_auth_error(monkeypatch):
    def boom(state, code):
        raise RuntimeError("Unexpected title: MFA")

    monkeypatch.setattr("garth.sso.resume_login", boom)
    with pytest.raises(GarminAuthError):
        GarminConnectProvider().resume_login({"client": _FakeGarthClient()}, "000000")
