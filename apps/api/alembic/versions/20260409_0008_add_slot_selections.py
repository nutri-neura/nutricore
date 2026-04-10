"""add slot selections"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260409_0008"
down_revision: str | None = "20260408_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "meal_plan_slot_selections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("meal_plan_meal_id", sa.Integer(), nullable=False),
        sa.Column("slot_code", sa.String(length=50), nullable=False),
        sa.Column("food_item_id", sa.Integer(), nullable=False),
        sa.Column("created_by_user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["food_item_id"], ["food_items.id"]),
        sa.ForeignKeyConstraint(["meal_plan_meal_id"], ["meal_plan_meals.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("meal_plan_meal_id", "slot_code", name="uq_meal_plan_slot"),
    )
    op.create_index(
        op.f("ix_meal_plan_slot_selections_id"),
        "meal_plan_slot_selections",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_meal_plan_slot_selections_meal_plan_meal_id"),
        "meal_plan_slot_selections",
        ["meal_plan_meal_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_meal_plan_slot_selections_meal_plan_meal_id"),
        table_name="meal_plan_slot_selections",
    )
    op.drop_index(op.f("ix_meal_plan_slot_selections_id"), table_name="meal_plan_slot_selections")
    op.drop_table("meal_plan_slot_selections")
