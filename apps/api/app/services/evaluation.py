from sqlalchemy.orm import Session

from app.models.evaluation import EvaluationStatus
from app.repositories.evaluation import create_evaluation, get_consultation_for_evaluation
from app.services.formulas.engine import (
    EQUATION_SELECTION_POLICY,
    FORMULA_SET_VERSION,
    execute_formula_set,
)


def run_evaluation_for_consultation(
    db: Session,
    *,
    consultation_id: int,
    created_by_user_id: int,
):
    consultation = get_consultation_for_evaluation(db, consultation_id)
    if consultation is None:
        return None

    summary, warnings, formula_results = execute_formula_set(consultation)
    return create_evaluation(
        db,
        consultation_id=consultation_id,
        status=EvaluationStatus.calculated,
        formula_set_version=FORMULA_SET_VERSION,
        equation_selection_policy=EQUATION_SELECTION_POLICY,
        summary_payload=summary,
        warnings_payload=warnings,
        created_by_user_id=created_by_user_id,
        formula_results=formula_results,
    )
