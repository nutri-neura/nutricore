from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.meal_plan import MealPlanStatus


class MealPlanCreate(BaseModel):
    notes: str | None = None


class MealPlanUpdate(BaseModel):
    status: MealPlanStatus
    notes: str | None = None


class MealPlanMealRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    meal_code: str
    label: str
    sort_order: int
    target_energy_kcal: float
    protein_target_g: float
    fat_target_g: float
    carbs_target_g: float
    structure_payload: list
    notes: str | None = None


class MealPlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    distribution_id: int
    status: MealPlanStatus
    plan_set_version: str
    notes: str | None = None
    created_by_user_id: int
    created_at: datetime
    updated_at: datetime
    meals: list[MealPlanMealRead]
