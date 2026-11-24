# Monitorización

Monitorizar es medir lo que hace el sistema para saber si cumple su función antes de que el fallo lo note el usuario. No es una pantalla con gráficas: es un conjunto de preguntas con respuesta sobre latencia, errores, tráfico y saturación.

## Tres tipos de dato

Una métrica es un número en el tiempo y sirve para ver tendencias y alertar. Un registro es un evento con contexto y sirve para explicar qué pasó. Una traza sigue una operación por varios servicios y dice en qué salto se fue el tiempo. La regla práctica: alertar sobre métricas, investigar con registros y trazas.

## Azure Monitor y Log Analytics

Azure Monitor recoge los tres tipos de dato de los recursos y de las aplicaciones, los guarda y permite actuar sobre ellos. Las métricas de plataforma vienen sin configurar nada; los registros se envían a un área de trabajo de Log Analytics, donde se cruzan datos de varios recursos y se consultan con KQL, un lenguaje de solo lectura que filtra, agrupa y ordena.

## Application Insights

Application Insights mide desde dentro de la aplicación: peticiones, dependencias, excepciones, trazas y la unión de todo bajo un mismo identificador, que es lo que da la traza distribuida. El muestreo descarta parte de la telemetría cuando hay volumen, y eso convierte los recuentos en estimaciones.
