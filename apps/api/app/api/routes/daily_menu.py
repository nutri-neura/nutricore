from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.daily_menu import DailyMenuRead
from app.services.daily_menu import read_daily_menu

router = APIRouter()


@router.get("/meal-plans/{meal_plan_id}/daily-menu", response_model=DailyMenuRead)
def read_daily_menu_for_meal_plan(
    meal_plan_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    payload = read_daily_menu(db, meal_plan_id=meal_plan_id)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal plan not found")

    return DailyMenuRead.model_validate(payload)
