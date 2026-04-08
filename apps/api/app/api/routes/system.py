from fastapi import APIRouter
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, generate_latest
from starlette.responses import Response

from app.core.config import get_settings
from app.infrastructure.health import postgres_check, redis_check

router = APIRouter()

REQUEST_COUNTER = Counter("api_requests_total", "Total API requests")
POSTGRES_UP = Gauge("api_postgres_up", "Postgres connectivity status")
REDIS_UP = Gauge("api_redis_up", "Redis connectivity status")


def readiness_payload() -> dict[str, bool | str]:
    postgres_ok = postgres_check()
    redis_ok = redis_check()
    POSTGRES_UP.set(1 if postgres_ok else 0)
    REDIS_UP.set(1 if redis_ok else 0)
    return {
        "status": "ready" if postgres_ok and redis_ok else "degraded",
        "postgres": postgres_ok,
        "redis": redis_ok,
    }


@router.get("/")
def root() -> dict[str, str]:
    REQUEST_COUNTER.inc()
    settings = get_settings()
    return {
        "service": "api",
        "product": settings.app_name,
        "status": "ok",
        "message": "NutriCore API",
    }


@router.get("/health")
def health() -> dict[str, str]:
    REQUEST_COUNTER.inc()
    return {"status": "ok"}


@router.get("/ready")
def ready() -> dict[str, bool | str]:
    REQUEST_COUNTER.inc()
    return readiness_payload()


@router.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
