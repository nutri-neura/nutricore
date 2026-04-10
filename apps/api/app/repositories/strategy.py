from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.consultation import Consultation
from app.models.evaluation import Evaluation
from app.models.patient import Patient
from app.models.strategy import NutritionStrategy


def get_evaluation_for_strategy(db: Session, evaluation_id: int) -> Evaluation | None:
    return db.scalar(
        select(Evaluation)
        .where(Evaluation.id == evaluation_id)
        .options(
            joinedload(Evaluation.formula_results),
            joinedload(Evaluation.strategies),
            joinedload(Evaluation.consultation)
            .joinedload(Consultation.patient)
            .joinedload(Patient.record),
            joinedload(Evaluation.consultation).joinedload(Consultation.measurement),
        )
    )


def create_nutrition_strategy(
    db: Session,
    *,
    evaluation_id: int,
    goal_code,
    status,
    strategy_set_version: str,
    recommendation_payload: dict,
    warnings_payload: list,
    created_by_user_id: int,
) -> NutritionStrategy:
    strategy = NutritionStrategy(
        evaluation_id=evaluation_id,
        goal_code=goal_code,
        status=status,
        strategy_set_version=strategy_set_version,
        recommendation_payload=recommendation_payload,
        warnings_payload=warnings_payload,
        created_by_user_id=created_by_user_id,
    )
    db.add(strategy)
    db.commit()
    db.refresh(strategy)
    return get_nutrition_strategy(db, strategy.id)


def get_nutrition_strategy(db: Session, strategy_id: int) -> NutritionStrategy | None:
    return db.scalar(select(NutritionStrategy).where(NutritionStrategy.id == strategy_id))


def list_strategies_for_evaluation(db: Session, evaluation_id: int) -> list[NutritionStrategy]:
    return list(
        db.scalars(
            select(NutritionStrategy)
            .where(NutritionStrategy.evaluation_id == evaluation_id)
            .order_by(NutritionStrategy.created_at.desc(), NutritionStrategy.id.desc())
        )
    )
