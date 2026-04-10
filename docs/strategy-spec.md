# Strategy Spec

## Objetivo

Definir la primera capa de interpretacion nutricional sobre una evaluacion ya calculada para que NutriCore pase de estimar gasto energetico a proponer una direccion de trabajo util en consulta.

## Principio rector

La estrategia nutricional no reemplaza el juicio clinico. En el MVP:

- interpreta una evaluacion energetica ya existente
- aplica reglas deterministas y auditables
- produce una recomendacion base de kcal y macros
- deja advertencias explicitas

No genera todavia un plan alimenticio completo.

## Alcance del MVP

Soportado en v1:

- adultos ambulatorios
- pacientes no criticos
- objetivos generales de consulta

Objetivos automaticos permitidos:

- `maintenance`
- `fat_loss`
- `muscle_gain`
- `recomposition`

Fuera de alcance en v1:

- patologias complejas con requerimientos clinicos especiales
- protocolos avanzados de nutricion deportiva
- embarazo
- pediatria
- nutricion hospitalaria

## Dependencias de entrada

La estrategia solo se genera si ya existe una `Evaluation` valida y si el contexto tiene:

- `maintenance_energy_kcal`
- `weight_kg`
- `sex`

Si falta alguno:

- no se genera estrategia
- se devuelve error explicito

## Politica del MVP para energia objetivo

### `maintenance`

- energia objetivo = `maintenance_energy_kcal`

### `fat_loss`

- energia objetivo = `maintenance_energy_kcal * 0.85`
- si el resultado cae por debajo del piso operativo, se aplica piso

### `muscle_gain`

- energia objetivo = `maintenance_energy_kcal * 1.10`

### `recomposition`

- si `bmi >= 25`: energia objetivo = `maintenance_energy_kcal * 0.95`
- si `bmi < 25`: energia objetivo = `maintenance_energy_kcal`
- debe agregarse advertencia cuando `recomposition` no aplica deficit

## Pisos operativos del MVP

- mujer: `1200 kcal`
- hombre: `1400 kcal`

Si la energia objetivo calculada queda por debajo del piso:

- se reemplaza por el piso correspondiente
- se registra advertencia

## Politica del MVP para macros

### Proteina

- `maintenance`: `1.6 g/kg`
- `fat_loss`: `1.8 g/kg`
- `muscle_gain`: `1.8 g/kg`
- `recomposition`: `2.0 g/kg`

### Grasa

- `maintenance`: `0.8 g/kg`
- `fat_loss`: `0.8 g/kg`
- `muscle_gain`: `0.9 g/kg`
- `recomposition`: `0.8 g/kg`

### Carbohidratos

- kcal remanentes = `target_energy_kcal - (protein_g * 4) - (fat_g * 9)`
- `carbs_g = max(remaining_kcal / 4, 0)`

Si el remanente es negativo:

- se fija `carbs_g = 0`
- se agrega advertencia

## Salida esperada del MVP

La estrategia debe devolver como minimo:

- `goal_code`
- `maintenance_energy_kcal`
- `target_energy_kcal`
- `energy_delta_kcal`
- `protein_g`
- `fat_g`
- `carbs_g`
- `protein_kcal`
- `fat_kcal`
- `carbs_kcal`
- `protein_pct`
- `fat_pct`
- `carbs_pct`
- `strategy_set_version`

## Persistencia

### `nutrition_strategies`

Debe guardar:

- `evaluation_id`
- `goal_code`
- `status`
- `strategy_set_version`
- `recommendation_payload`
- `warnings_payload`
- `created_by_user_id`
- `created_at`

## Reglas de seguridad del MVP

- no fingir precision clinica fuera del alcance
- no asumir que la estrategia ya es plan alimenticio
- no borrar ni sobreescribir estrategias previas
- permitir multiples estrategias por evaluacion para comparar objetivos
