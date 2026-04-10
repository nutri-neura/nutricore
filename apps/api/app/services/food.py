from sqlalchemy.orm import Session

from app.models.food import FoodCategory
from app.repositories.food import list_food_items
from app.repositories.meal_plan import get_meal_plan
from app.services.food_suggestion_engine import build_meal_plan_suggestions


def read_food_catalog(db: Session, category_code: FoodCategory | None = None):
    return list_food_items(db, category_code)


def read_meal_plan_suggestions(db: Session, meal_plan_id: int):
    meal_plan = get_meal_plan(db, meal_plan_id)
    if meal_plan is None:
        return None

    foods = list_food_items(db)
    return build_meal_plan_suggestions(meal_plan, foods)
