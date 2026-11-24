"""HeartXAI 2.0 - Administrative Console & Immutable Audit Trail Routes (Milestone 17)."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, cast

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.deps import normalize_role_name, require_role
from app.core.database import get_db
from app.core.errors import ResourceNotFoundError
from app.models.audit import AuditLog
from app.models.user import User
from app.schemas.base import BaseSchema
from app.services.audit_service import record_audit_event

router = APIRouter(prefix="/admin", tags=["Administrative Console & Audit"])
REPO_ROOT = Path(__file__).resolve().parents[5]
MODEL_CARD_PATH = REPO_ROOT / "ml" / "registry" / "model_card.json"


class AuditLogItemResponse(BaseSchema):
    """Immutable audit log entry view."""

    id: str
    timestamp: datetime
    user_id: str | None = None
    role: str
    action_type: str
    resource_id: str | None = None
    endpoint: str
    method: str
    ip_address: str
    status_code: int
    duration_ms: float


class AdminUserSummary(BaseSchema):
    """Administrator user management summary."""

    id: str
    email: str
    full_name: str
    role: str
    country_code: str
    clinician_status: str
    is_active: bool
    is_synthetic: bool


class UserStatusToggleRequest(BaseSchema):
    """Toggle user active/suspended state."""

    is_active: bool


@router.get(
    "/audit-logs", response_model=list[AuditLogItemResponse], status_code=status.HTTP_200_OK
)
def query_audit_logs(
    user_id: str | None = Query(default=None),
    action_type: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("ADMINISTRATOR")),
) -> list[AuditLogItemResponse]:
    """Read-only paginated search over append-only security audit logs."""
    stmt = select(AuditLog)
    if user_id:
        stmt = stmt.where(AuditLog.user_id == user_id)
    if action_type:
        stmt = stmt.where(AuditLog.action_type == action_type)
    rows = db.scalars(stmt.order_by(AuditLog.timestamp.desc()).limit(limit).offset(offset)).all()
    return [
        AuditLogItemResponse(
            id=str(r.id),
            timestamp=cast(datetime, r.timestamp),
            user_id=str(r.user_id) if r.user_id else None,
            role=str(r.role),
            action_type=str(r.action_type),
            resource_id=str(r.resource_id) if r.resource_id else None,
            endpoint=str(r.endpoint),
            method=str(r.method),
            ip_address=str(r.ip_address),
            status_code=int(r.status_code),
            duration_ms=float(r.duration_ms),
        )
        for r in rows
    ]


@router.get("/users", response_model=list[AdminUserSummary], status_code=status.HTTP_200_OK)
def list_users(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_role("ADMINISTRATOR")),
) -> list[AdminUserSummary]:
    """List platform accounts for administrative oversight."""
    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    return [
        AdminUserSummary(
            id=str(u.id),
            email=str(u.email),
            full_name=str(u.full_name),
            role=normalize_role_name(str(u.role)),
            country_code=str(getattr(u, "country_code", "US")),
            clinician_status=str(u.clinician_status),
            is_active=bool(u.is_active),
            is_synthetic=bool(getattr(u, "is_synthetic", True)),
        )
        for u in users
    ]


@router.patch(
    "/users/{user_id}/status",
    response_model=AdminUserSummary,
    status_code=status.HTTP_200_OK,
)
def toggle_user_status(
    user_id: str,
    payload: UserStatusToggleRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_role("ADMINISTRATOR")),
) -> AdminUserSummary:
    """Suspend or reactivate a user account and append an immutable audit event."""
    user = db.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise ResourceNotFoundError("User account not found.")

    user.is_active = payload.is_active  # type: ignore[assignment]
    record_audit_event(
        db,
        actor=admin,
        action_type="USER_STATUS_UPDATED",
        resource_id=str(user.id),
        endpoint=f"/api/v1/admin/users/{user_id}/status",
        method="PATCH",
        status_code=200,
    )
    db.commit()
    db.refresh(user)
    return AdminUserSummary(
        id=str(user.id),
        email=str(user.email),
        full_name=str(user.full_name),
        role=normalize_role_name(str(user.role)),
        country_code=str(getattr(user, "country_code", "US")),
        clinician_status=str(user.clinician_status),
        is_active=bool(user.is_active),
        is_synthetic=bool(getattr(user, "is_synthetic", True)),
    )


@router.get("/models", status_code=status.HTTP_200_OK)
def get_model_registry_card(
    _admin: User = Depends(require_role("ADMINISTRATOR")),
) -> dict[str, Any]:
    """Inspect active Task A ML model card and calibration provenance."""
    if MODEL_CARD_PATH.exists():
        return cast(dict[str, Any], json.loads(MODEL_CARD_PATH.read_text(encoding="utf-8")))
    return {"status": "no_registered_model"}
