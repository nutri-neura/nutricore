"""add evaluations

Revision ID: 20260408_0003
Revises: 20260408_0002
Create Date: 2026-04-08 00:20:00
"""

import sqlalchemy as sa
from sqlalchemy import inspect

from alembic import op

revision = "20260408_0003"
down_revision = "20260408_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "evaluations" not in existing_tables:
        op.create_table(
            "evaluations",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "consultation_id",
                sa.Integer(),
                sa.ForeignKey("consultations.id"),
                nullable=False,
            ),
            sa.Column("status", sa.String(length=50), nullable=False),
            sa.Column("formula_set_version", sa.String(length=100), nullable=False),
            sa.Column("equation_selection_policy", sa.String(length=255), nullable=False),
            sa.Column("summary_payload", sa.JSON(), nullable=False),
            sa.Column("warnings_payload", sa.JSON(), nullable=False),
            sa.Column("calculated_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column(
                "created_by_user_id",
                sa.Integer(),
                sa.ForeignKey("users.id"),
                nullable=False,
            ),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index("ix_evaluations_id", "evaluations", ["id"], unique=False)
        op.create_index(
            "ix_evaluations_consultation_id",
            "evaluations",
            ["consultation_id"],
            unique=False,
        )

    if "formula_results" not in existing_tables:
        op.create_table(
            "formula_results",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "evaluation_id",
                sa.Integer(),
                sa.ForeignKey("evaluations.id"),
                nullable=False,
            ),
            sa.Column("formula_code", sa.String(length=120), nullable=False),
            sa.Column("formula_version", sa.String(length=50), nullable=False),
            sa.Column("formula_family", sa.String(length=120), nullable=False),
            sa.Column("input_payload", sa.JSON(), nullable=False),
            sa.Column("output_payload", sa.JSON(), nullable=False),
            sa.Column("source_note", sa.String(length=255), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index("ix_formula_results_id", "formula_results", ["id"], unique=False)
        op.create_index(
            "ix_formula_results_evaluation_id",
            "formula_results",
            ["evaluation_id"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "formula_results" in existing_tables:
        indexes = {index["name"] for index in inspector.get_indexes("formula_results")}
        if "ix_formula_results_evaluation_id" in indexes:
            op.drop_index("ix_formula_results_evaluation_id", table_name="formula_results")
        if "ix_formula_results_id" in indexes:
            op.drop_index("ix_formula_results_id", table_name="formula_results")
        op.drop_table("formula_results")

    if "evaluations" in existing_tables:
        indexes = {index["name"] for index in inspector.get_indexes("evaluations")}
        if "ix_evaluations_consultation_id" in indexes:
            op.drop_index("ix_evaluations_consultation_id", table_name="evaluations")
        if "ix_evaluations_id" in indexes:
            op.drop_index("ix_evaluations_id", table_name="evaluations")
        op.drop_table("evaluations")
