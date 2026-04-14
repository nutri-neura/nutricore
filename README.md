# NutriCore

NutriCore es una plataforma para consulta nutricional que ya cubre un flujo clínico funcional de punta a punta:

- autenticación y usuarios
- pacientes y expediente
- consultas y mediciones
- evaluación nutricional
- estrategia de macros
- distribución diaria
- plan base
- sugerencias de alimentos
- cierre de slots con porciones finales
- menú diario consolidado
- resumen final exportable
- historial clínico por paciente

El proyecto corre sobre `FastAPI + Next.js + PostgreSQL + Redis + Traefik + Docker Compose`, con observabilidad y runbooks desde el inicio.

## Estado actual

Hoy el repositorio ya no es solo un starter. Ya implementa:

- `Auth` con JWT y admin bootstrap
- `Patients` con expediente clínico base
- `Consultations` con mediciones
- `Evaluations` con motor de fórmulas MVP
- `Strategies` para kcal objetivo y macros
- `Meal distributions` por patrón de comidas
- `Meal plans` semiautomáticos
- `Food suggestions` por slot
- `Slot finalization` con porción final y notas
- `Daily menu` consolidado
- `Final summary` para cierre clínico
- `Printable export view`
- `Patient history` y comparación entre consultas

## Alcance clínico del MVP

El MVP actual está enfocado en:

- adultos ambulatorios no críticos
- evaluación energética predictiva
- estrategia nutricional base
- construcción operativa de un plan diario

No cubre todavía:

- patologías complejas
- UCI o paciente crítico
- cálculo por calorimetría indirecta
- equivalentes clínicos avanzados tipo SMAE completo
- motor formal de recetas

## Arquitectura

### Backend

`apps/api`

- `FastAPI`
- `SQLAlchemy`
- `Alembic`
- JWT auth
- servicios por dominio

Rutas principales hoy:

- `/v1/auth`
- `/v1/users`
- `/v1/patients`
- `/v1/consultations/.../evaluations`
- `/v1/evaluations/.../strategies`
- `/v1/strategies/.../meal-distributions`
- `/v1/distributions/.../meal-plans`
- `/v1/meal-plans/.../suggestions`
- `/v1/meal-plans/.../daily-menu`
- `/v1/meal-plans/.../final-summary`
- `/v1/meal-plan-meals/.../slot-selections`

### Frontend

`apps/web`

Hoy la interfaz principal está en:

- [`/patients`](/home/elyarestark/develop-neura/nutri-neura-project/nutricore/apps/web/app/patients/page.tsx)

Desde ahí puedes:

- pegar JWT
- cargar pacientes
- abrir consultas
- ejecutar evaluación
- generar estrategia
- generar distribución
- generar plan
- seleccionar alimentos
- cerrar slots
- revisar menú diario
- revisar cierre clínico
- abrir vista imprimible
- descargar JSON final
- revisar historial clínico

### Infra

`infra`

- Traefik como proxy
- PostgreSQL
- Redis
- Prometheus
- Grafana
- overlays de Docker Compose para dev/prod/admin

## Estructura del repo

```text
nutricore/
├── apps/
│   ├── api/
│   └── web/
├── infra/
│   ├── compose/
│   ├── monitoring/
│   ├── proxy/
│   └── scripts/
├── docs/
├── .github/workflows/
├── .env.example
├── Makefile
└── README.md
```

## Instalación local

### 1. Preparar `.env`

```bash
make setup
```

Eso crea `.env` a partir de `.env.example` si todavía no existe.

Variables importantes:

- `POSTGRES_PASSWORD`
- `REDIS_PASSWORD`
- `GRAFANA_ADMIN_PASSWORD`
- `NUTRICORE_JWT_SECRET`
- `NUTRICORE_BOOTSTRAP_ADMIN_PASSWORD`
- `TRAEFIK_ADMIN_PASSWORD`
- `BACKUP_ENCRYPTION_PASSPHRASE`

Si usas puerto distinto para Traefik, ajusta también:

- `TRAEFIK_PORT`
- `API_BASE_URL`
- `NEXT_PUBLIC_API_BASE_URL`
- `NUTRICORE_CORS_ALLOWED_ORIGINS`

Ejemplo típico local:

```bash
TRAEFIK_PORT=8080
API_BASE_URL=http://api.localhost:8080
NEXT_PUBLIC_API_BASE_URL=http://api.localhost:8080
NUTRICORE_CORS_ALLOWED_ORIGINS=http://web.localhost,http://web.localhost:8080,http://localhost:3000
```

### 2. Instalar dependencias locales

```bash
make install
```

Eso hace:

- crea `apps/api/.venv`
- instala dependencias Python
- instala dependencias Node

### 3. Aplicar migraciones

```bash
make migrate-api
```

### 4. Levantar el stack

```bash
make up
```

## URLs útiles

Con Traefik local:

- web: `http://web.localhost:${TRAEFIK_PORT}`
- api: `http://api.localhost:${TRAEFIK_PORT}`

Ejemplo común:

- `http://web.localhost:8080`
- `http://api.localhost:8080`

Health:

- `http://api.localhost:${TRAEFIK_PORT}/health`

OpenAPI:

- `http://api.localhost:${TRAEFIK_PORT}/docs`

Vista imprimible:

- `http://web.localhost:${TRAEFIK_PORT}/meal-plans/{mealPlanId}/print`

## Flujo funcional actual

El flujo correcto del producto hoy es este:

1. login
2. paciente
3. consulta
4. evaluación
5. estrategia
6. distribución
7. plan base
8. sugerencias por slot
9. selección de alimento
10. cierre de slot
11. menú diario
12. cierre clínico
13. exportación
14. historial del paciente

### Qué genera cada fase

#### Evaluación

Genera:

- `BMI`
- `resting_energy_kcal`
- `maintenance_energy_kcal`

El MVP usa `Mifflin-St Jeor` como ecuación base para adultos ambulatorios no críticos.

#### Estrategia

Genera:

- `target_energy_kcal`
- `protein_g`
- `fat_g`
- `carbs_g`

#### Distribución

Genera patrones:

- `three_meals`
- `four_meals`
- `five_meals`

#### Plan base

Construye bloques por comida, por ejemplo:

- proteína
- carbohidrato base
- grasa
- verduras

#### Sugerencias y finalización

Permite:

- ver candidatos por slot
- elegir un alimento
- ajustar multiplicador
- definir porción final
- agregar nota del slot

#### Cierre clínico

Permite:

- revisar cobertura del plan
- ver resumen final
- marcar plan como:
  - `reviewed`
  - `finalized`
  - `ready_for_export`

## Exportación actual

Hoy ya puedes exportar de dos formas:

### 1. JSON

Desde el dashboard:

- `Descargar JSON`

O por API:

```bash
curl http://api.localhost:8080/v1/meal-plans/1/final-summary \
  -H "Authorization: Bearer $TOKEN"
```

### 2. Vista imprimible

Desde el dashboard:

- `Abrir vista imprimible`

Luego puedes usar:

- `Imprimir / Guardar PDF`

Esto todavía es una exportación web/imprimible, no un generador PDF de backend.

## Historial clínico

La vista `Historial clinico` ya muestra por paciente:

- consultas previas
- última evaluación por consulta
- última estrategia por consulta
- último plan por consulta
- cambios contra la consulta anterior

Campos comparados hoy:

- peso
- IMC
- kcal de mantenimiento
- kcal objetivo
- proteína
- grasa
- carbohidratos

## Comandos principales

### Setup y dependencias

```bash
make setup
make install
make install-api
make install-web
```

### Desarrollo local

```bash
make up
make down
make logs
make ps
make config
make migrate-api
```

### Calidad

```bash
make lint
make lint-fix
make test
```

### Admin y observabilidad

```bash
make up-admin
make down-admin
make logs-admin
make ps-admin
make config-admin
```

### Producción

```bash
make up-prod
make down-prod
make logs-prod
make ps-prod
make config-prod
make up-prod-admin
```

### Backup y restore

```bash
make backup
make restore BACKUP_FILE=path/to/file.sql.gz.enc
```

## Testing recomendado

### Backend

```bash
apps/api/.venv/bin/python -m pytest apps/api/tests/test_main.py
apps/api/.venv/bin/python -m ruff check apps/api
```

### Frontend

```bash
cd apps/web
npm run lint
npm run build
```

### Prueba funcional manual

En `/patients`:

1. pega JWT
2. carga paciente
3. crea o abre consulta
4. ejecuta evaluación
5. genera estrategia
6. genera distribución
7. genera plan base
8. llena todos los slots
9. revisa `Menu diario`
10. revisa `Cierre clinico`
11. marca `Finalizar plan`
12. marca `Listo para exportar`
13. usa `Abrir vista imprimible` o `Descargar JSON`

## Bootstrap admin

El sistema puede crear el admin inicial automáticamente usando:

- `NUTRICORE_BOOTSTRAP_ADMIN_ENABLED`
- `NUTRICORE_BOOTSTRAP_ADMIN_NAME`
- `NUTRICORE_BOOTSTRAP_ADMIN_EMAIL`
- `NUTRICORE_BOOTSTRAP_ADMIN_PASSWORD`

Login típico:

```bash
curl -X POST http://api.localhost:8080/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@nutricore.app","password":"TU_PASSWORD"}'
```

## Seguridad y operación

El repo ya incluye:

- validación de secretos inseguros en `.env`
- reverse proxy con Traefik
- headers de seguridad
- overlays dev/prod/admin
- runbooks
- backup y restore
- monitoreo base con Prometheus y Grafana

## Documentación disponible

El `README.md` ahora sirve como entrada general. Los detalles profundos están en `docs/`.

### Producto y dominio

- [product-mvp.md](/home/elyarestark/develop-neura/nutri-neura-project/nutricore/docs/product-mvp.md)
- [domain-model.md](/home/elyarestark/develop-neura/nutri-neura-project/nutricore/docs/domain-model.md)
- [mvp-roadmap.md](/home/elyarestark/develop-neura/nutri-neura-project/nutricore/docs/mvp-roadmap.md)
- [Requirements.md](/home/elyarestark/develop-neura/nutri-neura-project/nutricore/docs/Requirements.md)

### Specs funcionales implementadas

- [formula-spec.md](/home/elyarestark/develop-neura/nutri-neura-project/nutricore/docs/formula-spec.md)
- [strategy-spec.md](/home/elyarestark/develop-neura/nutri-neura-project/nutricore/docs/strategy-spec.md)
- [meal-distribution-spec.md](/home/elyarestark/develop-neura/nutri-neura-project/nutricore/docs/meal-distribution-spec.md)
- [plan-spec.md](/home/elyarestark/develop-neura/nutri-neura-project/nutricore/docs/plan-spec.md)
- [food-catalog-spec.md](/home/elyarestark/develop-neura/nutri-neura-project/nutricore/docs/food-catalog-spec.md)
- [equivalents-spec.md](/home/elyarestark/develop-neura/nutri-neura-project/nutricore/docs/equivalents-spec.md)
- [daily-menu-spec.md](/home/elyarestark/develop-neura/nutri-neura-project/nutricore/docs/daily-menu-spec.md)
- [portioning-spec.md](/home/elyarestark/develop-neura/nutri-neura-project/nutricore/docs/portioning-spec.md)
- [slot-finalization-spec.md](/home/elyarestark/develop-neura/nutri-neura-project/nutricore/docs/slot-finalization-spec.md)
- [finalization-spec.md](/home/elyarestark/develop-neura/nutri-neura-project/nutricore/docs/finalization-spec.md)
- [history-versioning-spec.md](/home/elyarestark/develop-neura/nutri-neura-project/nutricore/docs/history-versioning-spec.md)

### Infra y operación

- [architecture.md](/home/elyarestark/develop-neura/nutri-neura-project/nutricore/docs/architecture.md)
- [deployment.md](/home/elyarestark/develop-neura/nutri-neura-project/nutricore/docs/deployment.md)
- [security.md](/home/elyarestark/develop-neura/nutri-neura-project/nutricore/docs/security.md)
- [runbooks.md](/home/elyarestark/develop-neura/nutri-neura-project/nutricore/docs/runbooks.md)
- [troubleshooting.md](/home/elyarestark/develop-neura/nutri-neura-project/nutricore/docs/troubleshooting.md)
- [traefik-admin.md](/home/elyarestark/develop-neura/nutri-neura-project/nutricore/docs/traefik-admin.md)

## ¿Está completo `docs`?

Está bastante bien para:

- producto
- dominio
- specs por fase
- infraestructura
- operación

Pero no estaba consolidado como guía de entrada. Ese era el hueco principal del repo, y por eso actualicé este `README.md`.

## Siguiente foco recomendado

El siguiente bloque lógico del proyecto sería:

1. mejorar la exportación clínica formal para paciente
2. filtros clínicos reales en sugerencias
3. historial más comparativo entre versiones de plan
4. PDF más profesional o exportación backend dedicada
