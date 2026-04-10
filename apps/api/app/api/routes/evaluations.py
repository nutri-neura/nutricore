from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.evaluation import get_evaluation, list_evaluations_for_consultation
from app.schemas.evaluation import EvaluationCreate, EvaluationRead
from app.services.evaluation import run_evaluation_for_consultation
from app.services.formulas.engine import FormulaInputError

router = APIRouter()


@router.post(
    "/consultations/{consultation_id}/evaluations",
    response_model=EvaluationRead,
    status_code=status.HTTP_201_CREATED,
)
def create_evaluation_for_consultation(
    consultation_id: int,
    _: EvaluationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EvaluationRead:
    try:
        evaluation = run_evaluation_for_consultation(
            db,
            consultation_id=consultation_id,
            created_by_user_id=current_user.id,
        )
    except FormulaInputError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Missing required inputs for evaluation",
                "missing_fields": exc.missing_fields,
            },
        ) from exc

    if evaluation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation not found",
        )

    return EvaluationRead.model_validate(evaluation)


@router.get("/evaluations/{evaluation_id}", response_model=EvaluationRead)
def read_evaluation(
    evaluation_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> EvaluationRead:
    evaluation = get_evaluation(db, evaluation_id)
    if evaluation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found",
        )
    return EvaluationRead.model_validate(evaluation)


@router.get("/consultations/{consultation_id}/evaluations", response_model=list[EvaluationRead])
def read_consultation_evaluations(
    consultation_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[EvaluationRead]:
    evaluations = list_evaluations_for_consultation(db, consultation_id)
    return [EvaluationRead.model_validate(item) for item in evaluations]
