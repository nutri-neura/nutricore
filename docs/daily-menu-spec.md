# Daily Menu Spec

## Objetivo

La Fase J convierte un `meal_plan` con selecciones por slot en un menu diario legible para operacion clinica. No crea nueva persistencia: deriva una vista consolidada a partir de `meal_plan_meals`, `structure_payload` y `meal_plan_slot_selections`.

## Alcance MVP

Incluye:

- resumen global de cobertura del plan
- consolidado por tiempo de comida
- lista de alimentos ya seleccionados por slot
- slots pendientes por cubrir
- comparacion simple entre targets del plan y macros/energia seleccionados

No incluye:

- porciones optimizadas automaticamente
- equivalencias avanzadas
- generacion de recetas
- PDF final

## Fuente de verdad

- targets por tiempo: `meal_plan_meals`
- estructura esperada por slot: `meal_plan_meals.structure_payload`
- alimentos elegidos: `meal_plan_slot_selections`
- composicion de alimentos: `food_items`

## Endpoint

`GET /v1/meal-plans/{meal_plan_id}/daily-menu`

## Respuesta esperada

### Nivel global

- `meal_plan_id`
- `status`: `empty`, `partial`, `complete`
- `total_slots`
- `selected_slots`
- `pending_slots`
- `completion_pct`
- `target_energy_kcal`
- `selected_energy_kcal`
- `target_protein_g`
- `selected_protein_g`
- `target_fat_g`
- `selected_fat_g`
- `target_carbs_g`
- `selected_carbs_g`
- `warnings`

### Nivel comida

- `meal_plan_meal_id`
- `meal_code`
- `label`
- targets del tiempo
- totales seleccionados para ese tiempo
- `covered_slots`
- `total_slots`
- `pending_slots`
- `slots`

### Nivel slot

- `slot_code`
- `label`
- `guidance`
- `status`: `selected` o `pending`
- `selected_food`

## Reglas

1. Si no hay ninguna seleccion en todo el plan, el menu es `empty`.
2. Si todas las comidas tienen todos sus slots cubiertos, el menu es `complete`.
3. En cualquier otro caso, el menu es `partial`.
4. Los totales seleccionados se calculan sumando la composicion estandar de cada alimento elegido.
5. Los warnings deben recordar que:
   - el menu sigue siendo una vista MVP
   - las porciones finales requieren revision clinica
   - slots pendientes implican que el dia no esta completo

## Uso esperado

Esta vista debe permitir que el nutriologo responda rapido:

- que comidas ya quedaron armadas
- que slots siguen vacios
- cuanta energia y macros ya quedaron cubiertos
- si el dia esta listo para revision o todavia incompleto
