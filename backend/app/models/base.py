"""HeartXAI 2.0 - Base Model Mixin.

Provides common fields: UUID primary keys, creation timestamps, and update timestamps.
"""

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from app.core.database import Base


def generate_uuid() -> str:
    """Generate RFC 4122 compliant UUIDv4 string."""
    return str(uuid.uuid4())


def utc_now() -> datetime:
    """Return current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class TimestampMixin:
    """Mixin adding created_at and updated_at UTC timestamps."""

    created_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False
    )
