# Domain Model

## Objetivo

Definir las entidades nucleares de NutriCore, sus relaciones y las reglas de ciclo de vida del MVP.

## Principios del dominio

- separar datos permanentes del paciente de los datos por consulta
- no sobrescribir historia clinica pasada
- versionar resultados y planes cuando cambie el origen clinico o la propuesta nutricional
- mantener trazabilidad entre consulta, evaluacion y plan
- separar calculo, interpretacion y generacion del plan

## Mapa de modulos

- autenticacion y autorizacion
- pacientes y expediente
- consultas y mediciones
- evaluaciones y formulas
- resultados e interpretacion
- distribucion y planeacion alimentaria
- seguimiento
- reportes

## Entidades principales

### User

Representa a una persona con acceso al sistema.

Campos base:

- id
- full_name
- email
- password_hash
- role
- is_active
- created_at
- updated_at

### Patient

Representa la identidad base del paciente.

Campos base:

- id
- first_name
- last_name
- sex
- birth_date
- phone
- email
- created_at
- updated_at

Notas:

- la edad debe calcularse a partir de `birth_date`
- `Patient` no debe guardar resultados clinicos derivados

### PatientRecord

Expediente general y contexto relativamente estable del paciente.

Campos base:

- id
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
- updated_by_user_id
- created_at
- updated_at

Notas:

- puede editarse, pero debe conservar `updated_at`
- no sustituye el historial por consulta

### Consultation

Evento clinico fechado donde se registra una evaluacion o seguimiento.

Campos base:

- id
- patient_id
- nutritionist_user_id
- consultation_date
- reason
- adherence_report
- symptoms
- clinical_notes
- created_at

Notas:

- una consulta puede existir aunque la evaluacion aun no este cerrada

### Measurement

Datos antropometricos y operativos capturados en una consulta.

Campos base:

- id
- consultation_id
- weight_kg
- height_cm
- waist_cm
- hip_cm
- body_fat_percentage
- muscle_mass_kg
- blood_pressure
- activity_level
- hydration_notes
- created_at

Notas:

- una consulta puede tener una medicion principal en MVP
- si luego necesitas mas granularidad, podra versionarse o subdividirse

### Evaluation

Snapshot clinico que toma entradas de la consulta y dispara calculo.

Campos base:

- id
- consultation_id
- status
- formula_set_version
- calculated_at
- created_by_user_id
- created_at

Estados sugeridos:

- draft
- calculated
- reviewed
- archived

### FormulaResult

Salida numerica trazable de una formula ejecutada.

Campos base:

- id
- evaluation_id
- formula_code
- formula_version
- input_payload
- output_payload
- created_at

Notas:

- `input_payload` y `output_payload` permiten trazabilidad sin perder flexibilidad
- aqui debe quedar claro con que formula y que entradas se calculo cada valor

### NutritionStrategy

Interpretacion del resultado clinico para orientar el plan.

Campos base:

- id
- evaluation_id
- energy_strategy
- macro_strategy
- meal_frequency
- recommendation_notes
- alerts
- created_at

Ejemplos:

- deficit moderado
- mantenimiento
- proteina alta
- 4 comidas

### MealDistribution

Distribucion diaria de energia y macros por tiempo de comida.

Campos base:

- id
- evaluation_id
- meals_count
- distribution_payload
- created_at

Notas:

- `distribution_payload` puede guardar porcentajes y gramos por comida

### Food

Elemento del catalogo alimentario.

Campos base:

- id
- name
- category
- subcategory
- serving_size
- calories
- protein_g
- fat_g
- carbs_g
- fiber_g
- tags
- allowed_meal_types
- contraindications
- is_active
- created_at
- updated_at

### FoodEquivalent

Relacion de sustitucion o intercambio entre alimentos.

Campos base:

- id
- source_food_id
- target_food_id
- equivalence_rule
- notes

### MealTemplate

Estructura abstracta usada para construir una comida.

Campos base:

- id
- name
- meal_type
- objective_type
- rules_payload
- is_active

### MealPlan

Entidad padre del plan alimenticio originado por una evaluacion.

Campos base:

- id
- patient_id
- evaluation_id
- active_version_id
- status
- created_at
- updated_at

Estados sugeridos:

- draft
- active
- replaced
- archived

### MealPlanVersion

Version editable y trazable del plan.

Campos base:

- id
- meal_plan_id
- version_number
- generated_by
- generation_mode
- content_payload
- notes
- created_by_user_id
- created_at

Notas:

- `generation_mode` puede ser `automatic`, `semi_automatic` o `manual`
- `content_payload` debe guardar comidas, porciones, opciones y sustituciones

### FollowUp

Resumen comparativo derivado de una nueva consulta respecto a una anterior.

Campos base:

- id
- patient_id
- consultation_id
- previous_consultation_id
- progress_summary
- adjustment_reason
- created_at

## Relaciones principales

- `User 1:N Consultation`
- `Patient 1:1 PatientRecord`
- `Patient 1:N Consultation`
- `Consultation 1:1 Measurement`
- `Consultation 1:N Evaluation`
- `Evaluation 1:N FormulaResult`
- `Evaluation 1:1 NutritionStrategy`
- `Evaluation 1:1 MealDistribution`
- `Evaluation 1:N MealPlan`
- `MealPlan 1:N MealPlanVersion`
- `Patient 1:N FollowUp`

## Ciclo de vida del paciente

1. se registra `Patient`
2. se completa o ajusta `PatientRecord`
3. se crean consultas sucesivas en el tiempo
4. de cada consulta puede salir una evaluacion y eventualmente un plan
5. el historial nunca debe borrarse ni sobrescribirse logicamente

## Ciclo de vida de una evaluacion

1. se crea en estado `draft`
2. valida datos obligatorios
3. ejecuta formulas y guarda `FormulaResult`
4. genera `NutritionStrategy`
5. genera `MealDistribution` si aplica
6. pasa a `calculated`
7. el profesional revisa y confirma
8. queda disponible para originar un plan

## Ciclo de vida de un plan

1. nace desde una `Evaluation`
2. se crea `MealPlan`
3. se genera `MealPlanVersion` inicial
4. el profesional edita y guarda nuevas versiones
5. una version puede marcarse activa
6. si una nueva evaluacion reemplaza el plan, el plan anterior queda `replaced` o `archived`

## Reglas de negocio iniciales

- no debe existir evaluacion calculada sin consulta
- no debe existir plan sin evaluacion origen
- no debe recalcularse una evaluacion silenciosamente sobre el mismo registro sin dejar rastro
- cambios relevantes de entradas clinicas deben crear nuevo calculo o nueva evaluacion
- cambios relevantes del plan deben crear nueva version
- solo usuarios autorizados pueden cerrar evaluaciones o activar planes

## Datos permanentes vs variables

### Permanentes o semiestables

- identidad
- fecha de nacimiento
- sexo
- antecedentes generales
- alergias
- intolerancias
- preferencias

### Variables por consulta

- peso
- talla efectiva medida
- actividad fisica actual
- sintomas
- adherencia
- observaciones
- mediciones complementarias

## Pendientes por cerrar antes de implementar base de datos final

- catalogo exacto de roles y permisos
- formulas oficiales y sus versiones iniciales
- estructura exacta de `activity_level`
- formato definitivo de `content_payload` para planes
- si `Measurement` sera estrictamente `1:1` con `Consultation` en v1 o `1:N`
