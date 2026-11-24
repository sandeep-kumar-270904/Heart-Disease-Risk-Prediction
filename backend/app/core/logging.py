"""HeartXAI 2.0 - Structured JSON Logging & Correlation ID Management.

Emits structured JSON logs with automatic request correlation IDs and strict
PHI/credential scrubbing invariants.
"""

from __future__ import annotations

import json
import logging
import re
import sys
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any

from app.core.config import settings

request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")

_SENSITIVE_PATTERN = re.compile(
    r"(password|passwd|secret|token|authorization|cookie|email)\s*[:=]\s*[^\s,;]+",
    re.IGNORECASE,
)


def scrub_sensitive_text(message: str) -> str:
    """Redact potential credentials or identifiers before emitting logs."""
    return _SENSITIVE_PATTERN.sub(r"\1=[REDACTED]", message)


class StructuredJsonFormatter(logging.Formatter):
    """Format log records as single-line JSON objects for observability pipelines."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "service": "heartxai-backend",
            "environment": settings.ENVIRONMENT,
            "request_id": request_id_ctx.get("-"),
            "logger": record.name,
            "message": scrub_sensitive_text(record.getMessage()),
        }
        for attr in ("method", "path", "status_code", "duration_ms", "actor_id", "actor_role"):
            value = getattr(record, attr, None)
            if value is not None:
                payload[attr] = value
        if record.exc_info and record.levelno >= logging.ERROR:
            payload["exception_type"] = (
                record.exc_info[0].__name__ if record.exc_info[0] else "Exception"
            )
        return json.dumps(payload, default=str)


def setup_logging() -> None:
    """Initialize root logger with structured JSON formatting."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredJsonFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


logger = logging.getLogger("heartxai")
