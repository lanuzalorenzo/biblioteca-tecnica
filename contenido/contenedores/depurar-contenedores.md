# Depurar contenedores

Depurar un contenedor es responder unas pocas preguntas en orden: ¿está arrancado?, ¿con qué código de salida?, ¿qué escribió?, ¿qué configuración recibió?, ¿puede hablar con lo que necesita? Cada respuesta descarta una capa del problema. El depurador del lenguaje, si existe, se conecta después; antes hay que entender por qué el proceso no llega a ejecutarse.

## Estado y código de salida

```bash
docker ps -a
docker inspect --format '{{.State.Status}} {{.State.ExitCode}}' web
```

`Up` indica que el proceso sigue vivo; `Exited (0)` que terminó bien, algo normal en un proceso por lotes; `Exited (1)`, `(137)` o `(139)` apuntan a error, `SIGKILL` o fallo de segmentación. `137` suele ser memoria agotada o un `kill` externo, no un error de la aplicación. `docker inspect` guarda además la hora de arranque, el reinicio y el `OOMKilled`.

Un contenedor que sale inmediatamente casi siempre tiene una de estas causas: el comando no existe, el proceso no encuentra un fichero de configuración, la aplicación falla al conectar con una dependencia o el proceso termina porque su trabajo era puntual. El código de salida y los primeros logs distinguen los casos.

## Logs

```bash
docker logs web
docker logs --tail 100 web
docker logs --since 10m web
docker logs -f web
docker logs -t web
```

`logs` lee lo que el proceso escribió por `stdout` y `stderr`. No lee ficheros de log dentro del contenedor. Si la aplicación escribe en `/var/log/app.log`, el comando devuelve vacío aunque haya errores. La solución es configurar la aplicación para escribir en la salida estándar, o enlazar el fichero a `/dev/stdout` en la imagen, como hacen algunas imágenes de servidores web.

Las líneas se guardan en el driver de logs configurado (por defecto, `json-file`). Ese fichero crece sin límite si no se configura rotación; en un servicio con mucho tráfico puede llenar el disco. `docker info` muestra el driver y sus opciones.

Si el contenedor ya no existe, sus logs desaparecen con él. Para conservarlos hay que enviarlos a un colector externo o montar un volumen de logs.

## Cuando no arranca

La técnica más directa es sustituir el comando inicial por un shell. Si la imagen define un `CMD` que se pasaría como argumento, conviene neutralizarlo a la vez:

```bash
docker run --rm -it --entrypoint /bin/sh miimagen -c 'exec /bin/sh'
```

Eso crea un contenedor con la misma imagen pero sin ejecutar la aplicación, lo que permite mirar rutas, permisos, variables y ficheros. Si la imagen no tiene shell, se copia el sistema de archivos para examinarlo desde el anfitrión:

```bash
docker cp contenedor-roto:/app ./app-del-contenedor
docker export contenedor-roto | tar -tv
```

`--volumes-from` solo monta los volúmenes del contenedor, no el resto de su sistema de archivos, así que no sirve para explorar una imagen sin shell salvo que el problema esté en los datos.

Antes de eso, `docker inspect` ya dice mucho: `Config.Cmd`, `Config.Entrypoint`, `Config.Env`, `Config.User`, `Mounts` y `State`. Un `Entrypoint` mal escrito o un `USER` sin permisos sobre el directorio de trabajo son causas frecuentes.

## Copiar ficheros

```bash
docker cp web:/var/log/app.log .
docker cp ./config.json web:/app/config.json
```

`docker cp` funciona con contenedores parados, lo que lo hace útil cuando la aplicación muere antes de poder abrir una sesión. No copia el contenido de volúmenes ni de directorios privilegiados. Para un contenedor que falla al arrancar por un fichero ausente, se copia el fichero y se reinicia:

```bash
docker cp config.json web:/app/config.json
docker start web
```

Eso es un parche de diagnóstico; la corrección es incluir el fichero en la imagen o montarlo desde el exterior.

## Ejecutar herramientas dentro

```bash
docker exec -it web sh
docker exec web ps aux
docker exec web env
docker exec -u 0 web id
```

`exec` requiere un contenedor en marcha. Si el proceso principal está sano pero la aplicación no responde, dentro se comprueba si escucha, si resuelve nombres y si alcanza la base de datos. Muchas imágenes minimalistas no traen `curl`, `ping` ni `ps`; se puede lanzar un contenedor de diagnóstico compartiendo la red y el espacio de procesos:

```bash
docker run --rm -it --network container:web --pid container:web nicolaka/netshoot
```

Ese contenedor ve las mismas interfaces y los mismos procesos que `web`, sin modificarlo. Es la forma limpia de diagnosticar una imagen sin shell.

## Recursos y eventos

```bash
docker stats
docker top web
docker events --filter container=web
docker inspect --format '{{json .State.Health}}' web
```

`stats` muestra CPU, memoria, red y disco en tiempo real. `top` lista los procesos del contenedor. `events` sigue lo que hace el motor: creación, arranque, parada, muerte, salud. `State.Health` dice si el healthcheck pasa y cuántos fallos acumula; un contenedor `unhealthy` sigue en marcha, pero un orquestador puede retirarlo del servicio.

## Convertir un contenedor en imagen

```bash
docker commit web miimagen:debug
docker run --rm -it miimagen:debug sh
```

`commit` crea una imagen con la capa de escritura del contenedor. Sirve para conservar el estado justo antes de un fallo y explorarlo después, o para recuperar cambios hechos a mano. No es una forma de construir imágenes: el resultado no es reproducible, arrastra ficheros temporales y no documenta qué se cambió. `--change` permite ajustar el comando o las variables, pero no ejecutar `RUN` ni `COPY`.

## Problemas frecuentes

| Síntoma | Causa habitual | Comprobación |
|---|---|---|
| `permission denied` en el socket | Usuario fuera del grupo `docker` | `id`, `ls -l /var/run/docker.sock` |
| `port is already allocated` | Otro proceso o contenedor usa el puerto | `ss -ltnp`, `docker ps` |
| `OOMKilled` | Límite de memoria demasiado bajo | `docker inspect`, `stats` |
| `no space left on device` | Imágenes, logs o volúmenes sin limpiar | `docker system df` |
| `exec format error` | Arquitectura de imagen incorrecta | `docker image inspect` |
| `unhealthy` | La comprobación falla o tarda más que el plazo | `logs`, `State.Health` |
| No resuelve un servicio | Red distinta o nombre mal escrito | `docker network inspect` |
| Permiso denegado en un volumen | UID del proceso sin permiso | `ls -ln`, `docker exec id` |

## Con Compose

```bash
docker compose ps
docker compose logs -f servicio
docker compose config
docker compose exec servicio sh
```

`config` es el primer comando cuando el fichero no hace lo que se espera: muestra la configuración combinada, con valores resueltos y puertos normalizados. `logs` acepta el nombre del servicio y sigue la salida de todos sus contenedores. `ps` indica salud y estado, que es más útil que mirar el contenedor a mano.

La limpieza también es parte de la depuración: un disco lleno produce fallos que parecen de la aplicación. `docker system df` dice qué ocupa; `docker system prune` recupera espacio, con el cuidado de no borrar volúmenes que contienen datos. Nunca se limpia un entorno sin saber qué volúmenes son persistentes.
