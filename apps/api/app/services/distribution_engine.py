from __future__ import annotations

from app.models.distribution import MealPattern
from app.models.strategy import StrategyGoal

DISTRIBUTION_SET_VERSION = "adult_ambulatory_distribution_v1"
PATTERN_SELECTION_POLICY = "goal_based_default_distribution_pattern_v1"

DEFAULT_PATTERN_BY_GOAL = {
    StrategyGoal.maintenance: MealPattern.four_meals,
    StrategyGoal.fat_loss: MealPattern.five_meals,
    StrategyGoal.muscle_gain: MealPattern.five_meals,
    StrategyGoal.recomposition: MealPattern.five_meals,
}

PATTERN_TEMPLATES = {
    MealPattern.three_meals: [
        {"meal_code": "breakfast", "label": "Desayuno", "allocation_pct": 0.30},
        {"meal_code": "lunch", "label": "Comida", "allocation_pct": 0.40},
        {"meal_code": "dinner", "label": "Cena", "allocation_pct": 0.30},
    ],
    MealPattern.four_meals: [
        {"meal_code": "breakfast", "label": "Desayuno", "allocation_pct": 0.25},
        {"meal_code": "snack_am", "label": "Colacion AM", "allocation_pct": 0.15},
        {"meal_code": "lunch", "label": "Comida", "allocation_pct": 0.35},
        {"meal_code": "dinner", "label": "Cena", "allocation_pct": 0.25},
    ],
    MealPattern.five_meals: [
        {"meal_code": "breakfast", "label": "Desayuno", "allocation_pct": 0.25},
        {"meal_code": "snack_am", "label": "Colacion AM", "allocation_pct": 0.10},
        {"meal_code": "lunch", "label": "Comida", "allocation_pct": 0.30},
        {"meal_code": "snack_pm", "label": "Colacion PM", "allocation_pct": 0.10},
        {"meal_code": "dinner", "label": "Cena", "allocation_pct": 0.25},
    ],
}


class MealDistributionInputError(ValueError):
    def __init__(self, missing_fields: list[str]):
        self.missing_fields = missing_fields
        super().__init__(", ".join(missing_fields))


def round2(value: float) -> float:
    return round(value, 2)


def execute_meal_distribution(
    strategy,
    pattern_code: MealPattern | None,
) -> tuple[MealPattern, dict, list[str]]:
    recommendation = strategy.recommendation_payload or {}
    missing_fields: list[str] = []

    goal_code = strategy.goal_code
    selected_pattern = pattern_code or DEFAULT_PATTERN_BY_GOAL[goal_code]

    target_energy_kcal = recommendation.get("target_energy_kcal")
    protein_g = recommendation.get("protein_g")
    fat_g = recommendation.get("fat_g")
    carbs_g = recommendation.get("carbs_g")

    if target_energy_kcal is None:
        missing_fields.append("strategy.recommendation_payload.target_energy_kcal")
    if protein_g is None:
        missing_fields.append("strategy.recommendation_payload.protein_g")
    if fat_g is None:
        missing_fields.append("strategy.recommendation_payload.fat_g")
    if carbs_g is None:
        missing_fields.append("strategy.recommendation_payload.carbs_g")

    if missing_fields:
        raise MealDistributionInputError(missing_fields)

    warnings = [
        "MVP scope: daily distribution only, not a complete meal plan",
        "Meal timing percentages are operational defaults for the MVP",
    ]

    meals = []
    for item in PATTERN_TEMPLATES[selected_pattern]:
        allocation_pct = item["allocation_pct"]
        meals.append(
            {
                "meal_code": item["meal_code"],
                "label": item["label"],
                "allocation_pct": round2(float(allocation_pct * 100)),
                "target_energy_kcal": round2(float(target_energy_kcal * allocation_pct)),
                "protein_g": round2(float(protein_g * allocation_pct)),
                "fat_g": round2(float(fat_g * allocation_pct)),
                "carbs_g": round2(float(carbs_g * allocation_pct)),
            }
        )

    recommendation_payload = {
        "goal_code": goal_code.value,
        "pattern_code": selected_pattern.value,
        "pattern_selection_policy": PATTERN_SELECTION_POLICY,
        "target_energy_kcal": round2(float(target_energy_kcal)),
        "protein_g": round2(float(protein_g)),
        "fat_g": round2(float(fat_g)),
        "carbs_g": round2(float(carbs_g)),
        "distribution_set_version": DISTRIBUTION_SET_VERSION,
        "meals": meals,
    }
    return selected_pattern, recommendation_payload, warnings
