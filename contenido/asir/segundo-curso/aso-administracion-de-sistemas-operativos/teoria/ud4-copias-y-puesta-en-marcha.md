# UD4. Copias de seguridad y puesta en marcha del servidor

Montar un servidor tiene dos momentos que se suelen saltar: antes, decidir cómo se recupera si se pierde; después, comprobar que la recuperación funciona. El resto del tiempo el servidor funciona solo, y por eso nadie mira hasta que un día no está.

> **Módulo:** ASO. Administración de sistemas operativos

## Qué se copia en un servidor

Cuatro cosas distintas, y cada una con su herramienta:

- **El sistema:** la configuración, los paquetes instalados y los ficheros de `/etc`. Se protege con una imagen o con configuración declarativa que permita reconstruirlo.
- **Los datos:** lo que no se puede volver a generar. Es la copia que no se negocia.
- **Las bases de datos:** se copian con el mecanismo del motor, no copiando ficheros abiertos.
- **El directorio:** cuentas, grupos y directivas. Perderlo es perder el acceso a todo lo demás, y por eso necesita copia y, al menos, dos controladores.

## Herramientas y patrones

- **Imagen del sistema:** útil para reconstruir un equipo igual, no para recuperar un fichero. En Windows, la copia de imagen y los puntos de restauración; en Linux, una instantánea o una herramienta de clonado.
- **Copia a nivel de fichero:** `tar` para archivos completos de una carpeta, `rsync` para sincronizar manteniendo permisos y fechas. `rsync` es la base de casi todo: primero una copia completa, después solo las diferencias.
- **Instantáneas del hipervisor:** rápidas para volver atrás antes de un cambio. No son copia de seguridad: viven en el mismo almacenamiento y con las mismas credenciales.
- **Cifrado:** una copia fuera del servidor debe ir cifrada, y la clave se guarda en otro sitio. Si la clave viaja con la cinta o con el disco, el cifrado no protege de nada.

En el módulo se practicó con copias de imagen del sistema y con BitLocker. El cifrado de volumen es la pieza que protege el disco extraído, y por eso se configura antes de sacar el equipo del taller, no después.

## Programar y verificar

Una copia programada necesita cuatro decisiones escritas: qué se copia, cada cuánto, cuánto se conserva y quién comprueba. La quinta —cómo se restaura— es la que decide si el resto sirve.

- **Rotación:** conservar diarias, semanales y mensuales evita que un fallo detectado tarde se haya copiado encima de las copias buenas.
- **Comprobación:** el trabajo termina con éxito cuando el fichero se puede leer, no cuando la herramienta dice «hecho». Una suma de comprobación o una restauración de muestra lo demuestra.
- **Prueba de restauración:** al menos una vez al año, medida en tiempo y hecha por alguien distinto de quien montó la copia.

## La lista de puesta en marcha

Un servidor nuevo se entrega con una comprobación hecha, no con la promesa de que funciona:

1. Nombre, dirección y hora fijados, y servicio de tiempo funcionando.
2. Sistema actualizado y con el repositorio de seguridad aplicado.
3. Cuentas creadas por rol, sin cuentas compartidas; administrador local con contraseña única.
4. Servicios necesarios y habilitados; los demás, apagados.
5. Cortafuegos activo con solo los puertos del servicio.
6. Registro configurado, con retención y envío a un sistema central si existe.
7. Copia programada y una restauración de prueba hecha.
8. Documentación: qué es, para qué, quién responde y qué hacer si falla.

Esa lista es la diferencia entre un servidor y un servidor en producción. La octava línea es la que más se salta y la que más se agradece a las tres de la mañana.

## Lo que se comprueba

Que la copia se ha hecho de verdad —tamaño y fecha—; que se puede restaurar un fichero concreto y un servicio completo; que la restauración deja el sistema operativo, no solo los datos; que la contraseña de recuperación del cifrado está custodiada; y que la lista de puesta en marcha está firmada por quien la hizo.

## Errores que se repiten

- Copiar datos y no la configuración: se recuperan los ficheros y no el servicio.
- Copiar una base de datos con el motor en marcha y obtener un fichero inconsistente.
- Guardar la copia en el mismo servidor o con la misma cuenta que administra todo.
- Considerar que una instantánea del hipervisor es la copia de seguridad.
- No probar nunca la restauración y descubrirlo el día del incidente.

## Órdenes para copiar y restaurar

```bash
rsync -aAX --delete /srv/datos /backup/datos/     # conserva permisos y ACL
tar -czf /backup/etc-$(date +%F).tar.gz /etc      # configuración con fecha
rsync -aAX --dry-run /backup/datos/ /srv/datos/   # ensayo de restauración
find /backup -name "*.tar.gz" -mtime +90 -print   # qué caduca
```

En Windows, `wbadmin start backup` para imagen del sistema y `wbadmin get versions` antes de restaurar. El ensayo con `--dry-run` muestra qué se sobrescribiría sin tocar nada.

El soporte importa menos de lo que parece: un disco externo bien rotado protege más que una cinta mal gestionada, y el almacenamiento de objeto con retención bloqueada ha sustituido a la cinta en muchos sitios. Lo que no cambia es la regla: dos medios distintos, una copia fuera y una que no se pueda borrar desde la cuenta que administra el servidor.

## Fuentes

- ISO/IEC 27001:2022, control de copias de seguridad (A.8.13).
- NIST SP 800-34, guía de contingencias.
- Documentación oficial de `rsync`, `tar`, BitLocker y de las herramientas de copia del hipervisor.
