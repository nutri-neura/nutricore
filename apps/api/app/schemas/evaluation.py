from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.evaluation import EvaluationStatus


class EvaluationCreate(BaseModel):
    pass


class FormulaResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    formula_code: str
    formula_version: str
    formula_family: str
    input_payload: dict
    output_payload: dict
    source_note: str | None
    created_at: datetime


class EvaluationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    consultation_id: int
    status: EvaluationStatus
    formula_set_version: str
    equation_selection_policy: str
    summary_payload: dict
    warnings_payload: list
    calculated_at: datetime
    created_by_user_id: int
    created_at: datetime
    formula_results: list[FormulaResultRead]
