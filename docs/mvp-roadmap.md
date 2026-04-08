# MVP Roadmap

## Objetivo

Convertir el starter actual en un producto MVP funcional para consulta nutricional sin perder la base operativa ya resuelta en infraestructura.

## Estado actual del repo

### Ya resuelto por el starter

- Docker Compose y separacion de servicios
- Traefik y exposicion local
- PostgreSQL y Redis
- monitoreo base con Prometheus y Grafana
- healthchecks y readiness
- backups y restore
- hardening y controles base de seguridad

### Aun no resuelto

- dominio del negocio
- autenticacion real
- persistencia de entidades clinicas
- frontend de producto
- API de modulos funcionales
- motor de formulas
- motor de estrategia
- generador de planes

## Principios de ejecucion

- primero cerrar reglas del MVP, luego modelar
- primero evaluacion clinica, luego generacion de plan
- primero flujo diario editable, luego automatizaciones avanzadas
- primero reglas deterministas, luego IA asistida

## Fase A. Adaptacion del starter

Objetivo: convertir el repo de starter a plataforma de NutriCore.

Entregables:

- renombrar branding en frontend, API y docs
- actualizar README al producto
- definir variables de entorno de la app
- preparar estructura backend por modulos
- preparar estructura frontend por rutas privadas

Tareas:

1. cambiar identidad visual y textual de `DevOps Starter` a `NutriCore`
2. decidir ORM y sistema de migraciones
3. crear esqueleto de modulos backend
4. crear layout autenticado en frontend
5. dejar documentada la convencion de carpetas

## Fase B. Base operativa del producto

Objetivo: habilitar acceso real y datos persistentes.

Entregables:

- autenticacion
- roles iniciales
- modelo de usuarios
- proteccion de endpoints
- base de datos con migraciones iniciales

Tareas:

1. implementar modelo `User`
2. login con sesion o JWT
3. middleware o dependencias de autorizacion
4. migraciones iniciales
5. seed minimo de usuario admin

## Fase C. Pacientes y consultas

Objetivo: capturar y organizar la informacion clinica base.

Entregables:

- modulo de pacientes
- expediente general
- modulo de consultas
- modulo de mediciones
- listado e historial por paciente

Tareas:

1. implementar `Patient` y `PatientRecord`
2. implementar `Consultation` y `Measurement`
3. formularios frontend de alta y edicion
4. vista de detalle del paciente
5. timeline de consultas

## Fase D. Evaluacion y calculo

Objetivo: convertir datos capturados en resultados utilizables.

Entregables:

- modulo de evaluaciones
- motor de formulas versionado
- resultados persistidos
- reglas de validacion de entradas

Tareas:

1. definir tabla de formulas MVP
2. implementar servicios puros de calculo
3. persistir `Evaluation` y `FormulaResult`
4. exponer endpoint para ejecutar evaluacion
5. construir pantalla de resultados

## Fase E. Estrategia nutricional

Objetivo: transformar resultados numericos en una recomendacion inicial.

Entregables:

- reglas de interpretacion
- estrategia sugerida
- observaciones y alertas basicas

Tareas:

1. definir matriz de reglas inicial
2. implementar `NutritionStrategy`
3. mostrar estrategia en la evaluacion
4. permitir ajuste manual si aplica

## Fase F. Plan diario editable

Objetivo: llegar a una propuesta concreta de plan alimenticio.

Entregables:

- distribucion diaria
- catalogo base de alimentos
- equivalencias simples
- plantillas de comidas
- generador semiautomatico
- editor del plan

Tareas:

1. implementar `MealDistribution`
2. modelar `Food`, `FoodEquivalent` y `MealTemplate`
3. cargar catalogo inicial curado
4. generar plan diario base
5. permitir edicion manual completa

## Fase G. Versionado, seguimiento y salida

Objetivo: conservar trazabilidad y entregar informacion usable.

Entregables:

- `MealPlan` y `MealPlanVersion`
- seguimiento comparativo
- PDF basico de evaluacion y plan

Tareas:

1. implementar versionado del plan
2. activar una version vigente
3. comparar consultas previas
4. generar PDF imprimible

## Backlog posterior al MVP

- planes semanales
- reglas por patologias
- configuracion por clinica
- dashboard operativo avanzado
- jobs asincronos con Redis
- recordatorios y notificaciones
- IA asistida para resumenes y explicaciones

## Orden de implementacion recomendado

1. branding y adaptacion del starter
2. auth y usuarios
3. pacientes y expediente
4. consultas y mediciones
5. evaluaciones y formulas
6. resultados y estrategia
7. distribucion diaria
8. catalogo de alimentos
9. equivalencias y plantillas
10. generador de plan diario
11. versionado del plan
12. PDF y seguimiento

## Sprint sugerido

### Sprint 1

- adaptar starter
- definir stack backend
- implementar auth
- preparar base de datos y migraciones

### Sprint 2

- pacientes
- expediente
- consultas
- mediciones

### Sprint 3

- evaluaciones
- formulas
- resultados
- estrategia

### Sprint 4

- distribucion diaria
- alimentos
- equivalencias
- plantillas

### Sprint 5

- generador de plan
- editor manual
- versionado

### Sprint 6

- seguimiento
- PDF
- endurecimiento funcional
- pruebas del flujo principal

## Criterios de salida del MVP

- usuario autenticado puede registrar pacientes y consultas
- el sistema ejecuta evaluacion con formulas trazables
- el sistema muestra estrategia nutricional clara
- el sistema genera un plan diario editable
- el sistema conserva historial de versiones
- el flujo principal cuenta con pruebas basicas

## Decisiones tecnicas que deben cerrarse de inmediato

- ORM del backend
- esquema de auth
- libreria o estrategia para PDF
- formato de serializacion del plan
- fuente inicial del catalogo de alimentos

## Recomendacion pragmatica

No construir el generador de comidas antes de tener estable:

- modelo de evaluacion
- reglas de estrategia
- distribucion diaria
- estructura del plan editable

Si inviertes ese orden, vas a reescribir la mitad del sistema cuando cambien reglas clinicas.
