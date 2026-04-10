"""expand meal plan status"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260410_0010"
down_revision: str | None = "20260410_0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TABLE meal_plans DROP CONSTRAINT IF EXISTS meal_plan_status")
    op.create_check_constraint(
        "meal_plan_status",
        "meal_plans",
        "status IN ('draft', 'reviewed', 'finalized', 'ready_for_export')",
    )


def downgrade() -> None:
    op.drop_constraint("meal_plan_status", "meal_plans", type_="check")
    op.create_check_constraint(
        "meal_plan_status",
        "meal_plans",
        "status IN ('draft', 'reviewed')",
    )
