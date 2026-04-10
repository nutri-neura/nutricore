from __future__ import annotations

from enum import Enum

from sqlalchemy import Boolean, Float, String
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FoodCategory(str, Enum):
    protein = "protein"
    carb = "carb"
    fat = "fat"
    vegetable = "vegetable"
    fruit = "fruit"
    dairy = "dairy"


class FoodItem(Base):
    __tablename__ = "food_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    category_code: Mapped[FoodCategory] = mapped_column(
        SqlEnum(FoodCategory, name="food_category", native_enum=False),
        nullable=False,
        index=True,
    )
    portion_label: Mapped[str] = mapped_column(String(120), nullable=False)
    portion_grams: Mapped[float | None] = mapped_column(Float, nullable=True)
    energy_kcal: Mapped[float] = mapped_column(Float, nullable=False)
    protein_g: Mapped[float] = mapped_column(Float, nullable=False)
    fat_g: Mapped[float] = mapped_column(Float, nullable=False)
    carbs_g: Mapped[float] = mapped_column(Float, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
