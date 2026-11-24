"""Add governance synthetic markers, country adapter codes, and nullable Task B fields.

Revision ID: 002_milestone_04_governance_geo
Revises: 001_initial_schema
Create Date: 2026-11-25 01:10:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "002_milestone_04_governance_geo"
down_revision: str | None = "001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Users: country_code (DEC-004) & is_synthetic (DEC-005)
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(
            sa.Column("country_code", sa.String(7), nullable=False, server_default="US")
        )
        batch_op.add_column(
            sa.Column("is_synthetic", sa.Boolean(), nullable=False, server_default=sa.true())
        )

    # 2. Assessments: is_synthetic marker (DEC-005)
    with op.batch_alter_table("assessments") as batch_op:
        batch_op.add_column(
            sa.Column("is_synthetic", sa.Boolean(), nullable=False, server_default=sa.true())
        )

    # 3. Inference Results: nullable Task B fields per DEC-003 Option A (Task A MVP only)
    with op.batch_alter_table("inference_results") as batch_op:
        batch_op.alter_column(
            "ascvd_10yr_risk",
            existing_type=sa.Float(),
            nullable=True,
        )
        batch_op.alter_column(
            "ascvd_risk_tier",
            existing_type=sa.String(32),
            nullable=True,
        )

    # 4. Directory Tables: country_code indexes for multi-country adapter engine (ADR-011)
    with op.batch_alter_table("doctors") as batch_op:
        batch_op.add_column(
            sa.Column("country_code", sa.String(7), nullable=False, server_default="US")
        )
        batch_op.create_index("ix_doctors_country_code", ["country_code"])

    with op.batch_alter_table("hospitals") as batch_op:
        batch_op.add_column(
            sa.Column("country_code", sa.String(7), nullable=False, server_default="US")
        )
        batch_op.create_index("ix_hospitals_country_code", ["country_code"])

    with op.batch_alter_table("insurance_policies") as batch_op:
        batch_op.add_column(
            sa.Column("country_code", sa.String(7), nullable=False, server_default="US")
        )
        batch_op.create_index("ix_insurance_policies_country_code", ["country_code"])


def downgrade() -> None:
    with op.batch_alter_table("insurance_policies") as batch_op:
        batch_op.drop_index("ix_insurance_policies_country_code")
        batch_op.drop_column("country_code")

    with op.batch_alter_table("hospitals") as batch_op:
        batch_op.drop_index("ix_hospitals_country_code")
        batch_op.drop_column("country_code")

    with op.batch_alter_table("doctors") as batch_op:
        batch_op.drop_index("ix_doctors_country_code")
        batch_op.drop_column("country_code")

    with op.batch_alter_table("inference_results") as batch_op:
        batch_op.alter_column(
            "ascvd_risk_tier",
            existing_type=sa.String(32),
            nullable=False,
        )
        batch_op.alter_column(
            "ascvd_10yr_risk",
            existing_type=sa.Float(),
            nullable=False,
        )

    with op.batch_alter_table("assessments") as batch_op:
        batch_op.drop_column("is_synthetic")

    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("is_synthetic")
        batch_op.drop_column("country_code")
