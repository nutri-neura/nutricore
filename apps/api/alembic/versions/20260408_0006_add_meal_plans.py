"""add meal plans"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260408_0006"
down_revision: str | None = "20260408_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "meal_plans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("distribution_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("draft", "reviewed", name="meal_plan_status", native_enum=False),
            nullable=False,
        ),
        sa.Column("plan_set_version", sa.String(length=100), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["distribution_id"], ["meal_distributions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_meal_plans_distribution_id"),
        "meal_plans",
        ["distribution_id"],
        unique=False,
    )
    op.create_index(op.f("ix_meal_plans_id"), "meal_plans", ["id"], unique=False)

    op.create_table(
        "meal_plan_meals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("meal_plan_id", sa.Integer(), nullable=False),
        sa.Column("meal_code", sa.String(length=50), nullable=False),
        sa.Column("label", sa.String(length=120), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("target_energy_kcal", sa.Float(), nullable=False),
        sa.Column("protein_target_g", sa.Float(), nullable=False),
        sa.Column("fat_target_g", sa.Float(), nullable=False),
        sa.Column("carbs_target_g", sa.Float(), nullable=False),
        sa.Column("structure_payload", sa.JSON(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["meal_plan_id"], ["meal_plans.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_meal_plan_meals_id"), "meal_plan_meals", ["id"], unique=False)
    op.create_index(
        op.f("ix_meal_plan_meals_meal_plan_id"),
        "meal_plan_meals",
        ["meal_plan_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_meal_plan_meals_meal_plan_id"), table_name="meal_plan_meals")
    op.drop_index(op.f("ix_meal_plan_meals_id"), table_name="meal_plan_meals")
    op.drop_table("meal_plan_meals")
    op.drop_index(op.f("ix_meal_plans_id"), table_name="meal_plans")
    op.drop_index(op.f("ix_meal_plans_distribution_id"), table_name="meal_plans")
    op.drop_table("meal_plans")
