"""HeartXAI 2.0 - Time-Bounded 72-Hour Patient Consent & Clinician Notes Service (Milestone 16)."""

from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AuthorizationError, ResourceNotFoundError
from app.models.assessment import Assessment
from app.models.consent import ClinicalNote, DoctorGrant
from app.models.user import User
from app.services.audit_service import record_audit_event

GRANT_DURATION_HOURS = 72


def create_consent_grant(
    db: Session,
    *,
    patient: User,
    doctor_id: str,
) -> DoctorGrant:
    """Issue a 72-hour cryptographic sharing grant to a verified clinician."""
    doctor = db.scalar(select(User).where(User.id == doctor_id, User.role == "CLINICIAN"))
    if doctor is None or str(doctor.clinician_status) != "VERIFIED":
        raise ResourceNotFoundError("Verified clinician account not found.")

    now = datetime.now(UTC)
    access_code = secrets.token_urlsafe(16)
    grant = DoctorGrant(
        patient_id=str(patient.id),
        doctor_id=str(doctor.id),
        access_code=access_code,
        status="ACTIVE",
        granted_at=now,
        expires_at=now + timedelta(hours=GRANT_DURATION_HOURS),
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
) -> DoctorGrant:
    """Immediately revoke a patient consent grant."""
    grant = db.scalar(select(DoctorGrant).where(DoctorGrant.id == grant_id))
    if grant is None:
        raise ResourceNotFoundError("Consent grant not found.")
    if str(grant.patient_id) != str(patient.id):
        raise AuthorizationError("Only the granting patient may revoke this consent.")

    grant.status = "REVOKED"  # type: ignore[assignment]
    grant.revoked_at = datetime.now(UTC)  # type: ignore[assignment]
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


def _is_grant_currently_valid(grant: DoctorGrant) -> bool:
    if str(grant.status) != "ACTIVE" or grant.revoked_at is not None:
        return False
    expires = grant.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=UTC)
    return expires > datetime.now(UTC)


def verify_clinician_assessment_access(
    db: Session,
    *,
    doctor: User,
    assessment_id: str,
) -> Assessment:
    """Enforce active, non-expired, non-revoked consent grant for clinician access."""
    assessment = db.scalar(select(Assessment).where(Assessment.id == assessment_id))
    if assessment is None:
        raise ResourceNotFoundError("Assessment not found.")

    grants = db.scalars(
        select(DoctorGrant).where(
            DoctorGrant.patient_id == assessment.patient_id,
            DoctorGrant.doctor_id == str(doctor.id),
        )
    ).all()

    if not any(_is_grant_currently_valid(g) for g in grants):
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
        raise AuthorizationError("Consent grant missing, expired, or revoked.")

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


def list_clinician_shared_assessments(db: Session, *, doctor: User) -> list[Assessment]:
    """Return assessments across all patients with an active, unexpired grant to doctor."""
    grants = db.scalars(select(DoctorGrant).where(DoctorGrant.doctor_id == str(doctor.id))).all()
    active_patient_ids = {str(g.patient_id) for g in grants if _is_grant_currently_valid(g)}
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
    note_content: str,
) -> ClinicalNote:
    """Append a clinician review note on a validly consented assessment."""
    assessment = verify_clinician_assessment_access(db, doctor=doctor, assessment_id=assessment_id)
    note = ClinicalNote(
        assessment_id=str(assessment.id),
        author_id=str(doctor.id),
        note_content=note_content.strip(),
        signoff_status="FINAL_SIGNOFF",
        signed_at=datetime.now(UTC),
    )
    db.add(note)
    record_audit_event(
        db,
        actor=doctor,
        action_type="CLINICAL_NOTE_ADDED",
        resource_id=str(assessment.id),
        endpoint=f"/api/v1/consents/doctor/assessments/{assessment_id}/notes",
        method="POST",
        status_code=201,
    )
    db.commit()
    db.refresh(note)
    return note
