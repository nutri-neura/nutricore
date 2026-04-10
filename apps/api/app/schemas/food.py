from pydantic import BaseModel, ConfigDict

from app.models.food import FoodCategory


class FoodItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category_code: FoodCategory
    portion_label: str
    portion_grams: float | None = None
    energy_kcal: float
    protein_g: float
    fat_g: float
    carbs_g: float
    is_active: bool


class MealPlanSuggestionsRead(BaseModel):
    meal_plan_id: int
    warnings: list[str]
    meals: list[dict]
