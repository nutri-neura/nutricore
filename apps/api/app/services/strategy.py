from app.models.strategy import NutritionStrategyStatus
from app.repositories.strategy import create_nutrition_strategy, get_evaluation_for_strategy
from app.services.strategy_engine import StrategyInputError, execute_strategy


def generate_strategy_for_evaluation(
    db,
    *,
    evaluation_id: int,
    goal_code,
    created_by_user_id: int,
):
    evaluation = get_evaluation_for_strategy(db, evaluation_id)
    if evaluation is None:
        return None

    recommendation_payload, warnings_payload = execute_strategy(evaluation, goal_code)
    return create_nutrition_strategy(
        db,
        evaluation_id=evaluation_id,
        goal_code=goal_code,
        status=NutritionStrategyStatus.generated,
        strategy_set_version=recommendation_payload["strategy_set_version"],
        recommendation_payload=recommendation_payload,
        warnings_payload=warnings_payload,
        created_by_user_id=created_by_user_id,
    )


__all__ = ["StrategyInputError", "generate_strategy_for_evaluation"]
