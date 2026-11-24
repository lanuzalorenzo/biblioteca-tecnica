# UD1. Instalación y configuración segura del gestor

Instalar el motor es la parte que ocupa diez minutos de una tarde de tres horas. Lo que decide si ese servidor aguanta es lo que se configura después: cuánta memoria se le da, desde dónde escucha, con qué cifrado habla y qué cuentas quedan activas.

> **Módulo:** ASGBD. Administración de sistemas gestores de bases de datos

## Elegir motor es elegir compromisos

- **PostgreSQL:** cumplimiento estricto del estándar, tipos ricos, extensiones. Control de concurrencia por versiones, buen comportamiento con muchas escrituras simultáneas.
- **MySQL y MariaDB:** implantación enorme, motor InnoDB maduro. Históricamente más laxo con el estándar y más rápido en lecturas simples.
- **SQL Server:** integración con el ecosistema Windows y con herramientas de administración muy completas.

La decisión no se toma por gusto: depende de la aplicación, del equipo que lo mantiene y del soporte disponible. Cambiar de motor después de un año es una migración, no una reinstalación.

## La configuración que importa

Tres grupos de parámetros explican la mayoría de los problemas:

- **Memoria:** el motor necesita caché para trabajar. En PostgreSQL, `shared_buffers`; en MySQL con InnoDB, `innodb_buffer_pool_size`. Si la caché es pequeña, cada consulta va al disco; si se pasa, el sistema operativo empieza a intercambiar y todo se ralentiza.
- **Conexiones:** `max_connections` y el número de procesos que las atienden. Un límite alto sin memoria detrás aguanta más conexiones y va más lento con cada una.
- **Registro y ubicación de datos:** dónde escribe el motor su diario y sus datos. Mezclar datos, índices y registros en el mismo disco obliga a que compitan por el mismo cuello de botella.

Los cambios se hacen en el fichero de configuración, se validan y se aplican con recarga; y se anotan, porque un servidor configurado por acumulación es imposible de reproducir.

## Escucha y cifrado

Por defecto, muchos motores escuchan solo en local —bien— o en todas las interfaces —cómodo y expuesto—. La decisión correcta:

- Escuchar en la dirección concreta que se necesita, o solo en local si la aplicación está en el mismo equipo.
- **Nunca** exponer el puerto del motor a Internet. Si hace falta acceso externo, va por VPN o por un servicio intermedio, no por apertura de puerto.
- Cifrar el tráfico: TLS entre cliente y servidor, con certificado verificado. En PostgreSQL se controla en `pg_hba.conf`; en MySQL, con la configuración TLS del servidor.
- Autenticación con contraseña cifrada por `SCRAM-SHA-256` o equivalente, no con los métodos antiguos que envían el hash débil.

## Cuentas de instalación

El instalador crea cuentas de administración con privilegios totales y, según el motor, alguna cuenta sin contraseña accesible solo en local. Las tres tareas de después de instalar:

1. Poner contraseña a todo lo que la tenga vacía y desactivar lo que no se usa.
2. Eliminar las cuentas de ejemplo y las bases de datos de demostración.
3. Crear una cuenta de administración nominal por persona, y una cuenta distinta, más limitada, para la aplicación.

La guía de instalación que se escribió en el módulo tenía el mismo sentido que en sistemas operativos: dejar por escrito quién queda con qué permisos, para poder repetirlo y auditarlo.

## Lo que se comprueba

Que el motor solo escucha donde debe —`ss -tulpn` lo dice—; que el cifrado está activo y el cliente lo verifica; que no queda ninguna cuenta sin contraseña; que la aplicación entra con su cuenta limitada y no con la de administración; y que la configuración aplicada coincide con la documentada.

## Errores que se repiten

- Instalar, abrir el puerto «para probar desde casa» y olvidarlo.
- Administrar con la cuenta `root` o `sa` desde la aplicación.
- Dar memoria al motor sin dejar margen al sistema operativo.
- Copiar una configuración de un servidor de 32 GB a uno de 4.

## Órdenes para revisar la instalación

```bash
ss -tulpn | grep -E "5432|3306|1433"     # qué escucha y en qué dirección
psql -c "SHOW ssl;"                       # cifrado activo en PostgreSQL
psql -c "SHOW listen_addresses;"
mysql -e "SELECT user, host, plugin FROM mysql.user;"   # cuentas y método
```

En PostgreSQL, `pg_hba.conf` decide quién conecta desde dónde y con qué método; en MySQL, `bind-address` y los privilegios por origen. Los dos ficheros se leen antes de abrir un ticket por «no puedo conectar».

Una decisión de arquitectura que se toma al instalar y se paga después: compartir servidor con la aplicación. Ahorra una máquina y mezcla dos consumos que compiten —la aplicación usa CPU y el motor usa memoria y disco—, además de juntar dos superficies de ataque en un solo equipo. Cuando la carga crece, separarlas exige migrar, y migrar en caliente es un proyecto.

Dos parámetros que se olvidan y se notan meses después: la zona horaria del servidor y el orden de comparación de textos (collation). Cambiarlos después afecta a fechas ya guardadas y a comparaciones que devuelven resultados distintos según el idioma; se fijan al crear la base y se documentan.

## Fuentes

- Documentación oficial de PostgreSQL, MySQL/MariaDB y SQL Server.
- Guías de configuración segura (CIS Benchmarks) para cada motor.
- Recomendaciones del propio motor sobre memoria y conexiones.
- Instalar con las opciones por defecto y no volver a mirar la configuración hasta que algo falla.
- Compartir el mismo servidor para las pruebas y para producción: una prueba pesada tumba el servicio real.
