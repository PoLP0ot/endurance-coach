"""Token encryption helpers for secrets at rest (e.g. Garmin credentials)."""
from __future__ import annotations

import base64
import hashlib

from cryptography.fernet import Fernet

from app.core.config import settings


def _fernet() -> Fernet:
    """Build a Fernet from ENCRYPTION_KEY.

    Accepts either a urlsafe-base64 32-byte key, or any passphrase which is
    hashed to a valid key. Never log the key.
    """
    key = settings.encryption_key
    if not key:
        raise RuntimeError("ENCRYPTION_KEY is not configured")
    try:
        # Valid Fernet key?
        Fernet(key.encode())
        return Fernet(key.encode())
    except (ValueError, TypeError):
        digest = hashlib.sha256(key.encode()).digest()
        return Fernet(base64.urlsafe_b64encode(digest))


def encrypt(plaintext: str) -> str:
    """Encrypt a string for storage."""
    return _fernet().encrypt(plaintext.encode()).decode()


def decrypt(token: str) -> str:
    """Decrypt a previously encrypted string."""
    return _fernet().decrypt(token.encode()).decode()
