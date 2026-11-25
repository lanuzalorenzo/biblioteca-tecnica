# Persistencia y volúmenes

El sistema de archivos de un contenedor es una pila de capas de solo lectura con una capa de escritura encima. Esa capa es exclusiva del contenedor, sobrevive a un parado o un reinicio y desaparece al borrarlo. Sirve para temporales, cachés y ficheros que la aplicación genera sin valor propio; no sirve para nada que deba sobrevivir al contenedor. Para eso están los volúmenes y los *bind mounts*.

## La capa de escritura

```bash
docker run -it ubuntu sh
# dentro:
mkdir /datos && echo hola > /datos/saludo.txt
exit
docker start -i <id>
# el fichero sigue ahí
```

El fichero vive en la capa del contenedor. Otro contenedor de la misma imagen no lo ve, y al borrar el contenedor se pierde. `docker ps -s` muestra cuánto ocupa esa capa frente al tamaño virtual de las capas compartidas.

La recomendación es que los contenedores sean **sin estado**: que se puedan destruir y recrear sin pérdida. Todo lo que deba persistir se escribe fuera: base de datos, ficheros subidos, colas, registros. Eso permite reemplazar una instancia por otra, escalar y recuperarse de un fallo sin restaurar un disco.

## Tres formas de montar almacenamiento

| Tipo | Dónde vive | Lo gestiona | Uso típico |
|---|---|---|---|
| Volumen | Directorio del motor | Docker o Podman | Datos persistentes, bases de datos |
| *Bind mount* | Una ruta del anfitrión | El usuario | Configuración, código en desarrollo |
| `tmpfs` | Memoria | El kernel | Temporales rápidos, secretos en tránsito |

La sintaxis corta usa `-v`; la larga usa `--mount` y es más explícita:

```bash
docker run -v datos:/var/lib/postgresql/data postgres:16
docker run --mount type=bind,source="$PWD/config",target=/app/config,readonly miapp
docker run --tmpfs /tmp miapp
```

`-v` crea el volumen o el directorio si no existen. `--mount` falla si la ruta de origen no existe, lo que evita montajes accidentales sobre un directorio vacío. En documentación y en scripts conviene `--mount`; en la terminal, `-v` es más corto.

## Volúmenes

Un volumen es un objeto del motor con nombre propio. No depende de una ruta del anfitrión y se puede listar, inspeccionar y borrar con la CLI:

```bash
docker volume create datos
docker volume ls
docker volume inspect datos
docker volume rm datos
docker volume prune
```

Al crear un contenedor con `-v datos:/ruta`, el volumen se monta en esa ruta. Si no existe, se crea. `docker volume inspect` muestra el `Mountpoint` real en el anfitrión, pero no se debe escribir ahí a mano: el motor es el dueño.

Los **volúmenes anónimos** se crean cuando el Dockerfile declara `VOLUME /ruta` y nadie indica un origen, o con `-v /ruta` sin nombre. Tienen un identificador largo como nombre y la misma consideración que los nombrados. Su problema es que se acumulan sin que nadie los recuerde; `docker volume prune` elimina los que no usa ningún contenedor.

`VOLUME` en el Dockerfile declara un punto de montaje, pero no dice qué carpeta del anfitrión lo respalda. Esa decisión es del despliegue, no de la imagen, porque la imagen debe ser independiente del host.

## Bind mounts

Un *bind mount* monta una ruta concreta del anfitrión dentro del contenedor:

```bash
docker run -v "$PWD/src:/app" miapp
docker run -v "$PWD/nginx.conf:/etc/nginx/nginx.conf:ro" nginx
```

Es la vía natural para llevar configuración y código sin reconstruir la imagen. También es la más expuesta: el contenedor ve y puede modificar lo que haya en esa ruta, con los permisos del usuario que ejecuta el proceso. `:ro` lo monta en solo lectura. En sistemas con SELinux hay que añadir `:z` o `:Z` para etiquetar el contenido; sin eso, el proceso recibe permiso denegado aunque los permisos POSIX parezcan correctos.

En macOS y Windows, el rendimiento de un *bind mount* sobre el sistema de archivos del usuario es peor que el de un volumen, porque cada operación cruza la frontera de la máquina virtual. Para código con miles de ficheros pequeños se nota.

## tmpfs

`--tmpfs /ruta` monta un sistema de archivos en memoria. Es rápido y desaparece al parar el contenedor. Se usa para temporales que no deben tocar el disco y, con cuidado, para secretos que solo deben existir mientras el proceso arranca. No se comparte entre contenedores y consume RAM del anfitrión.

## Permisos y propietario

Los volúmenes nuevos pertenecen a `root` salvo que el motor o la imagen indiquen otra cosa. Si el proceso corre como usuario sin privilegios, puede no poder escribir. Las soluciones habituales son:

- Crear el volumen y ajustar el propietario con un contenedor auxiliar.
- Usar `--user` con un UID que tenga permiso.
- Declarar en la imagen el usuario y el `chown` de la ruta antes de cambiar de usuario.
- En Kubernetes y orquestadores, usar `fsGroup` o una política de seguridad equivalente.

Un `chown` sobre un volumen grande en cada arranque es lento; conviene hacerlo una vez o delegarlo en la inicialización de la aplicación.

## Copias y restauración

Un volumen se puede respaldar con un contenedor efímero que lo monte junto a un directorio del anfitrión:

```bash
docker run --rm \
  -v datos:/origen:ro \
  -v "$PWD:/copia" \
  alpine tar czf /copia/datos.tar.gz -C /origen .
```

La restauración invierte el proceso. Para bases de datos es preferible el mecanismo nativo —`pg_dump`, `mysqldump`, una copia consistente— porque copiar los ficheros en caliente puede dejar el volumen incoherente. El volumen conserva los datos, no la consistencia.

## Qué usar en cada caso

- Datos de una base de datos o ficheros subidos: volumen.
- Configuración distinta por entorno: *bind mount* de solo lectura o variables de entorno.
- Código en desarrollo: *bind mount*, con recarga en caliente.
- Temporales y caché: capa de escritura o `tmpfs`.
- Secretos: fichero montado en memoria o gestor de secretos, nunca en la imagen.

Compose declara los volúmenes en dos niveles: uno global con el nombre y otro por servicio con el punto de montaje. Esa separación permite que varios servicios compartan el mismo volumen sin repetir la ruta del anfitrión.
