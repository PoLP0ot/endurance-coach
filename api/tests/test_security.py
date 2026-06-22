"""Encryption-at-rest tests (US1.2)."""
from __future__ import annotations

from app.core.security import decrypt, encrypt


def test_encrypt_decrypt_roundtrip():
    secret = "garmin-session-token-blob"
    assert decrypt(encrypt(secret)) == secret


def test_ciphertext_differs_from_plaintext():
    secret = "garmin-session-token-blob"
    ciphertext = encrypt(secret)
    assert ciphertext != secret


def test_ciphertext_is_nondeterministic():
    secret = "garmin-session-token-blob"
    assert encrypt(secret) != encrypt(secret)
