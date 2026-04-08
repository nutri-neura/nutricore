# Product MVP

## Vision

NutriCore es un sistema para nutriologos que necesitan registrar pacientes, capturar evaluaciones, ejecutar calculos nutricionales estandar y generar una propuesta inicial de plan alimenticio editable sin depender de hojas de calculo dispersas.

El producto no busca reemplazar el criterio clinico. Su valor inicial es ordenar la operacion, reducir tiempo administrativo y dar consistencia al calculo y a la construccion del plan.

## Usuario principal

- nutriologo clinico independiente
- pequena clinica de nutricion

## Usuario secundario

- asistente o recepcionista para captura basica y administracion operativa

## Paciente objetivo del MVP

- adultos
- atencion ambulatoria
- enfoque principal en control de peso, recomposicion corporal y educacion alimentaria

Fuera de alcance inicial:

- pediatria
- embarazo
- nutricion hospitalaria
- protocolos complejos por patologia
- pacientes con requerimientos medicos altamente especializados

## Problema que resuelve

Hoy el nutriologo suele repartir el flujo entre notas, calculadoras, hojas de calculo, formatos PDF y experiencia manual. Eso genera:

- captura inconsistente de datos
- poca trazabilidad
- recalculo lento
- dificultad para comparar avance
- generacion tardada del plan alimenticio

## Objetivo del MVP

Entregar un sistema usable para:

1. registrar pacientes
2. capturar consultas y mediciones
3. ejecutar calculos nutricionales estandar
4. sugerir una estrategia nutricional inicial
5. construir una propuesta de plan diario editable
6. guardar historial de evaluaciones y versiones del plan

## Alcance funcional del MVP

### Incluido

- autenticacion y roles iniciales
- expediente general del paciente
- consultas y mediciones por fecha
- evaluacion nutricional con resultados calculados
- estrategia sugerida a partir de reglas
- distribucion diaria por tiempos de comida
- catalogo base de alimentos
- equivalencias simples
- plantillas de comidas
- generacion semiautomatica de plan diario
- edicion manual del plan
- versionado del plan
- PDF basico de evaluacion y plan
- seguimiento con comparacion de consultas

### No incluido en v1

- generacion semanal avanzada
- protocolos clinicos por patologia
- reglas por presupuesto
- automatizaciones complejas por correo o recordatorios
- IA generativa en flujo critico
- configuraciones multi clinica avanzadas

## Definiciones funcionales clave

### Resultado

Conjunto de salidas numericas y clinicas derivadas de una evaluacion. Incluye al menos:

- IMC
- peso objetivo o referencia
- TMB
- GET
- calorias objetivo
- gramos de proteina
- gramos de grasa
- gramos de carbohidratos
- agua estimada

### Estrategia nutricional

Interpretacion inicial de los resultados para orientar el plan. Incluye:

- objetivo energetico: mantenimiento, deficit o superavit
- sesgo de macros
- numero sugerido de comidas
- observaciones y alertas basicas

### Plan de comidas

Propuesta editable de estructura diaria con tiempos de comida, alimentos, porciones y opciones de sustitucion. En el MVP sera diario, no semanal.

## Nivel de automatizacion del MVP

El sistema sera semiautomatico.

- calcula automaticamente
- interpreta con reglas base
- propone estructura diaria
- propone comidas iniciales
- permite edicion manual total al nutriologo antes de guardar la version final

No se permitira que el sistema cierre un plan de forma completamente rigida o ineditable.

## Flujo general del negocio

1. usuario inicia sesion
2. registra o busca paciente
3. revisa expediente general
4. crea consulta
5. captura mediciones y contexto de la consulta
6. ejecuta evaluacion
7. revisa resultados y estrategia sugerida
8. genera distribucion diaria
9. genera propuesta de plan
10. ajusta manualmente
11. guarda version del plan
12. exporta PDF si aplica
13. en seguimiento crea nueva consulta y compara avance

## Datos obligatorios del MVP

### Paciente

- nombre completo
- sexo
- fecha de nacimiento
- objetivo principal

### Consulta o evaluacion

- fecha
- peso actual
- talla
- nivel de actividad fisica

### Opcionales en MVP

- circunferencias
- porcentaje de grasa corporal
- sintomas
- restricciones alimentarias
- alergias
- intolerancias
- horarios
- observaciones clinicas

## Regla cuando faltan datos

- si falta un dato obligatorio, la evaluacion no debe calcularse
- el sistema debe indicar exactamente que campo falta
- los datos opcionales no bloquean el flujo, pero pueden limitar sugerencias

## Roles iniciales

- `admin`: administra usuarios, catalogos y configuracion general
- `nutriologo`: acceso completo a pacientes, consultas, evaluaciones y planes
- `asistente`: captura y edicion operativa sin cerrar evaluaciones clinicas
- `recepcionista`: acceso basico a agenda futura y datos administrativos, sin acceso a resultados clinicos sensibles

## Reglas funcionales iniciales

- el expediente general no debe sobrescribir historia pasada
- cada consulta genera un registro independiente
- una evaluacion siempre pertenece a una consulta
- los resultados calculados deben guardar trazabilidad de formula y version
- un plan siempre nace de una evaluacion concreta
- un plan puede tener varias versiones
- solo una version del plan puede estar activa por paciente
- el profesional puede editar cualquier propuesta antes de guardarla

## Formulas base del MVP

El MVP debe soportar al menos:

- IMC
- peso de referencia
- TMB
- GET
- calorias objetivo
- distribucion diaria de macros
- agua estimada

La seleccion exacta de formulas debe documentarse aparte en una tabla tecnica con:

- nombre
- objetivo
- entradas requeridas
- unidad esperada
- formula aplicada
- validaciones
- version

## Modulos del MVP

- autenticacion
- usuarios y roles
- pacientes
- expediente clinico
- consultas y mediciones
- evaluaciones
- motor de formulas
- resultados
- estrategias nutricionales
- distribucion diaria
- catalogo de alimentos
- equivalencias
- plantillas de comidas
- planes generados
- seguimiento
- reportes y PDF

## Criterios de exito del MVP

- un nutriologo puede completar una evaluacion sin hojas externas
- el sistema calcula resultados consistentes y repetibles
- el sistema genera una propuesta inicial de plan diario editable
- el historial del paciente conserva consultas, evaluaciones y planes previos
- el profesional puede imprimir o exportar un resumen usable
