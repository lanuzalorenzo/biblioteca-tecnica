# UD4. Rendimiento, automatización y monitorización

Una consulta lenta no se arregla añadiendo hardware: se arregla sabiendo qué hace. El trabajo del administrador de un gestor es medir antes de tocar, automatizar lo que se repite y dejar por escrito qué se considera normal.

> **Módulo:** ASGBD. Administración de sistemas gestores de bases de datos

## Medir antes de tocar

Sin medición, optimizar es cambiar cosas al azar. Las herramientas mínimas:

- **Plan de ejecución:** `EXPLAIN ANALYZE` en PostgreSQL, `EXPLAIN` en MySQL. Muestra si el motor lee la tabla entera o usa un índice, y cuánto tarda cada paso.
- **Consultas lentas:** el registro de consultas lentas, configurado con un umbral. Sin él, el problema se detecta por la queja del usuario.
- **Estadísticas del motor:** número de conexiones, lecturas y escrituras por segundo, caché usada, bloqueos. Es lo que dice si el sistema está saturado o si solo hay una consulta mal escrita.
- **Estado del sistema operativo:** CPU, memoria, disco y latencia de escritura. El motor no es más rápido que el disco que tiene debajo.

## Índices

Un índice acelera las lecturas y penaliza las escrituras, porque hay que mantenerlo. La regla es crear índices para las consultas que se ejecutan mucho y filtrar por columnas selectivas.

- Un índice sobre una columna con dos valores distintos —un booleano— apenas ayuda.
- Un índice compuesto sirve si las consultas filtran por sus primeras columnas; en otro orden, no se usa.
- Los índices se revisan: los que no se usan ocupan espacio y ralentizan las escrituras.

Y una trampa habitual: aplicar una función a la columna en el `WHERE` —`WHERE upper(email) = ...`— anula el índice salvo que exista un índice funcional.

## Mantenimiento

Cada motor tiene su rutina:

- **PostgreSQL:** el espacio de filas muertas se recupera con `VACUUM`, que el sistema hace solo si el autovacuum está bien dimensionado. Si se queda atrás, las tablas crecen y las consultas empeoran.
- **MySQL:** las estadísticas de InnoDB se actualizan con `ANALYZE TABLE`; conviene revisar el registro de errores y el estado de los tablespaces.
- **SQL Server:** los índices se fragmentan y las estadísticas envejecen; hay tareas de mantenimiento estándar para ambas cosas.

Estas tareas se programan y se vigilan, no se ejecutan cuando alguien se acuerda.

## Automatizar sin sorpresas

Lo que se automatiza: copias, mantenimiento, revisión de espacio, comprobación de que las réplicas van al día y alertas. Lo que no conviene automatizar: cambios de esquema sin revisión, borrados masivos y reinicios.

Los guiones de administración se guardan en un repositorio, se prueban en un entorno y dejan registro. Un `cron` escrito a mano en un servidor es una tarea que se pierde en la siguiente reinstalación.

## Qué se vigila

Un cuadro de mando de base de datos con cuatro cifras y media:

| Indicador | Por qué |
|---|---|
| Conexiones activas frente al límite | El agotamiento se nota tarde |
| Consultas lentas por hora | Detecta el cambio de comportamiento |
| Espacio libre en datos y diario | Un disco lleno detiene el motor |
| Retraso de la réplica | Una réplica retrasada no sirve para leer |
| Copia de la última noche | Sin copia, todo lo demás da igual |

Cada uno necesita un umbral definido y una persona que lo mire. Una alerta que nadie atiende es ruido.

## Lo que se comprueba

Que las consultas más pesadas tienen plan revisado; que los índices creados se usan; que el mantenimiento corre solo y dejó registro; que las alertas llegan a alguien; y que la réplica, si existe, va al día.

## Errores que se repiten

- Crear índices «por si acaso» hasta ralentizar las escrituras.
- Optimizar sin medir y cambiar tres cosas a la vez.
- Dejar el registro de consultas lentas sin umbral y llenar el disco con él.
- Automatizar un borrado sin comprobar antes cuántas filas afecta.

Los umbrales no se copian de un manual: se fijan sobre lo que el sistema hace en un día normal. Una consulta de tres segundos puede ser correcta en un cierre mensual y un problema en una pantalla de atención al público. Lo que se mide una vez no sirve como referencia; hace falta una línea base de una o dos semanas antes de decidir qué es anómalo.

El número de conexiones se gestiona antes de que se agote: un agrupador delante del motor —que reutiliza un conjunto pequeño de conexiones— aguanta más carga que subir el límite. Subirlo suele ser la respuesta equivocada: más conexiones simultáneas compiten por la misma memoria y el mismo disco, y el sistema va más lento con más gente dentro.

Vigilar el crecimiento de las tablas y del diario del motor es tan importante como vigilar la CPU: un espacio de filas muertas que no se recupera crece sin ruido hasta que las consultas se vuelven lentas y el disco se llena. Es un aviso que se ve venir con semanas de antelación si alguien mira la serie temporal.

## Fuentes

- Documentación oficial de PostgreSQL, MySQL/MariaDB y SQL Server sobre `EXPLAIN`, índices y mantenimiento.
- Guías de configuración segura (CIS Benchmarks).
