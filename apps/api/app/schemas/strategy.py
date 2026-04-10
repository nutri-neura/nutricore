from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.strategy import NutritionStrategyStatus, StrategyGoal


class NutritionStrategyCreate(BaseModel):
    goal_code: StrategyGoal


class NutritionStrategyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    evaluation_id: int
    goal_code: StrategyGoal
    status: NutritionStrategyStatus
    strategy_set_version: str
    recommendation_payload: dict
    warnings_payload: list
    created_by_user_id: int
    created_at: datetime
