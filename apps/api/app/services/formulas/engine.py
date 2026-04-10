from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import pow

from app.models.consultation import Consultation
from app.models.patient import PatientSex

FORMULA_SET_VERSION = "adult_ambulatory_v1"
EQUATION_SELECTION_POLICY = "adult_noncritical_default_mifflin_st_jeor"


class FormulaInputError(ValueError):
    def __init__(self, missing_fields: list[str]):
        self.missing_fields = missing_fields
        super().__init__("Missing required fields for evaluation")


@dataclass(slots=True)
class FormulaExecution:
    formula_code: str
    formula_version: str
    formula_family: str
    input_payload: dict
    output_payload: dict
    source_note: str | None = None


def calculate_age_years(birth_date: date, on_date: date) -> int:
    years = on_date.year - birth_date.year
    before_birthday = (on_date.month, on_date.day) < (birth_date.month, birth_date.day)
    return years - int(before_birthday)


def normalize_activity_level(activity_level: str) -> str:
    normalized = activity_level.strip().lower().replace(" ", "_")
    aliases = {
        "sedentario": "sedentary",
        "sedentary": "sedentary",
        "bajo_activo": "low_active",
        "low_active": "low_active",
        "moderado": "active",
        "active": "active",
        "muy_activo": "very_active",
        "very_active": "very_active",
    }
    return aliases.get(normalized, normalized)


def ensure_required_inputs(consultation: Consultation) -> dict:
    patient = consultation.patient
    measurement = consultation.measurement
    missing_fields: list[str] = []

    if patient is None:
        missing_fields.append("patient")
    if measurement is None:
        missing_fields.append("measurement")

    if missing_fields:
        raise FormulaInputError(missing_fields)

    required = {
        "patient.sex": patient.sex,
        "patient.birth_date": patient.birth_date,
        "measurement.weight_kg": measurement.weight_kg,
        "measurement.height_cm": measurement.height_cm,
        "measurement.activity_level": measurement.activity_level,
    }

    missing_fields = [key for key, value in required.items() if value in (None, "")]
    if missing_fields:
        raise FormulaInputError(missing_fields)

    return {
        "sex": patient.sex.value if isinstance(patient.sex, PatientSex) else str(patient.sex),
        "birth_date": patient.birth_date,
        "weight_kg": float(measurement.weight_kg),
        "height_cm": float(measurement.height_cm),
        "activity_level": normalize_activity_level(str(measurement.activity_level)),
        "consultation_date": consultation.consultation_date,
    }


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    height_m = height_cm / 100
    return round(weight_kg / pow(height_m, 2), 2)


def calculate_mifflin_st_jeor(
    *,
    sex: str,
    age_years: int,
    weight_kg: float,
    height_cm: float,
) -> float:
    base = 9.99 * weight_kg + 6.25 * height_cm - 4.92 * age_years
    return round(base + (5 if sex == "male" else -161), 2)


def calculate_activity_factor(*, sex: str, activity_level: str) -> float:
    table = {
        "male": {
            "sedentary": 1.00,
            "low_active": 1.11,
            "active": 1.25,
            "very_active": 1.48,
        },
        "female": {
            "sedentary": 1.00,
            "low_active": 1.12,
            "active": 1.27,
            "very_active": 1.45,
        },
    }

    sex_table = table.get(sex)
    if sex_table is None or activity_level not in sex_table:
        raise FormulaInputError(["measurement.activity_level"])

    return sex_table[activity_level]


def execute_formula_set(consultation: Consultation) -> tuple[dict, list[str], list[dict]]:
    payload = ensure_required_inputs(consultation)
    age_years = calculate_age_years(payload["birth_date"], payload["consultation_date"])
    bmi = calculate_bmi(payload["weight_kg"], payload["height_cm"])
    resting_energy_kcal = calculate_mifflin_st_jeor(
        sex=payload["sex"],
        age_years=age_years,
        weight_kg=payload["weight_kg"],
        height_cm=payload["height_cm"],
    )
    activity_factor = calculate_activity_factor(
        sex=payload["sex"],
        activity_level=payload["activity_level"],
    )
    maintenance_energy_kcal = round(resting_energy_kcal * activity_factor, 2)

    formula_results = [
        FormulaExecution(
            formula_code="body_mass_index",
            formula_version="v1",
            formula_family="anthropometry",
            input_payload={
                "weight_kg": payload["weight_kg"],
                "height_cm": payload["height_cm"],
            },
            output_payload={"bmi": bmi},
            source_note="Derived anthropometric calculation",
        ),
        FormulaExecution(
            formula_code="mifflin_st_jeor",
            formula_version="v1",
            formula_family="resting_energy",
            input_payload={
                "sex": payload["sex"],
                "age_years": age_years,
                "weight_kg": payload["weight_kg"],
                "height_cm": payload["height_cm"],
            },
            output_payload={"resting_energy_kcal": resting_energy_kcal},
            source_note="Mifflin-St Jeor (1990)",
        ),
        FormulaExecution(
            formula_code="activity_factor",
            formula_version="v1",
            formula_family="activity_adjustment",
            input_payload={
                "sex": payload["sex"],
                "activity_level": payload["activity_level"],
            },
            output_payload={"activity_factor": activity_factor},
            source_note="MVP maintenance factor table for ambulatory adults",
        ),
        FormulaExecution(
            formula_code="maintenance_energy",
            formula_version="v1",
            formula_family="total_energy",
            input_payload={
                "resting_energy_kcal": resting_energy_kcal,
                "activity_factor": activity_factor,
            },
            output_payload={"maintenance_energy_kcal": maintenance_energy_kcal},
            source_note="RMR multiplied by activity factor",
        ),
    ]

    summary = {
        "age_years": age_years,
        "bmi": bmi,
        "resting_energy_kcal": resting_energy_kcal,
        "activity_factor": activity_factor,
        "maintenance_energy_kcal": maintenance_energy_kcal,
        "formula_set_version": FORMULA_SET_VERSION,
        "equation_selection_policy": EQUATION_SELECTION_POLICY,
    }

    warnings = [
        "MVP scope: adults ambulatorios no criticos",
        "This estimate is a planning baseline, not a final meal plan prescription",
    ]

    return (
        summary,
        warnings,
        [
            {
                "formula_code": item.formula_code,
                "formula_version": item.formula_version,
                "formula_family": item.formula_family,
                "input_payload": item.input_payload,
                "output_payload": item.output_payload,
                "source_note": item.source_note,
            }
            for item in formula_results
        ],
    )
