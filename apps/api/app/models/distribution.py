from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.meal_plan import MealPlan
    from app.models.strategy import NutritionStrategy


class MealPattern(str, Enum):
    three_meals = "three_meals"
    four_meals = "four_meals"
    five_meals = "five_meals"


class MealDistributionStatus(str, Enum):
    generated = "generated"


class MealDistribution(Base):
    __tablename__ = "meal_distributions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    strategy_id: Mapped[int] = mapped_column(
        ForeignKey("nutrition_strategies.id"),
        nullable=False,
        index=True,
    )
    pattern_code: Mapped[MealPattern] = mapped_column(
        SqlEnum(MealPattern, name="meal_pattern", native_enum=False),
        nullable=False,
    )
    status: Mapped[MealDistributionStatus] = mapped_column(
        SqlEnum(MealDistributionStatus, name="meal_distribution_status", native_enum=False),
        nullable=False,
    )
    distribution_set_version: Mapped[str] = mapped_column(String(100), nullable=False)
    recommendation_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    warnings_payload: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    strategy: Mapped["NutritionStrategy"] = relationship(back_populates="meal_distributions")
    meal_plans: Mapped[list["MealPlan"]] = relationship(
        back_populates="distribution",
        cascade="all, delete-orphan",
    )
