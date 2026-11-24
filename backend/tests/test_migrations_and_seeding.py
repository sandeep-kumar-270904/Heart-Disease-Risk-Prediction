"""Alembic migrations, RFC 9562 UUIDv7 generation, and synthetic seeding tests."""

import os
import sys
import uuid
from pathlib import Path

from alembic.config import Config
from sqlalchemy import create_engine, inspect

from alembic import command
from app.models.assessment import Assessment, InferenceResult
from app.models.base import generate_uuidv7
from app.models.directory import Doctor, Hospital
from app.models.user import User

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "backend"
SCRIPTS_DIR = REPO_ROOT / "scripts"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from seed_synthetic_database import seed_database  # noqa: E402


def test_uuidv7_rfc9562_format_and_monotonic_sorting() -> None:
    """Verify UUIDv7 emits valid RFC 9562 v7 identifiers that sort chronologically."""
    generated = [generate_uuidv7() for _ in range(500)]
    assert len(set(generated)) == 500

    for item in generated:
        parsed = uuid.UUID(item)
        assert parsed.version == 7
        assert parsed.variant == uuid.RFC_4122

    # Monotonic sorting guarantee within the same process
    assert generated == sorted(generated)


def test_alembic_upgrade_downgrade_upgrade_cycle(tmp_path: Path, monkeypatch) -> None:
    """Verify full Alembic migration up -> down -> up lifecycle cleanly."""
    test_pg = os.environ.get("TEST_DATABASE_URL")
    if test_pg and test_pg.startswith("postgresql"):
        db_url = test_pg
    else:
        db_file = tmp_path / "migration_test.db"
        db_url = f"sqlite:///{db_file.as_posix()}"

    monkeypatch.setenv("DATABASE_URL", db_url)

    alembic_cfg = Config(str(BACKEND_DIR / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)

    # Clean slate before testing full migration cycle
    test_engine = create_engine(db_url)
    if db_url.startswith("postgresql"):
        from sqlalchemy import text

        with test_engine.begin() as conn:
            conn.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))

    # 1. Upgrade to head (001 + 002)
    command.upgrade(alembic_cfg, "head")
    inspector = inspect(test_engine)
    tables = set(inspector.get_table_names())
    expected_tables = {
        "users",
        "patient_profiles",
        "assessments",
        "inference_results",
        "shap_explanations",
        "counterfactual_profiles",
        "patient_doctor_grants",
        "clinical_notes",
        "doctors",
        "hospitals",
        "insurance_policies",
        "educational_resources",
        "audit_logs",
        "model_registry",
    }
    assert expected_tables.issubset(tables)

    user_cols = {col["name"] for col in inspector.get_columns("users")}
    assert {"country_code", "is_synthetic"}.issubset(user_cols)

    inf_cols = {col["name"]: col for col in inspector.get_columns("inference_results")}
    assert inf_cols["ascvd_10yr_risk"]["nullable"] is True
    assert inf_cols["ascvd_risk_tier"]["nullable"] is True
    assert inf_cols["confidence_interval_low"]["nullable"] is True
    assert inf_cols["confidence_interval_high"]["nullable"] is True

    assess_cols = {col["name"]: col for col in inspector.get_columns("assessments")}
    assert "fasting_blood_sugar_mgdl" in assess_cols
    assert assess_cols["fasting_blood_sugar_mgdl"]["nullable"] is True

    # 2. Downgrade back to base
    command.downgrade(alembic_cfg, "base")
    inspector_after_down = inspect(test_engine)
    remaining = set(inspector_after_down.get_table_names()) - {"alembic_version"}
    assert remaining == set()

    # 3. Re-upgrade to head to confirm clean idempotency
    command.upgrade(alembic_cfg, "head")
    test_engine.dispose()


def test_task_a_mvp_inference_allows_null_task_b(db_session, sample_patient) -> None:
    """Verify Task A MVP inference persists cleanly with nullable Task B fields (DEC-003)."""
    assessment = Assessment(
        patient_id=sample_patient.id,
        status="COMPLETED",
        is_synthetic=True,
        age=58,
        sex=1,
        cp=3,
        trestbps=140,
        chol=250,
        fbs=0,
        restecg=0,
        thalach=145,
        exang=1,
        oldpeak=1.5,
        slope=1,
        ca=1,
        thal=3,
    )
    db_session.add(assessment)
    db_session.flush()

    inference = InferenceResult(
        assessment_id=assessment.id,
        model_version="v2.0.0",
        cad_probability=0.68,
        cad_risk_tier="MODERATE",
        confidence_interval_low=0.61,
        confidence_interval_high=0.75,
        ascvd_10yr_risk=None,
        ascvd_risk_tier=None,
        base_expected_value=-0.16,
        raw_decision_margin=0.75,
        is_out_of_distribution=False,
    )
    db_session.add(inference)
    db_session.commit()
    db_session.refresh(inference)

    assert inference.ascvd_10yr_risk is None
    assert inference.ascvd_risk_tier is None


def test_synthetic_seeder_idempotency_and_safety(db_session) -> None:
    """Verify synthetic database seeder populates Category B & multi-country records cleanly."""
    first_run = seed_database(db_session, assessment_count=10, seed=42)
    assert first_run["users_created"] == 3
    assert first_run["assessments_created"] == 10
    assert first_run["doctors_created"] == 3
    assert first_run["hospitals_created"] == 3

    # Second run must create 0 duplicate records
    second_run = seed_database(db_session, assessment_count=10, seed=42)
    assert all(count == 0 for count in second_run.values())

    # Verify strict DEC-005 synthetic tags and DEC-004 country codes
    users = db_session.query(User).all()
    assert all(u.is_synthetic is True for u in users)

    assessments = db_session.query(Assessment).all()
    assert len(assessments) == 10
    assert all(a.is_synthetic is True for a in assessments)

    doc_countries = {d.country_code for d in db_session.query(Doctor).all()}
    hosp_countries = {h.country_code for h in db_session.query(Hospital).all()}
    assert doc_countries == {"US", "IN", "GB"}
    assert hosp_countries == {"US", "IN", "GB"}
