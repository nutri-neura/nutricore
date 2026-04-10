from app.repositories.food import list_food_items
from app.repositories.slot_selection import (
    get_meal_plan_meal,
    get_slot_selection,
    upsert_slot_selection,
)
from app.services.food_suggestion_engine import build_slot_candidates
from app.services.portioning import build_portion_text, calculate_portion_plan_for_multiplier


def get_slot_candidates(db, *, meal_plan_meal_id: int, slot_code: str):
    meal_plan_meal = get_meal_plan_meal(db, meal_plan_meal_id)
    if meal_plan_meal is None:
        return None

    foods = list_food_items(db)
    return build_slot_candidates(meal_plan_meal, foods, slot_code)


def select_food_for_slot(
    db,
    *,
    meal_plan_meal_id: int,
    slot_code: str,
    food_item_id: int,
    created_by_user_id: int,
):
    meal_plan_meal = get_meal_plan_meal(db, meal_plan_meal_id)
    if meal_plan_meal is None:
        return None

    foods = {food.id: food for food in list_food_items(db)}
    selected_food = foods.get(food_item_id)
    if selected_food is None:
        return False

    slot_payload = build_slot_candidates(meal_plan_meal, list(foods.values()), slot_code)
    allowed_ids = {candidate["food_id"] for candidate in slot_payload["candidates"]}
    if food_item_id not in allowed_ids:
        return False

    return upsert_slot_selection(
        db,
        meal_plan_meal_id=meal_plan_meal_id,
        slot_code=slot_code,
        food_item_id=food_item_id,
        portion_multiplier=slot_payload["recommended_candidate"]["portion_multiplier"],
        final_portion_text=slot_payload["recommended_candidate"]["suggested_portion_text"],
        adjusted_energy_kcal=slot_payload["recommended_candidate"]["adjusted_energy_kcal"],
        adjusted_protein_g=slot_payload["recommended_candidate"]["adjusted_protein_g"],
        adjusted_fat_g=slot_payload["recommended_candidate"]["adjusted_fat_g"],
        adjusted_carbs_g=slot_payload["recommended_candidate"]["adjusted_carbs_g"],
        notes=None,
        created_by_user_id=created_by_user_id,
    )


def update_slot_selection(
    db,
    *,
    meal_plan_meal_id: int,
    slot_code: str,
    portion_multiplier: float,
    final_portion_text: str | None,
    notes: str | None,
    created_by_user_id: int,
):
    meal_plan_meal = get_meal_plan_meal(db, meal_plan_meal_id)
    if meal_plan_meal is None:
        return None

    selection = get_slot_selection(db, meal_plan_meal_id=meal_plan_meal_id, slot_code=slot_code)
    if selection is None:
        return False

    normalized_portion_text = final_portion_text.strip() if final_portion_text else None
    current_generated_text, _ = build_portion_text(
        selection.food_item,
        selection.portion_multiplier,
    )
    if normalized_portion_text in {None, "", selection.final_portion_text, current_generated_text}:
        normalized_portion_text = None

    portion_plan = calculate_portion_plan_for_multiplier(
        selection.food_item,
        portion_multiplier=portion_multiplier,
        final_portion_text=normalized_portion_text,
        notes=notes,
    )

    return upsert_slot_selection(
        db,
        meal_plan_meal_id=meal_plan_meal_id,
        slot_code=slot_code,
        food_item_id=selection.food_item_id,
        portion_multiplier=portion_plan["portion_multiplier"],
        final_portion_text=portion_plan["suggested_portion_text"],
        adjusted_energy_kcal=portion_plan["adjusted_energy_kcal"],
        adjusted_protein_g=portion_plan["adjusted_protein_g"],
        adjusted_fat_g=portion_plan["adjusted_fat_g"],
        adjusted_carbs_g=portion_plan["adjusted_carbs_g"],
        notes=notes,
        created_by_user_id=created_by_user_id,
    )
