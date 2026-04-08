from psycopg import connect
from redis import Redis

from app.core.config import get_settings


def redis_client() -> Redis:
    settings = get_settings()
    return Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
        decode_responses=True,
    )


def postgres_check() -> bool:
    settings = get_settings()
    try:
        with connect(settings.postgres_dsn) as conn:
            with conn.cursor() as cur:
                cur.execute("select 1;")
                cur.fetchone()
        return True
    except Exception:
        return False


def redis_check() -> bool:
    try:
        redis_client().ping()
        return True
    except Exception:
        return False
