from __future__ import annotations

from app.models.strategy import StrategyGoal

STRATEGY_SET_VERSION = "adult_ambulatory_strategy_v1"

ENERGY_ADJUSTMENTS = {
    StrategyGoal.maintenance: 1.00,
    StrategyGoal.fat_loss: 0.85,
    StrategyGoal.muscle_gain: 1.10,
}

PROTEIN_G_PER_KG = {
    StrategyGoal.maintenance: 1.6,
    StrategyGoal.fat_loss: 1.8,
    StrategyGoal.muscle_gain: 1.8,
    StrategyGoal.recomposition: 2.0,
}

FAT_G_PER_KG = {
    StrategyGoal.maintenance: 0.8,
    StrategyGoal.fat_loss: 0.8,
    StrategyGoal.muscle_gain: 0.9,
    StrategyGoal.recomposition: 0.8,
}

ENERGY_FLOOR_BY_SEX = {
    "female": 1200.0,
    "male": 1400.0,
}


class StrategyInputError(ValueError):
    def __init__(self, missing_fields: list[str]):
        self.missing_fields = missing_fields
        super().__init__(", ".join(missing_fields))


def round2(value: float) -> float:
    return round(value, 2)


def execute_strategy(evaluation, goal_code: StrategyGoal) -> tuple[dict, list[str]]:
    consultation = evaluation.consultation
    patient = consultation.patient if consultation else None
    measurement = consultation.measurement if consultation else None
    summary = evaluation.summary_payload or {}

    missing_fields: list[str] = []
    maintenance_energy = summary.get("maintenance_energy_kcal")
    bmi = summary.get("bmi")
    sex = patient.sex.value if patient and patient.sex else None
    weight_kg = measurement.weight_kg if measurement else None

    if maintenance_energy is None:
        missing_fields.append("evaluation.summary_payload.maintenance_energy_kcal")
    if sex is None:
        missing_fields.append("patient.sex")
    if weight_kg is None:
        missing_fields.append("measurement.weight_kg")

    if missing_fields:
        raise StrategyInputError(missing_fields)

    warnings = [
        "MVP scope: adults ambulatorios no criticos",
        "This strategy is a planning baseline, not a final meal plan",
    ]

    if goal_code == StrategyGoal.recomposition:
        if bmi is not None and bmi >= 25:
            target_energy = maintenance_energy * 0.95
        else:
            target_energy = maintenance_energy
            warnings.append(
                "Recomposition used maintenance energy because BMI is below 25 in MVP policy."
            )
    else:
        target_energy = maintenance_energy * ENERGY_ADJUSTMENTS[goal_code]

    floor = ENERGY_FLOOR_BY_SEX[sex]
    if target_energy < floor:
        target_energy = floor
        warnings.append(f"Energy floor applied for {sex} MVP policy.")

    protein_g = weight_kg * PROTEIN_G_PER_KG[goal_code]
    fat_g = weight_kg * FAT_G_PER_KG[goal_code]
    protein_kcal = protein_g * 4
    fat_kcal = fat_g * 9
    remaining_kcal = target_energy - protein_kcal - fat_kcal

    if remaining_kcal < 0:
        carbs_kcal = 0.0
        carbs_g = 0.0
        warnings.append("Carbohydrate remainder fell below zero and was clamped to zero.")
    else:
        carbs_kcal = remaining_kcal
        carbs_g = carbs_kcal / 4

    recommendation_payload = {
        "goal_code": goal_code.value,
        "maintenance_energy_kcal": round2(float(maintenance_energy)),
        "target_energy_kcal": round2(float(target_energy)),
        "energy_delta_kcal": round2(float(target_energy - maintenance_energy)),
        "protein_g": round2(float(protein_g)),
        "fat_g": round2(float(fat_g)),
        "carbs_g": round2(float(carbs_g)),
        "protein_kcal": round2(float(protein_kcal)),
        "fat_kcal": round2(float(fat_kcal)),
        "carbs_kcal": round2(float(carbs_kcal)),
        "protein_pct": (
            round2(float((protein_kcal / target_energy) * 100)) if target_energy else 0.0
        ),
        "fat_pct": round2(float((fat_kcal / target_energy) * 100)) if target_energy else 0.0,
        "carbs_pct": round2(float((carbs_kcal / target_energy) * 100)) if target_energy else 0.0,
        "strategy_set_version": STRATEGY_SET_VERSION,
    }
    return recommendation_payload, warnings
