"""GarminConnectProvider tests against a mocked garminconnect library (US1.1)."""
from __future__ import annotations

import sys
import types

import pytest
from app.services.garmin import (
    GarminAccountLocked,
    GarminAuthError,
    GarminConnectProvider,
    GarminMFARequired,
)


def _install_fake_garminconnect(monkeypatch, *, login_raises=None):
    fake = types.ModuleType("garminconnect")

    class AuthError(Exception):
        pass

    class TooMany(Exception):
        pass

    class FakeGarth:
        def dumps(self):
            return "TOKEN_BLOB"

    class FakeGarmin:
        def __init__(self, username=None, password=None):
            self.garth = FakeGarth()

        def login(self):
            if login_raises is not None:
                raise login_raises

    fake.Garmin = FakeGarmin
    fake.GarminConnectAuthenticationError = AuthError
    fake.GarminConnectTooManyRequestsError = TooMany
    monkeypatch.setitem(sys.modules, "garminconnect", fake)
    return fake


def test_login_returns_serialized_session_token(monkeypatch):
    _install_fake_garminconnect(monkeypatch)
    provider = GarminConnectProvider()
    assert provider.login("user", "pass") == "TOKEN_BLOB"


def test_login_maps_mfa_error(monkeypatch):
    fake = _install_fake_garminconnect(monkeypatch)
    err = fake.GarminConnectAuthenticationError("MFA code required")

    def boom():
        raise err

    monkeypatch.setattr(fake.Garmin, "login", lambda self: boom())
    provider = GarminConnectProvider()
    with pytest.raises(GarminMFARequired):
        provider.login("user", "pass")


def test_login_maps_auth_error(monkeypatch):
    fake = _install_fake_garminconnect(monkeypatch)

    def boom(self):
        raise fake.GarminConnectAuthenticationError("bad password")

    monkeypatch.setattr(fake.Garmin, "login", boom)
    provider = GarminConnectProvider()
    with pytest.raises(GarminAuthError):
        provider.login("user", "pass")


def test_login_maps_rate_limit_to_locked(monkeypatch):
    fake = _install_fake_garminconnect(monkeypatch)

    def boom(self):
        raise fake.GarminConnectTooManyRequestsError("locked")

    monkeypatch.setattr(fake.Garmin, "login", boom)
    provider = GarminConnectProvider()
    with pytest.raises(GarminAccountLocked):
        provider.login("user", "pass")
