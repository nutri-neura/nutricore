Fase 0. Descubrimiento y definición funcional
Objetivo

Definir con claridad qué va a resolver el sistema, para quién y con qué alcance.

Qué debes hacer

Aquí no programas todavía. Aquí diseñas el terreno.

Necesitas definir:

tipo de usuarios del sistema
tipo de paciente objetivo
flujo real de consulta
qué datos mínimos se capturan
qué fórmulas usarás
qué significa “resultado”
qué significa “plan de comidas”
qué grado de automatización tendrá el sistema
Preguntas que debes responder
¿es para consulta general, deportiva, control de peso o clínica?
¿el enfoque inicial será solo adultos?
¿el plan será diario, semanal o por equivalencias?
¿el sistema sugerirá comidas o solo estructuras?
¿qué datos son obligatorios para hacer cálculos?
¿qué pasa si faltan datos?
¿el nutriólogo podrá editar todo manualmente?
Entregables
visión del producto
definición del MVP
flujo general del negocio
listado de módulos
lista de fórmulas estándar
reglas funcionales iniciales
Resultado esperado

Tener una base clara para que todo lo demás tenga sentido.

Fase 1. Arquitectura funcional del sistema
Objetivo

Traducir la idea del producto a módulos, entidades y flujo técnico.

Qué debes definir
módulos del sistema
pantallas principales
casos de uso
entidades del dominio
relaciones entre entidades
ciclo de vida del paciente
ciclo de vida de una evaluación
ciclo de vida de un plan
Módulos recomendados
autenticación
pacientes
consultas
evaluaciones
fórmulas
resultados
estrategias nutricionales
alimentos
plantillas de comidas
planes generados
seguimiento
reportes
Casos de uso base
registrar paciente
capturar evaluación
ejecutar cálculo automático
ver resultados
generar estructura del plan
generar plan alimenticio
editar plan
guardar versión
crear seguimiento
recalcular plan
Entregables
mapa de módulos
diagrama de flujo funcional
mapa de pantallas
lista de entidades
reglas de negocio iniciales
Resultado esperado

Ya sabes qué partes tendrá el sistema y cómo se conectan.

Fase 2. Preparación y adaptación del starter
Objetivo

Tomar devops-starter y convertirlo en la base del proyecto de nutrición.

Qué debes hacer
hacer fork del repo
renombrar identidad del proyecto
ajustar README y documentación
revisar apps/api y apps/web
mantener Compose, PostgreSQL, Redis, Traefik y monitoreo
preparar nombres, variables de entorno y servicios para el nuevo producto
Qué revisar
nombre del proyecto
nombres de servicios
variables .env
rutas de API
branding base del frontend
estructura de módulos backend
estructura inicial del frontend
Resultado esperado

Tener el repo ya listo como plataforma del sistema de nutrición y no como starter genérico.

Fase 3. Diseño del dominio clínico-nutricional
Objetivo

Definir bien la lógica central del negocio.

Qué debes modelar
paciente
expediente
consulta
mediciones
evaluación nutricional
fórmula aplicada
resultado calculado
estrategia nutricional
distribución diaria
plan de comidas
seguimiento
historial
Qué necesitas documentar
qué datos son permanentes del paciente
qué datos cambian por consulta
qué cálculos se guardan
qué resultados deben quedar versionados
cuándo se considera que un plan cambió
cuándo se recalcula una evaluación
Resultado esperado

Tener el dominio claro antes de codificar a gran escala.

Fase 4. Módulo de autenticación y base operativa
Objetivo

Tener acceso seguro al sistema y una base utilizable.

Qué incluye
login
gestión básica de usuarios
roles iniciales
protección de endpoints
sesión o JWT según tu arquitectura
estructura inicial de permisos
Roles sugeridos
admin
nutriólogo
asistente
recepcionista
Resultado esperado

Poder entrar al sistema con usuarios reales y comenzar a usar módulos internos.

Fase 5. Módulo de pacientes y expediente clínico
Objetivo

Construir el registro base del paciente.

Qué incluye
alta de pacientes
edición de pacientes
ficha general
historial básico
antecedentes
restricciones alimentarias
intolerancias
alergias
preferencias
objetivos
hábitos y estilo de vida
Datos importantes
nombre
sexo
fecha de nacimiento
edad calculada
peso
talla
actividad física
objetivo
patologías
restricciones
horarios
observaciones
Reglas importantes
separar expediente general de datos por consulta
no sobrescribir historia pasada
permitir múltiples evaluaciones por paciente
guardar mediciones por fecha
Resultado esperado

Ya puedes registrar pacientes y capturar el contexto necesario para calcular.

Fase 6. Módulo de consultas y mediciones
Objetivo

Permitir registrar evaluaciones periódicas y datos antropométricos.

Qué incluye
crear consulta
capturar mediciones
guardar fecha de evaluación
registrar peso, talla y métricas complementarias
historial de cambios por consulta
Posibles datos por consulta
peso actual
talla
IMC calculado
circunferencias
grasa corporal si aplica
síntomas
adherencia reportada
observaciones clínicas
Resultado esperado

Tener una línea de tiempo clínica del paciente.

Fase 7. Motor de fórmulas estándar
Objetivo

Automatizar el núcleo matemático del sistema.

Qué debe resolver
validar entradas
detectar datos faltantes
ejecutar fórmulas
guardar trazabilidad
devolver resultados numéricos listos para usar
Ejemplos de cálculos
IMC
peso ideal
TMB
GET
calorías objetivo
proteína diaria
grasa diaria
carbohidratos diarios
agua estimada
Qué debes cuidar
unidades consistentes
entradas obligatorias
reglas por tipo de paciente
posibilidad futura de versionar fórmulas
separación entre cálculo y análisis
Resultado esperado

El sistema ya toma datos y devuelve resultados nutricionales útiles.

Fase 8. Motor de interpretación y estrategia nutricional
Objetivo

Convertir resultados numéricos en una estrategia aplicable.

Qué incluye
clasificación general del paciente
estrategia sugerida
mantenimiento, déficit o superávit
enfoque de macros
observaciones automáticas
alertas básicas
Ejemplos de salidas
déficit moderado
mantenimiento
aumento controlado
distribución alta en proteína
sugerencia de 4 comidas
advertencias por hábitos o restricciones
Resultado esperado

El sistema ya no solo calcula; también sugiere el rumbo nutricional.

Fase 9. Resultados clínicos y vista de evaluación
Objetivo

Presentar la información de forma clara y útil para el profesional.

Qué incluye
pantalla de resultados
resumen de evaluación
cálculos obtenidos
estrategia sugerida
observaciones
validaciones visuales
salida entendible para el nutriólogo
Idealmente debe mostrar
datos base del paciente
fórmulas aplicadas
resultados
interpretación
siguiente paso recomendado
Resultado esperado

El profesional puede revisar la evaluación antes de pasar al plan.

Fase 10. Distribución diaria del requerimiento
Objetivo

Transformar requerimientos diarios en estructura de comidas.

Qué incluye
decidir número de comidas
distribuir calorías por tiempo
distribuir proteína, grasa y carbohidratos por comida
adaptar según horarios y estilo de vida
Ejemplos
desayuno 25%
comida 35%
cena 25%
colación 15%

o

comida 1 con 30 g de proteína
comida 2 con 40 g de proteína
comida 3 con 35 g de proteína
Reglas importantes
si no desayuna
si entrena temprano
si trabaja por turnos
si necesita mayor saciedad
si prefiere pocas comidas
Resultado esperado

Tener una estructura alimentaria diaria lista para generar comidas.

Fase 11. Catálogo de alimentos
Objetivo

Construir la base alimentaria que usará el generador.

Qué incluye
catálogo de alimentos
porciones base
calorías por porción
macros por porción
categorías
etiquetas
restricciones
clasificación por tipo de comida
Campos recomendados
nombre
categoría
subcategoría
porción
calorías
proteína
grasa
carbohidratos
fibra
apto o no para ciertas condiciones
desayuno/comida/cena/snack
costo aproximado opcional
Resultado esperado

Tener los ingredientes básicos para construir planes reales.

Fase 12. Sistema de equivalencias y sustituciones
Objetivo

Hacer el sistema más flexible y clínicamente usable.

Qué incluye
grupos de alimentos
equivalencias
sustituciones válidas
filtros por preferencia
filtros por intolerancia
intercambios simples
Por qué importa

Porque no todo debe armarse alimento por alimento de forma rígida.
Esto permite planes más prácticos y editables.

Resultado esperado

El sistema puede ofrecer variantes y no solo un menú cerrado.

Fase 13. Plantillas de comidas
Objetivo

Crear estructuras base para generar comidas razonables.

Qué incluye
plantillas de desayuno
plantillas de comida
plantillas de cena
plantillas de colación
estructuras según objetivo
reglas para llenado de plantillas
Ejemplo

Una plantilla de desayuno podría exigir:

una proteína principal
un carbohidrato
una fruta
una grasa opcional
Resultado esperado

Ya no partes de cero al construir cada comida.

Fase 14. Generador semiautomático de comidas
Objetivo

Proponer comidas reales a partir de requerimientos y plantillas.

Qué incluye
selección de plantilla
selección de alimentos compatibles
filtrado por restricciones
propuesta de opciones por comida
armado de comida base
Qué debe respetar
macros objetivo
restricciones
preferencias
horarios
adherencia
Resultado esperado

El sistema ya propone comidas utilizables, aunque todavía editables.

Fase 15. Generador de plan de comidas editable
Objetivo

Llegar a tu meta central: generar el plan alimenticio del paciente.

Qué incluye
plan diario o semanal
comidas por tiempo
porciones
opciones
sustituciones
edición manual por el profesional
guardado de versión final
Muy importante

No lo hagas rígido.
Debe poder ajustarse manualmente.

Resultado esperado

El nutriólogo obtiene una propuesta rápida y puede afinarla.

Fase 16. Versionado y almacenamiento del plan
Objetivo

Guardar el historial de cambios y no perder trazabilidad.

Qué incluye
guardar versión del plan
registrar fecha
registrar qué evaluación originó el plan
conservar planes anteriores
marcar plan activo
Resultado esperado

Puedes saber qué plan tenía el paciente, cuándo y por qué.

Fase 17. Reportes y PDF
Objetivo

Entregar información lista para consulta y para el paciente.

Qué incluye
resumen de evaluación
resultados clínicos
estrategia nutricional
plan de comidas
versión imprimible
PDF para paciente
PDF para expediente
Posibles salidas
hoja resumen
plan semanal
equivalencias
recomendaciones generales
Resultado esperado

El sistema entrega documentos profesionales y no solo pantallas.

Fase 18. Seguimiento y reajuste
Objetivo

Dar continuidad clínica al paciente.

Qué incluye
nuevas consultas
nuevas mediciones
comparación de progreso
recalcular requerimientos
ajustar estrategia
regenerar plan
historial evolutivo
Qué debe responder
cómo cambió el paciente
si sigue en el mismo objetivo
si requiere ajustes calóricos
si necesita cambiar estructura de comidas
Resultado esperado

El sistema se vuelve útil a largo plazo, no solo para la primera visita.

Fase 19. Dashboard clínico y métricas internas
Objetivo

Dar visibilidad operativa al nutriólogo o clínica.

Qué incluye
pacientes activos
consultas recientes
seguimientos pendientes
planes activos
métricas generales
alertas operativas
Resultado esperado

Un panel útil para el día a día de la clínica.

Fase 20. Reglas avanzadas y personalización clínica
Objetivo

Hacer el sistema más fino y adaptable.

Qué podrías agregar
protocolos por perfil de paciente
ajustes por objetivo específico
reglas por patologías
adaptación por presupuesto
adaptación por alimentos regionales
configuraciones por nutriólogo o clínica
Resultado esperado

El sistema deja de ser genérico y empieza a sentirse muy potente.

Fase 21. Automatizaciones y jobs
Objetivo

Aprovechar Redis y la base del starter para procesos asíncronos.

Qué incluye
generación de PDF en background
envío de correos
recordatorios
exportaciones
tareas pesadas diferidas
Resultado esperado

Una experiencia más fluida y profesional.

Fase 22. Testing y calidad
Objetivo

Asegurar que el sistema no se rompa conforme crece.

Qué incluye
pruebas unitarias de fórmulas
pruebas de reglas
pruebas de API
pruebas de generación de planes
pruebas del frontend
pruebas end-to-end de flujos principales
Qué debes priorizar probar
motor de fórmulas
reglas de estrategia
distribución de comidas
generación de plan
guardado de versiones
Resultado esperado

Confianza técnica para seguir creciendo.

Fase 23. Observabilidad, seguridad y producción
Objetivo

Preparar el sistema para uso real.

Qué incluye
logs estructurados
métricas
health checks
monitoreo
respaldos
seguridad de variables de entorno
endurecimiento de auth y permisos
despliegue controlado
Resultado esperado

Sistema listo para operar de forma seria.

Fase 24. IA asistida
Objetivo

Agregar inteligencia como apoyo, no como sustitución.

Posibles usos
redactar resumen clínico
explicar resultados al paciente
sugerir variantes del plan
resumir evolución del paciente
ayudar a generar observaciones
Regla importante

La IA no debe reemplazar el motor de cálculo ni el criterio clínico.

Resultado esperado

Más velocidad y mejor experiencia, sin perder control.

Orden recomendado para construir el MVP real

Si quieres avanzar sin ahogarte, yo haría este orden:

MVP Etapa 1
Fase 2
Fase 4
Fase 5
Fase 6
MVP Etapa 2
Fase 7
Fase 8
Fase 9
MVP Etapa 3
Fase 10
Fase 11
Fase 12
MVP Etapa 4
Fase 13
Fase 14
Fase 15
MVP Etapa 5
Fase 16
Fase 17
Fase 18

Eso ya te deja un producto bastante sólido.

Fases críticas del proyecto

Si tuviera que decirte cuáles son las más importantes, serían estas:

1. Fase 3

Porque si el dominio está mal, todo se deforma.

1. Fase 7

Porque el motor de fórmulas es el corazón.

1. Fase 8

Porque los números solos no sirven si no se interpretan.

1. Fase 10

Porque ahí conviertes cálculos en estructura real.

1. Fase 15

Porque ahí llegas a la meta que tú quieres: el plan.

Mi recomendación de ejecución

No quieras construir todo de golpe.

Primero busca esto:

Paciente → Evaluación → Cálculo → Resultado

Luego:

Distribución → Alimentos → Plantillas → Plan editable

Y después:

Seguimiento → PDF → automatizaciones → IA

Ese orden es el más sano.

Resumen corto de todo el roadmap
Base
definición
arquitectura
adaptación del starter
Core clínico
pacientes
consultas
mediciones
fórmulas
interpretación
resultados
Core alimentario
distribución
alimentos
equivalencias
plantillas
generador
plan editable
Producto serio
versionado
reportes
seguimiento
dashboard
automatizaciones
calidad
producción
IA
