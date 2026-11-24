"""Add numeric fasting_blood_sugar_mgdl and make legacy confidence interval columns nullable.

Revision ID: 003_remediation_round_01
Revises: 002_milestone_04_governance_geo
Create Date: 2026-11-25 02:30:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "003_remediation_round_01"
down_revision: str | None = "002_milestone_04_governance_geo"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Preserve numeric fasting blood sugar while keeping legacy fbs (>120 mg/dL flag) intact
    with op.batch_alter_table("assessments") as batch_op:
        batch_op.add_column(sa.Column("fasting_blood_sugar_mgdl", sa.Float(), nullable=True))

    # 2. Omit unverified ±6.5% heuristic intervals cleanly by making legacy CI columns nullable
    with op.batch_alter_table("inference_results") as batch_op:
        batch_op.alter_column(
            "confidence_interval_low",
            existing_type=sa.Float(),
            nullable=True,
        )
        batch_op.alter_column(
            "confidence_interval_high",
            existing_type=sa.Float(),
            nullable=True,
        )


def downgrade() -> None:
    with op.batch_alter_table("inference_results") as batch_op:
        batch_op.alter_column(
            "confidence_interval_high",
            existing_type=sa.Float(),
            nullable=False,
        )
        batch_op.alter_column(
            "confidence_interval_low",
            existing_type=sa.Float(),
            nullable=False,
        )

    with op.batch_alter_table("assessments") as batch_op:
        batch_op.drop_column("fasting_blood_sugar_mgdl")
