"""add nutrition strategies

Revision ID: 20260408_0004
Revises: 20260408_0003
Create Date: 2026-04-08 18:20:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260408_0004"
down_revision: str | None = "20260408_0003"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "nutrition_strategies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("evaluation_id", sa.Integer(), nullable=False),
        sa.Column(
            "goal_code",
            sa.Enum(
                "maintenance",
                "fat_loss",
                "muscle_gain",
                "recomposition",
                name="strategy_goal",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("generated", name="nutrition_strategy_status", native_enum=False),
            nullable=False,
        ),
        sa.Column("strategy_set_version", sa.String(length=100), nullable=False),
        sa.Column("recommendation_payload", sa.JSON(), nullable=False),
        sa.Column("warnings_payload", sa.JSON(), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["evaluation_id"], ["evaluations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_nutrition_strategies_evaluation_id"),
        "nutrition_strategies",
        ["evaluation_id"],
    )
    op.create_index(op.f("ix_nutrition_strategies_id"), "nutrition_strategies", ["id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_nutrition_strategies_id"), table_name="nutrition_strategies")
    op.drop_index(op.f("ix_nutrition_strategies_evaluation_id"), table_name="nutrition_strategies")
    op.drop_table("nutrition_strategies")
