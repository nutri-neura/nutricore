# Food Catalog Spec

## Objetivo

Esta fase convierte los bloques del `meal_plan` en sugerencias reales de alimentos.
No intenta resolver un optimizador completo. La meta es que cada bloque del plan base
tenga candidatos concretos y trazables del catalogo interno.

## Alcance del MVP

Incluye:

- catalogo persistido de alimentos base
- perfiles simples por porcion
- categorias operativas
- endpoint para listar catalogo
- endpoint para generar sugerencias por `meal_plan`
- UI minima para revisar sugerencias desde el dashboard

No incluye:

- equivalentes formales por SMAE
- intercambio automatico entre alimentos
- combinaciones optimizadas por macros exactos
- recetas
- disponibilidad por pais o temporada

## Modelo base

Cada alimento del catalogo guarda:

- `name`
- `category_code`
- `portion_label`
- `portion_grams`
- `energy_kcal`
- `protein_g`
- `fat_g`
- `carbs_g`
- `is_active`

## Categorias MVP

- `protein`
- `carb`
- `fat`
- `vegetable`
- `fruit`
- `dairy`

## Regla de sugerencias

Cada `slot_code` del plan se mapea a una o mas categorias:

- `protein_base`, `main_protein`, `light_protein` -> `protein`, `dairy`
- `cereal_base`, `starch_base`, `easy_carb` -> `carb`, `fruit`
- `fruit_optional` -> `fruit`
- `light_fat`, `added_fat`, `optional_fat` -> `fat`
- `vegetables` -> `vegetable`

La salida MVP regresa hasta `3` candidatos por bloque.

## Warnings base

- `MVP suggestions are catalog candidates, not exact prescribed portions`
- `Clinician review is required before converting candidates into a final menu`
