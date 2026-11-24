# UD3. Administración de sistemas Linux

En Windows se administra con ventanas; en Linux se administra con ficheros de texto y órdenes. Eso no es una preferencia estética: significa que todo lo que hace el sistema se puede leer, comparar y reproducir, que es exactamente lo que se necesita cuando hay veinte servidores iguales.

> **Módulo:** ISO. Implantación de sistemas operativos

## Dónde está cada cosa

La jerarquía está normalizada para que un administrador encuentre lo mismo en cualquier distribución:

| Ruta | Qué contiene |
|---|---|
| `/etc` | Configuración del sistema y de los servicios |
| `/var` | Datos variables: registros, colas, bases de datos, web |
| `/usr` | Programas y bibliotecas |
| `/home` | Datos de usuario |
| `/tmp` | Temporal, se borra al reiniciar |
| `/srv` y `/opt` | Servicios y software instalado aparte |

Un fichero de configuración se edita, se prueba y se guarda la copia anterior. La costumbre de tocar a mano sin anotar es la causa de la mitad de las diferencias entre equipos que deberían ser iguales.

## Usuarios, grupos y permisos

- Las cuentas están en `/etc/passwd`, las contraseñas cifradas en `/etc/shadow` y los grupos en `/etc/group`.
- `useradd` crea, `usermod` modifica, `passwd` cambia la clave, `userdel` borra; `groupadd` y `gpasswd` para grupos.
- **`sudo`** ejecuta con privilegios y deja registro de quién lo hizo. Es la forma correcta de administrar; entrar como `root` directo no deja rastro de persona.

Los permisos son tres por cada uno de los tres ámbitos —dueño, grupo, resto— y se leen como `rwx` o en octal (lectura 4, escritura 2, ejecución 1):

```
-rw-r--r--  1 lorenzo devs  1024 ene 1 10:00 informe.txt
drwxrwxr-x  2 lorenzo devs  4096 ene 1 10:05 proyecto/
```

Además de los permisos básicos hay tres bits que se preguntan en los exámenes y se usan en producción:

- **Sticky** en un directorio (`t`): cada uno solo puede borrar lo suyo. Es lo que protege `/tmp`.
- **Setgid** en un directorio (`s`): lo creado dentro hereda el grupo del directorio. Imprescindible en carpetas compartidas.
- **Setuid** en un ejecutable: se ejecuta con los permisos del dueño. Es potente y peligroso; se revisa, no se deja a la ligera.

`umask` decide los permisos que **no** tendrá lo nuevo; con `022`, un fichero nace en `644` y un directorio en `755`. Para permisos más finos hay ACL (`setfacl`), que permiten dar acceso a un usuario concreto sin meterlo en el grupo.

## Procesos y servicios

- `ps` y `top` muestran procesos; `kill` envía señales, siendo `TERM` la petición amable y `KILL` el último recurso que no permite limpiar nada.
- Un proceso pasa por estados —en ejecución, dormido, detenido, zombi— y entenderlos explica por qué un servicio «está» pero no responde.
- Los servicios los gestiona **systemd**: `systemctl start`, `stop`, `status`, `enable`. Un servicio habilitado arranca solo; uno activo pero no habilitado se queda muerto en el siguiente reinicio, y esa diferencia explica muchas incidencias de madrugada.
- Los registros van a **journald** y a los ficheros de `/var/log`. `journalctl -u servicio` es la primera orden ante un fallo.

## Paquetes y red

El software se instala desde repositorios con el gestor de la distribución —`apt` en Debian y derivados, `dnf` en la familia Red Hat—, que resuelve dependencias y permite actualizar de forma controlada. Compilar desde el código fuente deja el sistema sin trazabilidad de versión y se reserva para lo que no está empaquetado.

La configuración de red vive en la herramienta de la distribución (`netplan`, NetworkManager, `systemd-networkd`), y se comprueba con `ip addr` y `ip route`, no adivinando.

## Lo que se comprueba

Que la cuenta de uso diario no es `root` ni está en el grupo `sudo` sin necesidad; que los servicios necesarios arrancan tras reiniciar; que los registros se conservan el tiempo previsto; que las actualizaciones de seguridad están aplicadas; y que una carpeta compartida se comporta igual para el dueño, para el grupo y para un tercero.

## Errores que se repiten

- Dar `777` para resolver un permiso. Casi siempre se arregla con un grupo y `2775`.
- Editar configuración y no recargar el servicio, o recargar y no comprobar.
- Instalar software a mano fuera del gestor de paquetes y perder el control de versiones.
- Dejar `root` con acceso por contraseña y SSH abierto.

## Órdenes que se usan a diario

```bash
id usuario                       # uid, gid y grupos efectivos
adduser lorenzo                  # crea cuenta con su home (Debian y derivados)
chmod 2775 /srv/proyectos        # setgid para heredar el grupo
chown -R lorenzo:devs /srv/proyectos
setfacl -m u:ana:rwx /srv/proyectos   # permiso puntual sin tocar el grupo
umask                            # qué permisos no se aplican por defecto
systemctl enable --now ssh       # habilitar y arrancar en una orden
journalctl -u ssh -n 50          # últimas líneas del servicio
ss -tulpn                        # puertos en escucha y proceso dueño
```

## Fuentes

- Estándar de jerarquía del sistema de ficheros (FHS).
- Páginas de manual de `systemctl`, `journalctl` y `setfacl`.
- Guías de configuración segura (CIS Benchmarks) para distribuciones Linux.
