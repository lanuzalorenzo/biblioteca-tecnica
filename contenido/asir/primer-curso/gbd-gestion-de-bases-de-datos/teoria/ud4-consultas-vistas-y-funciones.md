# UD4. Consultas, vistas y funciones

Consultar bien es hacer una pregunta precisa: qué columnas, de qué tablas, con qué condición, en qué orden y con qué agrupación. Cuando la pregunta está bien hecha, el resultado se lee solo; cuando está mal, se corrige con parches y acaba dando cifras distintas según quién la ejecute.

> **Módulo:** GBD. Gestión de bases de datos

## El orden lógico de una consulta

Se escribe empezando por `SELECT`, pero el motor la resuelve en otro orden:

```
FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT
```

Ese orden explica casi todas las dudas: por qué en `WHERE` no se puede usar un alias del `SELECT`, por qué `HAVING` filtra grupos y `WHERE` filtra filas, y por qué `ORDER BY` es lo último que se aplica.

## Unir tablas

El `JOIN` combina filas de dos tablas por una condición:

- **INNER:** solo las filas que coinciden en ambas. Es el caso habitual.
- **LEFT:** todas las de la izquierda, con nulos donde no hay coincidencia. Sirve para encontrar lo que falta —clientes sin pedidos—.
- **RIGHT:** lo mismo al revés; se usa menos porque se puede escribir al revés.
- **FULL:** ambas, con nulos por los dos lados.
- **CROSS:** producto cartesiano. Casi siempre es un error de condición olvidada.

```sql
SELECT c.nombre, COUNT(p.id_pedido) AS pedidos
FROM clientes c
LEFT JOIN pedidos p ON p.id_cliente = c.id_cliente
GROUP BY c.nombre
HAVING COUNT(p.id_pedido) = 0;
```

Esa consulta responde «quién no ha comprado nunca», una pregunta que con `INNER` devuelve vacío y hace perder media hora.

## Agrupar y agregar

`COUNT`, `SUM`, `AVG`, `MIN` y `MAX` resumen filas en grupos. Dos reglas: toda columna del `SELECT` que no esté agregada debe estar en el `GROUP BY`, y `COUNT(*)` cuenta filas mientras `COUNT(columna)` ignora los nulos. La diferencia entre esas dos cifras es un informe erróneo.

## Subconsultas y expresiones de tabla

Una subconsulta va dentro de otra y puede devolver un valor, una lista o una tabla. Es cómoda para leer y peligrosa si se anida sin criterio: tres niveles dentro de una consulta que se ejecuta cada segundo es un problema de rendimiento.

Las expresiones de tabla comunes (`WITH`) permiten nombrar pasos intermedios. Se leen de arriba abajo y suelen ser más claras que la misma lógica anidada.

## Vistas

Una vista es una consulta con nombre. Aporta tres cosas: **simplifica** lo que se repite, **restringe** columnas o filas para un perfil concreto y **desacopla** el programa de la estructura de las tablas.

```sql
CREATE VIEW pedidos_abiertos AS
SELECT id_pedido, id_cliente, fecha, total
FROM pedidos
WHERE estado = 'abierto';
```

Una vista normal se recalcula en cada consulta; una materializada guarda el resultado y hay que refrescarla. La primera siempre está al día y puede ser lenta; la segunda es rápida y puede estar desfasada. Elegir es decidir qué se prefiere.

## Funciones

Las funciones del motor evitan cálculos repetidos y centralizan reglas: formatear un importe, calcular una edad, normalizar un texto. Se escriben una vez, se prueban y se usan desde cualquier consulta o programa.

La advertencia es la de siempre: una función dentro de un `WHERE` sobre una columna indexada puede anular el índice. Lo que se gana en elegancia se paga en tiempo.

## Lo que se comprueba

Que la consulta devuelve el número de filas que se esperaba; que los `LEFT JOIN` no se han convertido en `INNER` por poner la condición en el sitio equivocado; que los grupos no pierden nulos; y que la vista no expone columnas que el perfil no debe ver.

## Errores que se repiten

- Condición de unión en el `WHERE` en lugar del `ON`, con lo que el `LEFT JOIN` pasa a comportarse como `INNER`.
- `COUNT(*)` donde se quería contar valores no nulos.
- Agrupar por una columna y seleccionar otra sin agregar.
- Crear vistas en cascada sobre vistas sin saber qué consulta se ejecuta al final.

Una función o una vista se ejecuta con los permisos que decide el motor: conviene revisar si corre con los del propietario o con los de quien la llama antes de exponerla, y versionar su definición junto al esquema.

## Fuentes

- ISO/IEC 9075 (SQL).
- Documentación de PostgreSQL y MySQL/MariaDB sobre `JOIN`, vistas y funciones.
