from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import models as app_models  # noqa: F401
from app.api.deps import get_db
from app.core.config import get_settings
from app.core.security import hash_password
from app.db.base import Base
from app.main import create_app
from app.models.food import FoodCategory, FoodItem
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
        db.add_all(
            [
                FoodItem(
                    name="Pechuga de pollo",
                    category_code=FoodCategory.protein,
                    portion_label="100 g cocidos",
                    portion_grams=100,
                    energy_kcal=165,
                    protein_g=31,
                    fat_g=3.6,
                    carbs_g=0,
                    is_active=True,
                ),
                FoodItem(
                    name="Yogur griego natural",
                    category_code=FoodCategory.dairy,
                    portion_label="170 g",
                    portion_grams=170,
                    energy_kcal=100,
                    protein_g=17,
                    fat_g=0,
                    carbs_g=6,
                    is_active=True,
                ),
                FoodItem(
                    name="Avena",
                    category_code=FoodCategory.carb,
                    portion_label="40 g crudos",
                    portion_grams=40,
                    energy_kcal=156,
                    protein_g=5.4,
                    fat_g=2.8,
                    carbs_g=26.5,
                    is_active=True,
                ),
                FoodItem(
                    name="Aguacate",
                    category_code=FoodCategory.fat,
                    portion_label="50 g",
                    portion_grams=50,
                    energy_kcal=80,
                    protein_g=1.0,
                    fat_g=7.4,
                    carbs_g=4.3,
                    is_active=True,
                ),
                FoodItem(
                    name="Brocoli",
                    category_code=FoodCategory.vegetable,
                    portion_label="1 taza cocida",
                    portion_grams=156,
                    energy_kcal=55,
                    protein_g=3.7,
                    fat_g=0.6,
                    carbs_g=11.2,
                    is_active=True,
                ),
                FoodItem(
                    name="Manzana",
                    category_code=FoodCategory.fruit,
                    portion_label="1 pieza mediana",
                    portion_grams=182,
                    energy_kcal=95,
                    protein_g=0.5,
                    fat_g=0.3,
                    carbs_g=25.1,
                    is_active=True,
                ),
            ]
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


def get_admin_token(client: TestClient) -> str:
    response = client.post(
        "/v1/auth/login",
        json={
            "email": "admin@nutricore.app",
            "password": "super-secret-password",
        },
    )
    return response.json()["access_token"]


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
    token = get_admin_token(client)

    response = client.get(
        "/v1/users",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_create_patient_with_record():
    client = build_test_client()
    token = get_admin_token(client)

    response = client.post(
        "/v1/patients",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Ana",
            "last_name": "Lopez",
            "sex": "female",
            "birth_date": "1994-02-10",
            "phone": "5551234567",
            "email": "ana@example.com",
            "record": {
                "primary_goal": "Perdida de grasa",
                "allergies": "Nuez",
                "food_preferences": "Comida casera",
            },
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["first_name"] == "Ana"
    assert body["record"]["primary_goal"] == "Perdida de grasa"


def test_upsert_patient_record():
    client = build_test_client()
    token = get_admin_token(client)
    create_response = client.post(
        "/v1/patients",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Luis",
            "last_name": "Perez",
            "sex": "male",
            "birth_date": "1990-07-15",
        },
    )
    patient_id = create_response.json()["id"]

    response = client.put(
        f"/v1/patients/{patient_id}/record",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "primary_goal": "Mantenimiento",
            "medical_history": "Sin antecedentes relevantes",
            "default_schedule": "9:00, 14:00, 20:00",
        },
    )

    assert response.status_code == 200
    assert response.json()["primary_goal"] == "Mantenimiento"


def test_create_consultation_with_measurement():
    client = build_test_client()
    token = get_admin_token(client)
    create_response = client.post(
        "/v1/patients",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Carla",
            "last_name": "Mendez",
            "sex": "female",
            "birth_date": "1988-11-20",
        },
    )
    patient_id = create_response.json()["id"]

    response = client.post(
        f"/v1/patients/{patient_id}/consultations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "consultation_date": "2026-04-08",
            "reason": "Consulta inicial",
            "clinical_notes": "Paciente con buena adherencia esperada",
            "measurement": {
                "weight_kg": 72.4,
                "height_cm": 165,
                "waist_cm": 81,
                "activity_level": "moderado",
            },
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["patient_id"] == patient_id
    assert body["measurement"]["weight_kg"] == 72.4


def test_list_patient_consultations():
    client = build_test_client()
    token = get_admin_token(client)
    create_response = client.post(
        "/v1/patients",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Mario",
            "last_name": "Rojas",
            "sex": "male",
            "birth_date": "1992-03-01",
        },
    )
    patient_id = create_response.json()["id"]

    client.post(
        f"/v1/patients/{patient_id}/consultations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "consultation_date": "2026-04-08",
            "reason": "Seguimiento",
            "measurement": {"weight_kg": 80.0},
        },
    )

    response = client.get(
        f"/v1/patients/{patient_id}/consultations",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_create_evaluation_for_consultation():
    client = build_test_client()
    token = get_admin_token(client)

    patient_response = client.post(
        "/v1/patients",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Elena",
            "last_name": "Soto",
            "sex": "female",
            "birth_date": "1991-01-05",
        },
    )
    patient_id = patient_response.json()["id"]

    consultation_response = client.post(
        f"/v1/patients/{patient_id}/consultations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "consultation_date": "2026-04-08",
            "reason": "Evaluacion inicial",
            "measurement": {
                "weight_kg": 68.0,
                "height_cm": 162.0,
                "activity_level": "moderado",
            },
        },
    )
    consultation_id = consultation_response.json()["id"]

    response = client.post(
        f"/v1/consultations/{consultation_id}/evaluations",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "calculated"
    assert body["summary_payload"]["bmi"] > 0
    assert body["summary_payload"]["resting_energy_kcal"] > 0
    assert body["summary_payload"]["maintenance_energy_kcal"] > 0
    assert len(body["formula_results"]) == 4


def test_list_consultation_evaluations():
    client = build_test_client()
    token = get_admin_token(client)

    patient_response = client.post(
        "/v1/patients",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Pablo",
            "last_name": "Ruiz",
            "sex": "male",
            "birth_date": "1989-10-15",
        },
    )
    patient_id = patient_response.json()["id"]

    consultation_response = client.post(
        f"/v1/patients/{patient_id}/consultations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "consultation_date": "2026-04-08",
            "measurement": {
                "weight_kg": 84.0,
                "height_cm": 178.0,
                "activity_level": "active",
            },
        },
    )
    consultation_id = consultation_response.json()["id"]

    client.post(
        f"/v1/consultations/{consultation_id}/evaluations",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )

    response = client.get(
        f"/v1/consultations/{consultation_id}/evaluations",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_create_evaluation_fails_when_required_inputs_are_missing():
    client = build_test_client()
    token = get_admin_token(client)

    patient_response = client.post(
        "/v1/patients",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Julia",
            "last_name": "Diaz",
            "sex": "female",
            "birth_date": "1993-09-12",
        },
    )
    patient_id = patient_response.json()["id"]

    consultation_response = client.post(
        f"/v1/patients/{patient_id}/consultations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "consultation_date": "2026-04-08",
            "measurement": {
                "weight_kg": 61.0,
                "height_cm": 167.0,
            },
        },
    )
    consultation_id = consultation_response.json()["id"]

    response = client.post(
        f"/v1/consultations/{consultation_id}/evaluations",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )

    assert response.status_code == 422
    assert "measurement.activity_level" in response.json()["detail"]["missing_fields"]


def test_create_strategy_for_evaluation():
    client = build_test_client()
    token = get_admin_token(client)

    patient_response = client.post(
        "/v1/patients",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Nora",
            "last_name": "Vega",
            "sex": "female",
            "birth_date": "1992-08-10",
        },
    )
    patient_id = patient_response.json()["id"]

    consultation_response = client.post(
        f"/v1/patients/{patient_id}/consultations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "consultation_date": "2026-04-08",
            "measurement": {
                "weight_kg": 74.0,
                "height_cm": 166.0,
                "activity_level": "moderado",
            },
        },
    )
    consultation_id = consultation_response.json()["id"]

    evaluation_response = client.post(
        f"/v1/consultations/{consultation_id}/evaluations",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )
    evaluation_id = evaluation_response.json()["id"]

    response = client.post(
        f"/v1/evaluations/{evaluation_id}/strategies",
        headers={"Authorization": f"Bearer {token}"},
        json={"goal_code": "fat_loss"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["goal_code"] == "fat_loss"
    assert body["recommendation_payload"]["target_energy_kcal"] > 0
    assert body["recommendation_payload"]["protein_g"] > 0
    assert body["recommendation_payload"]["carbs_g"] >= 0


def test_list_strategies_for_evaluation():
    client = build_test_client()
    token = get_admin_token(client)

    patient_response = client.post(
        "/v1/patients",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Rene",
            "last_name": "Torres",
            "sex": "male",
            "birth_date": "1987-12-01",
        },
    )
    patient_id = patient_response.json()["id"]

    consultation_response = client.post(
        f"/v1/patients/{patient_id}/consultations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "consultation_date": "2026-04-08",
            "measurement": {
                "weight_kg": 90.0,
                "height_cm": 180.0,
                "activity_level": "active",
            },
        },
    )
    consultation_id = consultation_response.json()["id"]

    evaluation_response = client.post(
        f"/v1/consultations/{consultation_id}/evaluations",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )
    evaluation_id = evaluation_response.json()["id"]

    client.post(
        f"/v1/evaluations/{evaluation_id}/strategies",
        headers={"Authorization": f"Bearer {token}"},
        json={"goal_code": "maintenance"},
    )

    response = client.get(
        f"/v1/evaluations/{evaluation_id}/strategies",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_create_meal_distribution_for_strategy():
    client = build_test_client()
    token = get_admin_token(client)

    patient_response = client.post(
        "/v1/patients",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Sara",
            "last_name": "Leon",
            "sex": "female",
            "birth_date": "1995-06-14",
        },
    )
    patient_id = patient_response.json()["id"]

    consultation_response = client.post(
        f"/v1/patients/{patient_id}/consultations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "consultation_date": "2026-04-08",
            "measurement": {
                "weight_kg": 70.0,
                "height_cm": 168.0,
                "activity_level": "moderado",
            },
        },
    )
    consultation_id = consultation_response.json()["id"]

    evaluation_response = client.post(
        f"/v1/consultations/{consultation_id}/evaluations",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )
    evaluation_id = evaluation_response.json()["id"]

    strategy_response = client.post(
        f"/v1/evaluations/{evaluation_id}/strategies",
        headers={"Authorization": f"Bearer {token}"},
        json={"goal_code": "fat_loss"},
    )
    strategy_id = strategy_response.json()["id"]

    response = client.post(
        f"/v1/strategies/{strategy_id}/meal-distributions",
        headers={"Authorization": f"Bearer {token}"},
        json={"pattern_code": "five_meals"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["pattern_code"] == "five_meals"
    assert body["recommendation_payload"]["pattern_code"] == "five_meals"
    assert len(body["recommendation_payload"]["meals"]) == 5
    assert body["recommendation_payload"]["meals"][0]["target_energy_kcal"] > 0


def test_list_meal_distributions_for_strategy():
    client = build_test_client()
    token = get_admin_token(client)

    patient_response = client.post(
        "/v1/patients",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Diego",
            "last_name": "Marin",
            "sex": "male",
            "birth_date": "1988-04-02",
        },
    )
    patient_id = patient_response.json()["id"]

    consultation_response = client.post(
        f"/v1/patients/{patient_id}/consultations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "consultation_date": "2026-04-08",
            "measurement": {
                "weight_kg": 88.0,
                "height_cm": 179.0,
                "activity_level": "active",
            },
        },
    )
    consultation_id = consultation_response.json()["id"]

    evaluation_response = client.post(
        f"/v1/consultations/{consultation_id}/evaluations",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )
    evaluation_id = evaluation_response.json()["id"]

    strategy_response = client.post(
        f"/v1/evaluations/{evaluation_id}/strategies",
        headers={"Authorization": f"Bearer {token}"},
        json={"goal_code": "maintenance"},
    )
    strategy_id = strategy_response.json()["id"]

    client.post(
        f"/v1/strategies/{strategy_id}/meal-distributions",
        headers={"Authorization": f"Bearer {token}"},
        json={"pattern_code": "four_meals"},
    )

    response = client.get(
        f"/v1/strategies/{strategy_id}/meal-distributions",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_create_meal_plan_for_distribution():
    client = build_test_client()
    token = get_admin_token(client)

    patient_response = client.post(
        "/v1/patients",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Olga",
            "last_name": "Neri",
            "sex": "female",
            "birth_date": "1994-03-08",
        },
    )
    patient_id = patient_response.json()["id"]

    consultation_response = client.post(
        f"/v1/patients/{patient_id}/consultations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "consultation_date": "2026-04-08",
            "measurement": {
                "weight_kg": 67.0,
                "height_cm": 164.0,
                "activity_level": "moderado",
            },
        },
    )
    consultation_id = consultation_response.json()["id"]

    evaluation_id = client.post(
        f"/v1/consultations/{consultation_id}/evaluations",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    ).json()["id"]
    strategy_id = client.post(
        f"/v1/evaluations/{evaluation_id}/strategies",
        headers={"Authorization": f"Bearer {token}"},
        json={"goal_code": "fat_loss"},
    ).json()["id"]
    distribution_id = client.post(
        f"/v1/strategies/{strategy_id}/meal-distributions",
        headers={"Authorization": f"Bearer {token}"},
        json={"pattern_code": "five_meals"},
    ).json()["id"]

    response = client.post(
        f"/v1/distributions/{distribution_id}/meal-plans",
        headers={"Authorization": f"Bearer {token}"},
        json={"notes": "Base inicial para revisar adherencia."},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "draft"
    assert body["notes"] == "Base inicial para revisar adherencia."
    assert len(body["meals"]) == 5
    assert len(body["meals"][0]["structure_payload"]) >= 3


def test_list_meal_plans_for_distribution():
    client = build_test_client()
    token = get_admin_token(client)

    patient_id = client.post(
        "/v1/patients",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Raul",
            "last_name": "Pineda",
            "sex": "male",
            "birth_date": "1986-01-12",
        },
    ).json()["id"]
    consultation_id = client.post(
        f"/v1/patients/{patient_id}/consultations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "consultation_date": "2026-04-08",
            "measurement": {
                "weight_kg": 86.0,
                "height_cm": 178.0,
                "activity_level": "active",
            },
        },
    ).json()["id"]
    evaluation_id = client.post(
        f"/v1/consultations/{consultation_id}/evaluations",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    ).json()["id"]
    strategy_id = client.post(
        f"/v1/evaluations/{evaluation_id}/strategies",
        headers={"Authorization": f"Bearer {token}"},
        json={"goal_code": "maintenance"},
    ).json()["id"]
    distribution_id = client.post(
        f"/v1/strategies/{strategy_id}/meal-distributions",
        headers={"Authorization": f"Bearer {token}"},
        json={"pattern_code": "four_meals"},
    ).json()["id"]

    client.post(
        f"/v1/distributions/{distribution_id}/meal-plans",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )

    response = client.get(
        f"/v1/distributions/{distribution_id}/meal-plans",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_update_meal_plan():
    client = build_test_client()
    token = get_admin_token(client)

    patient_id = client.post(
        "/v1/patients",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Marta",
            "last_name": "Gil",
            "sex": "female",
            "birth_date": "1990-05-21",
        },
    ).json()["id"]
    consultation_id = client.post(
        f"/v1/patients/{patient_id}/consultations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "consultation_date": "2026-04-08",
            "measurement": {
                "weight_kg": 71.0,
                "height_cm": 163.0,
                "activity_level": "moderado",
            },
        },
    ).json()["id"]
    evaluation_id = client.post(
        f"/v1/consultations/{consultation_id}/evaluations",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    ).json()["id"]
    strategy_id = client.post(
        f"/v1/evaluations/{evaluation_id}/strategies",
        headers={"Authorization": f"Bearer {token}"},
        json={"goal_code": "recomposition"},
    ).json()["id"]
    distribution_id = client.post(
        f"/v1/strategies/{strategy_id}/meal-distributions",
        headers={"Authorization": f"Bearer {token}"},
        json={"pattern_code": "five_meals"},
    ).json()["id"]
    meal_plan_id = client.post(
        f"/v1/distributions/{distribution_id}/meal-plans",
        headers={"Authorization": f"Bearer {token}"},
        json={"notes": "Borrador inicial."},
    ).json()["id"]

    response = client.put(
        f"/v1/meal-plans/{meal_plan_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "reviewed", "notes": "Revisado con ajustes clinicos manuales."},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "reviewed"
    assert response.json()["notes"] == "Revisado con ajustes clinicos manuales."


def test_list_food_catalog():
    client = build_test_client()
    token = get_admin_token(client)

    response = client.get(
        "/v1/foods",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert len(response.json()) > 0


def test_get_meal_plan_suggestions():
    client = build_test_client()
    token = get_admin_token(client)

    patient_id = client.post(
        "/v1/patients",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Clara",
            "last_name": "Silva",
            "sex": "female",
            "birth_date": "1991-02-03",
        },
    ).json()["id"]
    consultation_id = client.post(
        f"/v1/patients/{patient_id}/consultations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "consultation_date": "2026-04-08",
            "measurement": {
                "weight_kg": 69.0,
                "height_cm": 165.0,
                "activity_level": "moderado",
            },
        },
    ).json()["id"]
    evaluation_id = client.post(
        f"/v1/consultations/{consultation_id}/evaluations",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    ).json()["id"]
    strategy_id = client.post(
        f"/v1/evaluations/{evaluation_id}/strategies",
        headers={"Authorization": f"Bearer {token}"},
        json={"goal_code": "fat_loss"},
    ).json()["id"]
    distribution_id = client.post(
        f"/v1/strategies/{strategy_id}/meal-distributions",
        headers={"Authorization": f"Bearer {token}"},
        json={"pattern_code": "five_meals"},
    ).json()["id"]
    meal_plan_id = client.post(
        f"/v1/distributions/{distribution_id}/meal-plans",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    ).json()["id"]

    response = client.get(
        f"/v1/meal-plans/{meal_plan_id}/suggestions",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["meal_plan_id"] == meal_plan_id
    assert len(body["meals"]) > 0
    assert len(body["meals"][0]["slots"]) > 0
    assert len(body["meals"][0]["slots"][0]["candidates"]) > 0
    assert body["meals"][0]["slots"][0]["recommended_candidate"] is not None
    assert body["meals"][0]["slots"][0]["recommended_candidate"]["suggested_portion_text"]
    assert body["meals"][0]["slots"][0]["recommended_candidate"]["adjusted_energy_kcal"] > 0


def test_select_food_for_slot():
    client = build_test_client()
    token = get_admin_token(client)

    patient_id = client.post(
        "/v1/patients",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Lia",
            "last_name": "Santos",
            "sex": "female",
            "birth_date": "1992-05-11",
        },
    ).json()["id"]
    consultation_id = client.post(
        f"/v1/patients/{patient_id}/consultations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "consultation_date": "2026-04-09",
            "measurement": {
                "weight_kg": 68.0,
                "height_cm": 166.0,
                "activity_level": "moderado",
            },
        },
    ).json()["id"]
    evaluation_id = client.post(
        f"/v1/consultations/{consultation_id}/evaluations",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    ).json()["id"]
    strategy_id = client.post(
        f"/v1/evaluations/{evaluation_id}/strategies",
        headers={"Authorization": f"Bearer {token}"},
        json={"goal_code": "fat_loss"},
    ).json()["id"]
    distribution_id = client.post(
        f"/v1/strategies/{strategy_id}/meal-distributions",
        headers={"Authorization": f"Bearer {token}"},
        json={"pattern_code": "five_meals"},
    ).json()["id"]
    meal_plan = client.post(
        f"/v1/distributions/{distribution_id}/meal-plans",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    ).json()
    meal_plan_meal_id = meal_plan["meals"][0]["id"]

    candidates_response = client.get(
        f"/v1/meal-plan-meals/{meal_plan_meal_id}/candidates",
        headers={"Authorization": f"Bearer {token}"},
        params={"slot_code": "protein_base"},
    )
    food_item_id = candidates_response.json()["recommended_candidate"]["food_id"]

    selection_response = client.post(
        f"/v1/meal-plan-meals/{meal_plan_meal_id}/slot-selections",
        headers={"Authorization": f"Bearer {token}"},
        json={"slot_code": "protein_base", "food_item_id": food_item_id},
    )

    assert selection_response.status_code == 200

    updated_candidates = client.get(
        f"/v1/meal-plan-meals/{meal_plan_meal_id}/candidates",
        headers={"Authorization": f"Bearer {token}"},
        params={"slot_code": "protein_base"},
    )
    assert updated_candidates.status_code == 200
    assert updated_candidates.json()["selected_food"]["food_id"] == food_item_id
    assert updated_candidates.json()["selected_food"]["portion_multiplier"] > 0


def test_update_slot_selection_portion():
    client = build_test_client()
    token = get_admin_token(client)

    patient_id = client.post(
        "/v1/patients",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Mia",
            "last_name": "Reyes",
            "sex": "female",
            "birth_date": "1994-08-22",
        },
    ).json()["id"]
    consultation_id = client.post(
        f"/v1/patients/{patient_id}/consultations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "consultation_date": "2026-04-10",
            "measurement": {
                "weight_kg": 66.0,
                "height_cm": 164.0,
                "activity_level": "moderado",
            },
        },
    ).json()["id"]
    evaluation_id = client.post(
        f"/v1/consultations/{consultation_id}/evaluations",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    ).json()["id"]
    strategy_id = client.post(
        f"/v1/evaluations/{evaluation_id}/strategies",
        headers={"Authorization": f"Bearer {token}"},
        json={"goal_code": "fat_loss"},
    ).json()["id"]
    distribution_id = client.post(
        f"/v1/strategies/{strategy_id}/meal-distributions",
        headers={"Authorization": f"Bearer {token}"},
        json={"pattern_code": "five_meals"},
    ).json()["id"]
    meal_plan = client.post(
        f"/v1/distributions/{distribution_id}/meal-plans",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    ).json()
    meal_plan_meal_id = meal_plan["meals"][0]["id"]

    candidate = client.get(
        f"/v1/meal-plan-meals/{meal_plan_meal_id}/candidates",
        headers={"Authorization": f"Bearer {token}"},
        params={"slot_code": "protein_base"},
    ).json()["recommended_candidate"]

    client.post(
        f"/v1/meal-plan-meals/{meal_plan_meal_id}/slot-selections",
        headers={"Authorization": f"Bearer {token}"},
        json={"slot_code": "protein_base", "food_item_id": candidate["food_id"]},
    )

    update_response = client.put(
        f"/v1/meal-plan-meals/{meal_plan_meal_id}/slot-selections/protein_base",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "portion_multiplier": 1.5,
            "final_portion_text": "1.5 porciones clinicas",
            "notes": "Ajuste por adherencia",
        },
    )

    assert update_response.status_code == 200
    body = update_response.json()
    assert body["portion_multiplier"] == 1.5
    assert body["final_portion_text"] == "1.5 porciones clinicas"
    assert body["adjusted_energy_kcal"] > 0
    assert body["notes"] == "Ajuste por adherencia"


def test_update_slot_selection_regenerates_portion_text_when_only_multiplier_changes():
    client = build_test_client()
    token = get_admin_token(client)

    patient_id = client.post(
        "/v1/patients",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Lia",
            "last_name": "Campos",
            "sex": "female",
            "birth_date": "1992-05-14",
        },
    ).json()["id"]
    consultation_id = client.post(
        f"/v1/patients/{patient_id}/consultations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "consultation_date": "2026-04-10",
            "measurement": {
                "weight_kg": 68.0,
                "height_cm": 165.0,
                "activity_level": "moderado",
            },
        },
    ).json()["id"]
    evaluation_id = client.post(
        f"/v1/consultations/{consultation_id}/evaluations",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    ).json()["id"]
    strategy_id = client.post(
        f"/v1/evaluations/{evaluation_id}/strategies",
        headers={"Authorization": f"Bearer {token}"},
        json={"goal_code": "fat_loss"},
    ).json()["id"]
    distribution_id = client.post(
        f"/v1/strategies/{strategy_id}/meal-distributions",
        headers={"Authorization": f"Bearer {token}"},
        json={"pattern_code": "five_meals"},
    ).json()["id"]
    meal_plan = client.post(
        f"/v1/distributions/{distribution_id}/meal-plans",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    ).json()
    meal_plan_meal_id = meal_plan["meals"][0]["id"]

    candidate = client.get(
        f"/v1/meal-plan-meals/{meal_plan_meal_id}/candidates",
        headers={"Authorization": f"Bearer {token}"},
        params={"slot_code": "protein_base"},
    ).json()["recommended_candidate"]

    selection_response = client.post(
        f"/v1/meal-plan-meals/{meal_plan_meal_id}/slot-selections",
        headers={"Authorization": f"Bearer {token}"},
        json={"slot_code": "protein_base", "food_item_id": candidate["food_id"]},
    )
    previous_text = selection_response.json()["final_portion_text"]

    update_response = client.put(
        f"/v1/meal-plan-meals/{meal_plan_meal_id}/slot-selections/protein_base",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "portion_multiplier": 1.5,
            "final_portion_text": previous_text,
            "notes": None,
        },
    )

    assert update_response.status_code == 200
    body = update_response.json()
    assert body["portion_multiplier"] == 1.5
    assert body["final_portion_text"].startswith("1.5 x ")
    assert body["final_portion_text"] != previous_text


def test_get_daily_menu_for_meal_plan():
    client = build_test_client()
    token = get_admin_token(client)

    patient_id = client.post(
        "/v1/patients",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Eva",
            "last_name": "Morales",
            "sex": "female",
            "birth_date": "1990-07-19",
        },
    ).json()["id"]
    consultation_id = client.post(
        f"/v1/patients/{patient_id}/consultations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "consultation_date": "2026-04-09",
            "measurement": {
                "weight_kg": 67.0,
                "height_cm": 164.0,
                "activity_level": "moderado",
            },
        },
    ).json()["id"]
    evaluation_id = client.post(
        f"/v1/consultations/{consultation_id}/evaluations",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    ).json()["id"]
    strategy_id = client.post(
        f"/v1/evaluations/{evaluation_id}/strategies",
        headers={"Authorization": f"Bearer {token}"},
        json={"goal_code": "fat_loss"},
    ).json()["id"]
    distribution_id = client.post(
        f"/v1/strategies/{strategy_id}/meal-distributions",
        headers={"Authorization": f"Bearer {token}"},
        json={"pattern_code": "five_meals"},
    ).json()["id"]
    meal_plan = client.post(
        f"/v1/distributions/{distribution_id}/meal-plans",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    ).json()
    breakfast_id = meal_plan["meals"][0]["id"]

    candidates_response = client.get(
        f"/v1/meal-plan-meals/{breakfast_id}/candidates",
        headers={"Authorization": f"Bearer {token}"},
        params={"slot_code": "protein_base"},
    )
    food_item_id = candidates_response.json()["recommended_candidate"]["food_id"]
    client.post(
        f"/v1/meal-plan-meals/{breakfast_id}/slot-selections",
        headers={"Authorization": f"Bearer {token}"},
        json={"slot_code": "protein_base", "food_item_id": food_item_id},
    )

    response = client.get(
        f"/v1/meal-plans/{meal_plan['id']}/daily-menu",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["meal_plan_id"] == meal_plan["id"]
    assert body["status"] == "partial"
    assert body["selected_slots"] == 1
    assert body["pending_slots"] > 0
    assert body["selected_energy_kcal"] > 0
    assert len(body["meals"]) > 0
    assert body["meals"][0]["covered_slots"] == 1
    assert body["meals"][0]["slots"][0]["selected_food"] is not None
    assert body["meals"][0]["slots"][0]["selected_food"]["suggested_portion_text"]


def test_meal_plan_cannot_finalize_with_pending_slots():
    client = build_test_client()
    token = get_admin_token(client)

    patient_id = client.post(
        "/v1/patients",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Noa",
            "last_name": "Luna",
            "sex": "female",
            "birth_date": "1990-04-11",
        },
    ).json()["id"]
    consultation_id = client.post(
        f"/v1/patients/{patient_id}/consultations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "consultation_date": "2026-04-10",
            "measurement": {
                "weight_kg": 64.0,
                "height_cm": 163.0,
                "activity_level": "moderado",
            },
        },
    ).json()["id"]
    evaluation_id = client.post(
        f"/v1/consultations/{consultation_id}/evaluations",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    ).json()["id"]
    strategy_id = client.post(
        f"/v1/evaluations/{evaluation_id}/strategies",
        headers={"Authorization": f"Bearer {token}"},
        json={"goal_code": "fat_loss"},
    ).json()["id"]
    distribution_id = client.post(
        f"/v1/strategies/{strategy_id}/meal-distributions",
        headers={"Authorization": f"Bearer {token}"},
        json={"pattern_code": "five_meals"},
    ).json()["id"]
    meal_plan_id = client.post(
        f"/v1/distributions/{distribution_id}/meal-plans",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    ).json()["id"]

    response = client.put(
        f"/v1/meal-plans/{meal_plan_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "finalized", "notes": "Intento prematuro"},
    )

    assert response.status_code == 422


def test_meal_plan_final_summary_returns_exportable_payload_when_complete():
    client = build_test_client()
    token = get_admin_token(client)

    patient_id = client.post(
        "/v1/patients",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Sara",
            "last_name": "Lozano",
            "sex": "female",
            "birth_date": "1991-03-08",
        },
    ).json()["id"]
    consultation_id = client.post(
        f"/v1/patients/{patient_id}/consultations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "consultation_date": "2026-04-10",
            "measurement": {
                "weight_kg": 63.0,
                "height_cm": 162.0,
                "activity_level": "moderado",
            },
        },
    ).json()["id"]
    evaluation_id = client.post(
        f"/v1/consultations/{consultation_id}/evaluations",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    ).json()["id"]
    strategy_id = client.post(
        f"/v1/evaluations/{evaluation_id}/strategies",
        headers={"Authorization": f"Bearer {token}"},
        json={"goal_code": "fat_loss"},
    ).json()["id"]
    distribution_id = client.post(
        f"/v1/strategies/{strategy_id}/meal-distributions",
        headers={"Authorization": f"Bearer {token}"},
        json={"pattern_code": "three_meals"},
    ).json()["id"]
    meal_plan = client.post(
        f"/v1/distributions/{distribution_id}/meal-plans",
        headers={"Authorization": f"Bearer {token}"},
        json={"notes": "Plan de exportacion"},
    ).json()

    for meal in meal_plan["meals"]:
        for slot in meal["structure_payload"]:
            candidate = client.get(
                f"/v1/meal-plan-meals/{meal['id']}/candidates",
                headers={"Authorization": f"Bearer {token}"},
                params={"slot_code": slot["slot_code"]},
            ).json()["recommended_candidate"]
            client.post(
                f"/v1/meal-plan-meals/{meal['id']}/slot-selections",
                headers={"Authorization": f"Bearer {token}"},
                json={"slot_code": slot["slot_code"], "food_item_id": candidate["food_id"]},
            )

    finalize_response = client.put(
        f"/v1/meal-plans/{meal_plan['id']}",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "ready_for_export", "notes": "Plan final completo"},
    )
    assert finalize_response.status_code == 200

    summary_response = client.get(
        f"/v1/meal-plans/{meal_plan['id']}/final-summary",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert summary_response.status_code == 200
    body = summary_response.json()
    assert body["meal_plan_id"] == meal_plan["id"]
    assert body["status"] == "ready_for_export"
    assert body["export_ready"] is True
    assert body["pending_slots"] == 0
    assert body["patient"]["full_name"] == "Sara Lozano"
    assert body["goal_code"] == "fat_loss"
    assert len(body["meals"]) == 3


def test_patient_history_returns_consultation_timeline_and_deltas():
    client = build_test_client()
    token = get_admin_token(client)

    patient_id = client.post(
        "/v1/patients",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "first_name": "Diana",
            "last_name": "Ruiz",
            "sex": "female",
            "birth_date": "1993-06-12",
        },
    ).json()["id"]

    first_consultation_id = client.post(
        f"/v1/patients/{patient_id}/consultations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "consultation_date": "2026-04-01",
            "reason": "Primera consulta",
            "measurement": {
                "weight_kg": 70.0,
                "height_cm": 165.0,
                "activity_level": "moderado",
            },
        },
    ).json()["id"]
    first_evaluation_id = client.post(
        f"/v1/consultations/{first_consultation_id}/evaluations",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    ).json()["id"]
    first_strategy_id = client.post(
        f"/v1/evaluations/{first_evaluation_id}/strategies",
        headers={"Authorization": f"Bearer {token}"},
        json={"goal_code": "fat_loss"},
    ).json()["id"]
    first_distribution_id = client.post(
        f"/v1/strategies/{first_strategy_id}/meal-distributions",
        headers={"Authorization": f"Bearer {token}"},
        json={"pattern_code": "five_meals"},
    ).json()["id"]
    client.post(
        f"/v1/distributions/{first_distribution_id}/meal-plans",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )

    second_consultation_id = client.post(
        f"/v1/patients/{patient_id}/consultations",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "consultation_date": "2026-04-10",
            "reason": "Seguimiento",
            "measurement": {
                "weight_kg": 68.5,
                "height_cm": 165.0,
                "activity_level": "moderado",
            },
        },
    ).json()["id"]
    second_evaluation_id = client.post(
        f"/v1/consultations/{second_consultation_id}/evaluations",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    ).json()["id"]
    second_strategy_id = client.post(
        f"/v1/evaluations/{second_evaluation_id}/strategies",
        headers={"Authorization": f"Bearer {token}"},
        json={"goal_code": "fat_loss"},
    ).json()["id"]
    second_distribution_id = client.post(
        f"/v1/strategies/{second_strategy_id}/meal-distributions",
        headers={"Authorization": f"Bearer {token}"},
        json={"pattern_code": "three_meals"},
    ).json()["id"]
    client.post(
        f"/v1/distributions/{second_distribution_id}/meal-plans",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )

    response = client.get(
        f"/v1/patients/{patient_id}/history",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["patient_id"] == patient_id
    assert body["consultation_count"] == 2
    assert body["items"][0]["consultation_id"] == second_consultation_id
    assert body["items"][0]["strategy"]["goal_code"] == "fat_loss"
    assert body["items"][0]["meal_plan"]["pattern_code"] == "three_meals"
    assert body["items"][0]["delta_vs_previous"]["weight_kg"] == -1.5
    assert body["items"][1]["delta_vs_previous"] is None
