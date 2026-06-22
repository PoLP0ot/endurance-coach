"""Shared test fixtures. No network; the DB is in-memory SQLite."""
from __future__ import annotations

import os

# Configure deterministic test settings BEFORE app imports read them.
os.environ.setdefault("SUPABASE_JWT_SECRET", "test-secret-do-not-use-in-prod")
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("ENCRYPTION_KEY", "test-encryption-key-not-for-prod")

import pytest  # noqa: E402
from app.core.config import settings  # noqa: E402
from app.core.db import get_db  # noqa: E402
from app.core.deps import CurrentUser, get_current_user  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Base, User  # noqa: E402
from app.routers.garmin import get_enqueuer  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from jose import jwt  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

JWT_SECRET = "test-secret-do-not-use-in-prod"
TEST_USER_ID = "11111111-1111-1111-1111-111111111111"
TEST_USER_EMAIL = "athlete@example.com"


@pytest.fixture()
def client() -> TestClient:
    """Plain client with real auth (for health/auth tests)."""
    return TestClient(app)


@pytest.fixture()
def db_session() -> Session:
    """In-memory SQLite session with all tables created (cross-dialect models)."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, future=True)
    session = factory()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture()
def seed_user(db_session: Session) -> User:
    """A persisted user owning imported data."""
    user = User(id=TEST_USER_ID, email=TEST_USER_EMAIL)
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture()
def enqueue_spy():
    """Async enqueue stub that records its calls."""
    calls: list[tuple[str, str, str]] = []

    async def _spy(user_id: str, job_id: str, since_iso: str) -> None:
        calls.append((user_id, job_id, since_iso))

    _spy.calls = calls  # type: ignore[attr-defined]
    return _spy


@pytest.fixture()
def app_client(db_session: Session, enqueue_spy):
    """Client with DB, auth and enqueuer overridden for endpoint tests."""

    def _get_db():
        yield db_session

    def _current_user() -> CurrentUser:
        return CurrentUser(
            id=TEST_USER_ID,
            email=TEST_USER_EMAIL,
            role="authenticated",
            claims={},
        )

    app.dependency_overrides[get_db] = _get_db
    app.dependency_overrides[get_current_user] = _current_user
    app.dependency_overrides[get_enqueuer] = lambda: enqueue_spy
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def make_token(
    sub: str = TEST_USER_ID,
    email: str = TEST_USER_EMAIL,
    secret: str | None = None,
    aud: str = "authenticated",
) -> str:
    """Mint a Supabase-style HS256 JWT for tests."""
    payload = {"sub": sub, "email": email, "role": "authenticated", "aud": aud}
    return jwt.encode(payload, secret or settings.supabase_jwt_secret, algorithm="HS256")
