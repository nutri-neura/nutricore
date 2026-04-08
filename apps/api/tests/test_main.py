from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.core.config import get_settings
from app.core.security import hash_password
from app.db.base import Base
from app.main import create_app
from app.models.user import User, UserRole


def build_test_client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        class_=Session,
    )
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as db:
        db.add(
            User(
                full_name="Admin Test",
                email="admin@nutricore.app",
                password_hash=hash_password("super-secret-password"),
                role=UserRole.admin,
                is_active=True,
            )
        )
        db.commit()

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    get_settings.cache_clear()
    app = create_app()
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    return client


def test_health_endpoint():
    client = build_test_client()
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_endpoint_degraded_when_dependencies_fail(monkeypatch):
    client = build_test_client()
    monkeypatch.setattr("app.api.routes.system.postgres_check", lambda: False)
    monkeypatch.setattr("app.api.routes.system.redis_check", lambda: False)

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "degraded",
        "postgres": False,
        "redis": False,
    }


def test_docs_enabled_outside_production(monkeypatch):
    monkeypatch.setenv("APP_ENV", "development")
    get_settings.cache_clear()
    client = TestClient(create_app())

    response = client.get("/docs")

    assert response.status_code == 200


def test_docs_disabled_in_production(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    get_settings.cache_clear()
    client = TestClient(create_app())

    docs_response = client.get("/docs")
    redoc_response = client.get("/redoc")
    openapi_response = client.get("/openapi.json")

    assert docs_response.status_code == 404
    assert redoc_response.status_code == 404
    assert openapi_response.status_code == 404


def test_login_returns_bearer_token():
    client = build_test_client()

    response = client.post(
        "/v1/auth/login",
        json={
            "email": "admin@nutricore.app",
            "password": "super-secret-password",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["user"]["role"] == "admin"


def test_protected_route_requires_token():
    client = build_test_client()

    response = client.get("/v1/users/me")

    assert response.status_code == 401


def test_me_endpoint_returns_current_user():
    client = build_test_client()
    login_response = client.post(
        "/v1/auth/login",
        json={
            "email": "admin@nutricore.app",
            "password": "super-secret-password",
        },
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "admin@nutricore.app"


def test_admin_can_list_users():
    client = build_test_client()
    login_response = client.post(
        "/v1/auth/login",
        json={
            "email": "admin@nutricore.app",
            "password": "super-secret-password",
        },
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/v1/users",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
