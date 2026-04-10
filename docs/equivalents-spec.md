# Equivalents Spec

## Objetivo

Esta fase agrega seleccion asistida por slot encima de las sugerencias del catalogo.
No implementa un sistema formal de equivalentes. El objetivo es priorizar candidatos
por cercania al bloque y permitir fijar una opcion por slot dentro del plan.

## Alcance del MVP

Incluye:

- score simple por cercania al slot
- recomendado principal
- alternativas ordenadas
- persistencia de seleccion por slot
- filtros basicos por alergias y preferencias del expediente

No incluye:

- equivalentes SMAE formales
- porciones ajustadas automaticamente
- multiples selecciones por slot
- sustitucion automatica avanzada

## Reglas de score

Cada slot usa una macro dominante:

- proteina -> `protein_g`
- carbohidrato -> `carbs_g`
- grasa -> `fat_g`
- verduras -> energia baja y categoria correcta

El score del MVP combina:

- cercania a la macro dominante
- cercania energetica

El mejor score se marca como `recommended`.

## Persistencia

Se crea `meal_plan_slot_selections` con:

- `meal_plan_meal_id`
- `slot_code`
- `food_item_id`
- `created_by_user_id`
- `created_at`

La combinacion `meal_plan_meal_id + slot_code` debe ser unica.

## Filtros MVP

Se excluyen candidatos cuando el nombre del alimento coincide de forma simple con
tokens presentes en:

- `patient.record.allergies`
- `patient.record.food_preferences`

Es una heuristica operativa, no una validacion clinica completa.

## Endpoints

- `GET /v1/meal-plan-meals/{meal_plan_meal_id}/candidates?slot_code=...`
- `POST /v1/meal-plan-meals/{meal_plan_meal_id}/slot-selections`
- `GET /v1/meal-plans/{meal_plan_id}/suggestions`

## Resultado esperado

Cada slot debe devolver:

- `recommended_candidate`
- `candidates`
- `selected_food`
- `selection_status`

