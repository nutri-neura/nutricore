# Portioning Spec

## Objetivo

La Fase K agrega una porcion sugerida derivada para cada alimento candidato o seleccionado dentro de un slot del plan. No crea persistencia nueva: calcula una recomendacion operativa a partir del target de la comida, el tipo de slot y la composicion del alimento.

## Alcance MVP

Incluye:

- multiplicador sugerido por alimento
- porcion sugerida en gramos cuando exista `portion_grams`
- energia y macros ajustados por esa porcion
- warnings cuando la seleccion queda lejos del target operativo del slot

No incluye:

- equivalentes oficiales por SMAE
- optimizacion exacta multicriterio
- porciones persistidas por slot
- sustituciones clinicas avanzadas

## Fuente de verdad

- targets de la comida: `meal_plan_meals`
- tipo de slot: `structure_payload.slot_code`
- composicion del alimento: `food_items`

## Regla general

Cada slot usa un macro dominante y una fraccion operativa del target de la comida:

- `protein_*` -> proteina
- `cereal_base`, `starch_base`, `easy_carb`, `fruit_optional` -> carbohidratos
- `*_fat` -> grasa
- `vegetables` -> energia fija baja

Con eso se calcula un multiplicador:

`target_slot / aporte_base_alimento`

Luego:

- se redondea a pasos de `0.25`
- se limita a rango `0.5` a `3.0`
- se derivan kcal/macros ajustados

## Señales operativas

- `aligned`: el ajuste queda razonablemente cerca del target operativo
- `wide_gap`: el alimento sirve como candidato, pero el desajuste sigue siendo amplio
- `clamped`: el cálculo pidió una porción fuera del rango operativo del MVP

## Uso esperado

Esta fase debe permitir que el nutriólogo vea algo más útil que solo el nombre del alimento:

- qué porción inicial podría usar
- cuánto aportaría esa selección
- si el alimento encaja bien o mal en ese bloque
