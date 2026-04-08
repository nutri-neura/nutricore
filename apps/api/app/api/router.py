from fastapi import APIRouter

from app.api.routes import auth, system, users

api_router = APIRouter()
api_router.include_router(system.router, tags=["system"])
api_router.include_router(auth.router, prefix="/v1/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/v1/users", tags=["users"])
