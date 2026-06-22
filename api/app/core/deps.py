"""Auth dependencies: validate Supabase JWT and resolve the current user."""
from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.models.user import User
from app.services.subscriptions import is_premium


@dataclass(frozen=True)
class CurrentUser:
    """Identity extracted from a verified Supabase JWT."""

    id: str
    email: str | None
    role: str
    claims: dict


def _decode_token(token: str) -> dict:
    """Verify and decode a Supabase JWT.

    Supabase issues HS256 tokens signed with the project JWT secret. We verify
    signature, audience and expiry. Raises JWTError on any failure.
    """
    if not settings.supabase_jwt_secret:
        raise JWTError("SUPABASE_JWT_SECRET not configured")
    return jwt.decode(
        token,
        settings.supabase_jwt_secret,
        algorithms=[settings.jwt_algorithm],
        audience=settings.jwt_audience,
        options={"verify_aud": True},
    )


async def get_current_user(
    authorization: str | None = Header(default=None),
) -> CurrentUser:
    """FastAPI dependency. Requires a valid `Authorization: Bearer <jwt>`."""
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not authorization or not authorization.lower().startswith("bearer "):
        raise credentials_exc

    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = _decode_token(token)
    except JWTError:
        raise credentials_exc from None

    sub = payload.get("sub")
    if not sub:
        raise credentials_exc

    return CurrentUser(
        id=sub,
        email=payload.get("email"),
        role=payload.get("role", "authenticated"),
        claims=payload,
    )


# Type alias for cleaner route signatures
CurrentUserDep = Depends(get_current_user)


def get_llm_provider():
    """LLMProvider dependency (overridden in tests to avoid network)."""
    from app.services.llm import LLMProvider

    return LLMProvider()


async def require_premium(
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    """Gate premium-only features. Returns the DB user, 402 if not subscribed.

    Auto-provisions the profile row on first access so newly signed-up users
    resolve cleanly (subscription defaults to free → blocked until upgrade).
    """
    db_user = db.get(User, user.id)
    if db_user is None:
        db_user = User(id=user.id, email=user.email)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    if not is_premium(db_user):
        raise HTTPException(
            status.HTTP_402_PAYMENT_REQUIRED, "premium_required"
        )
    return db_user
