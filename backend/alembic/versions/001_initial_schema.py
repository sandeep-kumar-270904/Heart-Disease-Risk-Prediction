"""Initial relational database schema for HeartXAI 2.0.

Revision ID: 001_initial_schema
Revises: None
Create Date: 2026-11-15 18:30:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. users table
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("role", sa.String(32), nullable=False, server_default="PATIENT"),
        sa.Column("clinician_status", sa.String(32), nullable=False, server_default="N/A"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_role_status", "users", ["role", "clinician_status"])

    # 2. patient_profiles table
    op.create_table(
        "patient_profiles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "patient_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("biological_sex", sa.String(16), nullable=True),
        sa.Column("preferred_units", sa.String(16), nullable=False, server_default="US_STANDARD"),
        sa.Column("emergency_contact_name", sa.String(255), nullable=True),
        sa.Column("emergency_contact_phone", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_patient_profiles_patient_id", "patient_profiles", ["patient_id"])

    # 3. assessments table
    op.create_table(
        "assessments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "patient_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "clinician_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("status", sa.String(32), nullable=False, server_default="COMPLETED"),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("sex", sa.Integer(), nullable=False),
        sa.Column("cp", sa.Integer(), nullable=False),
        sa.Column("trestbps", sa.Integer(), nullable=False),
        sa.Column("chol", sa.Integer(), nullable=False),
        sa.Column("fbs", sa.Integer(), nullable=False),
        sa.Column("restecg", sa.Integer(), nullable=False),
        sa.Column("thalach", sa.Integer(), nullable=False),
        sa.Column("exang", sa.Integer(), nullable=False),
        sa.Column("oldpeak", sa.Float(), nullable=False),
        sa.Column("slope", sa.Integer(), nullable=False),
        sa.Column("ca", sa.Integer(), nullable=False),
        sa.Column("thal", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_assessments_patient_id", "assessments", ["patient_id"])
    op.create_index("ix_assessments_clinician_id", "assessments", ["clinician_id"])
    op.create_index("ix_assessments_patient_created", "assessments", ["patient_id", "created_at"])

    # 4. inference_results table
    op.create_table(
        "inference_results",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "assessment_id",
            sa.String(36),
            sa.ForeignKey("assessments.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("model_version", sa.String(32), nullable=False),
        sa.Column("cad_probability", sa.Float(), nullable=False),
        sa.Column("cad_risk_tier", sa.String(32), nullable=False),
        sa.Column("confidence_interval_low", sa.Float(), nullable=False),
        sa.Column("confidence_interval_high", sa.Float(), nullable=False),
        sa.Column("ascvd_10yr_risk", sa.Float(), nullable=False),
        sa.Column("ascvd_risk_tier", sa.String(32), nullable=False),
        sa.Column("base_expected_value", sa.Float(), nullable=False),
        sa.Column("raw_decision_margin", sa.Float(), nullable=False),
        sa.Column(
            "is_out_of_distribution", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
        sa.Column("computed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_inference_results_assessment_id", "inference_results", ["assessment_id"])

    # 5. shap_explanations table
    op.create_table(
        "shap_explanations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "inference_id",
            sa.String(36),
            sa.ForeignKey("inference_results.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("feature_name", sa.String(32), nullable=False),
        sa.Column("feature_value", sa.Float(), nullable=False),
        sa.Column("shap_value", sa.Float(), nullable=False),
        sa.Column("rank_importance", sa.Integer(), nullable=False),
        sa.Column("directional_impact", sa.String(32), nullable=False),
        sa.Column("clinical_interpretation", sa.String(512), nullable=False),
    )
    op.create_index("ix_shap_inference_id", "shap_explanations", ["inference_id"])
    op.create_index(
        "ix_shap_inference_rank", "shap_explanations", ["inference_id", "rank_importance"]
    )

    # 6. counterfactual_profiles table
    op.create_table(
        "counterfactual_profiles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "inference_id",
            sa.String(36),
            sa.ForeignKey("inference_results.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("target_risk_threshold", sa.Float(), nullable=False),
        sa.Column("achieved_risk_probability", sa.Float(), nullable=False),
        sa.Column("modified_biomarkers", sa.JSON(), nullable=False),
        sa.Column("immutable_biomarkers", sa.JSON(), nullable=False),
        sa.Column("l1_normalized_distance", sa.Float(), nullable=False),
        sa.Column("feasibility_rating", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_counterfactual_inference_id", "counterfactual_profiles", ["inference_id"])

    # 7. patient_doctor_grants table
    op.create_table(
        "patient_doctor_grants",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "patient_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "doctor_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("access_code", sa.String(64), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="ACTIVE"),
        sa.Column("granted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_grants_patient_id", "patient_doctor_grants", ["patient_id"])
    op.create_index("ix_grants_doctor_id", "patient_doctor_grants", ["doctor_id"])
    op.create_index(
        "ix_grants_patient_doctor_status",
        "patient_doctor_grants",
        ["patient_id", "doctor_id", "status"],
    )

    # 8. clinical_notes table
    op.create_table(
        "clinical_notes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "assessment_id",
            sa.String(36),
            sa.ForeignKey("assessments.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "author_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("note_content", sa.Text(), nullable=False),
        sa.Column("signoff_status", sa.String(32), nullable=False, server_default="DRAFT"),
        sa.Column("signed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_clinical_notes_assessment_id", "clinical_notes", ["assessment_id"])
    op.create_index("ix_clinical_notes_author_id", "clinical_notes", ["author_id"])

    # 9. doctors table
    op.create_table(
        "doctors",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("doctor_name", sa.String(255), nullable=False),
        sa.Column("specialization", sa.String(128), nullable=False),
        sa.Column("hospital_name", sa.String(255), nullable=False),
        sa.Column("contact_number", sa.String(64), nullable=False),
        sa.Column("location", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("telehealth_available", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_doctors_spec_loc", "doctors", ["specialization", "location"])

    # 10. hospitals table
    op.create_table(
        "hospitals",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("hospital_name", sa.String(255), nullable=False),
        sa.Column("facility_type", sa.String(128), nullable=False),
        sa.Column("emergency_phone", sa.String(64), nullable=False),
        sa.Column("address", sa.String(255), nullable=False),
        sa.Column("city", sa.String(128), nullable=False),
        sa.Column("state", sa.String(64), nullable=False),
        sa.Column("accreditation_details", sa.String(255), nullable=False),
        sa.Column("has_247_cath_lab", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_hospitals_city_type", "hospitals", ["city", "facility_type"])

    # 11. insurance_policies table
    op.create_table(
        "insurance_policies",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("provider_name", sa.String(255), nullable=False),
        sa.Column("policy_name", sa.String(255), nullable=False),
        sa.Column("coverage_summary", sa.Text(), nullable=False),
        sa.Column("monthly_premium_est", sa.Float(), nullable=True),
        sa.Column("waiting_period_days", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("exclusions_summary", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # 12. educational_resources table
    op.create_table(
        "educational_resources",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("biomarker_code", sa.String(32), nullable=False),
        sa.Column("summary", sa.String(512), nullable=False),
        sa.Column("guideline_source", sa.String(255), nullable=False),
        sa.Column("diet_plan_summary", sa.Text(), nullable=False),
        sa.Column("exercise_tips_summary", sa.Text(), nullable=False),
        sa.Column("lifestyle_guidance", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_educational_biomarker_code", "educational_resources", ["biomarker_code"])

    # 13. audit_logs table
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=True),
        sa.Column("role", sa.String(32), nullable=False),
        sa.Column("action_type", sa.String(64), nullable=False),
        sa.Column("resource_id", sa.String(64), nullable=True),
        sa.Column("endpoint", sa.String(255), nullable=False),
        sa.Column("method", sa.String(16), nullable=False),
        sa.Column("ip_address", sa.String(64), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("duration_ms", sa.Float(), nullable=False),
    )
    op.create_index("ix_audit_logs_timestamp", "audit_logs", ["timestamp"])
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_action_type", "audit_logs", ["action_type"])
    op.create_index("ix_audit_user_action", "audit_logs", ["user_id", "action_type"])
    op.create_index("ix_audit_time_action", "audit_logs", ["timestamp", "action_type"])

    # 14. model_registry table
    op.create_table(
        "model_registry",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("version", sa.String(32), nullable=False),
        sa.Column("algorithm", sa.String(128), nullable=False),
        sa.Column("training_cohort", sa.String(255), nullable=False),
        sa.Column("test_auroc", sa.Float(), nullable=False),
        sa.Column("brier_score", sa.Float(), nullable=False),
        sa.Column("sha256_hash", sa.String(64), nullable=False),
        sa.Column("deployed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Integer(), nullable=False, server_default="1"),
    )
    op.create_index("ix_model_registry_version", "model_registry", ["version"], unique=True)


def downgrade() -> None:
    op.drop_table("model_registry")
    op.drop_table("audit_logs")
    op.drop_table("educational_resources")
    op.drop_table("insurance_policies")
    op.drop_table("hospitals")
    op.drop_table("doctors")
    op.drop_table("clinical_notes")
    op.drop_table("patient_doctor_grants")
    op.drop_table("counterfactual_profiles")
    op.drop_table("shap_explanations")
    op.drop_table("inference_results")
    op.drop_table("assessments")
    op.drop_table("patient_profiles")
    op.drop_table("users")
