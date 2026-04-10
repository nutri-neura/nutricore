from __future__ import annotations

import re

ROUNDING_STEP = 0.25
MIN_MULTIPLIER = 0.5
MAX_MULTIPLIER = 3.0
AUTO_PORTION_TEXT_PATTERN = re.compile(r"^(?P<multiplier>\d+(?:\.\d+)?) x ")

DOMINANT_METRIC_MAP = {
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

SLOT_TARGET_SHARE = {
    "protein_base": {"protein_g": 0.55, "energy": 0.3},
    "main_protein": {"protein_g": 0.6, "energy": 0.35},
    "light_protein": {"protein_g": 0.35, "energy": 0.18},
    "cereal_base": {"carbs_g": 0.45, "energy": 0.28},
    "starch_base": {"carbs_g": 0.5, "energy": 0.32},
    "easy_carb": {"carbs_g": 0.25, "energy": 0.12},
    "fruit_optional": {"carbs_g": 0.2, "energy": 0.1},
    "light_fat": {"fat_g": 0.35, "energy": 0.12},
    "added_fat": {"fat_g": 0.45, "energy": 0.16},
    "optional_fat": {"fat_g": 0.3, "energy": 0.1},
    "vegetables": {"energy": 40.0},
}


def _round(value: float) -> float:
    return round(value, 2)


def _round_to_step(value: float, step: float = ROUNDING_STEP) -> float:
    return round(value / step) * step


def clamp_portion_multiplier(value: float) -> float:
    return min(max(_round(value), MIN_MULTIPLIER), MAX_MULTIPLIER)


def build_portion_text(food, portion_multiplier: float) -> tuple[str, float | None]:
    safe_multiplier = clamp_portion_multiplier(portion_multiplier)
    suggested_portion_grams = (
        _round(food.portion_grams * safe_multiplier) if food.portion_grams is not None else None
    )
    suggested_portion_text = (
        f"{safe_multiplier} x {food.portion_label}"
        if suggested_portion_grams is None
        else f"{safe_multiplier} x {food.portion_label} (~{suggested_portion_grams} g)"
    )
    return suggested_portion_text, suggested_portion_grams


def resolve_final_portion_text(
    food,
    portion_multiplier: float,
    final_portion_text: str | None,
) -> str:
    generated_portion_text, _ = build_portion_text(food, portion_multiplier)
    if final_portion_text is None:
        return generated_portion_text

    cleaned_text = final_portion_text.strip()
    if not cleaned_text:
        return generated_portion_text

    match = AUTO_PORTION_TEXT_PATTERN.match(cleaned_text)
    if match and f" x {food.portion_label}" in cleaned_text:
        text_multiplier = clamp_portion_multiplier(float(match.group("multiplier")))
        current_multiplier = clamp_portion_multiplier(portion_multiplier)
        if text_multiplier != current_multiplier:
            return generated_portion_text

    return cleaned_text


def _meal_macro_targets(meal_plan_meal) -> dict[str, float]:
    return {
        "protein_g": meal_plan_meal.protein_target_g,
        "fat_g": meal_plan_meal.fat_target_g,
        "carbs_g": meal_plan_meal.carbs_target_g,
        "energy": meal_plan_meal.target_energy_kcal,
    }


def estimate_slot_target(meal_plan_meal, slot_code: str) -> dict[str, float | str]:
    share_config = SLOT_TARGET_SHARE.get(
        slot_code,
        {"energy": meal_plan_meal.target_energy_kcal * 0.2},
    )
    meal_targets = _meal_macro_targets(meal_plan_meal)
    if slot_code == "vegetables":
        return {"metric": "energy", "target_value": float(share_config["energy"])}

    metric = DOMINANT_METRIC_MAP.get(slot_code, "carbs_g")
    raw_share = share_config.get(metric, 0.25)
    return {
        "metric": metric,
        "target_value": meal_targets[metric] * raw_share,
        "energy_target": meal_targets["energy"] * share_config.get("energy", 0.2),
    }


def calculate_portion_plan(food, meal_plan_meal, slot_code: str) -> dict:
    slot_target = estimate_slot_target(meal_plan_meal, slot_code)
    metric = str(slot_target["metric"])
    target_value = float(slot_target["target_value"])
    base_value = food.energy_kcal if metric == "energy" else getattr(food, metric)

    if base_value <= 0:
        raw_multiplier = 1.0
    else:
        raw_multiplier = target_value / base_value

    rounded_multiplier = _round_to_step(raw_multiplier)
    clamped = rounded_multiplier < MIN_MULTIPLIER or rounded_multiplier > MAX_MULTIPLIER
    portion_multiplier = clamp_portion_multiplier(rounded_multiplier)

    adjusted_energy_kcal = food.energy_kcal * portion_multiplier
    adjusted_protein_g = food.protein_g * portion_multiplier
    adjusted_fat_g = food.fat_g * portion_multiplier
    adjusted_carbs_g = food.carbs_g * portion_multiplier
    adjusted_value = adjusted_energy_kcal if metric == "energy" else {
        "protein_g": adjusted_protein_g,
        "fat_g": adjusted_fat_g,
        "carbs_g": adjusted_carbs_g,
    }[metric]

    gap = abs(adjusted_value - target_value)
    fit_status = "aligned"
    warnings: list[str] = []

    if clamped:
        fit_status = "clamped"
        warnings.append("Suggested portion hit the operational MVP limit")
    elif target_value > 0 and (gap / target_value) > 0.35:
        fit_status = "wide_gap"
        warnings.append("Selected food still sits far from the slot target")

    suggested_portion_text, suggested_portion_grams = build_portion_text(food, portion_multiplier)

    return {
        "portion_multiplier": clamp_portion_multiplier(portion_multiplier),
        "suggested_portion_grams": suggested_portion_grams,
        "suggested_portion_text": suggested_portion_text,
        "adjusted_energy_kcal": _round(adjusted_energy_kcal),
        "adjusted_protein_g": _round(adjusted_protein_g),
        "adjusted_fat_g": _round(adjusted_fat_g),
        "adjusted_carbs_g": _round(adjusted_carbs_g),
        "fit_status": fit_status,
        "target_metric": metric,
        "target_value": _round(target_value),
        "gap_value": _round(gap),
        "warnings": warnings,
        "notes": None,
    }


def calculate_portion_plan_for_multiplier(
    food,
    *,
    portion_multiplier: float,
    final_portion_text: str | None = None,
    notes: str | None = None,
) -> dict:
    safe_multiplier = clamp_portion_multiplier(portion_multiplier)
    suggested_portion_text, suggested_portion_grams = build_portion_text(food, safe_multiplier)
    suggested_portion_text = resolve_final_portion_text(food, safe_multiplier, final_portion_text)
    return {
        "portion_multiplier": safe_multiplier,
        "suggested_portion_grams": suggested_portion_grams,
        "suggested_portion_text": suggested_portion_text,
        "adjusted_energy_kcal": _round(food.energy_kcal * safe_multiplier),
        "adjusted_protein_g": _round(food.protein_g * safe_multiplier),
        "adjusted_fat_g": _round(food.fat_g * safe_multiplier),
        "adjusted_carbs_g": _round(food.carbs_g * safe_multiplier),
        "fit_status": "manual",
        "target_metric": "manual",
        "target_value": _round(safe_multiplier),
        "gap_value": 0.0,
        "warnings": ["Manual portion override applied"] if notes else [],
        "notes": notes,
    }


def get_selection_portion_plan(selection, meal_plan_meal, slot_code: str) -> dict:
    if selection.adjusted_energy_kcal is None:
        return calculate_portion_plan(selection.food_item, meal_plan_meal, slot_code)

    resolved_portion_text = resolve_final_portion_text(
        selection.food_item,
        selection.portion_multiplier,
        selection.final_portion_text,
    )
    _, suggested_portion_grams = build_portion_text(
        selection.food_item,
        selection.portion_multiplier,
    )

    return {
        "portion_multiplier": _round(selection.portion_multiplier),
        "suggested_portion_grams": suggested_portion_grams,
        "suggested_portion_text": resolved_portion_text,
        "adjusted_energy_kcal": _round(selection.adjusted_energy_kcal),
        "adjusted_protein_g": _round(selection.adjusted_protein_g or 0.0),
        "adjusted_fat_g": _round(selection.adjusted_fat_g or 0.0),
        "adjusted_carbs_g": _round(selection.adjusted_carbs_g or 0.0),
        "fit_status": "finalized",
        "target_metric": "manual",
        "target_value": _round(selection.portion_multiplier),
        "gap_value": 0.0,
        "warnings": [selection.notes] if selection.notes else [],
        "notes": selection.notes,
    }
