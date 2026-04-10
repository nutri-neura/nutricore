from app.models.distribution import MealDistributionStatus, MealPattern
from app.repositories.distribution import create_meal_distribution, get_strategy_for_distribution
from app.services.distribution_engine import (
    MealDistributionInputError,
    execute_meal_distribution,
)


def generate_distribution_for_strategy(
    db,
    *,
    strategy_id: int,
    pattern_code: MealPattern | None,
    created_by_user_id: int,
):
    strategy = get_strategy_for_distribution(db, strategy_id)
    if strategy is None:
        return None

    selected_pattern, recommendation_payload, warnings_payload = execute_meal_distribution(
        strategy,
        pattern_code,
    )
    return create_meal_distribution(
        db,
        strategy_id=strategy_id,
        pattern_code=selected_pattern,
        status=MealDistributionStatus.generated,
        distribution_set_version=recommendation_payload["distribution_set_version"],
        recommendation_payload=recommendation_payload,
        warnings_payload=warnings_payload,
        created_by_user_id=created_by_user_id,
    )


__all__ = ["MealDistributionInputError", "generate_distribution_for_strategy"]
