from pydantic import BaseModel


class FinalSummarySlotRead(BaseModel):
    slot_code: str
    label: str
    guidance: str
    status: str
    food_name: str | None = None
    portion_text: str | None = None
    adjusted_energy_kcal: float | None = None
    adjusted_protein_g: float | None = None
    adjusted_fat_g: float | None = None
    adjusted_carbs_g: float | None = None
    notes: str | None = None


class FinalSummaryMealRead(BaseModel):
    meal_plan_meal_id: int
    meal_code: str
    label: str
    completion_pct: float
    target_energy_kcal: float
    selected_energy_kcal: float
    target_protein_g: float
    selected_protein_g: float
    target_fat_g: float
    selected_fat_g: float
    target_carbs_g: float
    selected_carbs_g: float
    pending_slots: list[str]
    slots: list[FinalSummarySlotRead]


class FinalSummaryRead(BaseModel):
    meal_plan_id: int
    status: str
    export_ready: bool
    consultation_id: int
    consultation_date: str
    patient: dict
    goal_code: str
    pattern_code: str
    plan_notes: str | None = None
    completion_pct: float
    total_slots: int
    selected_slots: int
    pending_slots: int
    target_energy_kcal: float
    selected_energy_kcal: float
    target_protein_g: float
    selected_protein_g: float
    target_fat_g: float
    selected_fat_g: float
    target_carbs_g: float
    selected_carbs_g: float
    warnings: list[str]
    meals: list[FinalSummaryMealRead]
