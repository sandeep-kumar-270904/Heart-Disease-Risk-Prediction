"""HeartXAI 2.0 - Base Model Mixin & RFC 9562 UUIDv7 Generator.

Provides common fields: time-ordered UUIDv7 primary keys, creation timestamps,
and update timestamps.
"""

import os
import threading
import time
import uuid
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime

_UUID_LOCK = threading.Lock()
_LAST_TIMESTAMP_MS = 0
_LAST_RAND_A = 0


def generate_uuidv7() -> str:
    """Generate an RFC 9562 compliant, monotonically sortable UUIDv7 string.

    Layout (128 bits):
    - 48 bits: Unix timestamp in milliseconds (big-endian)
    -  4 bits: Version (0b0111 = 7)
    - 12 bits: Monotonic sub-millisecond counter / random_a
    -  2 bits: Variant (0b10)
    - 62 bits: Cryptographically random_b
    """
    global _LAST_TIMESTAMP_MS, _LAST_RAND_A

    with _UUID_LOCK:
        timestamp_ms = time.time_ns() // 1_000_000
        if timestamp_ms <= _LAST_TIMESTAMP_MS:
            timestamp_ms = _LAST_TIMESTAMP_MS
            _LAST_RAND_A = (_LAST_RAND_A + 1) & 0x0FFF
            if _LAST_RAND_A == 0:
                timestamp_ms += 1
                _LAST_RAND_A = int.from_bytes(os.urandom(2), "big") & 0x07FF
        else:
            _LAST_RAND_A = int.from_bytes(os.urandom(2), "big") & 0x07FF

        _LAST_TIMESTAMP_MS = timestamp_ms
        rand_a = _LAST_RAND_A
        rand_b = int.from_bytes(os.urandom(8), "big") & 0x3FFFFFFFFFFFFFFF

    uuid_int = (
        ((timestamp_ms & 0xFFFFFFFFFFFF) << 80)
        | (0x7 << 76)
        | ((rand_a & 0x0FFF) << 64)
        | (0x2 << 62)
        | rand_b
    )
    return str(uuid.UUID(int=uuid_int))


def generate_uuid() -> str:
    """Primary key default factory returning RFC 9562 UUIDv7 strings."""
    return generate_uuidv7()


def utc_now() -> datetime:
    """Return current timezone-aware UTC datetime."""
    return datetime.now(UTC)


class TimestampMixin:
    """Mixin adding created_at and updated_at UTC timestamps."""

    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
