"""HeartXAI 2.0 - Authoritative 72-Hour Patient Consent & Clinician Access Control."""

from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AuthorizationError, ClinicalBoundaryError, ResourceNotFoundError
from app.models.assessment import Assessment
from app.models.consent import ClinicalNote, DoctorGrant
from app.models.user import User
from app.services.audit_service import record_audit_event

GRANT_DURATION_HOURS = 72


def resolve_utc_now(now: datetime | None = None) -> datetime:
    """Return a timezone-aware UTC timestamp (supports deterministic test clocks)."""
    if now is None:
        return datetime.now(UTC)
    return now.replace(tzinfo=UTC) if now.tzinfo is None else now.astimezone(UTC)


def is_grant_active_at(grant: DoctorGrant, *, now: datetime | None = None) -> bool:
    """Authoritative predicate validating active, unrevoked, non-expired grant status."""
    if str(grant.status) != "ACTIVE" or grant.revoked_at is not None:
        return False
    expires = grant.expires_at
    expires = expires.replace(tzinfo=UTC) if expires.tzinfo is None else expires.astimezone(UTC)
    return expires > resolve_utc_now(now)


def authorize_clinician_grant(
    db: Session,
    *,
    patient_id: str,
    doctor: User,
    now: datetime | None = None,
) -> DoctorGrant:
    """Single authoritative clinician consent verification check across all endpoints.

    Verifies:
      1. Authenticated actor is an active VERIFIED CLINICIAN.
      2. Grant belongs to the target patient_id and authenticated doctor.id.
      3. Grant status == 'ACTIVE', revoked_at IS NULL, and expires_at > current UTC time.
    """
    if (
        str(doctor.role) != "CLINICIAN"
        or str(doctor.clinician_status) != "VERIFIED"
        or not bool(doctor.is_active)
    ):
        raise AuthorizationError("Authenticated clinician account is not verified or active.")

    grants = db.scalars(
        select(DoctorGrant).where(
            DoctorGrant.patient_id == str(patient_id),
            DoctorGrant.doctor_id == str(doctor.id),
        )
    ).all()

    for grant in grants:
        if (
            str(grant.patient_id) == str(patient_id)
            and str(grant.doctor_id) == str(doctor.id)
            and is_grant_active_at(grant, now=now)
        ):
            return grant

    raise AuthorizationError("Consent grant missing, expired, or revoked.")


def create_consent_grant(
    db: Session,
    *,
    patient: User,
    doctor_id: str,
    now: datetime | None = None,
) -> DoctorGrant:
    """Issue a 72-hour cryptographic sharing grant to a verified clinician."""
    doctor = db.scalar(select(User).where(User.id == doctor_id, User.role == "CLINICIAN"))
    if doctor is None or str(doctor.clinician_status) != "VERIFIED":
        raise ResourceNotFoundError("Verified clinician account not found.")

    current_utc = resolve_utc_now(now)
    access_code = secrets.token_urlsafe(16)
    grant = DoctorGrant(
        patient_id=str(patient.id),
        doctor_id=str(doctor.id),
        access_code=access_code,
        status="ACTIVE",
        granted_at=current_utc,
        expires_at=current_utc + timedelta(hours=GRANT_DURATION_HOURS),
    )
    db.add(grant)
    db.flush()
    record_audit_event(
        db,
        actor=patient,
        action_type="CONSENT_GRANT_CREATED",
        resource_id=str(grant.id),
        endpoint="/api/v1/consents",
        method="POST",
        status_code=201,
    )
    db.commit()
    db.refresh(grant)
    return grant


def revoke_consent_grant(
    db: Session,
    *,
    patient: User,
    grant_id: str,
    now: datetime | None = None,
) -> DoctorGrant:
    """Immediately revoke a patient consent grant."""
    grant = db.scalar(select(DoctorGrant).where(DoctorGrant.id == grant_id))
    if grant is None:
        raise ResourceNotFoundError("Consent grant not found.")
    if str(grant.patient_id) != str(patient.id):
        raise AuthorizationError("Only the granting patient may revoke this consent.")

    grant.status = "REVOKED"  # type: ignore[assignment]
    grant.revoked_at = resolve_utc_now(now)  # type: ignore[assignment]
    record_audit_event(
        db,
        actor=patient,
        action_type="CONSENT_GRANT_REVOKED",
        resource_id=str(grant.id),
        endpoint=f"/api/v1/consents/{grant_id}/revoke",
        method="POST",
        status_code=200,
    )
    db.commit()
    db.refresh(grant)
    return grant


def verify_clinician_assessment_access(
    db: Session,
    *,
    doctor: User,
    assessment_id: str,
    now: datetime | None = None,
) -> Assessment:
    """Enforce active, non-expired, non-revoked consent grant for clinician access."""
    assessment = db.scalar(select(Assessment).where(Assessment.id == assessment_id))
    if assessment is None:
        raise ResourceNotFoundError("Assessment not found.")

    try:
        authorize_clinician_grant(
            db,
            patient_id=str(assessment.patient_id),
            doctor=doctor,
            now=now,
        )
    except AuthorizationError:
        record_audit_event(
            db,
            actor=doctor,
            action_type="CLINICIAN_ACCESS_DENIED",
            resource_id=assessment_id,
            endpoint=f"/api/v1/consents/doctor/assessments/{assessment_id}",
            method="GET",
            status_code=403,
        )
        db.commit()
        raise

    record_audit_event(
        db,
        actor=doctor,
        action_type="CLINICIAN_ASSESSMENT_VIEWED",
        resource_id=assessment_id,
        endpoint=f"/api/v1/consents/doctor/assessments/{assessment_id}",
        method="GET",
        status_code=200,
    )
    db.commit()
    return assessment


def list_clinician_shared_assessments(
    db: Session,
    *,
    doctor: User,
    now: datetime | None = None,
) -> list[Assessment]:
    """Return assessments across patients with an active, unexpired grant to doctor."""
    if (
        str(doctor.role) != "CLINICIAN"
        or str(doctor.clinician_status) != "VERIFIED"
        or not bool(doctor.is_active)
    ):
        raise AuthorizationError("Authenticated clinician account is not verified or active.")

    grants = db.scalars(select(DoctorGrant).where(DoctorGrant.doctor_id == str(doctor.id))).all()
    active_patient_ids = {str(g.patient_id) for g in grants if is_grant_active_at(g, now=now)}
    if not active_patient_ids:
        return []
    return list(
        db.scalars(
            select(Assessment)
            .where(Assessment.patient_id.in_(active_patient_ids))
            .order_by(Assessment.created_at.desc())
        ).all()
    )


def add_clinician_note(
    db: Session,
    *,
    doctor: User,
    assessment_id: str,
    note_content: str,  # noqa: ARG001
    now: datetime | None = None,
) -> ClinicalNote:
    """Disabled in synthetic-only MVP (DEC-005): prevents arbitrary free-text PHI entry."""
    # Still validate authoritative consent before reporting feature status
    verify_clinician_assessment_access(db, doctor=doctor, assessment_id=assessment_id, now=now)
    record_audit_event(
        db,
        actor=doctor,
        action_type="CLINICAL_NOTE_BLOCKED_DEC005",
        resource_id=assessment_id,
        endpoint=f"/api/v1/consents/doctor/assessments/{assessment_id}/notes",
        method="POST",
        status_code=422,
    )
    db.commit()
    raise ClinicalBoundaryError(
        "Arbitrary clinician free-text notes are disabled in the synthetic-only MVP "
        "to enforce Category C real-PHI prohibition (DEC-005)."
    )
