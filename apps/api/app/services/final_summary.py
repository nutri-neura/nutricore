from __future__ import annotations

from app.models.meal_plan import MealPlanStatus
from app.repositories.meal_plan import get_meal_plan
from app.services.daily_menu import read_daily_menu


def read_final_summary(db, *, meal_plan_id: int):
    meal_plan = get_meal_plan(db, meal_plan_id)
    if meal_plan is None:
        return None

    daily_menu = read_daily_menu(db, meal_plan_id=meal_plan_id)
    if daily_menu is None:
        return None

    evaluation = meal_plan.distribution.strategy.evaluation
    consultation = evaluation.consultation
    patient = consultation.patient

    meals: list[dict] = []
    for meal in daily_menu["meals"]:
        slots: list[dict] = []
        for slot in meal["slots"]:
            selected_food = slot["selected_food"]
            slots.append(
                {
                    "slot_code": slot["slot_code"],
                    "label": slot["label"],
                    "guidance": slot["guidance"],
                    "status": slot["status"],
                    "food_name": selected_food["name"] if selected_food else None,
                    "portion_text": (
                        selected_food["suggested_portion_text"] if selected_food else None
                    ),
                    "adjusted_energy_kcal": (
                        selected_food["adjusted_energy_kcal"] if selected_food else None
                    ),
                    "adjusted_protein_g": (
                        selected_food["adjusted_protein_g"] if selected_food else None
                    ),
                    "adjusted_fat_g": selected_food["adjusted_fat_g"] if selected_food else None,
                    "adjusted_carbs_g": (
                        selected_food["adjusted_carbs_g"] if selected_food else None
                    ),
                    "notes": selected_food["notes"] if selected_food else None,
                }
            )

        meals.append(
            {
                "meal_plan_meal_id": meal["meal_plan_meal_id"],
                "meal_code": meal["meal_code"],
                "label": meal["label"],
                "completion_pct": meal["completion_pct"],
                "target_energy_kcal": meal["target_energy_kcal"],
                "selected_energy_kcal": meal["selected_energy_kcal"],
                "target_protein_g": meal["protein_target_g"],
                "selected_protein_g": meal["selected_protein_g"],
                "target_fat_g": meal["fat_target_g"],
                "selected_fat_g": meal["selected_fat_g"],
                "target_carbs_g": meal["carbs_target_g"],
                "selected_carbs_g": meal["selected_carbs_g"],
                "pending_slots": meal["pending_slots"],
                "slots": slots,
            }
        )

    warnings = list(daily_menu["warnings"])
    if daily_menu["pending_slots"] > 0:
        warnings.append("The plan cannot be finalized while there are pending slots")
    if meal_plan.status != MealPlanStatus.ready_for_export:
        warnings.append("The plan is still internal until it is marked ready for export")

    return {
        "meal_plan_id": meal_plan.id,
        "status": meal_plan.status.value,
        "export_ready": meal_plan.status == MealPlanStatus.ready_for_export,
        "consultation_id": consultation.id,
        "consultation_date": consultation.consultation_date.isoformat(),
        "patient": {
            "id": patient.id,
            "full_name": f"{patient.first_name} {patient.last_name}",
            "sex": patient.sex.value,
            "birth_date": patient.birth_date.isoformat(),
        },
        "goal_code": meal_plan.distribution.strategy.goal_code.value,
        "pattern_code": meal_plan.distribution.pattern_code.value,
        "plan_notes": meal_plan.notes,
        "completion_pct": daily_menu["completion_pct"],
        "total_slots": daily_menu["total_slots"],
        "selected_slots": daily_menu["selected_slots"],
        "pending_slots": daily_menu["pending_slots"],
        "target_energy_kcal": daily_menu["target_energy_kcal"],
        "selected_energy_kcal": daily_menu["selected_energy_kcal"],
        "target_protein_g": daily_menu["target_protein_g"],
        "selected_protein_g": daily_menu["selected_protein_g"],
        "target_fat_g": daily_menu["target_fat_g"],
        "selected_fat_g": daily_menu["selected_fat_g"],
        "target_carbs_g": daily_menu["target_carbs_g"],
        "selected_carbs_g": daily_menu["selected_carbs_g"],
        "warnings": warnings,
        "meals": meals,
    }
