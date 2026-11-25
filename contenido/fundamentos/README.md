# Fundamentos de Azure

Azure no es un catálogo de servicios: es una jerarquía donde cada cosa que se crea tiene un dueño, un ámbito y un precio. Antes de elegir un servicio conviene tener claro dónde vive, quién manda sobre él y qué hereda de lo que hay por encima.

## La unidad es el recurso

Todo lo que se crea —una máquina, una base de datos, una red, una regla— es un recurso con un tipo, una configuración y un coste. Los recursos se agrupan, se etiquetan y se despliegan en conjunto, y ninguno existe fuera de una suscripción.

## El ámbito decide

Los permisos, las políticas y los bloqueos se aplican en un nivel de la jerarquía y bajan a los hijos. Un problema de ámbito no se arregla concediendo más permisos: se arregla moviendo la decisión al nivel que le corresponde.

## Por qué importa

Casi todos los fallos de gobierno en la nube nacen en estas cuatro piezas: recursos fuera de su grupo, permisos concedidos en la suscripción entera, políticas que nadie aplicó porque se asignaron donde no tocaba y nombres que se decidieron tarde.

Leer esto antes que cualquier servicio ahorra el trabajo de rehacer lo que ya estaba mal colocado.
