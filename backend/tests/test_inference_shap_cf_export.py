"""Milestone 11–14 Tests: In-Process ML Inference, TreeSHAP Axioms, Counterfactuals & PDF Export."""

import time

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.core.redis_client import get_token_store
from app.core.security import create_access_token
from app.main import app
from app.ml.counterfactual_service import IMMUTABLE_FIELDS, get_counterfactual_service
from app.ml.inference_service import get_inference_service
from app.ml.shap_service import get_shap_service
from app.schemas.assessment import AssessmentCreateDto
from tests.test_auth import InMemoryTokenStore


def _sample_dto(resting_bp: float = 158.0) -> AssessmentCreateDto:
    return AssessmentCreateDto(
        age=57.0,
        sex=1,
        chest_pain_type=3,
        unit_system="us_customary",
        resting_bp=resting_bp,
        serum_cholesterol=268.0,
        fasting_blood_sugar=135.0,
        resting_ecg=2,
        max_heart_rate=138.0,
        exercise_angina=1,
        st_depression=2.2,
        st_slope=1,
        major_vessels=2,
        thallium_stress=3,
    )


def test_inference_latency_and_probability_bounds() -> None:
    """Milestone 11: Verify sub-20ms p95 latency and strictly bounded [0, 1] outputs."""
    svc = get_inference_service()
    dto = _sample_dto()

    # Warmup call
    svc.predict(dto)

    latencies_ms: list[float] = []
    for _ in range(100):
        t0 = time.perf_counter()
        out = svc.predict(dto)
        latencies_ms.append((time.perf_counter() - t0) * 1000.0)
        assert 0.0 <= out.probability <= 1.0
        assert "NOT a medical diagnosis" in out.plain_language_summary

    latencies_ms.sort()
    p95_ms = latencies_ms[94]
    assert p95_ms < 20.0


def test_treeshap_efficiency_axiom() -> None:
    """Milestone 12: Verify sum(phi_i) + expected_value == raw_margin within 1e-4."""
    dto = _sample_dto()
    inf_out = get_inference_service().predict(dto)
    shap_out = get_shap_service().explain(dto)

    assert len(shap_out.features) == 13
    sum_shap = sum(item.shap_value for item in shap_out.features)
    reconstructed = shap_out.base_value + sum_shap
    assert abs(reconstructed - inf_out.raw_margin) < 1e-3
    assert all(
        "not biological causation" in f.plain_language_explanation for f in shap_out.features
    )


def test_counterfactual_immutability_and_physiological_floors() -> None:
    """Milestone 13: Verify immutable locking and physiological clamp enforcement."""
    cf_svc = get_counterfactual_service()
    dto = _sample_dto()

    # Optimal search must never modify immutable attributes
    optimal = cf_svc.generate_optimal(dto)
    for imm in IMMUTABLE_FIELDS:
        assert optimal.immutable_biomarkers[imm] == getattr(dto, imm)

    # Attempting to mutate age must trip clamp violation
    age_attempt = cf_svc.simulate("test-id", dto, {"age": 30.0})
    assert age_attempt.is_biological_clamp_violated is True

    # Attempting resting_bp below 90 mmHg floor must trip clamp violation
    bp_floor_violation = cf_svc.simulate("test-id", dto, {"resting_bp": 65.0})
    assert bp_floor_violation.is_biological_clamp_violated is True

    # Attempting serum_cholesterol below 120 mg/dL floor must trip clamp violation
    chol_floor_violation = cf_svc.simulate("test-id", dto, {"serum_cholesterol": 85.0})
    assert chol_floor_violation.is_biological_clamp_violated is True

    # Valid exploratory modification succeeds
    valid_sim = cf_svc.simulate("test-id", dto, {"resting_bp": 118.0, "serum_cholesterol": 175.0})
    assert valid_sim.is_biological_clamp_violated is False
    assert 0.0 <= valid_sim.feasibility_score <= 1.0


def test_end_to_end_assessment_shap_cf_and_pdf_export_api(db_session, sample_patient) -> None:
    """Milestone 11–14 API: Submit, inspect SHAP, simulate CF, and download sealed PDF."""
    store = InMemoryTokenStore()
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_token_store] = lambda: store

    try:
        client = TestClient(app)
        token = create_access_token(subject=sample_patient.id, role="PATIENT")
        headers = {"Authorization": f"Bearer {token}"}

        # 1. POST /api/v1/assessments
        payload = _sample_dto(resting_bp=188.0).model_dump()
        create_resp = client.post("/api/v1/assessments", json=payload, headers=headers)
        assert create_resp.status_code == 201
        detail = create_resp.json()
        assessment_id = detail["id"]
        assert detail["ten_year_population_risk_percent"] is None  # DEC-003 Option A
        assert detail["emergency_warning_active"] is True
        assert 0.0 <= detail["cad_likelihood_percent"] <= 100.0

        # 2. GET /api/v1/assessments/{id}/shap
        shap_resp = client.get(f"/api/v1/assessments/{assessment_id}/shap", headers=headers)
        assert shap_resp.status_code == 200
        assert len(shap_resp.json()["features"]) == 13

        # 3. POST /api/v1/assessments/{id}/simulate
        sim_resp = client.post(
            f"/api/v1/assessments/{assessment_id}/simulate",
            json={"modified_features": {"resting_bp": 120.0, "serum_cholesterol": 180.0}},
            headers=headers,
        )
        assert sim_resp.status_code == 200
        assert sim_resp.json()["is_biological_clamp_violated"] is False

        # 4. GET /api/v1/assessments/{id}/export-pdf
        pdf_resp = client.get(f"/api/v1/assessments/{assessment_id}/export-pdf", headers=headers)
        assert pdf_resp.status_code == 200
        assert pdf_resp.headers["content-type"] == "application/pdf"
        assert len(pdf_resp.headers["x-document-sha256"]) == 64
        assert pdf_resp.content.startswith(b"%PDF-")
    finally:
        app.dependency_overrides.clear()
