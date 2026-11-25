# Normalización

Normalizar es quitar de la tabla lo que no depende de su clave. Suena a purismo y es lo contrario: es la forma de que un dato viva en un solo sitio, de modo que corregirlo no exija recorrer seis pantallas ni dejar copias contradictorias.


## Por qué una tabla mal hecha duele

Imagina una tabla de pedidos con estos datos: número de pedido, fecha, cliente, dirección del cliente, producto, precio del producto y cantidad.

- Cambiar la dirección del cliente obliga a cambiarla en todos sus pedidos. Si uno se queda sin cambiar, hay dos direcciones y nadie sabe cuál vale.
- El precio del producto se repite en cada línea; si sube, hay que decidir si se actualiza el histórico —no— y entonces el dato ya no es único.
- Borrar el único pedido de un cliente borra también sus datos de contacto.

Cada uno de esos síntomas es una **dependencia** que sobra. La normalización las nombra y las elimina por pasos.

## Primera forma normal

Una tabla está en **1FN** si cada celda contiene un valor simple y atómico, sin listas y sin grupos repetidos.

- Mal: una columna «teléfonos» con `600111222, 600333444`.
- Bien: una tabla de teléfonos con el identificador del cliente y un teléfono por fila.

Se cumple además que cada fila es distinguible, lo que exige clave primaria.

## Segunda forma normal

Está en **2FN** si está en 1FN y todo atributo que no es clave depende de la clave **completa**, no de una parte. Solo aplica cuando la clave es compuesta.

En el ejemplo, con clave `(pedido, producto)`, la dirección del cliente depende solo del pedido y el precio solo del producto: son dependencias parciales y salen a tablas propias.

## Tercera forma normal

Está en **3FN** si está en 2FN y ningún atributo no clave depende de otro atributo no clave. Es la **dependencia transitiva**.

Si en la tabla de productos guardo el código de proveedor y su nombre, el nombre depende del código, no de la clave del producto. El nombre se va a la tabla de proveedores y aquí queda el código.

## Un resultado legible

Tras normalizar, el ejemplo queda en cinco tablas: clientes, pedidos, líneas de pedido, productos y proveedores. Cada hecho tiene su sitio y las relaciones se declaran con claves ajenas.

| Tabla | Clave | Qué guarda |
|---|---|---|
| `clientes` | `id_cliente` | Identidad y contacto |
| `pedidos` | `id_pedido` | Fecha y cliente |
| `lineas` | `id_pedido`, `id_producto` | Cantidad y precio aplicado |
| `productos` | `id_producto` | Nombre, precio actual, proveedor |

El precio en la línea no es una repetición: es el precio pactado en ese pedido. Un histórico no se normaliza fuera; se guarda a propósito.

## Cuándo se desnormaliza

La teoría pide 3FN y la práctica a veces pide leer rápido. Se desnormaliza a sabiendas cuando el coste de unir tablas es alto y el dato repetido es estable: un total calculado que se guarda, un nombre que se copia al documento emitido.

La diferencia entre desnormalizar y no haber normalizado es que en el primer caso hay una decisión escrita y una comprobación que mantiene la copia coherente. En el segundo hay un error.

Existen formas más estrictas —la forma normal de Boyce-Codd, la cuarta y la quinta— que resuelven casos de dependencias múltiples. Para una administración, 3FN es el objetivo razonable y el resto se consulta cuando aparece el caso.

## Lo que se comprueba

Que cada tabla tiene una clave; que ningún atributo no clave depende de parte de la clave; que no hay atributos que dependan de otro atributo no clave; y que las tablas que se han dejado sin normalizar están justificadas.

## Errores que se repiten

- Normalizar sobre el papel y dejar la base de datos con texto libre donde debería haber referencias.
- Creer que 3FN prohíbe guardar importes históricos.
- Aplicar 1FN a medias: campos separados por comas «porque son pocos».
- Normalizar hasta el extremo y descubrir que la consulta principal une ocho tablas.

| Comprobación | Pregunta que se hace |
|---|---|
| 1FN | ¿Hay celdas con listas o valores compuestos? |
| 2FN | ¿Algún atributo depende solo de parte de la clave? |
| 3FN | ¿Algún atributo no clave depende de otro no clave? |

## Fuentes

- E. F. Codd, formas normales y dependencias funcionales.
- ISO/IEC 9075 (SQL).
- Documentación de los motores citados.
