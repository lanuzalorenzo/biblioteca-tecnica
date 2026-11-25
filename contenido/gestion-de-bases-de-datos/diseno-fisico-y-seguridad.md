# Diseño físico y seguridad de los datos

Un modelo relacional bien normalizado es el plano; el diseño físico es la obra: dónde se guarda cada dato, con qué tipo, qué índices lo buscan y quién puede leerlo. Dos bases con el mismo plano pueden responder en milisegundos o en minutos según esa obra.


## Del modelo al físico

El diseño lógico dice qué entidades hay y cómo se relacionan. El físico decide:

- **Tablas y columnas**, con nombres estables y sin abreviaturas crípticas.
- **Tipos de datos** ajustados: un identificador entero no es una cadena; una fecha no es un texto; un importe lleva decimales y moneda.
- **Restricciones:** clave primaria, claves foráneas, `NOT NULL`, `UNIQUE`, `CHECK`. La base defiende la integridad aunque la aplicación falle.
- **Valores por defecto** y reglas de borrado —`ON DELETE`— coherentes con el negocio.

Un tipo mal elegido se paga en espacio y en errores: comparar fechas como texto ordena mal, un `FLOAT` para dinero pierde céntimos y un `VARCHAR` sin límite esconde datos que no deberían existir.

## Almacenamiento

Cada motor organiza el disco a su manera, pero los conceptos se repiten:

- **Archivos y espacios de tabla** (*tablespaces*): dónde viven los datos y los índices. Separarlos permite mover, crecer o hacer copias por partes.
- **Páginas o bloques:** unidad de lectura y escritura. Una fila grande o un `UPDATE` que cambia de tamaño puede moverla de página.
- **Crecimiento:** el archivo de datos y el registro de transacciones crecen; hay que vigilar espacio libre, tamaño de los logs y ritmo de crecimiento.

El almacenamiento no es infinita: una base que crece sin control acaba llenando el disco y parando el servicio.

## Índices

Un índice acelera la búsqueda a cambio de espacio y de trabajo en cada escritura. Los tipos habituales:

- **B-tree:** el general; sirve para igualdad y rangos, y para ordenar.
- **Hash:** solo igualdad; útil en casos concretos.
- **Bitmap:** para columnas de baja cardinalidad; habitual en almacenes de datos, no en sistemas con muchas escrituras.
- **Compuestos:** el orden de las columnas importa; un índice `(cliente, fecha)` no sirve igual que `(fecha, cliente)`.
- **Parciales o filtrados:** indexan solo una parte de las filas, como los pedidos pendientes.
- **De cobertura:** incluyen las columnas que la consulta necesita y evitan leer la tabla.

Regla práctica: indexar las columnas de búsqueda, de unión y de orden; no indexar todo «por si acaso». Cada índice se justifica con una consulta y se comprueba con el plan de ejecución.

## Planes y estadísticas

El motor decide cómo ejecutar una consulta con las estadísticas de las tablas. Si están desactualizadas, elige mal: un recorrido completo donde bastaba un índice. Se revisa con `EXPLAIN` —o su equivalente— y se actualizan las estadísticas con `ANALYZE`. Un plan lento no se arregla añadiendo índices a ciegas; se lee primero.

## Particionado

Una tabla grande se puede dividir por rango —fechas—, por lista —país— o por hash. Sirve para borrar rápido una partición antigua, para repartir el mantenimiento y para que las consultas lean solo la parte que necesitan. No sustituye al índice y añade complejidad: se usa cuando el volumen lo justifica.

## Seguridad

La seguridad se organiza en capas:

- **Usuarios y roles:** cada aplicación con su usuario, sin compartir la cuenta de administrador. Los permisos se agrupan en roles.
- **`GRANT` y `REVOKE`:** se concede lo mínimo —`SELECT` sobre una vista, `INSERT` sobre una tabla— y se retira lo que sobra.
- **Vistas:** exponen solo las columnas necesarias y evitan dar acceso directo a la tabla.
- **Seguridad a nivel de fila:** el motor filtra por usuario o tenant cuando la política lo permite.
- **Cifrado:** en tránsito con TLS y, si se requiere, en reposo; las copias también se cifran.
- **Auditoría:** registrar accesos y cambios sensibles, con retención y protección del propio registro.

La contraseña de la base no va en el código ni en el repositorio: va en un gestor de secretos o en una variable de entorno protegida.

## Lo que se comprueba

Que los tipos y restricciones reflejan el negocio; que cada índice responde a una consulta y se ve en el plan; que las estadísticas se actualizan; que el crecimiento está vigilado; que la aplicación no usa la cuenta de administrador; que `GRANT` concede lo mínimo; y que las copias están cifradas y se restauran.

## Fuentes

- Documentación de PostgreSQL: tipos, índices, `EXPLAIN`, particionado y seguridad a nivel de fila.
- Documentación de MySQL y MariaDB: motores, índices, planes y privilegios.
- ISO/IEC 9075, lenguaje SQL.
- Orden EDU/392/2010, de 20 de enero (BOE-A-2010-3028).
