"""finalize slot selections"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260410_0009"
down_revision: str | None = "20260409_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "meal_plan_slot_selections",
        sa.Column("portion_multiplier", sa.Float(), nullable=False, server_default="1.0"),
    )
    op.add_column(
        "meal_plan_slot_selections",
        sa.Column("final_portion_text", sa.String(length=160), nullable=True),
    )
    op.add_column(
        "meal_plan_slot_selections",
        sa.Column("adjusted_energy_kcal", sa.Float(), nullable=True),
    )
    op.add_column(
        "meal_plan_slot_selections",
        sa.Column("adjusted_protein_g", sa.Float(), nullable=True),
    )
    op.add_column(
        "meal_plan_slot_selections",
        sa.Column("adjusted_fat_g", sa.Float(), nullable=True),
    )
    op.add_column(
        "meal_plan_slot_selections",
        sa.Column("adjusted_carbs_g", sa.Float(), nullable=True),
    )
    op.add_column(
        "meal_plan_slot_selections",
        sa.Column("notes", sa.Text(), nullable=True),
    )
    op.add_column(
        "meal_plan_slot_selections",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
    )


def downgrade() -> None:
    op.drop_column("meal_plan_slot_selections", "updated_at")
    op.drop_column("meal_plan_slot_selections", "notes")
    op.drop_column("meal_plan_slot_selections", "adjusted_carbs_g")
    op.drop_column("meal_plan_slot_selections", "adjusted_fat_g")
    op.drop_column("meal_plan_slot_selections", "adjusted_protein_g")
    op.drop_column("meal_plan_slot_selections", "adjusted_energy_kcal")
    op.drop_column("meal_plan_slot_selections", "final_portion_text")
    op.drop_column("meal_plan_slot_selections", "portion_multiplier")
