"""Milestone 15–17 Tests: Directory Filtering, 72h Consent Portal & Immutable Admin Audit."""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.core.redis_client import get_token_store
from app.core.security import create_access_token
from app.main import app
from app.models.assessment import Assessment, InferenceResult
from app.models.consent import DoctorGrant
from app.models.directory import Doctor, Hospital
from tests.test_auth import InMemoryTokenStore


def _create_sample_assessment(db_session, patient_id: str) -> Assessment:
    a = Assessment(
        patient_id=patient_id,
        status="COMPLETED",
        is_synthetic=True,
        age=55,
        sex=1,
        cp=2,
        trestbps=140,
        chol=230,
        fbs=0,
        restecg=0,
        thalach=155,
        exang=0,
        oldpeak=1.0,
        slope=0,
        ca=0,
        thal=1,
    )
    db_session.add(a)
    db_session.flush()
    db_session.add(
        InferenceResult(
            assessment_id=a.id,
            model_version="v2.0.0",
            cad_probability=0.35,
            cad_risk_tier="BORDERLINE",
            confidence_interval_low=28.5,
            confidence_interval_high=41.5,
            ascvd_10yr_risk=None,
            ascvd_risk_tier=None,
            base_expected_value=-0.15,
            raw_decision_margin=-0.6,
        )
    )
    db_session.commit()
    return a


def test_directory_filtering_and_countries(db_session) -> None:
    """Milestone 15: Verify multi-country filtering and local directory search."""
    db_session.add_all(
        [
            Doctor(
                doctor_name="Dr. US Cardio",
                specialization="Preventative Cardiology",
                hospital_name="Boston Heart",
                contact_number="+1-555-0100",
                location="Boston, MA",
                country_code="US",
            ),
            Doctor(
                doctor_name="Dr. IN Cardio",
                specialization="Interventional Cardiology",
                hospital_name="Delhi Cardiac",
                contact_number="+91-11-5550-0100",
                location="New Delhi",
                country_code="IN",
            ),
        ]
    )
    db_session.add(
        Hospital(
            hospital_name="Thames Heart Center",
            facility_type="Cardiac Center",
            emergency_phone="999",
            address="10 Demo Sq",
            city="London",
            state="GL",
            country_code="GB",
            accreditation_details="Synthetic Demo",
        )
    )
    db_session.commit()

    app.dependency_overrides[get_db] = lambda: db_session
    try:
        client = TestClient(app)
        countries = client.get("/api/v1/directory/countries")
        assert countries.status_code == 200
        assert len(countries.json()["profiles"]) == 4

        in_docs = client.get("/api/v1/directory/doctors?country_code=IN")
        assert in_docs.status_code == 200
        assert len(in_docs.json()) == 1
        assert in_docs.json()[0]["full_name"] == "Dr. IN Cardio"

        gb_hosp = client.get("/api/v1/directory/hospitals?country_code=GB")
        assert gb_hosp.status_code == 200
        assert gb_hosp.json()[0]["emergency_phone"] == "999"
    finally:
        app.dependency_overrides.clear()


def test_consent_lifecycle_expiry_and_revocation_403(
    db_session, sample_patient, sample_doctor
) -> None:
    """Milestone 16: Verify 72h grants, clinician notes, expiry 403, and instant revocation 403."""
    assessment = _create_sample_assessment(db_session, sample_patient.id)
    store = InMemoryTokenStore()
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_token_store] = lambda: store

    try:
        client = TestClient(app)
        patient_headers = {
            "Authorization": f"Bearer {create_access_token(sample_patient.id, 'PATIENT')}"
        }
        doctor_headers = {
            "Authorization": f"Bearer {create_access_token(sample_doctor.id, 'CLINICIAN')}"
        }

        # Before grant: clinician access must return 403 Forbidden
        pre_grant = client.get(
            f"/api/v1/consents/doctor/assessments/{assessment.id}", headers=doctor_headers
        )
        assert pre_grant.status_code == 403

        # Patient creates 72-hour grant
        grant_resp = client.post(
            "/api/v1/consents",
            json={"doctor_id": sample_doctor.id},
            headers=patient_headers,
        )
        assert grant_resp.status_code == 201
        grant_id = grant_resp.json()["id"]

        # Clinician can now list shared assessment and append clinical note
        shared = client.get("/api/v1/consents/doctor/shared", headers=doctor_headers)
        assert shared.status_code == 200
        assert len(shared.json()) == 1

        note_resp = client.post(
            f"/api/v1/consents/doctor/assessments/{assessment.id}/notes",
            json={"note_content": "Recommend repeating fasting lipid panel in 3 months."},
            headers=doctor_headers,
        )
        assert note_resp.status_code == 201

        # Patient revokes grant -> clinician IMMEDIATELY receives 403
        rev_resp = client.post(f"/api/v1/consents/{grant_id}/revoke", headers=patient_headers)
        assert rev_resp.status_code == 200
        assert rev_resp.json()["status"] == "REVOKED"

        post_revoke = client.get(
            f"/api/v1/consents/doctor/assessments/{assessment.id}", headers=doctor_headers
        )
        assert post_revoke.status_code == 403

        # Expired grant also returns 403
        expired_grant = DoctorGrant(
            patient_id=sample_patient.id,
            doctor_id=sample_doctor.id,
            status="ACTIVE",
            granted_at=datetime.now(UTC) - timedelta(hours=80),
            expires_at=datetime.now(UTC) - timedelta(hours=8),
        )
        db_session.add(expired_grant)
        db_session.commit()

        post_expiry = client.get(
            f"/api/v1/consents/doctor/assessments/{assessment.id}", headers=doctor_headers
        )
        assert post_expiry.status_code == 403
    finally:
        app.dependency_overrides.clear()


def test_admin_console_rbac_and_append_only_audit(
    db_session, sample_patient, sample_doctor, sample_admin
) -> None:
    """Milestone 17: Enforce ADMIN-only RBAC and verify audit logs cannot be modified/deleted."""
    store = InMemoryTokenStore()
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_token_store] = lambda: store

    try:
        client = TestClient(app)
        patient_headers = {
            "Authorization": f"Bearer {create_access_token(sample_patient.id, 'PATIENT')}"
        }
        doctor_headers = {
            "Authorization": f"Bearer {create_access_token(sample_doctor.id, 'CLINICIAN')}"
        }
        admin_headers = {
            "Authorization": f"Bearer {create_access_token(sample_admin.id, 'ADMINISTRATOR')}"
        }

        # Non-admins strictly rejected with 403 Forbidden
        assert client.get("/api/v1/admin/audit-logs", headers=patient_headers).status_code == 403
        assert client.get("/api/v1/admin/users", headers=doctor_headers).status_code == 403

        # Admin can toggle user status, generating an audit log entry
        toggle = client.patch(
            f"/api/v1/admin/users/{sample_patient.id}/status",
            json={"is_active": False},
            headers=admin_headers,
        )
        assert toggle.status_code == 200
        assert toggle.json()["is_active"] is False

        logs = client.get("/api/v1/admin/audit-logs", headers=admin_headers)
        assert logs.status_code == 200
        assert any(row["action_type"] == "USER_STATUS_UPDATED" for row in logs.json())

        # Audit logs have zero DELETE/PATCH/PUT modification routes (405 Method Not Allowed)
        assert client.delete("/api/v1/admin/audit-logs", headers=admin_headers).status_code == 405
        assert client.put("/api/v1/admin/audit-logs", headers=admin_headers).status_code == 405

        models_resp = client.get("/api/v1/admin/models", headers=admin_headers)
        assert models_resp.status_code == 200
        assert models_resp.json()["model_version"] == "v2.0.0"
    finally:
        app.dependency_overrides.clear()
