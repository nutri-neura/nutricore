from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MealPlanSlotSelection(Base):
    __tablename__ = "meal_plan_slot_selections"
    __table_args__ = (UniqueConstraint("meal_plan_meal_id", "slot_code", name="uq_meal_plan_slot"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    meal_plan_meal_id: Mapped[int] = mapped_column(
        ForeignKey("meal_plan_meals.id"),
        nullable=False,
        index=True,
    )
    slot_code: Mapped[str] = mapped_column(String(50), nullable=False)
    food_item_id: Mapped[int] = mapped_column(ForeignKey("food_items.id"), nullable=False)
    portion_multiplier: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    final_portion_text: Mapped[str | None] = mapped_column(String(160), nullable=True)
    adjusted_energy_kcal: Mapped[float | None] = mapped_column(Float, nullable=True)
    adjusted_protein_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    adjusted_fat_g: Mapped[float | None] = mapped_column(Float, nullable=True)
    adjusted_carbs_g: Mapped[float | None] = mapped_column(Float, nullable=True)
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

    meal_plan_meal = relationship("MealPlanMeal", back_populates="slot_selections")
    food_item = relationship("FoodItem")
