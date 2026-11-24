# UD1. El modelo relacional

Una tabla no es una lista: es la representación de un hecho del negocio. Antes de escribir la primera consulta hay que decidir qué es una fila, qué la identifica y qué no puede repetirse. Ese trabajo se hace una vez y condiciona todo lo demás; hacerlo mal se paga en cada consulta durante años.

> **Módulo:** GBD. Gestión de bases de datos

## De la realidad a las tablas

Un sistema gestor de bases de datos relacionales guarda la información en **relaciones** —tablas— formadas por **tuplas** (filas) y **atributos** (columnas). Lo que distingue a un modelo relacional de un fichero es que las relaciones entre datos también se guardan y se pueden comprobar.

Vocabulario que conviene fijar antes de seguir:

- **Clave primaria:** el atributo o conjunto que identifica una fila sin ambigüedad. No admite nulos y no se repite.
- **Clave ajena:** un atributo que apunta a la clave primaria de otra tabla. Es lo que impide que exista un pedido sin cliente.
- **Clave candidata:** cualquier conjunto de atributos que podría identificar la fila; se elige una como primaria y las demás quedan como alternativas.
- **Dominio:** el conjunto de valores válidos de un atributo. Un importe no es texto y una fecha no es una cadena de caracteres.

## Las reglas que sostienen el modelo

Codd formuló la integridad como parte del modelo, no como una comprobación posterior:

1. **Integridad de entidad:** la clave primaria existe y es única; ningún atributo de ella puede ser nulo.
2. **Integridad referencial:** una clave ajena solo puede contener un valor que exista en la tabla a la que apunta, o nulo si se permite.
3. **Integridad de dominio:** cada valor pertenece al dominio declarado.

El motor lo comprueba si se declara. Un esquema sin claves ajenas es más rápido de escribir y más caro de mantener, porque las incoherencias las acaba detectando el usuario.

## Diseño en dos pasos

**Modelo conceptual:** entidades, atributos y relaciones, sin pensar en tablas ni en tipos. Un pedido *tiene* líneas; un cliente *realiza* pedidos; un producto *aparece en* muchas líneas.

**Modelo lógico y físico:** se traduce a tablas, se eligen claves, tipos y restricciones, y se decide qué se indexa. Aquí se toman las decisiones que afectan al rendimiento.

Y una relación de muchos a muchos no se puede representar con dos tablas: necesita una **tabla intermedia** que guarde las dos claves ajenas y, si procede, atributos propios como la cantidad.

## Tipos de datos con criterio

- **Numéricos:** enteros para identificadores; decimal exacto para dinero. Un `float` para importes produce céntimos que no cuadran.
- **Texto:** longitud variable con límite, y juego de caracteres UTF-8 desde el principio; cambiarlo después obliga a migrar todo.
- **Fechas:** tipo fecha, no texto. Ordenar cadenas con formato `dd/mm/aaaa` no ordena por tiempo.
- **Booleanos:** para estados de dos valores; para estados con más de dos, una tabla de referencia.
- **Nulos:** significan «no se sabe», no «cero» ni «vacío». Una columna que admite nulos obliga a decidir qué hacer en cada consulta.

## Lo que se comprueba

Que cada tabla tiene clave primaria; que las relaciones están declaradas con clave ajena y su acción al borrar; que no hay datos de negocio guardados como texto libre; que los importes son decimales; y que el modelo se puede leer en voz alta: «un cliente hace pedidos, un pedido tiene líneas, una línea referencia un producto».

## Errores que se repiten

- Usar una columna «id» autoincremental sin preguntarse si hay una clave natural mejor.
- Guardar datos repetidos en varias tablas «para no hacer joins».
- Declarar claves ajenas sin decidir qué pasa al borrar el padre.
- Mezclar en una columna el valor y su descripción.

## El modelo en cuatro líneas de SQL

```sql
CREATE TABLE clientes (
  id_cliente INTEGER PRIMARY KEY,
  nombre     VARCHAR(80) NOT NULL,
  email      VARCHAR(120) UNIQUE
);

CREATE TABLE pedidos (
  id_pedido  INTEGER PRIMARY KEY,
  id_cliente INTEGER NOT NULL REFERENCES clientes(id_cliente),
  fecha      DATE NOT NULL
);
```

Las dos claves hacen el trabajo: `id_cliente` identifica y `REFERENCES` impide que exista un pedido de un cliente que no está. Nada de eso lo garantiza el programa que escribe.

## Fuentes

- E. F. Codd, modelo relacional e integridad referencial.
- ISO/IEC 9075 (SQL).
- Documentación de los motores citados (PostgreSQL, MySQL/MariaDB, SQL Server).
