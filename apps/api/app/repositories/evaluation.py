from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.consultation import Consultation
from app.models.evaluation import Evaluation, FormulaResult
from app.models.patient import Patient


def get_consultation_for_evaluation(db: Session, consultation_id: int) -> Consultation | None:
    return db.scalar(
        select(Consultation)
        .where(Consultation.id == consultation_id)
        .options(
            joinedload(Consultation.patient).joinedload(Patient.record),
            joinedload(Consultation.measurement),
        )
    )


def create_evaluation(
    db: Session,
    *,
    consultation_id: int,
    status,
    formula_set_version: str,
    equation_selection_policy: str,
    summary_payload: dict,
    warnings_payload: list,
    created_by_user_id: int,
    formula_results: list[dict],
) -> Evaluation:
    evaluation = Evaluation(
        consultation_id=consultation_id,
        status=status,
        formula_set_version=formula_set_version,
        equation_selection_policy=equation_selection_policy,
        summary_payload=summary_payload,
        warnings_payload=warnings_payload,
        created_by_user_id=created_by_user_id,
    )
    db.add(evaluation)
    db.flush()

    for item in formula_results:
        db.add(
            FormulaResult(
                evaluation_id=evaluation.id,
                **item,
            )
        )

    db.commit()
    db.refresh(evaluation)
    return get_evaluation(db, evaluation.id)


def get_evaluation(db: Session, evaluation_id: int) -> Evaluation | None:
    return db.scalar(
        select(Evaluation)
        .where(Evaluation.id == evaluation_id)
        .options(joinedload(Evaluation.formula_results))
    )


def list_evaluations_for_consultation(db: Session, consultation_id: int) -> list[Evaluation]:
    return list(
        db.scalars(
            select(Evaluation)
            .where(Evaluation.consultation_id == consultation_id)
            .options(joinedload(Evaluation.formula_results))
            .order_by(Evaluation.created_at.desc(), Evaluation.id.desc())
        ).unique()
    )
