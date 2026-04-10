from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.distribution import MealDistribution
    from app.models.slot_selection import MealPlanSlotSelection


class MealPlanStatus(str, Enum):
    draft = "draft"
    reviewed = "reviewed"
    finalized = "finalized"
    ready_for_export = "ready_for_export"


class MealPlan(Base):
    __tablename__ = "meal_plans"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    distribution_id: Mapped[int] = mapped_column(
        ForeignKey("meal_distributions.id"),
        nullable=False,
        index=True,
    )
    status: Mapped[MealPlanStatus] = mapped_column(
        SqlEnum(MealPlanStatus, name="meal_plan_status", native_enum=False),
        nullable=False,
    )
    plan_set_version: Mapped[str] = mapped_column(String(100), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    distribution: Mapped["MealDistribution"] = relationship(back_populates="meal_plans")
    meals: Mapped[list["MealPlanMeal"]] = relationship(
        back_populates="meal_plan",
        cascade="all, delete-orphan",
        order_by="MealPlanMeal.sort_order",
    )


class MealPlanMeal(Base):
    __tablename__ = "meal_plan_meals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    meal_plan_id: Mapped[int] = mapped_column(
        ForeignKey("meal_plans.id"),
        nullable=False,
        index=True,
    )
    meal_code: Mapped[str] = mapped_column(String(50), nullable=False)
    label: Mapped[str] = mapped_column(String(120), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    target_energy_kcal: Mapped[float] = mapped_column(Float, nullable=False)
    protein_target_g: Mapped[float] = mapped_column(Float, nullable=False)
    fat_target_g: Mapped[float] = mapped_column(Float, nullable=False)
    carbs_target_g: Mapped[float] = mapped_column(Float, nullable=False)
    structure_payload: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    meal_plan: Mapped["MealPlan"] = relationship(back_populates="meals")
    slot_selections: Mapped[list["MealPlanSlotSelection"]] = relationship(
        back_populates="meal_plan_meal",
        cascade="all, delete-orphan",
    )
