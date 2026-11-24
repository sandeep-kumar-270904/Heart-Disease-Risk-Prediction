"""HeartXAI 2.0 - Assessments, TreeSHAP, Counterfactual Simulation & PDF Export Routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.assessment import (
    AssessmentCreateDto,
    AssessmentDetailResponse,
    ScenarioResultDto,
    ScenarioSimulationRequest,
    ShapExplanationResponse,
)
from app.services.assessment_service import (
    create_and_score_assessment,
    get_assessment_detail,
    get_assessment_shap,
    list_patient_assessments,
    simulate_assessment_scenario,
)
from app.services.export_service import generate_assessment_pdf_bytes

router = APIRouter(prefix="/assessments", tags=["Assessments & Explainability"])


@router.post(
    "",
    response_model=AssessmentDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_assessment(
    payload: AssessmentCreateDto,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AssessmentDetailResponse:
    """Create a new clinical assessment and run in-process Task A inference + SHAP + CF."""
    return create_and_score_assessment(db, current_user, payload)


@router.get("", response_model=list[AssessmentDetailResponse], status_code=status.HTTP_200_OK)
def get_my_assessments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[AssessmentDetailResponse]:
    """List all assessments owned by the authenticated patient."""
    return list_patient_assessments(db, current_user)


@router.get(
    "/{assessment_id}", response_model=AssessmentDetailResponse, status_code=status.HTTP_200_OK
)
def get_assessment(
    assessment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AssessmentDetailResponse:
    """Fetch a single authorized assessment."""
    return get_assessment_detail(db, assessment_id, current_user)


@router.get(
    "/{assessment_id}/shap",
    response_model=ShapExplanationResponse,
    status_code=status.HTTP_200_OK,
)
def get_shap_explanation(
    assessment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ShapExplanationResponse:
    """Fetch exact TreeSHAP local feature attributions for an assessment."""
    return get_assessment_shap(db, assessment_id, current_user)


@router.post(
    "/{assessment_id}/simulate",
    response_model=ScenarioResultDto,
    status_code=status.HTTP_200_OK,
)
def simulate_counterfactual(
    assessment_id: str,
    payload: ScenarioSimulationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ScenarioResultDto:
    """Run constrained 'what-if' lifestyle scenario keeping immutable attributes frozen."""
    return simulate_assessment_scenario(db, assessment_id, current_user, payload.modified_features)


@router.get("/{assessment_id}/export-pdf", status_code=status.HTTP_200_OK)
def export_assessment_pdf(
    assessment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    """Export cryptographically sealed 2-page PDF summary dossier (Task B excluded)."""
    detail = get_assessment_detail(db, assessment_id, current_user)
    shap_data = get_assessment_shap(db, assessment_id, current_user)
    pdf_bytes, sha256_hex = generate_assessment_pdf_bytes(detail, shap_data)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="heartxai_assessment_{detail.id}.pdf"',
            "X-Document-SHA256": sha256_hex,
        },
    )
