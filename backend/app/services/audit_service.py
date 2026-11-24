"""HeartXAI 2.0 - Append-Only Security Audit Logging Helper (Milestone 17)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.audit import AuditLog
from app.models.user import User


def record_audit_event(
    db: Session,
    *,
    actor: User | None,
    action_type: str,
    endpoint: str,
    method: str,
    status_code: int,
    resource_id: str | None = None,
    ip_address: str = "127.0.0.1",
    duration_ms: float = 0.0,
) -> AuditLog:
    """Append an immutable security/clinical-access audit row."""
    row = AuditLog(
        user_id=str(actor.id) if actor else None,
        role=str(actor.role) if actor else "ANONYMOUS",
        action_type=action_type,
        resource_id=resource_id,
        endpoint=endpoint,
        method=method,
        ip_address=ip_address,
        status_code=status_code,
        duration_ms=duration_ms,
    )
    db.add(row)
    return row
