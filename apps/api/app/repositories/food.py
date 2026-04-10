from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.food import FoodCategory, FoodItem


def list_food_items(db: Session, category_code: FoodCategory | None = None) -> list[FoodItem]:
    query: Select[tuple[FoodItem]] = select(FoodItem).where(FoodItem.is_active.is_(True))
    if category_code is not None:
        query = query.where(FoodItem.category_code == category_code)
    query = query.order_by(FoodItem.category_code.asc(), FoodItem.name.asc())
    return list(db.scalars(query))
