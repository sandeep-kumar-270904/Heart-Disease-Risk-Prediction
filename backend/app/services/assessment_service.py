"""HeartXAI 2.0 - Clinical Assessment Orchestration Service (Milestones 11–13)."""

from __future__ import annotations

from datetime import datetime
from typing import cast

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AuthorizationError, ResourceNotFoundError
from app.ml.counterfactual_service import get_counterfactual_service
from app.ml.inference_service import get_inference_service
from app.ml.shap_service import get_shap_service
from app.models.assessment import (
    Assessment,
    CounterfactualProfile,
    InferenceResult,
    ShapExplanation,
)
from app.models.consent import DoctorGrant
from app.models.user import User
from app.schemas.assessment import (
    AssessmentCreateDto,
    AssessmentDetailResponse,
    FeatureImpactDto,
    RiskStrata,
    ScenarioResultDto,
    ShapExplanationResponse,
)


def _assessment_to_dto(record: Assessment) -> AssessmentCreateDto:
    return AssessmentCreateDto(
        age=float(record.age),
        sex=int(record.sex),
        chest_pain_type=int(record.cp),
        unit_system="us_customary",
        resting_bp=float(record.trestbps),
        serum_cholesterol=float(record.chol),
        fasting_blood_sugar=130.0 if int(record.fbs) == 1 else 95.0,
        resting_ecg=int(record.restecg),
        max_heart_rate=float(record.thalach),
        exercise_angina=int(record.exang),
        st_depression=float(record.oldpeak),
        st_slope=int(record.slope),
        major_vessels=int(record.ca),
        thallium_stress=int(record.thal),
    )


def _inference_to_response(
    assessment: Assessment,
    inf: InferenceResult,
) -> AssessmentDetailResponse:
    pct = round(float(inf.cad_probability) * 100.0, 2)
    risk_strata: RiskStrata = "low" if pct < 30.0 else ("moderate" if pct < 70.0 else "elevated")
    emergency = bool(
        int(assessment.trestbps) > 180 or (int(assessment.cp) == 0 and int(assessment.exang) == 1)
    )
    summary = (
        f"Educational Task A Benchmark Association: {pct:.1f}% "
        f"({risk_strata} tier, UCI Cleveland retrospective cohort similarity). "
        "Informational model output only — NOT a medical diagnosis or 10-year risk forecast."
    )
    return AssessmentDetailResponse(
        id=str(assessment.id),
        patient_id=str(assessment.patient_id),
        age=float(assessment.age),
        sex=int(assessment.sex),
        chest_pain_type=int(assessment.cp),
        resting_bp=float(assessment.trestbps),
        serum_cholesterol=float(assessment.chol),
        fasting_blood_sugar=130.0 if int(assessment.fbs) == 1 else 95.0,
        resting_ecg=int(assessment.restecg),
        max_heart_rate=float(assessment.thalach),
        exercise_angina=int(assessment.exang),
        st_depression=float(assessment.oldpeak),
        st_slope=int(assessment.slope),
        major_vessels=int(assessment.ca),
        thallium_stress=int(assessment.thal),
        cad_likelihood_percent=pct,
        confidence_interval=[
            float(inf.confidence_interval_low),
            float(inf.confidence_interval_high),
        ],
        risk_strata=risk_strata,
        ten_year_population_risk_percent=None,  # DEC-003 Option A: Task B excluded in MVP
        model_version=str(inf.model_version),
        cohort_name="UCI Cleveland Retrospective Benchmark (N=303)",
        plain_language_summary=summary,
        emergency_warning_active=emergency,
        created_at=cast(datetime, assessment.created_at),
    )


def create_and_score_assessment(
    db: Session,
    patient: User,
    dto: AssessmentCreateDto,
) -> AssessmentDetailResponse:
    """Persist synthetic clinical intake, execute XGBoost + TreeSHAP + Counterfactuals."""
    inference_svc = get_inference_service()
    shap_svc = get_shap_service()
    cf_svc = get_counterfactual_service()

    pred = inference_svc.predict(dto)
    shap_out = shap_svc.explain(dto)
    cf_out = cf_svc.generate_optimal(dto)

    assessment = Assessment(
        patient_id=str(patient.id),
        status="COMPLETED",
        is_synthetic=settings.SYNTHETIC_DATA_ONLY,
        age=int(round(dto.age)),
        sex=int(dto.sex),
        cp=int(dto.chest_pain_type),
        trestbps=int(round(dto.resting_bp)),
        chol=int(round(dto.serum_cholesterol)),
        fbs=1 if dto.fasting_blood_sugar > 120.0 else 0,
        restecg=int(dto.resting_ecg),
        thalach=int(round(dto.max_heart_rate)),
        exang=int(dto.exercise_angina),
        oldpeak=float(dto.st_depression),
        slope=int(dto.st_slope),
        ca=int(dto.major_vessels if dto.major_vessels is not None else 0),
        thal=int(dto.thallium_stress if dto.thallium_stress is not None else 1),
    )
    db.add(assessment)
    db.flush()

    inf_row = InferenceResult(
        assessment_id=str(assessment.id),
        model_version=pred.model_version,
        cad_probability=pred.probability,
        cad_risk_tier=pred.db_risk_tier,
        confidence_interval_low=pred.confidence_interval[0],
        confidence_interval_high=pred.confidence_interval[1],
        ascvd_10yr_risk=None,
        ascvd_risk_tier=None,
        base_expected_value=shap_out.base_value,
        raw_decision_margin=pred.raw_margin,
        is_out_of_distribution=pred.is_out_of_distribution,
    )
    db.add(inf_row)
    db.flush()

    for rank_idx, feat in enumerate(shap_out.features, start=1):
        db.add(
            ShapExplanation(
                inference_id=str(inf_row.id),
                feature_name=feat.feature_name,
                feature_value=feat.raw_patient_value,
                shap_value=feat.shap_value,
                rank_importance=rank_idx,
                directional_impact=(
                    "RISK_INCREASING" if feat.direction == "increases_likelihood" else "PROTECTIVE"
                ),
                clinical_interpretation=feat.plain_language_explanation,
            )
        )

    db.add(
        CounterfactualProfile(
            inference_id=str(inf_row.id),
            target_risk_threshold=cf_out.target_threshold,
            achieved_risk_probability=cf_out.achieved_probability,
            modified_biomarkers=cf_out.modified_biomarkers,
            immutable_biomarkers=cf_out.immutable_biomarkers,
            l1_normalized_distance=cf_out.l1_normalized_distance,
            feasibility_rating=cf_out.feasibility_rating,
        )
    )

    db.commit()
    db.refresh(assessment)
    db.refresh(inf_row)
    return _inference_to_response(assessment, inf_row)


def authorize_assessment_access(
    db: Session,
    assessment_id: str,
    actor: User,
) -> Assessment:
    """Enforce strict Anti-IDOR ownership or active clinician consent grant verification."""
    assessment = db.scalar(select(Assessment).where(Assessment.id == assessment_id))
    if assessment is None:
        raise ResourceNotFoundError("Assessment record was not found.")

    actor_role = str(actor.role)
    if str(assessment.patient_id) == str(actor.id) or actor_role in {"ADMIN", "ADMINISTRATOR"}:
        return assessment

    if actor_role == "CLINICIAN":
        grant = db.scalar(
            select(DoctorGrant).where(
                DoctorGrant.patient_id == assessment.patient_id,
                DoctorGrant.doctor_id == actor.id,
                DoctorGrant.status == "ACTIVE",
            )
        )
        if grant is not None:
            return assessment

    raise AuthorizationError("You are not authorized to access this assessment record.")


def get_assessment_detail(db: Session, assessment_id: str, actor: User) -> AssessmentDetailResponse:
    """Retrieve a single authorized assessment with inference results."""
    assessment = authorize_assessment_access(db, assessment_id, actor)
    if assessment.inference_result is None:
        raise ResourceNotFoundError("Inference output not found for assessment.")
    return _inference_to_response(assessment, assessment.inference_result)


def list_patient_assessments(db: Session, patient: User) -> list[AssessmentDetailResponse]:
    """List chronological assessments owned strictly by the authenticated patient."""
    rows = db.scalars(
        select(Assessment)
        .where(Assessment.patient_id == str(patient.id))
        .order_by(Assessment.created_at.desc())
    ).all()
    return [
        _inference_to_response(row, row.inference_result)
        for row in rows
        if row.inference_result is not None
    ]


def get_assessment_shap(db: Session, assessment_id: str, actor: User) -> ShapExplanationResponse:
    """Retrieve persisted TreeSHAP local attributions for an authorized assessment."""
    assessment = authorize_assessment_access(db, assessment_id, actor)
    inf = assessment.inference_result
    if inf is None:
        raise ResourceNotFoundError("Inference result not found.")

    shap_svc = get_shap_service()
    art = shap_svc._inference_service.artifact
    cohort_means: dict[str, float] = art["cohort_feature_means"]

    ordered_rows = sorted(inf.shap_explanations, key=lambda r: int(r.rank_importance))
    features = [
        FeatureImpactDto(
            feature_name=str(row.feature_name),
            raw_patient_value=float(row.feature_value),
            unit="units",
            cohort_average_value=float(cohort_means.get(str(row.feature_name), 0.0)),
            shap_value=float(row.shap_value),
            direction=(
                "increases_likelihood"
                if str(row.directional_impact) == "RISK_INCREASING"
                else "decreases_likelihood"
            ),
            plain_language_explanation=str(row.clinical_interpretation),
        )
        for row in ordered_rows
    ]

    return ShapExplanationResponse(
        assessment_id=str(assessment.id),
        model_version=str(inf.model_version),
        base_value=float(inf.base_expected_value),
        final_likelihood=float(inf.raw_decision_margin),
        features=features,
    )


def simulate_assessment_scenario(
    db: Session,
    assessment_id: str,
    actor: User,
    modified_features: dict[str, float],
) -> ScenarioResultDto:
    """Simulate a constrained counterfactual lifestyle adjustment."""
    assessment = authorize_assessment_access(db, assessment_id, actor)
    baseline_dto = _assessment_to_dto(assessment)
    cf_svc = get_counterfactual_service()
    return cf_svc.simulate(
        assessment_id=str(assessment.id),
        baseline=baseline_dto,
        modified_features=modified_features,
    )
