from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SlotSelectionCreate(BaseModel):
    slot_code: str
    food_item_id: int


class SlotSelectionUpdate(BaseModel):
    portion_multiplier: float
    final_portion_text: str | None = None
    notes: str | None = None


class SlotSelectionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    meal_plan_meal_id: int
    slot_code: str
    food_item_id: int
    portion_multiplier: float
    final_portion_text: str | None = None
    adjusted_energy_kcal: float | None = None
    adjusted_protein_g: float | None = None
    adjusted_fat_g: float | None = None
    adjusted_carbs_g: float | None = None
    notes: str | None = None
    created_by_user_id: int
    created_at: datetime
    updated_at: datetime


class SlotCandidatesRead(BaseModel):
    meal_plan_meal_id: int
    slot_code: str
    recommended_candidate: dict | None = None
    selected_food: dict | None = None
    candidates: list[dict]
