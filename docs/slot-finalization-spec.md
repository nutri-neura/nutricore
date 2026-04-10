# Slot Finalization Spec

## Objetivo

La Fase L convierte la seleccion de un slot en una decision clinica persistida: no solo guarda el alimento, sino tambien la porcion final operativa y sus macros calculados.

## Alcance MVP

Incluye:

- persistir multiplicador de porcion
- persistir texto final de porcion
- persistir kcal y macros finales del slot
- notas breves por slot
- permitir actualizar manualmente esos valores desde la UI

No incluye:

- equivalentes oficiales SMAE
- recetas
- exportacion PDF

## Entidad afectada

`meal_plan_slot_selections`

Campos nuevos:

- `portion_multiplier`
- `final_portion_text`
- `adjusted_energy_kcal`
- `adjusted_protein_g`
- `adjusted_fat_g`
- `adjusted_carbs_g`
- `notes`
- `updated_at`

## Reglas

1. Al crear una seleccion nueva, el backend guarda por defecto la porcion sugerida calculada.
2. El nutriologo puede editar:
   - multiplicador
   - texto final de porcion
   - notas
3. Al guardar un cambio manual, el backend recalcula kcal/macros finales del slot.
4. El menu diario debe usar primero los valores persistidos del slot y solo caer a derivacion si no existen.

## API

- `POST /v1/meal-plan-meals/{meal_plan_meal_id}/slot-selections`
- `PUT /v1/meal-plan-meals/{meal_plan_meal_id}/slot-selections/{slot_code}`

## Cierre funcional

La fase se considera cerrada si un slot puede:

- seleccionar alimento
- guardar una porcion inicial
- editar multiplicador o texto final
- persistir el cambio
- reflejarlo en sugerencias y menu diario
