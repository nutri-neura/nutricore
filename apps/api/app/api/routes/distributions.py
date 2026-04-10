from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.repositories.distribution import get_meal_distribution, list_distributions_for_strategy
from app.schemas.distribution import MealDistributionCreate, MealDistributionRead
from app.services.distribution import MealDistributionInputError, generate_distribution_for_strategy

router = APIRouter()


@router.post(
    "/strategies/{strategy_id}/meal-distributions",
    response_model=MealDistributionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_distribution_for_strategy(
    strategy_id: int,
    payload: MealDistributionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        distribution = generate_distribution_for_strategy(
            db,
            strategy_id=strategy_id,
            pattern_code=payload.pattern_code,
            created_by_user_id=current_user.id,
        )
    except MealDistributionInputError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Missing required inputs for meal distribution",
                "missing_fields": error.missing_fields,
            },
        ) from error

    if distribution is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Strategy not found")

    return MealDistributionRead.model_validate(distribution)


@router.get("/meal-distributions/{distribution_id}", response_model=MealDistributionRead)
def read_distribution(
    distribution_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    distribution = get_meal_distribution(db, distribution_id)
    if distribution is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal distribution not found",
        )

    return MealDistributionRead.model_validate(distribution)


@router.get(
    "/strategies/{strategy_id}/meal-distributions",
    response_model=list[MealDistributionRead],
)
def read_strategy_distributions(
    strategy_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    distributions = list_distributions_for_strategy(db, strategy_id)
    return [MealDistributionRead.model_validate(item) for item in distributions]
