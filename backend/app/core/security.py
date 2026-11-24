"""HeartXAI 2.0 - Cryptographic Security & Authentication Primitives.

Implements RFC 9106 Argon2id password hashing (64 MB, 3 iterations, 4 threads)
and dual-token JWT lifecycle (15-min access JWT + 7-day family-tracked refresh JWT).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any, cast

import bcrypt
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.core.config import settings
from app.models.base import generate_uuidv7

# ADR-003: Argon2id RFC 9106 (m=64 MB, t=3, p=4)
_ARGON2_HASHER = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
)


def hash_password(password: str) -> str:
    """Hash plaintext password using Argon2id (64 MB memory, 3 iterations, 4 threads)."""
    return _ARGON2_HASHER.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plaintext password against stored Argon2id (or legacy bcrypt) hash."""
    if hashed_password.startswith("$argon2"):
        try:
            return _ARGON2_HASHER.verify(hashed_password, plain_password)
        except (VerifyMismatchError, Exception):
            return False
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def create_access_token(
    subject: str | Any,
    role: str,
    expires_delta: timedelta | None = None,
    jti: str | None = None,
) -> str:
    """Generate short-lived signed JWT access token containing subject, role, and jti."""
    now = datetime.now(UTC)
    expire = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode: dict[str, Any] = {
        "sub": str(subject),
        "role": role,
        "type": "access",
        "jti": jti or generate_uuidv7(),
        "exp": expire,
        "iat": now,
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(
    subject: str | Any,
    role: str,
    family_id: str,
    expires_delta: timedelta | None = None,
    jti: str | None = None,
) -> str:
    """Generate family-tracked refresh JWT for HttpOnly cookie rotation."""
    now = datetime.now(UTC)
    expire = now + (expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode: dict[str, Any] = {
        "sub": str(subject),
        "role": role,
        "type": "refresh",
        "family_id": family_id,
        "jti": jti or generate_uuidv7(),
        "exp": expire,
        "iat": now,
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decode and cryptographically verify a signed JWT access token."""
    try:
        payload = cast(
            dict[str, Any],
            jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]),
        )
        token_type = payload.get("type")
        if token_type is not None and token_type != "access":
            return None
        return payload
    except (jwt.PyJWTError, Exception):
        return None


def decode_refresh_token(token: str) -> dict[str, Any] | None:
    """Decode and cryptographically verify a signed refresh JWT token."""
    try:
        payload = cast(
            dict[str, Any],
            jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]),
        )
        if payload.get("type") != "refresh" or not payload.get("family_id"):
            return None
        return payload
    except (jwt.PyJWTError, Exception):
        return None
