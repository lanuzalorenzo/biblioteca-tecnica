# UD3. SQL: definición y manipulación de datos

SQL no es un lenguaje, son varios que comparten sintaxis: uno crea la estructura, otro la rellena, otro la consulta y otro decide quién puede hacer cada cosa. Confundirlos es la causa de la mitad de los errores de un principiante.

> **Módulo:** GBD. Gestión de bases de datos

## Las familias de órdenes

| Familia | Qué hace | Órdenes |
|---|---|---|
| DDL | Define la estructura | `CREATE`, `ALTER`, `DROP`, `TRUNCATE` |
| DML | Manipula los datos | `SELECT`, `INSERT`, `UPDATE`, `DELETE` |
| DCL | Controla permisos | `GRANT`, `REVOKE` |
| TCL | Gestiona transacciones | `BEGIN`, `COMMIT`, `ROLLBACK` |

`TRUNCATE` pertenece al DDL aunque borre datos: no se puede deshacer fila a fila y no dispara los mismos eventos que `DELETE`.

## Crear una tabla con criterio

```sql
CREATE TABLE pedidos (
  id_pedido    INTEGER      PRIMARY KEY,
  id_cliente   INTEGER      NOT NULL REFERENCES clientes(id_cliente),
  fecha        DATE         NOT NULL DEFAULT CURRENT_DATE,
  estado       VARCHAR(20)  NOT NULL CHECK (estado IN ('abierto','servido','anulado')),
  total        DECIMAL(10,2)
);
```

Cada pieza tiene una razón: la clave primaria identifica; `NOT NULL` impide el vacío accidental; la referencia impide pedidos huérfanos; el `CHECK` evita estados inventados; y el decimal guarda dinero sin redondear.

Al declarar una clave ajena se decide qué ocurre al borrar el padre: `ON DELETE RESTRICT` impide borrar lo que tiene hijos, `CASCADE` los borra en cascada —cómodo y peligroso— y `SET NULL` los deja sin referencia. La opción por defecto, si no se escribe, rara vez es la que se quiere.

## Modificar la estructura

`ALTER TABLE` añade, cambia o quita columnas y restricciones. Tres avisos de administración:

- Añadir una columna obligatoria a una tabla con datos exige un valor por defecto o dos pasos: crearla opcional, rellenar y luego declararla obligatoria.
- Cambiar el tipo puede reescribir la tabla entera y bloquear escrituras mientras dura.
- Quitar una columna en producción destruye datos que quizá alguien consulta.

Por eso los cambios de esquema se versionan y se aplican con un guion, no a mano en cada entorno.

## Manipular datos

- `INSERT` con lista de columnas explícita: si mañana se añade una columna, la orden sigue siendo válida.
- `UPDATE` y `DELETE` **siempre con `WHERE`**. El orden habitual es escribir primero el `SELECT` con la misma condición, comprobar las filas que salen y convertirlo después.
- Las operaciones sobre muchas filas se hacen dentro de una transacción: o se aplican todas, o ninguna.

```sql
BEGIN;
UPDATE pedidos SET estado = 'servido' WHERE fecha < '2015-12-31' AND estado = 'abierto';
-- comprobar el número de filas afectadas
COMMIT;
```

Si el número de filas no es el esperado, `ROLLBACK` y a investigar. Esa comprobación cuesta dos segundos y evita restaurar una copia.

## Cargar y actualizar en bloque

Cuando hay que insertar muchas filas, la diferencia entre una orden por fila y una carga masiva se mide en minutos. `INSERT ... SELECT` copia entre tablas sin salir del motor, y la mayoría de los motores admiten cargar desde un fichero de texto con formato delimitado. Para actualizar si existe o insertar si no, existe la orden de mezcla (`MERGE`, o `INSERT ... ON CONFLICT` en PostgreSQL), que evita el patrón de consultar primero y decidir después, que falla en cuanto dos sesiones hacen lo mismo a la vez.

Y una precaución: una carga masiva dentro de una transacción mantiene bloqueos y registro de cambios durante toda la operación. En tablas grandes se hace por lotes, comprobando después que el número de filas insertadas coincide con el de líneas leídas.

## Restricciones frente a validación en la aplicación

Se puede validar en el programa y dejar la tabla sin restricciones. Funciona hasta que otro programa, un volcado o una consulta manual escriben directamente. La base de datos es el último lugar donde una regla se cumple siempre, y por eso las reglas importantes se declaran ahí.

## Lo que se comprueba

Que cada tabla tiene clave y restricciones; que los cambios de esquema están en un guion versionado; que ninguna orden de modificación se ejecutó sin comprobar antes cuántas filas afecta; y que los tipos admiten los datos que se van a guardar, incluido el juego de caracteres.

## Errores que se repiten

- `UPDATE` sin `WHERE`.
- Guardar importes en `FLOAT`.
- Declarar claves ajenas sin acción de borrado y descubrirlo con el primer borrado.
- Mezclar en un guion cambios de esquema y de datos, sin poder repetirlo.

## Fuentes

- ISO/IEC 9075 (SQL).
- Documentación de PostgreSQL, MySQL/MariaDB y SQL Server sobre DDL y transacciones.
