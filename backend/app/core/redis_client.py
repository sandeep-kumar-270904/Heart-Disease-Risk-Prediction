"""HeartXAI 2.0 - Fail-Closed Redis Token Family & Blacklist Store (ADR-005)."""

from __future__ import annotations

import time
from typing import Protocol

import redis
from redis.exceptions import RedisError

from app.core.config import settings
from app.core.errors import AuthenticationError, ServiceUnavailableError
from app.core.logging import logger


class TokenStoreBackend(Protocol):
    """Protocol for Redis-backed token family & revocation storage."""

    def register_family(self, family_id: str, jti: str, ttl_seconds: int) -> None: ...

    def rotate_family_token(
        self, family_id: str, presented_jti: str, new_jti: str, ttl_seconds: int
    ) -> None: ...

    def invalidate_family(self, family_id: str) -> None: ...

    def blacklist_access_jti(self, jti: str, ttl_seconds: int) -> None: ...

    def is_access_jti_blacklisted(self, jti: str) -> bool: ...


class RedisTokenStore:
    """Production fail-closed Redis token rotation and replay detection store."""

    def __init__(self, redis_url: str = settings.REDIS_URL, max_retries: int = 2) -> None:
        self._client = redis.Redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=1.5,
            socket_timeout=1.5,
        )
        self._max_retries = max_retries

    def _with_fail_closed_retry(self, op_name: str, fn):  # type: ignore[no-untyped-def]
        last_exc: Exception | None = None
        for attempt in range(self._max_retries + 1):
            try:
                return fn()
            except (RedisError, OSError) as exc:
                last_exc = exc
                if attempt < self._max_retries:
                    time.sleep(0.05 * (2**attempt))
        logger.error("Redis fail-closed triggered during %s: %s", op_name, last_exc)
        raise ServiceUnavailableError(
            "Session revocation store unavailable. Failing closed for security."
        ) from last_exc

    def register_family(self, family_id: str, jti: str, ttl_seconds: int) -> None:
        def _op() -> None:
            self._client.setex(f"auth:family:{family_id}:active", ttl_seconds, jti)

        self._with_fail_closed_retry("register_family", _op)

    def rotate_family_token(
        self, family_id: str, presented_jti: str, new_jti: str, ttl_seconds: int
    ) -> None:
        key = f"auth:family:{family_id}:active"

        def _op() -> str:
            active_jti = self._client.get(key)
            if active_jti is None:
                return "MISSING"
            if active_jti != presented_jti:
                # Replay attack detected: invalidate entire token family immediately
                self._client.delete(key)
                return "REPLAY"
            self._client.setex(key, ttl_seconds, new_jti)
            return "OK"

        outcome = self._with_fail_closed_retry("rotate_family_token", _op)
        if outcome == "MISSING":
            raise AuthenticationError("Refresh session expired or revoked.")
        if outcome == "REPLAY":
            raise AuthenticationError(
                "Refresh token reuse detected. Session token family invalidated."
            )

    def invalidate_family(self, family_id: str) -> None:
        def _op() -> None:
            self._client.delete(f"auth:family:{family_id}:active")

        self._with_fail_closed_retry("invalidate_family", _op)

    def blacklist_access_jti(self, jti: str, ttl_seconds: int) -> None:
        def _op() -> None:
            self._client.setex(f"auth:blacklist:{jti}", max(ttl_seconds, 1), "1")

        self._with_fail_closed_retry("blacklist_access_jti", _op)

    def is_access_jti_blacklisted(self, jti: str) -> bool:
        def _op() -> bool:
            return bool(self._client.exists(f"auth:blacklist:{jti}"))

        return bool(self._with_fail_closed_retry("is_access_jti_blacklisted", _op))


_default_token_store: TokenStoreBackend | None = None


def get_token_store() -> TokenStoreBackend:
    """FastAPI dependency returning the active Redis token store."""
    global _default_token_store
    if _default_token_store is None:
        _default_token_store = RedisTokenStore()
    return _default_token_store
