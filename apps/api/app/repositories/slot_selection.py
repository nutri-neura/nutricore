from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.consultation import Consultation
from app.models.distribution import MealDistribution
from app.models.evaluation import Evaluation
from app.models.meal_plan import MealPlan, MealPlanMeal
from app.models.patient import Patient
from app.models.slot_selection import MealPlanSlotSelection
from app.models.strategy import NutritionStrategy


def get_meal_plan_meal(db: Session, meal_plan_meal_id: int) -> MealPlanMeal | None:
    return db.scalar(
        select(MealPlanMeal)
        .where(MealPlanMeal.id == meal_plan_meal_id)
        .options(
            joinedload(MealPlanMeal.meal_plan)
            .joinedload(MealPlan.distribution)
            .joinedload(MealDistribution.strategy)
            .joinedload(NutritionStrategy.evaluation)
            .joinedload(Evaluation.consultation)
            .joinedload(Consultation.patient)
            .joinedload(Patient.record),
            joinedload(MealPlanMeal.slot_selections).joinedload(MealPlanSlotSelection.food_item),
        )
    )


def list_slot_selections_for_meal_plan_meal(
    db: Session,
    meal_plan_meal_id: int,
) -> list[MealPlanSlotSelection]:
    return list(
        db.scalars(
            select(MealPlanSlotSelection)
            .where(MealPlanSlotSelection.meal_plan_meal_id == meal_plan_meal_id)
            .options(joinedload(MealPlanSlotSelection.food_item))
        )
    )


def upsert_slot_selection(
    db: Session,
    *,
    meal_plan_meal_id: int,
    slot_code: str,
    food_item_id: int,
    portion_multiplier: float,
    final_portion_text: str | None,
    adjusted_energy_kcal: float,
    adjusted_protein_g: float,
    adjusted_fat_g: float,
    adjusted_carbs_g: float,
    notes: str | None,
    created_by_user_id: int,
) -> MealPlanSlotSelection:
    selection = db.scalar(
        select(MealPlanSlotSelection).where(
            MealPlanSlotSelection.meal_plan_meal_id == meal_plan_meal_id,
            MealPlanSlotSelection.slot_code == slot_code,
        )
    )
    if selection is None:
        selection = MealPlanSlotSelection(
            meal_plan_meal_id=meal_plan_meal_id,
            slot_code=slot_code,
            food_item_id=food_item_id,
            portion_multiplier=portion_multiplier,
            final_portion_text=final_portion_text,
            adjusted_energy_kcal=adjusted_energy_kcal,
            adjusted_protein_g=adjusted_protein_g,
            adjusted_fat_g=adjusted_fat_g,
            adjusted_carbs_g=adjusted_carbs_g,
            notes=notes,
            created_by_user_id=created_by_user_id,
        )
    else:
        selection.food_item_id = food_item_id
        selection.portion_multiplier = portion_multiplier
        selection.final_portion_text = final_portion_text
        selection.adjusted_energy_kcal = adjusted_energy_kcal
        selection.adjusted_protein_g = adjusted_protein_g
        selection.adjusted_fat_g = adjusted_fat_g
        selection.adjusted_carbs_g = adjusted_carbs_g
        selection.notes = notes
        selection.created_by_user_id = created_by_user_id

    db.add(selection)
    db.commit()
    db.refresh(selection)
    return db.scalar(
        select(MealPlanSlotSelection)
        .where(MealPlanSlotSelection.id == selection.id)
        .options(joinedload(MealPlanSlotSelection.food_item))
    )


def get_slot_selection(
    db: Session,
    *,
    meal_plan_meal_id: int,
    slot_code: str,
) -> MealPlanSlotSelection | None:
    return db.scalar(
        select(MealPlanSlotSelection)
        .where(
            MealPlanSlotSelection.meal_plan_meal_id == meal_plan_meal_id,
            MealPlanSlotSelection.slot_code == slot_code,
        )
        .options(joinedload(MealPlanSlotSelection.food_item))
    )
