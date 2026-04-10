# Formula Spec

## Objetivo

Definir el alcance técnico y clínico inicial del motor de evaluación de NutriCore para evitar tratar el GET como una sola fórmula universal.

## Principio rector

El sistema debe distinguir entre:

- medición del gasto energético
- estimación predictiva del gasto energético
- gasto en reposo
- gasto total
- resultado energético base
- objetivo nutricional posterior

En el MVP no se medirá gasto con calorimetría indirecta. Solo se estimará con ecuaciones predictivas y reglas explícitas.

## Alcance clínico del MVP

Soportado en v1:

- adultos ambulatorios
- pacientes no críticos
- contexto de consulta nutricional general

Fuera de alcance en v1:

- UCI
- ventilación mecánica
- quemados
- nutrición hospitalaria especializada
- protocolos oncológicos avanzados
- pediatría
- embarazo
- atletas de alto rendimiento con carga extrema

## Regla de seguridad clínica

Si el contexto del paciente cae fuera del alcance del MVP, el sistema no debe fingir precisión clínica. Debe marcar advertencia o impedir selección automática de ecuación no apropiada.

## Fuentes base usadas para esta fase

- NASEM DRI for Energy 2023: el EER está orientado a mantenimiento y depende de sexo, edad, talla, peso y nivel de actividad.
  - https://www.ncbi.nlm.nih.gov/books/NBK591020/
- Endotext: si no se puede medir RMR, Mifflin-St Jeor con peso actual es una opción sólida para adultos ambulatorios, y el gasto total puede obtenerse multiplicando por un factor de actividad.
  - https://www.ncbi.nlm.nih.gov/books/NBK278991/
- Mifflin-St Jeor original:
  - https://doi.org/10.1093/ajcn/51.2.241

## Política del MVP para selección de fórmula

### Método de referencia conceptual

- referencia de medición ideal: calorimetría indirecta
- implementación MVP: ecuaciones predictivas

### Método por defecto en v1

Para adultos ambulatorios no críticos:

- ecuación por defecto de gasto en reposo: `mifflin_st_jeor_v1`
- estimación de gasto total: `resting_energy * activity_factor`

Esto es una decisión de producto para el MVP, no una afirmación de validez universal.

## Fórmulas aprobadas en v1

### `body_mass_index_v1`

Objetivo:

- calcular IMC como dato antropométrico base

Entradas requeridas:

- `weight_kg`
- `height_cm`

Salida:

- `bmi`

Regla:

- `bmi = weight_kg / (height_m ^ 2)`

### `mifflin_st_jeor_v1`

Objetivo:

- estimar gasto energético en reposo para adultos

Entradas requeridas:

- `sex`
- `age_years`
- `weight_kg`
- `height_cm`

Salida:

- `resting_energy_kcal`

Regla:

- hombre: `9.99 * weight_kg + 6.25 * height_cm - 4.92 * age_years + 5`
- mujer: `9.99 * weight_kg + 6.25 * height_cm - 4.92 * age_years - 161`

### `activity_factor_v1`

Objetivo:

- transformar gasto en reposo en estimación de mantenimiento

Entradas requeridas:

- `sex`
- `activity_level`

Salida:

- `activity_factor`

Categorías admitidas en v1:

- `sedentary`
- `low_active`
- `active`
- `very_active`

Factores iniciales:

- hombre:
  - sedentary: `1.00`
  - low_active: `1.11`
  - active: `1.25`
  - very_active: `1.48`
- mujer:
  - sedentary: `1.00`
  - low_active: `1.12`
  - active: `1.27`
  - very_active: `1.45`

Nota:

- estos factores se usan como aproximación operativa de mantenimiento en el MVP
- no deben interpretarse como prescripción final del plan

### `maintenance_energy_v1`

Objetivo:

- calcular la estimación base de mantenimiento para la evaluación

Entradas requeridas:

- `resting_energy_kcal`
- `activity_factor`

Salida:

- `maintenance_energy_kcal`

Regla:

- `maintenance_energy_kcal = resting_energy_kcal * activity_factor`

## Resultados principales del MVP en Fase D

El resumen consolidado de evaluación debe incluir como mínimo:

- `age_years`
- `bmi`
- `resting_energy_kcal`
- `activity_factor`
- `maintenance_energy_kcal`
- `formula_set_version`
- `equation_selection_policy`

## Entradas mínimas obligatorias

Para evaluación energética básica:

- sexo del paciente
- fecha de nacimiento
- peso actual
- talla
- nivel de actividad

Si falta cualquiera:

- la evaluación no se calcula
- se devuelve lista explícita de campos faltantes

## Diseño de persistencia

### Evaluation

Debe guardar:

- consulta origen
- usuario que ejecutó
- estado
- versión del set de fórmulas
- resumen consolidado
- advertencias

### FormulaResult

Debe guardar por cada fórmula:

- código de fórmula
- versión
- familia
- entradas usadas
- salida producida
- notas de trazabilidad

## Decisiones de implementación para esta fase

- no se implementan ecuaciones ICU
- no se implementa Cunningham todavía
- no se implementa EER directo de NASEM todavía
- no se calculan objetivos de pérdida o ganancia como si fueran requerimiento fisiológico
- no se generan macros aún

## Camino de expansión posterior

Fase siguiente del motor:

- `harris_benedict_v1`
- `cunningham_v1` cuando exista masa libre de grasa
- `naesm_eer_v1` para flujos de planificación energética
- estrategia nutricional sobre el resultado energético
- reglas de contexto clínico
