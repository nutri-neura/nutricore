"""add meal distributions"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260408_0005"
down_revision: str | None = "20260408_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "meal_distributions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("strategy_id", sa.Integer(), nullable=False),
        sa.Column(
            "pattern_code",
            sa.Enum(
                "three_meals",
                "four_meals",
                "five_meals",
                name="meal_pattern",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "generated",
                name="meal_distribution_status",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("distribution_set_version", sa.String(length=100), nullable=False),
        sa.Column("recommendation_payload", sa.JSON(), nullable=False),
        sa.Column("warnings_payload", sa.JSON(), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["strategy_id"], ["nutrition_strategies.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_meal_distributions_id"), "meal_distributions", ["id"], unique=False)
    op.create_index(
        op.f("ix_meal_distributions_strategy_id"),
        "meal_distributions",
        ["strategy_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_meal_distributions_strategy_id"), table_name="meal_distributions")
    op.drop_index(op.f("ix_meal_distributions_id"), table_name="meal_distributions")
    op.drop_table("meal_distributions")
