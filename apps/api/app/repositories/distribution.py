from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.distribution import MealDistribution, MealPattern
from app.models.strategy import NutritionStrategy


def get_strategy_for_distribution(db: Session, strategy_id: int) -> NutritionStrategy | None:
    return db.scalar(select(NutritionStrategy).where(NutritionStrategy.id == strategy_id))


def create_meal_distribution(
    db: Session,
    *,
    strategy_id: int,
    pattern_code: MealPattern,
    status,
    distribution_set_version: str,
    recommendation_payload: dict,
    warnings_payload: list[str],
    created_by_user_id: int,
) -> MealDistribution | None:
    distribution = MealDistribution(
        strategy_id=strategy_id,
        pattern_code=pattern_code,
        status=status,
        distribution_set_version=distribution_set_version,
        recommendation_payload=recommendation_payload,
        warnings_payload=warnings_payload,
        created_by_user_id=created_by_user_id,
    )
    db.add(distribution)
    db.commit()
    db.refresh(distribution)
    return get_meal_distribution(db, distribution.id)


def get_meal_distribution(db: Session, distribution_id: int) -> MealDistribution | None:
    return db.scalar(select(MealDistribution).where(MealDistribution.id == distribution_id))


def list_distributions_for_strategy(db: Session, strategy_id: int) -> list[MealDistribution]:
    return list(
        db.scalars(
            select(MealDistribution)
            .where(MealDistribution.strategy_id == strategy_id)
            .order_by(MealDistribution.created_at.desc(), MealDistribution.id.desc())
        )
    )
