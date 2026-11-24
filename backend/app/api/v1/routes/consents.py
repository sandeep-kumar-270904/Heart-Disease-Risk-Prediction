"""HeartXAI 2.0 - Patient Consent Grants & Clinician Portal Routes (Milestone 16)."""

from __future__ import annotations

from datetime import datetime
from typing import cast

from fastapi import APIRouter, Depends, status
from pydantic import Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.v1.deps import require_role
from app.core.database import get_db
from app.models.consent import DoctorGrant
from app.models.user import User
from app.schemas.assessment import AssessmentDetailResponse
from app.schemas.base import BaseSchema
from app.services.assessment_service import _inference_to_response
from app.services.consent_service import (
    add_clinician_note,
    create_consent_grant,
    list_clinician_shared_assessments,
    revoke_consent_grant,
    verify_clinician_assessment_access,
)

router = APIRouter(prefix="/consents", tags=["Patient Consents & Clinician Portal"])


class ConsentGrantCreateRequest(BaseSchema):
    """Request to grant 72-hour assessment access to a verified clinician."""

    doctor_id: str = Field(..., min_length=1)


class ConsentGrantResponse(BaseSchema):
    """Consent grant summary."""

    id: str
    patient_id: str
    doctor_id: str
    access_code: str | None = None
    status: str
    granted_at: datetime
    expires_at: datetime
    revoked_at: datetime | None = None


class ClinicalNoteCreateRequest(BaseSchema):
    """Clinician note submission payload."""

    note_content: str = Field(..., min_length=3, max_length=4000)


class ClinicalNoteResponse(BaseSchema):
    """Persisted clinician note response."""

    id: str
    assessment_id: str
    author_id: str
    note_content: str
    signoff_status: str
    signed_at: datetime | None = None


def _to_grant_response(grant: DoctorGrant) -> ConsentGrantResponse:
    return ConsentGrantResponse(
        id=str(grant.id),
        patient_id=str(grant.patient_id),
        doctor_id=str(grant.doctor_id),
        access_code=str(grant.access_code) if grant.access_code else None,
        status=str(grant.status),
        granted_at=cast(datetime, grant.granted_at),
        expires_at=cast(datetime, grant.expires_at),
        revoked_at=cast(datetime | None, grant.revoked_at),
    )


@router.post("", response_model=ConsentGrantResponse, status_code=status.HTTP_201_CREATED)
def issue_grant(
    payload: ConsentGrantCreateRequest,
    db: Session = Depends(get_db),
    patient: User = Depends(require_role("PATIENT")),
) -> ConsentGrantResponse:
    """Patient creates a 72-hour cryptographic sharing grant for a verified clinician."""
    grant = create_consent_grant(db, patient=patient, doctor_id=payload.doctor_id)
    return _to_grant_response(grant)


@router.get("", response_model=list[ConsentGrantResponse], status_code=status.HTTP_200_OK)
def list_my_grants(
    db: Session = Depends(get_db),
    patient: User = Depends(require_role("PATIENT")),
) -> list[ConsentGrantResponse]:
    """List consent grants created by the authenticated patient."""
    grants = db.scalars(
        select(DoctorGrant)
        .where(DoctorGrant.patient_id == str(patient.id))
        .order_by(DoctorGrant.granted_at.desc())
    ).all()
    return [_to_grant_response(g) for g in grants]


@router.post(
    "/{grant_id}/revoke",
    response_model=ConsentGrantResponse,
    status_code=status.HTTP_200_OK,
)
def revoke_grant(
    grant_id: str,
    db: Session = Depends(get_db),
    patient: User = Depends(require_role("PATIENT")),
) -> ConsentGrantResponse:
    """Patient immediately revokes a previously issued clinician grant."""
    grant = revoke_consent_grant(db, patient=patient, grant_id=grant_id)
    return _to_grant_response(grant)


@router.get(
    "/doctor/shared",
    response_model=list[AssessmentDetailResponse],
    status_code=status.HTTP_200_OK,
)
def doctor_list_shared_assessments(
    db: Session = Depends(get_db),
    doctor: User = Depends(require_role("CLINICIAN")),
) -> list[AssessmentDetailResponse]:
    """Clinician lists assessments covered by active, unexpired patient consent grants."""
    rows = list_clinician_shared_assessments(db, doctor=doctor)
    return [
        _inference_to_response(row, row.inference_result)
        for row in rows
        if row.inference_result is not None
    ]


@router.get(
    "/doctor/assessments/{assessment_id}",
    response_model=AssessmentDetailResponse,
    status_code=status.HTTP_200_OK,
)
def doctor_view_assessment(
    assessment_id: str,
    db: Session = Depends(get_db),
    doctor: User = Depends(require_role("CLINICIAN")),
) -> AssessmentDetailResponse:
    """Clinician views an assessment if and only if an active, unexpired grant exists."""
    row = verify_clinician_assessment_access(db, doctor=doctor, assessment_id=assessment_id)
    assert row.inference_result is not None
    return _inference_to_response(row, row.inference_result)


@router.post(
    "/doctor/assessments/{assessment_id}/notes",
    response_model=ClinicalNoteResponse,
    status_code=status.HTTP_201_CREATED,
)
def doctor_add_note(
    assessment_id: str,
    payload: ClinicalNoteCreateRequest,
    db: Session = Depends(get_db),
    doctor: User = Depends(require_role("CLINICIAN")),
) -> ClinicalNoteResponse:
    """Disabled in synthetic-only MVP (DEC-005): blocks arbitrary free-text clinical notes."""
    note = add_clinician_note(
        db,
        doctor=doctor,
        assessment_id=assessment_id,
        note_content=payload.note_content,
    )
    return ClinicalNoteResponse(
        id=str(note.id),
        assessment_id=str(note.assessment_id),
        author_id=str(note.author_id),
        note_content=str(note.note_content),
        signoff_status=str(note.signoff_status),
        signed_at=cast(datetime | None, note.signed_at),
    )
