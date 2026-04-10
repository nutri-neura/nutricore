from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.repositories.meal_plan import get_meal_plan, list_meal_plans_for_distribution
from app.schemas.final_summary import FinalSummaryRead
from app.schemas.meal_plan import MealPlanCreate, MealPlanRead, MealPlanUpdate
from app.services.final_summary import read_final_summary
from app.services.meal_plan import (
    MealPlanFinalizationError,
    MealPlanInputError,
    generate_plan_for_distribution,
    revise_meal_plan,
)

router = APIRouter()


@router.post(
    "/distributions/{distribution_id}/meal-plans",
    response_model=MealPlanRead,
    status_code=status.HTTP_201_CREATED,
)
def create_plan_for_distribution(
    distribution_id: int,
    payload: MealPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        meal_plan = generate_plan_for_distribution(
            db,
            distribution_id=distribution_id,
            notes=payload.notes,
            created_by_user_id=current_user.id,
        )
    except MealPlanInputError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Missing required inputs for meal plan",
                "missing_fields": error.missing_fields,
            },
        ) from error

    if meal_plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal distribution not found",
        )

    return MealPlanRead.model_validate(meal_plan)


@router.get("/meal-plans/{meal_plan_id}", response_model=MealPlanRead)
def read_meal_plan(
    meal_plan_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    meal_plan = get_meal_plan(db, meal_plan_id)
    if meal_plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal plan not found")

    return MealPlanRead.model_validate(meal_plan)


@router.get(
    "/distributions/{distribution_id}/meal-plans",
    response_model=list[MealPlanRead],
)
def read_distribution_meal_plans(
    distribution_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    meal_plans = list_meal_plans_for_distribution(db, distribution_id)
    return [MealPlanRead.model_validate(item) for item in meal_plans]


@router.put("/meal-plans/{meal_plan_id}", response_model=MealPlanRead)
def update_meal_plan_route(
    meal_plan_id: int,
    payload: MealPlanUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    try:
        meal_plan = revise_meal_plan(
            db,
            meal_plan_id=meal_plan_id,
            status=payload.status,
            notes=payload.notes,
        )
    except MealPlanFinalizationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Meal plan still has pending slots and cannot be finalized",
        ) from error
    if meal_plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal plan not found")

    return MealPlanRead.model_validate(meal_plan)


@router.get("/meal-plans/{meal_plan_id}/final-summary", response_model=FinalSummaryRead)
def read_meal_plan_final_summary(
    meal_plan_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    payload = read_final_summary(db, meal_plan_id=meal_plan_id)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal plan not found")

    return FinalSummaryRead.model_validate(payload)
