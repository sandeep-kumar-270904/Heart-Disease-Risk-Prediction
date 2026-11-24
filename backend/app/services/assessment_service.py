"""HeartXAI 2.0 - Clinical Assessment Orchestration Service (Remediation Round 01)."""

from __future__ import annotations

from datetime import datetime
from typing import cast

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AuthorizationError, ClinicalBoundaryError, ResourceNotFoundError
from app.ml.counterfactual_service import get_counterfactual_service
from app.ml.inference_service import get_inference_service
from app.ml.shap_service import get_shap_service
from app.models.assessment import (
    Assessment,
    CounterfactualProfile,
    InferenceResult,
    ShapExplanation,
)
from app.models.user import User
from app.schemas.assessment import (
    AssessmentCreateDto,
    AssessmentDetailResponse,
    FeatureImpactDto,
    ScenarioResultDto,
    ShapExplanationResponse,
)
from app.schemas.auth import ALLOWED_SYNTHETIC_DOMAINS
from app.services.audit_service import record_audit_event
from app.services.consent_service import authorize_clinician_grant


def _verify_synthetic_provenance(actor: User) -> str:
    """Verify server-side DEC-005 synthetic boundary (do not blindly trust config flag alone)."""
    if not settings.SYNTHETIC_DATA_ONLY:
        raise ClinicalBoundaryError(
            "Assessment submission is disabled because SYNTHETIC_DATA_ONLY is false."
        )
    email_domain = str(actor.email).rsplit("@", 1)[-1].lower()
    if not bool(actor.is_synthetic) or email_domain not in ALLOWED_SYNTHETIC_DOMAINS:
        raise AuthorizationError(
            "Account does not hold verified Category B synthetic persona provenance (DEC-005)."
        )
    return f"Category B — Controlled Synthetic Persona ({email_domain})"


def _assessment_to_dto(record: Assessment) -> AssessmentCreateDto:
    """Convert stored Assessment to AssessmentCreateDto without fabricating missing glucose."""
    if record.fasting_blood_sugar_mgdl is None:
        raise ClinicalBoundaryError(
            "Legacy record lacks preserved numeric fasting_blood_sugar measurement; "
            "numeric simulation cannot run without reconstructing placeholder values."
        )
    return AssessmentCreateDto(
        synthetic_fixture_confirmed=True,
        age=float(record.age),
        sex=int(record.sex),
        chest_pain_type=int(record.cp),
        unit_system="us_customary",
        resting_bp=float(record.trestbps),
        serum_cholesterol=float(record.chol),
        fasting_blood_sugar=float(record.fasting_blood_sugar_mgdl),
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
    fbs_numeric = (
        round(float(assessment.fasting_blood_sugar_mgdl), 2)
        if assessment.fasting_blood_sugar_mgdl is not None
        else None
    )
    fbs_gt_120 = bool(int(assessment.fbs) == 1)
    provenance = (
        "Category B — Verified Synthetic Persona Record"
        if bool(assessment.is_synthetic)
        else "UNVERIFIED PROVENANCE — REJECTED FROM SYNTHETIC COHORT"
    )
    summary = (
        f"Experimental Retrospective Task A Model Score: {pct:.1f}% "
        "(UCI Cleveland retrospective binary CAD classification model). "
        "Informational model output only — NOT a medical diagnosis, risk tier, or 10-year risk forecast."
    )
    return AssessmentDetailResponse(
        id=str(assessment.id),
        patient_id=str(assessment.patient_id),
        age=float(assessment.age),
        sex=int(assessment.sex),
        chest_pain_type=int(assessment.cp),
        resting_bp=float(assessment.trestbps),
        serum_cholesterol=float(assessment.chol),
        fasting_blood_sugar=fbs_numeric,
        fasting_blood_sugar_gt_120=fbs_gt_120,
        resting_ecg=int(assessment.restecg),
        max_heart_rate=float(assessment.thalach),
        exercise_angina=int(assessment.exang),
        st_depression=float(assessment.oldpeak),
        st_slope=int(assessment.slope),
        major_vessels=int(assessment.ca),
        thallium_stress=int(assessment.thal),
        cad_likelihood_percent=pct,
        risk_strata="unstratified",
        ten_year_population_risk_percent=None,  # DEC-003 Option A: Task B excluded in MVP
        model_version=str(inf.model_version),
        cohort_name="UCI Cleveland Retrospective Benchmark (N=303)",
        data_provenance=provenance,
        plain_language_summary=summary,
        emergency_warning_active=False,  # Automated clinical red-flag triage pending clinical sign-off
        created_at=cast(datetime, assessment.created_at),
    )


def create_and_score_assessment(
    db: Session,
    patient: User,
    dto: AssessmentCreateDto,
) -> AssessmentDetailResponse:
    """Persist verified synthetic intake, run Task A inference + SHAP + CF, preserve numeric FBS."""
    _verify_synthetic_provenance(patient)

    inference_svc = get_inference_service()
    shap_svc = get_shap_service()
    cf_svc = get_counterfactual_service()

    pred = inference_svc.predict(dto)
    shap_out = shap_svc.explain(dto)
    cf_out = cf_svc.generate_optimal(dto)

    imputers = inference_svc.artifact.get("training_fold_imputers", {})
    ca_val = int(dto.major_vessels) if dto.major_vessels is not None else int(imputers.get("ca", 0))
    thal_val = (
        int(dto.thallium_stress)
        if dto.thallium_stress is not None
        else int(imputers.get("thal", 1))
    )

    assessment = Assessment(
        patient_id=str(patient.id),
        status="COMPLETED",
        is_synthetic=True,
        age=int(round(dto.age)),
        sex=int(dto.sex),
        cp=int(dto.chest_pain_type),
        trestbps=int(round(dto.resting_bp)),
        chol=int(round(dto.serum_cholesterol)),
        fbs=1 if dto.fasting_blood_sugar > 120.0 else 0,
        fasting_blood_sugar_mgdl=round(float(dto.fasting_blood_sugar), 2),
        restecg=int(dto.resting_ecg),
        thalach=int(round(dto.max_heart_rate)),
        exang=int(dto.exercise_angina),
        oldpeak=float(dto.st_depression),
        slope=int(dto.st_slope),
        ca=ca_val,
        thal=thal_val,
    )
    db.add(assessment)
    db.flush()

    inf_row = InferenceResult(
        assessment_id=str(assessment.id),
        model_version=pred.model_version,
        cad_probability=pred.probability,
        cad_risk_tier=pred.db_risk_tier,
        confidence_interval_low=None,
        confidence_interval_high=None,
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

    record_audit_event(
        db,
        actor=patient,
        action_type="SYNTHETIC_ASSESSMENT_CREATED",
        resource_id=str(assessment.id),
        endpoint="/api/v1/assessments",
        method="POST",
        status_code=201,
    )
    db.commit()
    db.refresh(assessment)
    db.refresh(inf_row)
    return _inference_to_response(assessment, inf_row)


def authorize_assessment_access(
    db: Session,
    assessment_id: str,
    actor: User,
    *,
    now: datetime | None = None,
) -> Assessment:
    """Enforce owner-only or authoritative active/unrevoked/unexpired clinician consent."""
    assessment = db.scalar(select(Assessment).where(Assessment.id == assessment_id))
    if assessment is None:
        raise ResourceNotFoundError("Assessment record was not found.")

    if str(assessment.patient_id) == str(actor.id):
        return assessment

    if str(actor.role) == "CLINICIAN":
        authorize_clinician_grant(
            db,
            patient_id=str(assessment.patient_id),
            doctor=actor,
            now=now,
        )
        return assessment

    raise AuthorizationError("You are not authorized to access this assessment record.")


def get_assessment_detail(
    db: Session,
    assessment_id: str,
    actor: User,
    *,
    now: datetime | None = None,
) -> AssessmentDetailResponse:
    """Retrieve a single authorized assessment with inference results."""
    assessment = authorize_assessment_access(db, assessment_id, actor, now=now)
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


def get_assessment_shap(
    db: Session,
    assessment_id: str,
    actor: User,
    *,
    now: datetime | None = None,
) -> ShapExplanationResponse:
    """Retrieve persisted TreeSHAP local attributions for an authorized assessment."""
    assessment = authorize_assessment_access(db, assessment_id, actor, now=now)
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
    *,
    now: datetime | None = None,
) -> ScenarioResultDto:
    """Simulate a constrained counterfactual hypothetical scenario."""
    assessment = authorize_assessment_access(db, assessment_id, actor, now=now)
    baseline_dto = _assessment_to_dto(assessment)
    cf_svc = get_counterfactual_service()
    return cf_svc.simulate(
        assessment_id=str(assessment.id),
        baseline=baseline_dto,
        modified_features=modified_features,
    )
