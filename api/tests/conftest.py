"""Shared test fixtures. No network, no real DB required."""
from __future__ import annotations

import os

# Configure deterministic test settings BEFORE app imports read them.
os.environ.setdefault("SUPABASE_JWT_SECRET", "test-secret-do-not-use-in-prod")
os.environ.setdefault("ENVIRONMENT", "test")

import pytest  # noqa: E402
from app.core.config import settings  # noqa: E402
from app.main import app  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from jose import jwt  # noqa: E402

JWT_SECRET = "test-secret-do-not-use-in-prod"


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


def make_token(
    sub: str = "11111111-1111-1111-1111-111111111111",
    email: str = "athlete@example.com",
    secret: str | None = None,
    aud: str = "authenticated",
) -> str:
    """Mint a Supabase-style HS256 JWT for tests."""
    payload = {"sub": sub, "email": email, "role": "authenticated", "aud": aud}
    return jwt.encode(payload, secret or settings.supabase_jwt_secret, algorithm="HS256")
