"""Auth dependencies: validate Supabase JWT and resolve the current user."""
from __future__ import annotations

import time
from dataclasses import dataclass

import httpx
from fastapi import Depends, Header, HTTPException, status
from jose import JWTError, jwt
from jose.jwk import construct
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.models.user import User
from app.services.subscriptions import is_premium

# Cache for JWKS keys, refreshed at most once an hour.
_jwks_cache: dict = {"keys": {}, "fetched_at": 0.0}


@dataclass(frozen=True)
class CurrentUser:
    """Identity extracted from a verified Supabase JWT."""
    id: str
    email: str | None
    role: str
    claims: dict


def _fetch_jwks_key(kid: str) -> dict:
    """Return the JWKS key for ``kid``, fetching synchronously and caching for 1h.

    Synchronous httpx is used so this is safe inside FastAPI's running event loop.
    """
    now = time.time()
    if now - _jwks_cache["fetched_at"] < 3600 and kid in _jwks_cache["keys"]:
        return _jwks_cache["keys"][kid]

    jwks_url = f"{settings.supabase_url}/auth/v1/.well-known/jwks.json"
    resp = httpx.get(jwks_url)
    resp.raise_for_status()
    jwks = resp.json()

    _jwks_cache["keys"] = {k["kid"]: k for k in jwks.get("keys", [])}
    _jwks_cache["fetched_at"] = now
    return _jwks_cache["keys"].get(kid, {})


def _decode_token(token: str) -> dict:
    """Verify and decode a Supabase JWT.

    Asymmetric tokens (ES256/RS256) carry a ``kid`` and are verified against the
    project's JWKS. Symmetric tokens (HS256) carry no ``kid`` and are verified
    with the shared JWT secret. Raises ``JWTError`` on any failure.
    """
    header = jwt.get_unverified_header(token)
    kid = header.get("kid")

    if kid:
        key_data = _fetch_jwks_key(kid)
        if not key_data:
            raise JWTError(f"JWKS key {kid} not found")
        return jwt.decode(
            token,
            construct(key_data),
            algorithms=[key_data.get("alg", "ES256")],
            audience=settings.jwt_audience,
            options={"verify_aud": True},
        )

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
    """FastAPI dependency. Requires a valid Authorization: Bearer <token>."""
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
    """Gate premium-only features. Returns the DB user, 402 if not subscribed."""
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
