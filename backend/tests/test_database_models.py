"""HeartXAI 2.0 - Database Models & Relational Integrity Unit Tests.

Verifies table creation, CRUD operations, foreign key cascades, and unique constraints.
"""

from datetime import datetime, timedelta, timezone, date
import pytest
from sqlalchemy.exc import IntegrityError

from app.models.user import User, PatientProfile
from app.models.assessment import Assessment, InferenceResult, ShapExplanation, CounterfactualProfile
from app.models.consent import DoctorGrant, ClinicalNote
from app.models.directory import Doctor, Hospital, InsurancePolicy, EducationalResource
from app.models.audit import AuditLog, ModelRegistry


def test_user_creation_and_unique_email(db_session, sample_patient):
    """Verify user persistence and unique constraint on email."""
    assert sample_patient.id is not None
    assert sample_patient.email == "patient.marcus@example.com"
    assert sample_patient.role == "PATIENT"

    # Attempt duplicate email insert
    duplicate = User(
        email="patient.marcus@example.com",
        hashed_password="DifferentHash",
        full_name="Impostor",
        role="PATIENT",
    )
    db_session.add(duplicate)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_patient_profile_relationship(db_session, sample_patient):
    """Verify 1:1 PatientProfile relationship with User."""
    profile = PatientProfile(
        patient_id=sample_patient.id,
        date_of_birth=date(1972, 5, 14),
        biological_sex="MALE",
        preferred_units="US_STANDARD",
        emergency_contact_name="Sarah Vance",
        emergency_contact_phone="+1-555-0192",
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(sample_patient)

    assert sample_patient.profile is not None
    assert sample_patient.profile.biological_sex == "MALE"
    assert sample_patient.profile.date_of_birth == date(1972, 5, 14)


def test_assessment_intake_and_relationships(db_session, sample_patient):
    """Verify full 13-biomarker assessment persistence and child records."""
    assessment = Assessment(
        patient_id=sample_patient.id,
        status="COMPLETED",
        age=54,
        sex=1,
        cp=2,
        trestbps=158,
        chol=248,
        fbs=0,
        restecg=0,
        thalach=164,
        exang=0,
        oldpeak=1.2,
        slope=0,
        ca=0,
        thal=1,
    )
    db_session.add(assessment)
    db_session.commit()
    db_session.refresh(assessment)

    assert assessment.id is not None
    assert assessment.trestbps == 158
    assert assessment.patient.email == sample_patient.email

    # Add InferenceResult
    inference = InferenceResult(
        assessment_id=assessment.id,
        model_version="v2.0.0",
        cad_probability=0.44,
        cad_risk_tier="BORDERLINE",
        confidence_interval_low=0.39,
        confidence_interval_high=0.49,
        ascvd_10yr_risk=9.8,
        ascvd_risk_tier="BORDERLINE",
        base_expected_value=-0.12,
        raw_decision_margin=0.35,
        is_out_of_distribution=False,
    )
    db_session.add(inference)
    db_session.commit()
    db_session.refresh(assessment)

    assert assessment.inference_result is not None
    assert assessment.inference_result.cad_probability == 0.44

    # Add SHAP explanations
    shap_bp = ShapExplanation(
        inference_id=inference.id,
        feature_name="trestbps",
        feature_value=158.0,
        shap_value=0.42,
        rank_importance=1,
        directional_impact="RISK_INCREASING",
        clinical_interpretation="Resting blood pressure (158 mm Hg) increased risk significantly.",
    )
    shap_hr = ShapExplanation(
        inference_id=inference.id,
        feature_name="thalach",
        feature_value=164.0,
        shap_value=-0.31,
        rank_importance=2,
        directional_impact="PROTECTIVE",
        clinical_interpretation="High exercise heart rate capacity provided protective benefit.",
    )
    db_session.add_all([shap_bp, shap_hr])

    # Add Counterfactual Profile
    cf = CounterfactualProfile(
        inference_id=inference.id,
        target_risk_threshold=0.20,
        achieved_risk_probability=0.21,
        modified_biomarkers={"trestbps": 125, "chol": 190},
        immutable_biomarkers={"age": 54, "sex": 1, "ca": 0, "thal": 1},
        l1_normalized_distance=1.45,
        feasibility_rating="MODERATE",
    )
    db_session.add(cf)
    db_session.commit()

    db_session.refresh(inference)
    assert len(inference.shap_explanations) == 2
    assert len(inference.counterfactual_profiles) == 1
    assert inference.counterfactual_profiles[0].modified_biomarkers["trestbps"] == 125


def test_cascading_deletion(db_session, sample_patient):
    """Verify that deleting a User cascades to purge all profiles, assessments, inferences, and SHAP rows."""
    assessment = Assessment(
        patient_id=sample_patient.id,
        status="COMPLETED",
        age=54, sex=1, cp=0, trestbps=130, chol=200, fbs=0,
        restecg=0, thalach=150, exang=0, oldpeak=0.0, slope=0, ca=0, thal=1,
    )
    db_session.add(assessment)
    db_session.commit()

    inference = InferenceResult(
        assessment_id=assessment.id,
        model_version="v2.0.0",
        cad_probability=0.15,
        cad_risk_tier="LOW",
        confidence_interval_low=0.10,
        confidence_interval_high=0.20,
        ascvd_10yr_risk=3.2,
        ascvd_risk_tier="LOW",
        base_expected_value=-0.2,
        raw_decision_margin=-1.1,
    )
    db_session.add(inference)
    db_session.commit()

    shap_row = ShapExplanation(
        inference_id=inference.id,
        feature_name="age",
        feature_value=54.0,
        shap_value=0.1,
        rank_importance=1,
        directional_impact="RISK_INCREASING",
        clinical_interpretation="Age factor",
    )
    db_session.add(shap_row)
    db_session.commit()

    # Assert records exist
    assert db_session.query(Assessment).count() == 1
    assert db_session.query(InferenceResult).count() == 1
    assert db_session.query(ShapExplanation).count() == 1

    # Delete Patient User
    db_session.delete(sample_patient)
    db_session.commit()

    # Verify complete cascade erasure (GDPR Right to Erasure)
    assert db_session.query(Assessment).count() == 0
    assert db_session.query(InferenceResult).count() == 0
    assert db_session.query(ShapExplanation).count() == 0


def test_doctor_grant_and_clinical_notes(db_session, sample_patient, sample_doctor):
    """Verify time-bounded doctor authorization grant and clinical notes."""
    expires_at = datetime.now(timezone.utc) + timedelta(days=14)
    grant = DoctorGrant(
        patient_id=sample_patient.id,
        doctor_id=sample_doctor.id,
        status="ACTIVE",
        expires_at=expires_at,
    )
    db_session.add(grant)
    db_session.commit()

    assert grant.id is not None
    assert grant.status == "ACTIVE"
    assert grant.patient.email == sample_patient.email
    assert grant.doctor.email == sample_doctor.email

    # Doctor attaches clinical note to an assessment
    assessment = Assessment(
        patient_id=sample_patient.id,
        status="COMPLETED",
        age=54, sex=1, cp=1, trestbps=140, chol=210, fbs=0,
        restecg=0, thalach=160, exang=0, oldpeak=0.5, slope=0, ca=0, thal=1,
    )
    db_session.add(assessment)
    db_session.commit()

    note = ClinicalNote(
        assessment_id=assessment.id,
        author_id=sample_doctor.id,
        note_content="Patient advised on 30 min daily aerobic walking and low sodium intake.",
        signoff_status="FINAL_SIGNOFF",
        signed_at=datetime.now(timezone.utc),
    )
    db_session.add(note)
    db_session.commit()

    assert note.id is not None
    assert note.author.full_name == "Dr. Sarah Lin, MD"
    assert assessment.clinical_notes[0].note_content.startswith("Patient advised")


def test_directory_models_crud(db_session):
    """Verify Doctor, Hospital, InsurancePolicy, and EducationalResource models."""
    doc = Doctor(
        doctor_name="Dr. Sarah Lin, MD",
        specialization="Preventative Cardiology",
        hospital_name="Bay Area Cardiac Institute",
        contact_number="+1-415-555-0144",
        location="San Francisco, CA",
        email="clinician@example.com",
    )
    hosp = Hospital(
        hospital_name="UCSF Medical Center",
        facility_type="Comprehensive Cardiac Center",
        emergency_phone="+1-415-555-9999",
        address="505 Parnassus Ave",
        city="San Francisco",
        state="CA",
        accreditation_details="ACC Chest Pain Center",
    )
    policy = InsurancePolicy(
        provider_name="Blue Cross Blue Shield",
        policy_name="Standard Preventative Health",
        coverage_summary="100% covered annual lipid panel and BP check under ACA 2713.",
        monthly_premium_est=320.0,
        waiting_period_days=0,
        exclusions_summary="Non-emergency experimental therapies excluded.",
    )
    edu = EducationalResource(
        title="Hypertension Management",
        biomarker_code="trestbps",
        summary="Clinical overview of systolic arterial pressure.",
        guideline_source="2019 ACC/AHA Prevention Guidelines",
        diet_plan_summary="DASH Dietary Pattern (< 2,300 mg daily sodium)",
        exercise_tips_summary="150 min/week moderate aerobic activity",
        lifestyle_guidance="Limit alcohol and manage stress.",
    )
    db_session.add_all([doc, hosp, policy, edu])
    db_session.commit()

    assert db_session.query(Doctor).count() == 1
    assert db_session.query(Hospital).count() == 1
    assert db_session.query(InsurancePolicy).count() == 1
    assert db_session.query(EducationalResource).count() == 1


def test_audit_log_and_model_registry(db_session):
    """Verify audit log append and model registry tracking."""
    audit = AuditLog(
        role="PATIENT",
        action_type="ASSESSMENT_SUBMITTED",
        endpoint="/api/v1/assessments",
        method="POST",
        ip_address="192.168.1.100",
        status_code=201,
        duration_ms=45.2,
    )
    registry = ModelRegistry(
        version="v2.0.0",
        algorithm="Calibrated XGBoost + HistGradient",
        training_cohort="UCI Cleveland N=297",
        test_auroc=0.872,
        brier_score=0.118,
        sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    )
    db_session.add_all([audit, registry])
    db_session.commit()

    assert db_session.query(AuditLog).count() == 1
    assert db_session.query(ModelRegistry).filter_by(version="v2.0.0").first().test_auroc == 0.872
