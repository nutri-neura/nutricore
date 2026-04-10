from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.slot_selection import (
    SlotCandidatesRead,
    SlotSelectionCreate,
    SlotSelectionRead,
    SlotSelectionUpdate,
)
from app.services.slot_selection import (
    get_slot_candidates,
    select_food_for_slot,
    update_slot_selection,
)

router = APIRouter()


@router.get("/meal-plan-meals/{meal_plan_meal_id}/candidates", response_model=SlotCandidatesRead)
def read_meal_plan_meal_candidates(
    meal_plan_meal_id: int,
    slot_code: str = Query(...),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    payload = get_slot_candidates(db, meal_plan_meal_id=meal_plan_meal_id, slot_code=slot_code)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan meal not found",
        )

    return SlotCandidatesRead.model_validate(payload)


@router.post(
    "/meal-plan-meals/{meal_plan_meal_id}/slot-selections",
    response_model=SlotSelectionRead,
)
def create_slot_selection(
    meal_plan_meal_id: int,
    payload: SlotSelectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    selection = select_food_for_slot(
        db,
        meal_plan_meal_id=meal_plan_meal_id,
        slot_code=payload.slot_code,
        food_item_id=payload.food_item_id,
        created_by_user_id=current_user.id,
    )
    if selection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan meal not found",
        )
    if selection is False:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Food item is not valid for this slot",
    )

    return SlotSelectionRead.model_validate(selection)


@router.put(
    "/meal-plan-meals/{meal_plan_meal_id}/slot-selections/{slot_code}",
    response_model=SlotSelectionRead,
)
def update_slot_selection_route(
    meal_plan_meal_id: int,
    slot_code: str,
    payload: SlotSelectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    selection = update_slot_selection(
        db,
        meal_plan_meal_id=meal_plan_meal_id,
        slot_code=slot_code,
        portion_multiplier=payload.portion_multiplier,
        final_portion_text=payload.final_portion_text,
        notes=payload.notes,
        created_by_user_id=current_user.id,
    )
    if selection is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan meal not found",
        )
    if selection is False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Slot selection not found",
        )

    return SlotSelectionRead.model_validate(selection)
