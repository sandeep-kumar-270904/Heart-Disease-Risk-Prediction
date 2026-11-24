"""Critical Remediation Round 01 — Comprehensive Regression Tests (Priorities 1–5 & 7)."""

from __future__ import annotations

import io
import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from cryptography.exceptions import InvalidTag
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.config import LOCAL_DEV_SECRET_KEY, Settings
from app.core.database import get_db
from app.core.errors import AuthorizationError
from app.core.redis_client import get_token_store
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.assessment import Assessment, InferenceResult
from app.models.consent import DoctorGrant
from app.models.user import User
from app.services.assessment_service import authorize_assessment_access
from app.services.consent_service import authorize_clinician_grant
from tests.test_auth import InMemoryTokenStore

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from backup_aead import decrypt_bytes_aes256_gcm, encrypt_bytes_aes256_gcm  # noqa: E402


def _valid_assessment_payload(fbs: float = 164.5) -> dict[str, object]:
    return {
        "synthetic_fixture_confirmed": True,
        "age": 56,
        "sex": 1,
        "chest_pain_type": 2,
        "unit_system": "us_customary",
        "resting_bp": 144,
        "serum_cholesterol": 248,
        "fasting_blood_sugar": fbs,
        "resting_ecg": 0,
        "max_heart_rate": 148,
        "exercise_angina": 0,
        "st_depression": 1.4,
        "st_slope": 1,
        "major_vessels": 0,
        "thallium_stress": 1,
    }


def test_priority_1_authoritative_consent_blocks_expired_revoked_and_exact_boundary(
    db_session, sample_patient, sample_doctor, sample_admin
) -> None:
    """Verify ALL clinician assessment paths enforce active, unrevoked, strict expiry."""
    other_doctor = User(
        email="dr.other@example.com",
        hashed_password=hash_password("OtherDoc!2026"),
        full_name="Dr. Other Synthetic",
        role="CLINICIAN",
        country_code="US",
        clinician_status="VERIFIED",
        is_synthetic=True,
    )
    unverified_doc = User(
        email="dr.pending@example.com",
        hashed_password=hash_password("PendingDoc!2026"),
        full_name="Dr. Pending Synthetic",
        role="CLINICIAN",
        country_code="US",
        clinician_status="PENDING_VERIFICATION",
        is_synthetic=True,
    )
    other_patient = User(
        email="other.patient@example.com",
        hashed_password=hash_password("OtherPat!2026"),
        full_name="Other Patient Synthetic",
        role="PATIENT",
        country_code="US",
        clinician_status="N/A",
        is_synthetic=True,
    )
    db_session.add_all([other_doctor, unverified_doc, other_patient])
    db_session.commit()

    store = InMemoryTokenStore()
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_token_store] = lambda: store

    try:
        client = TestClient(app)
        pat_headers = {
            "Authorization": f"Bearer {create_access_token(sample_patient.id, 'PATIENT')}"
        }
        doc_headers = {
            "Authorization": f"Bearer {create_access_token(sample_doctor.id, 'CLINICIAN')}"
        }
        other_doc_headers = {
            "Authorization": f"Bearer {create_access_token(other_doctor.id, 'CLINICIAN')}"
        }
        admin_headers = {
            "Authorization": f"Bearer {create_access_token(sample_admin.id, 'ADMINISTRATOR')}"
        }

        created = client.post(
            "/api/v1/assessments", json=_valid_assessment_payload(), headers=pat_headers
        )
        assert created.status_code == 201
        assess_id = created.json()["id"]

        # Exact-clock test on authorize_clinician_grant / authorize_assessment_access
        t0 = datetime(2026, 11, 25, 12, 0, 0, tzinfo=UTC)
        exact_expiry = t0 + timedelta(hours=72)
        grant = DoctorGrant(
            patient_id=sample_patient.id,
            doctor_id=sample_doctor.id,
            status="ACTIVE",
            granted_at=t0,
            expires_at=exact_expiry,
            revoked_at=None,
        )
        db_session.add(grant)
        db_session.commit()

        # 1 microsecond BEFORE expiry -> permitted
        before_exp = exact_expiry - timedelta(microseconds=1)
        assert (
            authorize_assessment_access(db_session, assess_id, sample_doctor, now=before_exp).id
            == assess_id
        )

        # AT exact expiration boundary -> DENIED (expires_at must be strictly later)
        with pytest.raises(AuthorizationError):
            authorize_clinician_grant(
                db_session, patient_id=sample_patient.id, doctor=sample_doctor, now=exact_expiry
            )
        with pytest.raises(AuthorizationError):
            authorize_assessment_access(db_session, assess_id, sample_doctor, now=exact_expiry)

        # Expired grant (status left "ACTIVE" intentionally to reproduce original bypass!) -> 403 everywhere
        grant.expires_at = datetime.now(UTC) - timedelta(minutes=1)
        db_session.commit()

        for method, url, kwargs in [
            ("get", f"/api/v1/assessments/{assess_id}", {}),
            ("get", f"/api/v1/assessments/{assess_id}/shap", {}),
            (
                "post",
                f"/api/v1/assessments/{assess_id}/simulate",
                {"json": {"modified_features": {"resting_bp": 120.0}}},
            ),
            ("get", f"/api/v1/assessments/{assess_id}/export-pdf", {}),
            ("get", f"/api/v1/consents/doctor/assessments/{assess_id}", {}),
        ]:
            resp = getattr(client, method)(url, headers=doc_headers, **kwargs)
            assert resp.status_code == 403, f"Expired grant bypass on {method} {url}"

        # Unexpired valid grant -> permits clinician on ALL assessment paths
        grant.expires_at = datetime.now(UTC) + timedelta(hours=12)
        db_session.commit()
        assert (
            client.get(f"/api/v1/assessments/{assess_id}", headers=doc_headers).status_code == 200
        )
        assert (
            client.get(f"/api/v1/assessments/{assess_id}/shap", headers=doc_headers).status_code
            == 200
        )
        assert (
            client.post(
                f"/api/v1/assessments/{assess_id}/simulate",
                json={"modified_features": {"resting_bp": 120.0}},
                headers=doc_headers,
            ).status_code
            == 200
        )
        assert (
            client.get(
                f"/api/v1/assessments/{assess_id}/export-pdf", headers=doc_headers
            ).status_code
            == 200
        )

        # Wrong clinician, unverified clinician, admin without consent, wrong patient -> all denied
        assert (
            client.get(f"/api/v1/assessments/{assess_id}", headers=other_doc_headers).status_code
            == 403
        )
        assert (
            client.get(f"/api/v1/assessments/{assess_id}", headers=admin_headers).status_code == 403
        )
        with pytest.raises(AuthorizationError):
            authorize_clinician_grant(
                db_session, patient_id=sample_patient.id, doctor=unverified_doc
            )
        with pytest.raises(AuthorizationError):
            authorize_clinician_grant(db_session, patient_id=other_patient.id, doctor=sample_doctor)

        # Instant revocation blocks subsequent requests immediately
        rev = client.post(f"/api/v1/consents/{grant.id}/revoke", headers=pat_headers)
        assert rev.status_code == 200
        assert (
            client.get(f"/api/v1/assessments/{assess_id}", headers=doc_headers).status_code == 403
        )
        assert (
            client.get(
                f"/api/v1/assessments/{assess_id}/export-pdf", headers=doc_headers
            ).status_code
            == 403
        )
    finally:
        app.dependency_overrides.clear()


def test_priority_2_and_7_no_false_confidence_interval_or_30_70_tiers(
    db_session, sample_patient
) -> None:
    """Verify ±6.5 heuristic 95% CI and unsupported 30%/70% clinical tiers are absent everywhere."""
    store = InMemoryTokenStore()
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_token_store] = lambda: store

    try:
        client = TestClient(app)
        headers = {"Authorization": f"Bearer {create_access_token(sample_patient.id, 'PATIENT')}"}

        resp = client.post("/api/v1/assessments", json=_valid_assessment_payload(), headers=headers)
        assert resp.status_code == 201
        body = resp.json()
        assert "confidence_interval" not in body
        assert body["risk_strata"] == "unstratified"
        assert body["ten_year_population_risk_percent"] is None
        assert body["emergency_warning_active"] is False
        assert "NOT a medical diagnosis" in body["plain_language_summary"]

        from pypdf import PdfReader

        pdf = client.get(f"/api/v1/assessments/{body['id']}/export-pdf", headers=headers)
        assert pdf.status_code == 200
        pdf_text = "\n".join(
            page.extract_text() or "" for page in PdfReader(io.BytesIO(pdf.content)).pages
        )
        assert "95% Confidence Interval" not in pdf_text
        assert "95% Interval" not in pdf_text
        assert "Unstratified" in pdf_text
    finally:
        app.dependency_overrides.clear()


def test_priority_3_synthetic_only_boundary_blocks_real_domains_and_notes(
    db_session, sample_doctor
) -> None:
    """Verify server rejects real-world registration domains, missing attestations, and free-text notes."""
    non_synth_user = User(
        email="real.person@gmail.com",
        hashed_password=hash_password("RealPerson!2026"),
        full_name="Real User",
        role="PATIENT",
        country_code="US",
        clinician_status="N/A",
        is_synthetic=False,
    )
    db_session.add(non_synth_user)
    db_session.commit()

    store = InMemoryTokenStore()
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_token_store] = lambda: store

    try:
        client = TestClient(app)

        # 1. Real domain email rejected on /auth/register
        real_reg = client.post(
            "/api/v1/auth/register",
            json={
                "email": "john.doe@gmail.com",
                "password": "StrongPassword!2026",
                "full_name": "John Doe",
                "country_code": "US",
                "consent_given": True,
                "synthetic_persona_acknowledged": True,
            },
        )
        assert real_reg.status_code == 422

        # 2. Missing synthetic_persona_acknowledged rejected on /auth/register
        no_ack_reg = client.post(
            "/api/v1/auth/register",
            json={
                "email": "demo.persona@example.com",
                "password": "StrongPassword!2026",
                "full_name": "Demo Persona",
                "country_code": "US",
                "consent_given": True,
            },
        )
        assert no_ack_reg.status_code == 422

        # 3. Non-synthetic DB account blocked from submitting assessment
        bad_headers = {
            "Authorization": f"Bearer {create_access_token(non_synth_user.id, 'PATIENT')}"
        }
        blocked_assess = client.post(
            "/api/v1/assessments", json=_valid_assessment_payload(), headers=bad_headers
        )
        assert blocked_assess.status_code == 403

        # 4. Payload missing synthetic_fixture_confirmed rejected with 422
        payload_no_flag = _valid_assessment_payload()
        del payload_no_flag["synthetic_fixture_confirmed"]
        valid_reg = client.post(
            "/api/v1/auth/register",
            json={
                "email": "synth.check@example.org",
                "password": "StrongPassword!2026",
                "full_name": "Synthetic Persona Check",
                "country_code": "US",
                "consent_given": True,
                "synthetic_persona_acknowledged": True,
            },
        )
        assert valid_reg.status_code == 201
        synth_id = valid_reg.json()["id"]
        synth_headers = {"Authorization": f"Bearer {create_access_token(synth_id, 'PATIENT')}"}

        missing_confirm = client.post(
            "/api/v1/assessments", json=payload_no_flag, headers=synth_headers
        )
        assert missing_confirm.status_code == 422

        # 5. Free-text clinician notes disabled in synthetic-only MVP even with active grant
        created = client.post(
            "/api/v1/assessments", json=_valid_assessment_payload(), headers=synth_headers
        )
        assess_id = created.json()["id"]
        client.post("/api/v1/consents", json={"doctor_id": sample_doctor.id}, headers=synth_headers)
        doc_headers = {
            "Authorization": f"Bearer {create_access_token(sample_doctor.id, 'CLINICIAN')}"
        }
        note_attempt = client.post(
            f"/api/v1/consents/doctor/assessments/{assess_id}/notes",
            json={"note_content": "Real patient John SSN 123-45-6789."},
            headers=doc_headers,
        )
        assert note_attempt.status_code == 422
    finally:
        app.dependency_overrides.clear()


def test_priority_4_fasting_blood_sugar_numeric_roundtrip_and_no_legacy_reconstruction(
    db_session, sample_patient
) -> None:
    """Verify exact numeric glucose is persisted/returned/exported and legacy nulls are not faked."""
    store = InMemoryTokenStore()
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_token_store] = lambda: store

    try:
        client = TestClient(app)
        headers = {"Authorization": f"Bearer {create_access_token(sample_patient.id, 'PATIENT')}"}

        # 1. Exact numeric glucose 164.5 mg/dL round-trip
        created = client.post(
            "/api/v1/assessments", json=_valid_assessment_payload(fbs=164.5), headers=headers
        )
        assert created.status_code == 201
        detail = created.json()
        assert detail["fasting_blood_sugar"] == 164.5
        assert detail["fasting_blood_sugar_gt_120"] is True

        fetched = client.get(f"/api/v1/assessments/{detail['id']}", headers=headers)
        assert fetched.status_code == 200
        assert fetched.json()["fasting_blood_sugar"] == 164.5

        sim = client.post(
            f"/api/v1/assessments/{detail['id']}/simulate",
            json={"modified_features": {"fasting_blood_sugar": 100.0}},
            headers=headers,
        )
        assert sim.status_code == 200
        assert sim.json()["is_biological_clamp_violated"] is False

        # PDF contains exact 164.5 mg/dL (not placeholder 130)
        from pypdf import PdfReader

        pdf = client.get(f"/api/v1/assessments/{detail['id']}/export-pdf", headers=headers)
        assert pdf.status_code == 200
        extracted_text = "\n".join(
            page.extract_text() or "" for page in PdfReader(io.BytesIO(pdf.content)).pages
        )
        assert "164.5 mg/dL" in extracted_text

        # 2. Legacy record (fasting_blood_sugar_mgdl=None, fbs=1) must return None (NOT 130.0!)
        legacy = Assessment(
            patient_id=sample_patient.id,
            status="COMPLETED",
            is_synthetic=True,
            age=60,
            sex=1,
            cp=2,
            trestbps=135,
            chol=230,
            fbs=1,
            fasting_blood_sugar_mgdl=None,
            restecg=0,
            thalach=145,
            exang=0,
            oldpeak=1.0,
            slope=1,
            ca=0,
            thal=1,
        )
        db_session.add(legacy)
        db_session.flush()
        db_session.add(
            InferenceResult(
                assessment_id=legacy.id,
                model_version="v2.0.0",
                cad_probability=0.45,
                cad_risk_tier="UNSTRATIFIED",
                confidence_interval_low=None,
                confidence_interval_high=None,
                ascvd_10yr_risk=None,
                ascvd_risk_tier=None,
                base_expected_value=-0.1,
                raw_decision_margin=-0.2,
            )
        )
        db_session.commit()

        legacy_resp = client.get(f"/api/v1/assessments/{legacy.id}", headers=headers)
        assert legacy_resp.status_code == 200
        assert legacy_resp.json()["fasting_blood_sugar"] is None
        assert legacy_resp.json()["fasting_blood_sugar_gt_120"] is True

        legacy_sim = client.post(
            f"/api/v1/assessments/{legacy.id}/simulate",
            json={"modified_features": {"resting_bp": 120.0}},
            headers=headers,
        )
        assert legacy_sim.status_code == 422
    finally:
        app.dependency_overrides.clear()


def test_priority_5_config_fail_closed_and_canonical_routing() -> None:
    """Verify staging/prod fail closed on insecure secrets and duplicate unversioned API is gone."""
    with pytest.raises(ValidationError):
        Settings(ENVIRONMENT="staging", DEBUG=False, SECRET_KEY=LOCAL_DEV_SECRET_KEY)

    with pytest.raises(ValidationError):
        Settings(ENVIRONMENT="production", DEBUG=False, SECRET_KEY="too-short")

    valid_prod = Settings(
        ENVIRONMENT="production",
        DEBUG=False,
        SECRET_KEY="x" * 48,
    )
    assert valid_prod.ENVIRONMENT == "production"

    client = TestClient(app)
    # Unversioned API endpoints must return 404; versioned /api/v1 and /health/* remain mounted
    assert client.post("/auth/login", json={}).status_code == 404
    assert client.get("/assessments").status_code == 404
    assert client.get("/consents").status_code == 404
    assert client.get("/admin/users").status_code == 404
    assert client.get("/health/live").status_code == 200

    schema_paths = set(app.openapi()["paths"].keys())
    assert "/api/v1/auth/login" in schema_paths
    assert "/auth/login" not in schema_paths


def test_priority_5d_backup_aes256_gcm_roundtrip_wrong_key_and_tamper(tmp_path: Path) -> None:
    """Verify authenticated AES-256-GCM encryption, restore, wrong-key rejection & tamper check."""
    passphrase = "StrongBackupPassphrase#2026!Vault"
    wrong_passphrase = "WrongBackupPassphrase#2026!Vault"
    payload = b"-- synthetic sql dump\nSELECT 1;\n"

    encrypted = encrypt_bytes_aes256_gcm(payload, passphrase)
    assert encrypted.startswith(b"HXAEAD01")
    assert payload not in encrypted

    archive_path = tmp_path / "test_backup.sql.gz.gcm"
    archive_path.write_bytes(encrypted)

    # 1. Valid decrypt succeeds cleanly & leaves zero temp files
    before_files = set(os.listdir(tmp_path))
    decrypted = decrypt_bytes_aes256_gcm(archive_path.read_bytes(), passphrase)
    assert decrypted == payload
    assert set(os.listdir(tmp_path)) == before_files

    # 2. Wrong passphrase fails authentication
    with pytest.raises(InvalidTag):
        decrypt_bytes_aes256_gcm(encrypted, wrong_passphrase)

    # 3. Single-byte tamper in ciphertext or GCM tag fails authentication
    tampered = bytearray(encrypted)
    tampered[-5] ^= 0xFF
    with pytest.raises(InvalidTag):
        decrypt_bytes_aes256_gcm(bytes(tampered), passphrase)

    # 4. Tamper in header fails cleanly
    bad_header = bytearray(encrypted)
    bad_header[0] = ord("X")
    with pytest.raises(ValueError):
        decrypt_bytes_aes256_gcm(bytes(bad_header), passphrase)
