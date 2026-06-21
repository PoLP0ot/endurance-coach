"""JWT auth tests for the protected /me endpoint."""
from __future__ import annotations

from tests.conftest import make_token


def test_me_requires_auth(client):
    resp = client.get("/me")
    assert resp.status_code == 401


def test_me_rejects_malformed_header(client):
    resp = client.get("/me", headers={"Authorization": "NotBearer xyz"})
    assert resp.status_code == 401


def test_me_rejects_invalid_token(client):
    resp = client.get("/me", headers={"Authorization": "Bearer not.a.jwt"})
    assert resp.status_code == 401


def test_me_rejects_wrong_signature(client):
    token = make_token(secret="a-different-secret")
    resp = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401


def test_me_accepts_valid_token(client):
    token = make_token()
    resp = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == "11111111-1111-1111-1111-111111111111"
    assert body["email"] == "athlete@example.com"


def test_error_envelope_shape(client):
    resp = client.get("/me")
    assert resp.status_code == 401
    assert "error" in resp.json()
    assert resp.json()["error"]["code"] == 401
