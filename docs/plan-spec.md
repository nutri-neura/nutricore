# Plan Spec

## Objetivo

Esta fase convierte una `meal_distribution` en un plan alimenticio base semiautomatico.
No genera menus finales ni intercambios detallados. Genera una estructura editable por
tiempo de comida para que el nutriologo parta de una base consistente.

## Alcance del MVP

Incluye:

- entidad `meal_plans`
- entidad `meal_plan_meals`
- generacion base desde una distribucion existente
- bloques estructurales por tiempo de comida
- notas manuales del plan
- cambio de estatus `draft` y `reviewed`

No incluye:

- equivalentes
- lista exhaustiva de alimentos
- recetas
- PDFs
- automatizacion avanzada por horario o entrenamiento

## Punto de partida

El plan nace desde `meal_distribution.recommendation_payload.meals`.

Cada comida trae ya definidos:

- `meal_code`
- `label`
- `target_energy_kcal`
- `protein_g`
- `fat_g`
- `carbs_g`

## Generacion base

### breakfast

- proteina base
- cereal / avena / pan
- fruta opcional
- grasa ligera

### lunch / dinner

- proteina principal
- cereal o tuberculo
- verduras libres
- grasa de adicion

### snack_am / snack_pm

- proteina ligera
- fruta o carbohidrato simple
- grasa opcional

## Persistencia

### meal_plans

- `distribution_id`
- `status`
- `plan_set_version`
- `notes`
- `created_by_user_id`
- `created_at`
- `updated_at`

### meal_plan_meals

- `meal_plan_id`
- `meal_code`
- `label`
- `sort_order`
- `target_energy_kcal`
- `protein_target_g`
- `fat_target_g`
- `carbs_target_g`
- `structure_payload`
- `notes`

## Edicion MVP

La primera version permite editar:

- notas globales del plan
- estatus del plan

La estructura generada queda visible y persistida, pero no se edita bloque por bloque
todavia en la UI.

## Warnings base

- `MVP scope: base structure only, not a final prescribed menu`
- `Blocks are planning placeholders for clinician review`
