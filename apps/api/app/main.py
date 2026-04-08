from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.db.session import SessionLocal, engine
from app.services.bootstrap import bootstrap_admin


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        with SessionLocal() as db:
            bootstrap_admin(db)
    except Exception:
        # Keep the API bootable even if infra dependencies are still starting.
        pass
    yield


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=f"{settings.app_name} API",
        lifespan=lifespan,
        docs_url=None if settings.is_production else "/docs",
        redoc_url=None if settings.is_production else "/redoc",
        openapi_url=None if settings.is_production else "/openapi.json",
    )
    app.include_router(api_router)
    return app


app = create_app()
