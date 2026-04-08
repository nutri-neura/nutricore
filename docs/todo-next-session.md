# Todo Next Session

## Estado actual

Fase A y Fase B quedaron implementadas y validadas.

### Ya funciona

- branding base de NutriCore en frontend y backend
- estructura modular inicial en `apps/api`
- `SQLAlchemy + Alembic`
- modelo `User`
- roles iniciales:
  - `admin`
  - `nutriologo`
  - `asistente`
  - `recepcionista`
- login JWT en `POST /v1/auth/login`
- endpoint protegido `GET /v1/users/me`
- endpoint admin `GET /v1/users`
- bootstrap automático de admin desde `.env`
- stack levantando con Docker Compose

### Validado manualmente

- `make up` funciona
- `make migrate-api` funciona dentro de Compose
- login con:
  - `admin@nutricore.app`
  - password definida en `.env`
- `GET /v1/users/me` respondió correctamente con token válido

### Validado por tests

- `apps/api/.venv/bin/python -m pytest apps/api` -> `8 passed`
- `apps/api/.venv/bin/python -m ruff check apps/api` -> ok
- `npm run test` en `apps/web` -> ok
- `npm run lint` en `apps/web` -> ok

## Decisiones ya tomadas

- backend con FastAPI
- persistencia con SQLAlchemy
- migraciones con Alembic
- auth con JWT
- paciente objetivo MVP: adultos
- producto semiautomático, no totalmente automático

## Importante para no repetir errores

- no usar `create_all()` para esquema; ya se quitó para no competir con Alembic
- correr migraciones con `make migrate-api`, no con Alembic directo desde host
- si el token JWT se prueba por curl, debe ir en una sola línea
- si un valor en `.env` tiene espacios o símbolos raros, usar comillas
- Traefik está corriendo en el puerto definido en `.env`, no asumir `80`

## Siguiente objetivo

Arrancar Fase C:

- `patients`
- `patient_record`
- `consultations`
- `measurements`

## Orden recomendado para la próxima sesión

1. crear modelo y migración de `patients`
2. crear modelo y migración de `patient_records`
3. construir CRUD básico de pacientes
4. agregar endpoints protegidos para expediente
5. crear modelo de `consultations`
6. crear modelo de `measurements`
7. conectar una vista básica de pacientes en frontend

## Entidades siguientes a implementar

### Patient

Campos mínimos:

- id
- first_name
- last_name
- sex
- birth_date
- phone
- email
- created_at
- updated_at

### PatientRecord

Campos mínimos:

- patient_id
- primary_goal
- medical_history
- pathologies
- allergies
- intolerances
- dietary_restrictions
- food_preferences
- lifestyle_notes
- default_schedule
- general_observations

### Consultation

Campos mínimos:

- patient_id
- nutritionist_user_id
- consultation_date
- reason
- adherence_report
- symptoms
- clinical_notes

### Measurement

Campos mínimos:

- consultation_id
- weight_kg
- height_cm
- waist_cm
- hip_cm
- body_fat_percentage
- activity_level

## Criterio de la próxima entrega

Al terminar la siguiente sesión debería existir:

- migraciones nuevas para pacientes y consultas
- CRUD mínimo de pacientes
- expediente persistido
- consultas y mediciones base
- pruebas mínimas de API para esos módulos
