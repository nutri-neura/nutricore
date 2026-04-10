# Meal Distribution Spec

## Objetivo

Esta fase agrega una capa de planificacion diaria encima de `nutrition_strategy`.
No genera menus ni equivalentes de alimentos. Solo reparte la energia y los macros
objetivo entre tiempos de comida con plantillas explicitas del MVP.

## Alcance del MVP

Incluye:

- distribucion diaria persistida
- patrones de `3`, `4` y `5` tiempos
- seleccion manual del patron
- politica por defecto cuando no se envia patron
- reparto de kcal, proteina, grasa y carbohidratos por tiempo
- warnings de alcance

No incluye:

- menus completos
- equivalentes o sustituciones
- catalogo de alimentos
- recetas
- ajuste por horario laboral o entrenamiento

## Punto de partida

La distribucion nace desde una `nutrition_strategy` ya calculada. Eso garantiza que
el sistema no mezcle evaluacion, interpretacion y planificacion.

Entradas requeridas:

- `target_energy_kcal`
- `protein_g`
- `fat_g`
- `carbs_g`
- `goal_code`

## Patrones del MVP

### three_meals

- desayuno: `30%`
- comida: `40%`
- cena: `30%`

### four_meals

- desayuno: `25%`
- colacion_am: `15%`
- comida: `35%`
- cena: `25%`

### five_meals

- desayuno: `25%`
- colacion_am: `10%`
- comida: `30%`
- colacion_pm: `10%`
- cena: `25%`

## Politica por defecto

Si el cliente no manda `pattern_code`, el sistema usa:

- `maintenance` -> `four_meals`
- `fat_loss` -> `five_meals`
- `muscle_gain` -> `five_meals`
- `recomposition` -> `five_meals`

Es una politica operativa del MVP, no una regla clinica universal.

## Regla de reparto

En esta version el porcentaje del tiempo se aplica igual a:

- kcal
- proteina
- grasa
- carbohidratos

Eso simplifica la trazabilidad y evita introducir heuristicas todavia no definidas.

## Persistencia

Se crea una entidad `meal_distributions` con:

- `strategy_id`
- `pattern_code`
- `status`
- `distribution_set_version`
- `recommendation_payload`
- `warnings_payload`
- `created_by_user_id`
- `created_at`

## Salida esperada

El `recommendation_payload` devuelve:

- totales objetivo de la estrategia
- patron usado
- politica de seleccion del patron
- arreglo `meals`

Cada item de `meals` incluye:

- `meal_code`
- `label`
- `allocation_pct`
- `target_energy_kcal`
- `protein_g`
- `fat_g`
- `carbs_g`

## Warnings base

- `MVP scope: daily distribution only, not a complete meal plan`
- `Meal timing percentages are operational defaults for the MVP`
