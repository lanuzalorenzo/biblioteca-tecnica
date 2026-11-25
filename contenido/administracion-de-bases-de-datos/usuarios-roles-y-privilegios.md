# Usuarios, roles y privilegios

En una base de datos, el permiso no se da a la persona: se da a un rol, y el rol se asigna. Esa indirección es lo que permite contestar en un minuto «quién puede leer los datos de clientes» sin revisar cien cuentas una por una.


## Tres capas de permiso

Un usuario llega a una tabla pasando por tres puertas, y las tres están en sitios distintos:

1. **El sistema operativo y la red:** quién puede conectarse al puerto del motor.
2. **La autenticación del motor:** qué cuenta y con qué método se valida.
3. **Los privilegios sobre objetos:** qué puede leer, escribir o administrar esa cuenta.

Un problema de acceso se diagnostica en ese orden. Si el cliente ni siquiera conecta, el error no está en el `GRANT`.

## Cuentas y roles

Los motores modernos tratan cuentas y roles casi igual: un rol es un usuario sin capacidad de iniciar sesión, o una cuenta con ella según el caso.

- **PostgreSQL:** `CREATE ROLE` para ambos; `LOGIN` da capacidad de conexión. Un patrón habitual es crear roles de grupo (`lectura`, `escritura`) con sus privilegios y añadir los usuarios a ellos.
- **MySQL y MariaDB:** la cuenta se identifica por usuario **y** origen (`'app'@'10.0.0.%'`). Ese detalle permite limitar desde qué red entra cada cuenta, y es una defensa real.
- **SQL Server:** separa el inicio de sesión (servidor) del usuario (base de datos), y el esquema como contenedor de objetos.

```sql
CREATE ROLE app_lectura NOLOGIN;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_lectura;
CREATE ROLE app_usuario LOGIN PASSWORD '...';
GRANT app_lectura TO app_usuario;
```

## El principio de mínimo privilegio, aplicado

- La aplicación escribe en sus tablas y lee las que necesita; no necesita `CREATE`, ni `DROP`, ni acceso a las tablas de otros esquemas.
- Nunca `GRANT ALL` «para que funcione»: se concede lo mínimo, se prueba y se amplía solo lo que falla.
- Los privilegios de administración (crear usuarios, cambiar configuración, ver todas las bases) van a cuentas nominales, una por persona.
- Las cuentas de servicio no inician sesión interactiva y su contraseña se guarda en el gestor de secretos, no en un fichero de configuración versionado.

En PostgreSQL conviene además revisar `search_path`: si es configurable por el usuario, alguien puede crear un objeto con el mismo nombre en su esquema y hacer que una función privilegiada ejecute el suyo.

## Conceder y retirar

`GRANT` concede y `REVOKE` retira; ambos se pueden dar «con opción de concesión», que permite a quien recibe volver a conceder. Esa opción se da pocas veces y se revisa siempre.

Los permisos por columna existen —`GRANT SELECT (nombre, email)`— y son la forma de dejar leer un dato personal sin abrir la tabla entera.

Y hay que poder auditar: saber qué privilegios tiene hoy cada cuenta, no cuáles se dieron. Los catálogos del sistema (`information_schema`, `pg_roles`, `SHOW GRANTS`) lo responden; merece la pena tener una consulta guardada que lo liste.

## Cuentas que hay que revisar

- Cuentas de ejemplo del instalador.
- Cuentas de empleados que ya no están.
- Cuentas con contraseña que no rota desde 2015.
- Cuentas de aplicación compartidas por tres servicios distintos: cuando uno se ve comprometido, no se sabe cuál fue.

## Lo que se comprueba

Que la aplicación conecta con su cuenta limitada; que esa cuenta no puede crear ni borrar tablas; que un usuario de lectura no puede escribir; que ninguna cuenta privilegiada es compartida; y que la lista de privilegios efectivos coincide con lo que la política dice.

## Errores que se repiten

- Dar `ALL` al usuario de la aplicación.
- Identificar las cuentas de MySQL solo por nombre, sin origen.
- Conceder con opción de concesión y crear una cadena de permisos que nadie controla.
- Olvidar las cuentas locales que el instalador deja sin contraseña.

Las cuentas de servicio merecen su propia rutina: una por aplicación, con permisos acotados, con la contraseña en un gestor de secretos y con una fecha de revisión. Si dos servicios comparten cuenta, cuando uno se compromete no se sabe cuál fue el origen, y rotar la contraseña obliga a parar los dos a la vez.

La contraseña de una cuenta de base de datos no se acorta para que quepa en un fichero de configuración: se guarda donde corresponde y se rota con un procedimiento. Un cambio de contraseña que obliga a parar el servicio se convierte en una contraseña que nunca se cambia.

## Fuentes

- Documentación oficial de PostgreSQL, MySQL/MariaDB y SQL Server sobre roles y privilegios.
- Guías de configuración segura (CIS Benchmarks).
- Dejar una cuenta de aplicación con permisos sobre el esquema de administración.
- No revisar nunca quién tiene privilegios: los permisos concedidos por una urgencia se quedan para siempre.
