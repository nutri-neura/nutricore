from pydantic import BaseModel


class DailyMenuSlotRead(BaseModel):
    slot_code: str
    label: str
    guidance: str
    status: str
    selected_food: dict | None = None


class DailyMenuMealRead(BaseModel):
    meal_plan_meal_id: int
    meal_code: str
    label: str
    target_energy_kcal: float
    protein_target_g: float
    fat_target_g: float
    carbs_target_g: float
    selected_energy_kcal: float
    selected_protein_g: float
    selected_fat_g: float
    selected_carbs_g: float
    covered_slots: int
    total_slots: int
    completion_pct: float
    pending_slots: list[str]
    slots: list[DailyMenuSlotRead]


class DailyMenuRead(BaseModel):
    meal_plan_id: int
    status: str
    total_slots: int
    selected_slots: int
    pending_slots: int
    completion_pct: float
    target_energy_kcal: float
    selected_energy_kcal: float
    target_protein_g: float
    selected_protein_g: float
    target_fat_g: float
    selected_fat_g: float
    target_carbs_g: float
    selected_carbs_g: float
    warnings: list[str]
    meals: list[DailyMenuMealRead]
