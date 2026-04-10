from __future__ import annotations

from app.models.meal_plan import MealPlanStatus
from app.repositories.meal_plan import get_meal_plan
from app.services.portioning import get_selection_portion_plan


def _round(value: float) -> float:
    return round(value, 2)


def _serialize_food(food, portion_plan: dict) -> dict:
    payload = {
        "food_id": food.id,
        "name": food.name,
        "category_code": food.category_code.value,
        "portion_label": food.portion_label,
        "energy_kcal": food.energy_kcal,
        "protein_g": food.protein_g,
        "fat_g": food.fat_g,
        "carbs_g": food.carbs_g,
    }
    payload.update(portion_plan)
    return payload


def _build_meal_payload(meal) -> dict:
    selected_by_slot = {
        selection.slot_code: selection.food_item for selection in meal.slot_selections
    }
    slots: list[dict] = []
    pending_slots: list[str] = []
    selected_energy_kcal = 0.0
    selected_protein_g = 0.0
    selected_fat_g = 0.0
    selected_carbs_g = 0.0

    for slot in meal.structure_payload:
        selected_food = selected_by_slot.get(slot["slot_code"])
        if selected_food is None:
            pending_slots.append(slot["label"])
        else:
            selection = next(
                item for item in meal.slot_selections if item.slot_code == slot["slot_code"]
            )
            portion_plan = get_selection_portion_plan(selection, meal, slot["slot_code"])
            selected_energy_kcal += portion_plan["adjusted_energy_kcal"]
            selected_protein_g += portion_plan["adjusted_protein_g"]
            selected_fat_g += portion_plan["adjusted_fat_g"]
            selected_carbs_g += portion_plan["adjusted_carbs_g"]
        selected_payload = None
        if selected_food is not None:
            selection = next(
                item for item in meal.slot_selections if item.slot_code == slot["slot_code"]
            )
            selected_payload = _serialize_food(
                selected_food,
                get_selection_portion_plan(selection, meal, slot["slot_code"]),
            )

        slots.append(
            {
                "slot_code": slot["slot_code"],
                "label": slot["label"],
                "guidance": slot["guidance"],
                "status": "selected" if selected_food is not None else "pending",
                "selected_food": selected_payload,
            }
        )

    total_slots = len(slots)
    covered_slots = total_slots - len(pending_slots)
    completion_pct = 0.0 if total_slots == 0 else _round((covered_slots / total_slots) * 100)

    return {
        "meal_plan_meal_id": meal.id,
        "meal_code": meal.meal_code,
        "label": meal.label,
        "target_energy_kcal": meal.target_energy_kcal,
        "protein_target_g": meal.protein_target_g,
        "fat_target_g": meal.fat_target_g,
        "carbs_target_g": meal.carbs_target_g,
        "selected_energy_kcal": _round(selected_energy_kcal),
        "selected_protein_g": _round(selected_protein_g),
        "selected_fat_g": _round(selected_fat_g),
        "selected_carbs_g": _round(selected_carbs_g),
        "covered_slots": covered_slots,
        "total_slots": total_slots,
        "completion_pct": completion_pct,
        "pending_slots": pending_slots,
        "slots": slots,
    }


def read_daily_menu(db, *, meal_plan_id: int):
    meal_plan = get_meal_plan(db, meal_plan_id)
    if meal_plan is None:
        return None

    meals = [_build_meal_payload(meal) for meal in meal_plan.meals]
    total_slots = sum(item["total_slots"] for item in meals)
    selected_slots = sum(item["covered_slots"] for item in meals)
    pending_slots = total_slots - selected_slots
    completion_pct = 0.0 if total_slots == 0 else _round((selected_slots / total_slots) * 100)

    if selected_slots == 0:
        status = "empty"
    elif pending_slots == 0:
        status = "complete"
    else:
        status = "partial"

    warnings = [
        "Daily menu totals now reflect the suggested portion estimate for each selected slot",
    ]
    if pending_slots > 0:
        warnings.append("Pending slots mean the day is still incomplete")
    if meal_plan.status not in {MealPlanStatus.finalized, MealPlanStatus.ready_for_export}:
        warnings.append("Final portions still require clinician review")

    return {
        "meal_plan_id": meal_plan.id,
        "status": status,
        "total_slots": total_slots,
        "selected_slots": selected_slots,
        "pending_slots": pending_slots,
        "completion_pct": completion_pct,
        "target_energy_kcal": _round(sum(item.target_energy_kcal for item in meal_plan.meals)),
        "selected_energy_kcal": _round(sum(item["selected_energy_kcal"] for item in meals)),
        "target_protein_g": _round(sum(item.protein_target_g for item in meal_plan.meals)),
        "selected_protein_g": _round(sum(item["selected_protein_g"] for item in meals)),
        "target_fat_g": _round(sum(item.fat_target_g for item in meal_plan.meals)),
        "selected_fat_g": _round(sum(item["selected_fat_g"] for item in meals)),
        "target_carbs_g": _round(sum(item.carbs_target_g for item in meal_plan.meals)),
        "selected_carbs_g": _round(sum(item["selected_carbs_g"] for item in meals)),
        "warnings": warnings,
        "meals": meals,
    }
