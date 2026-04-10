from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.strategy import get_nutrition_strategy, list_strategies_for_evaluation
from app.schemas.strategy import NutritionStrategyCreate, NutritionStrategyRead
from app.services.strategy import StrategyInputError, generate_strategy_for_evaluation

router = APIRouter()


@router.post(
    "/evaluations/{evaluation_id}/strategies",
    response_model=NutritionStrategyRead,
    status_code=status.HTTP_201_CREATED,
)
def create_strategy_for_evaluation(
    evaluation_id: int,
    payload: NutritionStrategyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NutritionStrategyRead:
    try:
        strategy = generate_strategy_for_evaluation(
            db,
            evaluation_id=evaluation_id,
            goal_code=payload.goal_code,
            created_by_user_id=current_user.id,
        )
    except StrategyInputError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Missing required inputs for strategy",
                "missing_fields": exc.missing_fields,
            },
        ) from exc

    if strategy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation not found",
        )

    return NutritionStrategyRead.model_validate(strategy)


@router.get("/strategies/{strategy_id}", response_model=NutritionStrategyRead)
def read_strategy(
    strategy_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> NutritionStrategyRead:
    strategy = get_nutrition_strategy(db, strategy_id)
    if strategy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Strategy not found",
        )
    return NutritionStrategyRead.model_validate(strategy)


@router.get("/evaluations/{evaluation_id}/strategies", response_model=list[NutritionStrategyRead])
def read_evaluation_strategies(
    evaluation_id: int,
    _: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[NutritionStrategyRead]:
    strategies = list_strategies_for_evaluation(db, evaluation_id)
    return [NutritionStrategyRead.model_validate(item) for item in strategies]
