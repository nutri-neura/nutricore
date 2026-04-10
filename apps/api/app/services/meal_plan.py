from app.models.meal_plan import MealPlanStatus
from app.repositories.meal_plan import (
    create_meal_plan,
    get_distribution_for_plan,
    get_meal_plan,
    update_meal_plan,
)
from app.services.daily_menu import read_daily_menu
from app.services.meal_plan_engine import PLAN_SET_VERSION, MealPlanInputError, execute_meal_plan


class MealPlanFinalizationError(Exception):
    pass


def generate_plan_for_distribution(
    db,
    *,
    distribution_id: int,
    notes: str | None,
    created_by_user_id: int,
):
    distribution = get_distribution_for_plan(db, distribution_id)
    if distribution is None:
        return None

    _, meals, _warnings = execute_meal_plan(distribution, notes)
    return create_meal_plan(
        db,
        distribution_id=distribution_id,
        status=MealPlanStatus.draft,
        plan_set_version=PLAN_SET_VERSION,
        notes=notes,
        created_by_user_id=created_by_user_id,
        meals=meals,
    )


def revise_meal_plan(
    db,
    *,
    meal_plan_id: int,
    status: MealPlanStatus,
    notes: str | None,
):
    meal_plan = get_meal_plan(db, meal_plan_id)
    if meal_plan is None:
        return None

    if status in {MealPlanStatus.finalized, MealPlanStatus.ready_for_export}:
        daily_menu = read_daily_menu(db, meal_plan_id=meal_plan_id)
        if daily_menu is None or daily_menu["pending_slots"] > 0:
            raise MealPlanFinalizationError

    return update_meal_plan(db, meal_plan, status=status, notes=notes)


__all__ = [
    "MealPlanFinalizationError",
    "MealPlanInputError",
    "generate_plan_for_distribution",
    "revise_meal_plan",
]
