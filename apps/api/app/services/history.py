from __future__ import annotations

from app.repositories.patient import get_patient_with_history


def _round(value: float | None) -> float | None:
    if value is None:
        return None
    return round(value, 2)


def _latest_by_id(items: list):
    if not items:
        return None
    return sorted(
        items,
        key=lambda item: (getattr(item, "created_at", None), item.id),
        reverse=True,
    )[0]


def _plan_completion(plan) -> tuple[int, int, float]:
    total_slots = sum(len(meal.structure_payload) for meal in plan.meals)
    selected_slots = sum(len(meal.slot_selections) for meal in plan.meals)
    completion_pct = 0.0 if total_slots == 0 else round((selected_slots / total_slots) * 100, 2)
    return selected_slots, total_slots, completion_pct


def read_patient_history(db, *, patient_id: int):
    patient = get_patient_with_history(db, patient_id)
    if patient is None:
        return None

    consultations = sorted(
        patient.consultations,
        key=lambda item: (item.consultation_date, item.id),
        reverse=True,
    )

    snapshots: list[dict] = []
    for consultation in consultations:
        evaluation = _latest_by_id(consultation.evaluations)
        strategy = _latest_by_id(evaluation.strategies) if evaluation is not None else None
        distribution = _latest_by_id(strategy.meal_distributions) if strategy is not None else None
        meal_plan = _latest_by_id(distribution.meal_plans) if distribution is not None else None

        current_snapshot = {
            "weight_kg": consultation.measurement.weight_kg if consultation.measurement else None,
            "bmi": (
                evaluation.summary_payload.get("bmi")
                if evaluation is not None
                else None
            ),
            "maintenance_energy_kcal": (
                evaluation.summary_payload.get("maintenance_energy_kcal")
                if evaluation is not None
                else None
            ),
            "target_energy_kcal": (
                strategy.recommendation_payload.get("target_energy_kcal")
                if strategy is not None
                else None
            ),
            "protein_g": (
                strategy.recommendation_payload.get("protein_g")
                if strategy is not None
                else None
            ),
            "fat_g": (
                strategy.recommendation_payload.get("fat_g")
                if strategy is not None
                else None
            ),
            "carbs_g": (
                strategy.recommendation_payload.get("carbs_g")
                if strategy is not None
                else None
            ),
        }

        plan_snapshot = None
        if meal_plan is not None:
            selected_slots, total_slots, completion_pct = _plan_completion(meal_plan)
            plan_snapshot = {
                "id": meal_plan.id,
                "created_at": meal_plan.created_at,
                "status": meal_plan.status.value,
                "pattern_code": (
                    distribution.pattern_code.value if distribution is not None else None
                ),
                "completion_pct": completion_pct,
                "selected_slots": selected_slots,
                "total_slots": total_slots,
            }

        snapshots.append(
            {
                "consultation_id": consultation.id,
                "consultation_date": consultation.consultation_date,
                "reason": consultation.reason,
                "measurement": (
                    {
                        "weight_kg": consultation.measurement.weight_kg,
                        "height_cm": consultation.measurement.height_cm,
                        "activity_level": consultation.measurement.activity_level,
                    }
                    if consultation.measurement is not None
                    else None
                ),
                "evaluation": (
                    {
                        "id": evaluation.id,
                        "created_at": evaluation.created_at,
                        "formula_set_version": evaluation.formula_set_version,
                        "bmi": _round(evaluation.summary_payload.get("bmi")),
                        "resting_energy_kcal": _round(
                            evaluation.summary_payload.get("resting_energy_kcal")
                        ),
                        "maintenance_energy_kcal": _round(
                            evaluation.summary_payload.get("maintenance_energy_kcal")
                        ),
                    }
                    if evaluation is not None
                    else None
                ),
                "strategy": (
                    {
                        "id": strategy.id,
                        "created_at": strategy.created_at,
                        "goal_code": strategy.goal_code.value,
                        "target_energy_kcal": _round(
                            strategy.recommendation_payload.get("target_energy_kcal")
                        ),
                        "protein_g": _round(strategy.recommendation_payload.get("protein_g")),
                        "fat_g": _round(strategy.recommendation_payload.get("fat_g")),
                        "carbs_g": _round(strategy.recommendation_payload.get("carbs_g")),
                    }
                    if strategy is not None
                    else None
                ),
                "meal_plan": plan_snapshot,
                "delta_vs_previous": None,
                "_current_snapshot": current_snapshot,
            }
        )

    items: list[dict] = []
    for index, item in enumerate(snapshots):
        next_item = snapshots[index + 1] if index + 1 < len(snapshots) else None
        delta_vs_previous = None
        if next_item is not None:
            current_snapshot = item["_current_snapshot"]
            previous_snapshot = next_item["_current_snapshot"]
            delta_vs_previous = {
                key: _round(current_snapshot[key] - previous_snapshot[key])
                if current_snapshot[key] is not None and previous_snapshot[key] is not None
                else None
                for key in current_snapshot
            }

        normalized_item = {key: value for key, value in item.items() if key != "_current_snapshot"}
        normalized_item["delta_vs_previous"] = delta_vs_previous
        items.append(normalized_item)

    return {
        "patient_id": patient.id,
        "patient_name": f"{patient.first_name} {patient.last_name}",
        "consultation_count": len(consultations),
        "latest_consultation_date": consultations[0].consultation_date if consultations else None,
        "items": items,
    }
