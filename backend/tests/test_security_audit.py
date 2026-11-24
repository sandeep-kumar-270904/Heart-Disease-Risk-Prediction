"""Milestone 18 Security Audit: Cross-Tenant Anti-IDOR Verification Across All Patient Routes."""

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.core.redis_client import get_token_store
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.user import User
from tests.test_auth import InMemoryTokenStore


def test_anti_idor_cross_tenant_isolation(db_session, sample_patient, sample_doctor) -> None:
    """Verify Patient B cannot access, simulate, export, or revoke Patient A's records."""
    patient_b = User(
        email="patient.intruder@example.com",
        hashed_password=hash_password("IntruderPass!2026"),
        full_name="Patient B",
        role="PATIENT",
        country_code="US",
        clinician_status="N/A",
        is_synthetic=True,
    )
    db_session.add(patient_b)
    db_session.commit()
    db_session.refresh(patient_b)

    store = InMemoryTokenStore()
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_token_store] = lambda: store

    try:
        client = TestClient(app)
        headers_a = {"Authorization": f"Bearer {create_access_token(sample_patient.id, 'PATIENT')}"}
        headers_b = {"Authorization": f"Bearer {create_access_token(patient_b.id, 'PATIENT')}"}

        # Patient A creates an assessment and a consent grant
        assess_resp = client.post(
            "/api/v1/assessments",
            json={
                "synthetic_fixture_confirmed": True,
                "age": 54,
                "sex": 1,
                "chest_pain_type": 2,
                "unit_system": "us_customary",
                "resting_bp": 135,
                "serum_cholesterol": 225,
                "fasting_blood_sugar": 95,
                "resting_ecg": 0,
                "max_heart_rate": 152,
                "exercise_angina": 0,
                "st_depression": 1.1,
                "st_slope": 0,
                "major_vessels": 0,
                "thallium_stress": 1,
            },
            headers=headers_a,
        )
        assert assess_resp.status_code == 201
        assessment_id = assess_resp.json()["id"]

        grant_resp = client.post(
            "/api/v1/consents",
            json={"doctor_id": sample_doctor.id},
            headers=headers_a,
        )
        assert grant_resp.status_code == 201
        grant_id = grant_resp.json()["id"]

        # Patient B's own list must never return Patient A's records
        list_b = client.get("/api/v1/assessments", headers=headers_b)
        assert list_b.status_code == 200
        assert list_b.json() == []

        # Patient B targeting Patient A's assessment IDs MUST receive 403 Forbidden everywhere
        assert (
            client.get(f"/api/v1/assessments/{assessment_id}", headers=headers_b).status_code == 403
        )
        assert (
            client.get(f"/api/v1/assessments/{assessment_id}/shap", headers=headers_b).status_code
            == 403
        )
        assert (
            client.post(
                f"/api/v1/assessments/{assessment_id}/simulate",
                json={"modified_features": {"resting_bp": 120}},
                headers=headers_b,
            ).status_code
            == 403
        )
        assert (
            client.get(
                f"/api/v1/assessments/{assessment_id}/export-pdf", headers=headers_b
            ).status_code
            == 403
        )
        assert (
            client.post(f"/api/v1/consents/{grant_id}/revoke", headers=headers_b).status_code == 403
        )
    finally:
        app.dependency_overrides.clear()
