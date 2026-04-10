from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.consultation import Consultation
from app.models.distribution import MealDistribution
from app.models.evaluation import Evaluation
from app.models.meal_plan import MealPlan, MealPlanMeal
from app.models.patient import Patient
from app.models.slot_selection import MealPlanSlotSelection
from app.models.strategy import NutritionStrategy


def get_distribution_for_plan(db: Session, distribution_id: int) -> MealDistribution | None:
    return db.scalar(select(MealDistribution).where(MealDistribution.id == distribution_id))


def create_meal_plan(
    db: Session,
    *,
    distribution_id: int,
    status,
    plan_set_version: str,
    notes: str | None,
    created_by_user_id: int,
    meals: list[dict],
) -> MealPlan | None:
    meal_plan = MealPlan(
        distribution_id=distribution_id,
        status=status,
        plan_set_version=plan_set_version,
        notes=notes,
        created_by_user_id=created_by_user_id,
    )
    db.add(meal_plan)
    db.flush()

    for item in meals:
        db.add(
            MealPlanMeal(
                meal_plan_id=meal_plan.id,
                meal_code=item["meal_code"],
                label=item["label"],
                sort_order=item["sort_order"],
                target_energy_kcal=item["target_energy_kcal"],
                protein_target_g=item["protein_target_g"],
                fat_target_g=item["fat_target_g"],
                carbs_target_g=item["carbs_target_g"],
                structure_payload=item["structure_payload"],
                notes=item.get("notes"),
            )
        )

    db.commit()
    return get_meal_plan(db, meal_plan.id)


def get_meal_plan(db: Session, meal_plan_id: int) -> MealPlan | None:
    return db.scalar(
        select(MealPlan)
        .where(MealPlan.id == meal_plan_id)
        .options(
            selectinload(MealPlan.distribution)
            .selectinload(MealDistribution.strategy)
            .selectinload(NutritionStrategy.evaluation)
            .selectinload(Evaluation.consultation)
            .selectinload(Consultation.patient)
            .selectinload(Patient.record),
            selectinload(MealPlan.meals)
            .selectinload(MealPlanMeal.slot_selections)
            .selectinload(MealPlanSlotSelection.food_item),
        )
    )


def list_meal_plans_for_distribution(db: Session, distribution_id: int) -> list[MealPlan]:
    return list(
        db.scalars(
            select(MealPlan)
            .where(MealPlan.distribution_id == distribution_id)
            .options(
                selectinload(MealPlan.meals)
                .selectinload(MealPlanMeal.slot_selections)
                .selectinload(MealPlanSlotSelection.food_item)
            )
            .order_by(MealPlan.created_at.desc(), MealPlan.id.desc())
        )
    )


def update_meal_plan(
    db: Session,
    meal_plan: MealPlan,
    *,
    status,
    notes: str | None,
) -> MealPlan | None:
    meal_plan.status = status
    meal_plan.notes = notes
    db.add(meal_plan)
    db.commit()
    return get_meal_plan(db, meal_plan.id)
