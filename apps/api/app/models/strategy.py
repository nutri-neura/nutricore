from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.distribution import MealDistribution
    from app.models.evaluation import Evaluation


class StrategyGoal(str, Enum):
    maintenance = "maintenance"
    fat_loss = "fat_loss"
    muscle_gain = "muscle_gain"
    recomposition = "recomposition"


class NutritionStrategyStatus(str, Enum):
    generated = "generated"


class NutritionStrategy(Base):
    __tablename__ = "nutrition_strategies"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    evaluation_id: Mapped[int] = mapped_column(
        ForeignKey("evaluations.id"),
        nullable=False,
        index=True,
    )
    goal_code: Mapped[StrategyGoal] = mapped_column(
        SqlEnum(StrategyGoal, name="strategy_goal", native_enum=False),
        nullable=False,
    )
    status: Mapped[NutritionStrategyStatus] = mapped_column(
        SqlEnum(NutritionStrategyStatus, name="nutrition_strategy_status", native_enum=False),
        nullable=False,
    )
    strategy_set_version: Mapped[str] = mapped_column(String(100), nullable=False)
    recommendation_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    warnings_payload: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    evaluation: Mapped["Evaluation"] = relationship(back_populates="strategies")
    meal_distributions: Mapped[list["MealDistribution"]] = relationship(
        back_populates="strategy",
        cascade="all, delete-orphan",
    )
