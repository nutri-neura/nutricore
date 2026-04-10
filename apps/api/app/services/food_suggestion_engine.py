from __future__ import annotations

from app.models.food import FoodCategory
from app.services.portioning import calculate_portion_plan, get_selection_portion_plan

MAX_CANDIDATES_PER_SLOT = 3

SLOT_CATEGORY_MAP = {
    "protein_base": [FoodCategory.protein, FoodCategory.dairy],
    "main_protein": [FoodCategory.protein],
    "light_protein": [FoodCategory.dairy, FoodCategory.protein],
    "cereal_base": [FoodCategory.carb],
    "starch_base": [FoodCategory.carb],
    "easy_carb": [FoodCategory.fruit, FoodCategory.carb],
    "fruit_optional": [FoodCategory.fruit],
    "light_fat": [FoodCategory.fat],
    "added_fat": [FoodCategory.fat],
    "optional_fat": [FoodCategory.fat],
    "vegetables": [FoodCategory.vegetable],
}

DOMINANT_MACRO_MAP = {
    "protein_base": "protein_g",
    "main_protein": "protein_g",
    "light_protein": "protein_g",
    "cereal_base": "carbs_g",
    "starch_base": "carbs_g",
    "easy_carb": "carbs_g",
    "fruit_optional": "carbs_g",
    "light_fat": "fat_g",
    "added_fat": "fat_g",
    "optional_fat": "fat_g",
}


def normalize_tokens(value: str | None) -> set[str]:
    if not value:
        return set()
    return {token.strip().lower() for token in value.replace(",", " ").split() if token.strip()}


def build_exclusion_tokens(meal_plan_meal) -> set[str]:
    meal_plan = meal_plan_meal.meal_plan
    distribution = meal_plan.distribution if meal_plan else None
    strategy = distribution.strategy if distribution else None
    evaluation = strategy.evaluation if strategy else None
    consultation = evaluation.consultation if evaluation else None
    patient = consultation.patient if consultation else None
    record = patient.record if patient else None
    return normalize_tokens(record.allergies if record else None) | normalize_tokens(
        record.food_preferences if record else None
    )


def score_candidate(food, slot_code: str, meal_plan_meal) -> float:
    if slot_code == "vegetables":
        return abs(food.energy_kcal - 40)

    target_value = {
        "protein_g": meal_plan_meal.protein_target_g,
        "fat_g": meal_plan_meal.fat_target_g,
        "carbs_g": meal_plan_meal.carbs_target_g,
    }[DOMINANT_MACRO_MAP[slot_code]]
    food_value = getattr(food, DOMINANT_MACRO_MAP[slot_code])
    macro_gap = abs(food_value - target_value)
    energy_gap = abs(food.energy_kcal - meal_plan_meal.target_energy_kcal * 0.35)
    return round(macro_gap * 2 + (energy_gap / 25), 2)


def serialize_food(food, score: float, portion_plan: dict | None = None) -> dict:
    payload = {
        "food_id": food.id,
        "name": food.name,
        "category_code": food.category_code.value,
        "portion_label": food.portion_label,
        "energy_kcal": food.energy_kcal,
        "protein_g": food.protein_g,
        "fat_g": food.fat_g,
        "carbs_g": food.carbs_g,
        "fit_score": score,
    }
    if portion_plan is not None:
        payload.update(portion_plan)
    return payload


def build_slot_candidates(meal_plan_meal, foods: list, slot_code: str) -> dict:
    slot = next(
        (item for item in meal_plan_meal.structure_payload if item["slot_code"] == slot_code),
        None,
    )
    if slot is None:
        return {
            "meal_plan_meal_id": meal_plan_meal.id,
            "slot_code": slot_code,
            "recommended_candidate": None,
            "selected_food": None,
            "candidates": [],
        }

    exclusions = build_exclusion_tokens(meal_plan_meal)
    categories = SLOT_CATEGORY_MAP.get(slot_code, [])
    ranked_candidates: list[dict] = []
    for food in foods:
        if food.category_code not in categories:
            continue
        if any(token in food.name.lower() for token in exclusions):
            continue
        ranked_candidates.append(
            serialize_food(
                food,
                score_candidate(food, slot_code, meal_plan_meal),
                calculate_portion_plan(food, meal_plan_meal, slot_code),
            )
        )

    ranked_candidates.sort(key=lambda item: (item["fit_score"], item["name"]))
    ranked_candidates = ranked_candidates[:MAX_CANDIDATES_PER_SLOT]

    selected_selection = next(
        (
            selection
            for selection in meal_plan_meal.slot_selections
            if selection.slot_code == slot_code
        ),
        None,
    )
    selected_food = (
        serialize_food(
            selected_selection.food_item,
            0.0,
            get_selection_portion_plan(selected_selection, meal_plan_meal, slot_code),
        )
        if selected_selection
        else None
    )
    recommended_candidate = ranked_candidates[0] if ranked_candidates else None

    return {
        "meal_plan_meal_id": meal_plan_meal.id,
        "slot_code": slot_code,
        "recommended_candidate": recommended_candidate,
        "selected_food": selected_food,
        "candidates": ranked_candidates,
    }


def build_meal_plan_suggestions(meal_plan, foods: list) -> dict:
    meals: list[dict] = []
    for meal in meal_plan.meals:
        slots: list[dict] = []
        for slot in meal.structure_payload:
            slot_payload = build_slot_candidates(meal, foods, slot["slot_code"])
            slots.append(
                {
                    "slot_code": slot["slot_code"],
                    "label": slot["label"],
                    "guidance": slot["guidance"],
                    "recommended_candidate": slot_payload["recommended_candidate"],
                    "selected_food": slot_payload["selected_food"],
                    "candidates": slot_payload["candidates"],
                }
            )

        meals.append(
            {
                "id": meal.id,
                "meal_code": meal.meal_code,
                "label": meal.label,
                "target_energy_kcal": meal.target_energy_kcal,
                "protein_target_g": meal.protein_target_g,
                "fat_target_g": meal.fat_target_g,
                "carbs_target_g": meal.carbs_target_g,
                "slots": slots,
            }
        )

    return {
        "meal_plan_id": meal_plan.id,
        "warnings": [
            "Suggested portions are operational estimates, not final prescription grams",
            "Clinician review is required before converting candidates into a final menu",
        ],
        "meals": meals,
    }
