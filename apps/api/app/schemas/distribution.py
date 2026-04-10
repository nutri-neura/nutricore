from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.distribution import MealDistributionStatus, MealPattern


class MealDistributionCreate(BaseModel):
    pattern_code: MealPattern | None = None


class MealDistributionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    strategy_id: int
    pattern_code: MealPattern
    status: MealDistributionStatus
    distribution_set_version: str
    recommendation_payload: dict
    warnings_payload: list
    created_by_user_id: int
    created_at: datetime
