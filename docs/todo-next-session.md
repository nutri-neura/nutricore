# Todo Next Session

## Estado actual

Fases A hasta J quedaron implementadas y validadas.

### Ya funciona

- base técnica de NutriCore en frontend y backend
- `SQLAlchemy + Alembic`
- auth JWT con bootstrap admin
- pacientes, expediente, consultas y mediciones
- evaluaciones nutricionales con trazabilidad por fórmula
- estrategias nutricionales base
- distribución diaria por tiempos de comida
- plan base semiautomático
- catálogo de alimentos
- sugerencias por slot
- selección persistida de alimentos por slot
- menú diario consolidado derivado del plan
- dashboard web operativo en `/patients`

### Endpoints clave ya activos

- `POST /v1/auth/login`
- `GET /v1/users/me`
- `GET /v1/patients`
- `POST /v1/patients`
- `PUT /v1/patients/{id}/record`
- `POST /v1/patients/{id}/consultations`
- `POST /v1/consultations/{id}/evaluations`
- `POST /v1/evaluations/{id}/strategies`
- `POST /v1/strategies/{id}/meal-distributions`
- `POST /v1/distributions/{id}/meal-plans`
- `GET /v1/meal-plans/{id}/suggestions`
- `GET /v1/meal-plan-meals/{id}/candidates`
- `POST /v1/meal-plan-meals/{id}/slot-selections`
- `GET /v1/meal-plans/{id}/daily-menu`

### Documentación ya creada

- [product-mvp.md](/home/elyarestark/develop-neura/nutri-neura-project/nutricore/docs/product-mvp.md)
- [domain-model.md](/home/elyarestark/develop-neura/nutri-neura-project/nutricore/docs/domain-model.md)
- [mvp-roadmap.md](/home/elyarestark/develop-neura/nutri-neura-project/nutricore/docs/mvp-roadmap.md)
- [formula-spec.md](/home/elyarestark/develop-neura/nutri-neura-project/nutricore/docs/formula-spec.md)
- [strategy-spec.md](/home/elyarestark/develop-neura/nutri-neura-project/nutricore/docs/strategy-spec.md)
- [meal-distribution-spec.md](/home/elyarestark/develop-neura/nutri-neura-project/nutricore/docs/meal-distribution-spec.md)
- [plan-spec.md](/home/elyarestark/develop-neura/nutri-neura-project/nutricore/docs/plan-spec.md)
- [food-catalog-spec.md](/home/elyarestark/develop-neura/nutri-neura-project/nutricore/docs/food-catalog-spec.md)
- [equivalents-spec.md](/home/elyarestark/develop-neura/nutri-neura-project/nutricore/docs/equivalents-spec.md)
- [daily-menu-spec.md](/home/elyarestark/develop-neura/nutri-neura-project/nutricore/docs/daily-menu-spec.md)

## Validado

### Manualmente

- `make up` funciona
- `make migrate-api` funciona dentro de Compose
- login con admin bootstrap funciona
- creación de paciente funciona
- actualización de expediente funciona
- creación de consulta y mediciones funciona
- evaluación funciona y persiste fórmulas
- estrategia funciona y persiste resultados
- distribución diaria funciona y persiste
- plan base funciona y persiste
- sugerencias de catálogo funcionan
- selección de slot funciona y persiste
- menú diario en web refleja cobertura y pendientes

### Por tests

- `apps/api/.venv/bin/python -m pytest apps/api/tests/test_main.py` -> `26 passed`
- `apps/api/.venv/bin/python -m ruff check apps/api` -> ok
- `npm run lint` en `apps/web` -> ok
- `npm run build` en `apps/web` -> ok

## Decisiones ya tomadas

- backend con FastAPI
- persistencia con SQLAlchemy
- migraciones con Alembic
- auth con JWT
- paciente objetivo MVP: adultos ambulatorios no críticos
- evaluación energética MVP con `Mifflin-St Jeor` como default
- producto semiautomático, no prescripción final automática
- frontend usa proxy interno `/api/proxy/...` para evitar problemas de CORS
- Fase J se resolvió como vista derivada, no como nueva tabla persistida

## Importante para no repetir errores

- no usar `create_all()` para esquema; el flujo correcto es Alembic
- correr migraciones con `make migrate-api`, no con Alembic directo desde host
- si el token JWT se prueba por curl, debe ir en una sola línea
- si un valor en `.env` tiene espacios o símbolos raros, usar comillas
- Traefik está corriendo en el puerto definido en `.env`, no asumir `80`
- el frontend debe consumir `/api/proxy/...`, no pegarle directo a `api.localhost`

## Siguiente objetivo

Arrancar Fase K:

- porciones y equivalencias más finas
- ajuste más útil entre slot target y alimento seleccionado
- resumen clínico más cercano a un día prescribible

## Orden recomendado para la próxima sesión

1. redactar `docs/portioning-spec.md`
2. definir si el ajuste será por:
   - porción escalada simple
   - múltiplos de porción
   - equivalentes cerrados por categoría
3. extender catálogo para soportar porción sugerida calculada
4. calcular ajuste entre target del slot y alimento seleccionado
5. mostrar porción sugerida en sugerencias y menú diario
6. agregar warnings cuando el ajuste quede muy lejos del target
7. evaluar si conviene persistir la porción sugerida por slot

## Preguntas abiertas para Fase K

- si la porción sugerida debe persistirse o derivarse al vuelo
- si el ajuste permitido será libre o por múltiplos discretos
- si las frutas, grasas y verduras usarán reglas distintas a proteína/carbos
- si conviene introducir equivalentes mexicanos desde esta fase o esperar

## Criterio de la próxima entrega

Al terminar la siguiente sesión debería existir:

- una spec clara de porcionamiento
- cálculo base de porción sugerida por slot
- menú diario mostrando alimento + porción sugerida
- validaciones o warnings por desajuste
- pruebas mínimas de API para esa lógica
