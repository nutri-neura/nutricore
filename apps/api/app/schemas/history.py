from datetime import date, datetime

from pydantic import BaseModel


class HistoryDeltaRead(BaseModel):
    weight_kg: float | None = None
    bmi: float | None = None
    maintenance_energy_kcal: float | None = None
    target_energy_kcal: float | None = None
    protein_g: float | None = None
    fat_g: float | None = None
    carbs_g: float | None = None


class HistoryMeasurementRead(BaseModel):
    weight_kg: float | None = None
    height_cm: float | None = None
    activity_level: str | None = None


class HistoryEvaluationSnapshotRead(BaseModel):
    id: int
    created_at: datetime
    formula_set_version: str
    bmi: float | None = None
    resting_energy_kcal: float | None = None
    maintenance_energy_kcal: float | None = None


class HistoryStrategySnapshotRead(BaseModel):
    id: int
    created_at: datetime
    goal_code: str
    target_energy_kcal: float | None = None
    protein_g: float | None = None
    fat_g: float | None = None
    carbs_g: float | None = None


class HistoryPlanSnapshotRead(BaseModel):
    id: int
    created_at: datetime
    status: str
    pattern_code: str | None = None
    completion_pct: float
    selected_slots: int
    total_slots: int


class ConsultationHistoryItemRead(BaseModel):
    consultation_id: int
    consultation_date: date
    reason: str | None = None
    measurement: HistoryMeasurementRead | None = None
    evaluation: HistoryEvaluationSnapshotRead | None = None
    strategy: HistoryStrategySnapshotRead | None = None
    meal_plan: HistoryPlanSnapshotRead | None = None
    delta_vs_previous: HistoryDeltaRead | None = None


class PatientHistoryRead(BaseModel):
    patient_id: int
    patient_name: str
    consultation_count: int
    latest_consultation_date: date | None = None
    items: list[ConsultationHistoryItemRead]
