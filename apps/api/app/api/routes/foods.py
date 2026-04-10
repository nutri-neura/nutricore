from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.food import FoodCategory
from app.models.user import User
from app.schemas.food import FoodItemRead, MealPlanSuggestionsRead
from app.services.food import read_food_catalog, read_meal_plan_suggestions

router = APIRouter()


@router.get("/foods", response_model=list[FoodItemRead])
def read_foods(
    category_code: FoodCategory | None = Query(default=None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    foods = read_food_catalog(db, category_code)
    return [FoodItemRead.model_validate(item) for item in foods]


@router.get("/meal-plans/{meal_plan_id}/suggestions", response_model=MealPlanSuggestionsRead)
def read_suggestions_for_meal_plan(
    meal_plan_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    payload = read_meal_plan_suggestions(db, meal_plan_id)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal plan not found")

    return MealPlanSuggestionsRead.model_validate(payload)
