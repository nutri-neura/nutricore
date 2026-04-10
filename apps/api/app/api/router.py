from fastapi import APIRouter

from app.api.routes import (
    auth,
    daily_menu,
    distributions,
    evaluations,
    foods,
    meal_plans,
    patients,
    slot_selections,
    strategies,
    system,
    users,
)

api_router = APIRouter()
api_router.include_router(system.router, tags=["system"])
api_router.include_router(auth.router, prefix="/v1/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/v1/users", tags=["users"])
api_router.include_router(patients.router, prefix="/v1/patients", tags=["patients"])
api_router.include_router(evaluations.router, prefix="/v1", tags=["evaluations"])
api_router.include_router(strategies.router, prefix="/v1", tags=["strategies"])
api_router.include_router(distributions.router, prefix="/v1", tags=["meal-distributions"])
api_router.include_router(meal_plans.router, prefix="/v1", tags=["meal-plans"])
api_router.include_router(foods.router, prefix="/v1", tags=["foods"])
api_router.include_router(daily_menu.router, prefix="/v1", tags=["daily-menu"])
api_router.include_router(slot_selections.router, prefix="/v1", tags=["slot-selections"])
