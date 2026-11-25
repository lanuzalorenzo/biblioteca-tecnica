# Imágenes y ciclo de vida

Una imagen se descarga, se inspecciona y se ejecuta. El contenedor que nace de ella tiene un ciclo de vida corto o largo según lo que haga su proceso inicial: si el proceso termina, el contenedor se para, pero no desaparece hasta que se borra. Entender esa separación —parado no es borrado, borrado no es lo mismo que desetiquetado— evita la mayor parte de las sorpresas al limpiar.

## Descargar y mirar imágenes

```bash
docker pull nginx
docker images
docker image inspect nginx
docker history nginx
```

`pull` trae la imagen del registro y todas sus capas; si ya existe, comprueba si la etiqueta apunta a otra cosa. `images` lista repositorio, etiqueta, identificador, fecha y tamaño. `inspect` devuelve el JSON de configuración: comando, variables, puertos declarados, capas y arquitectura. `history` muestra qué instrucción generó cada capa y cuánto ocupa.

El tamaño que muestra `images` es la suma de las capas de la imagen, no el espacio real en disco: las capas compartidas se cuentan una vez por imagen aunque existan una sola vez. Por eso dos imágenes derivadas de la misma base parecen grandes y ocupan bastante menos.

## Ejecutar

```bash
docker run nginx
docker run -d --name web -p 8080:80 nginx
docker run --rm -it alpine sh
```

Sin modificadores, el contenedor ocupa el terminal: la salida del proceso se enlaza a la consola y el comando espera a que termine. Con `-d` se crea en segundo plano y se devuelve el identificador. Con `-it` se abre una sesión interactiva, que solo tiene sentido si el proceso inicial lee de la entrada estándar, como un shell.

| Modificador | Efecto |
|---|---|
| `--name` | Nombre legible en lugar del generado |
| `-d`, `--detach` | Segundo plano |
| `-it` | Entrada interactiva y terminal |
| `-e CLAVE=valor` | Variable de entorno para ese contenedor |
| `-p host:contenedor` | Publica un puerto |
| `--rm` | Borra el contenedor al terminar |
| `--restart unless-stopped` | Política de reinicio |
| `-v origen:destino` | Volumen o *bind mount* |

Si la imagen no está en local, `run` la descarga. Esa comodidad esconde un detalle: la etiqueta puede haber cambiado en el registro desde la última descarga. Para reproducir un despliegue se fija un digest o se usa `--pull=always`.

## Listar y leer el estado

```bash
docker ps
docker ps -a
docker ps -q
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

`ps` muestra solo los que están en marcha; `-a` incluye los parados, que siguen existiendo con su capa de escritura. `-q` devuelve solo identificadores, útil para encadenar comandos. La columna `STATUS` distingue `Up` de `Exited (código)`; ese código es la pista más directa cuando algo falla al arrancar.

## Parar, reiniciar y borrar

```bash
docker stop web
docker kill web
docker start web
docker restart web
docker rm web
docker rm -f web
```

`stop` envía `SIGTERM`, espera diez segundos y después `SIGKILL`. Ese plazo se ajusta con `-t`. `kill` envía la señal directamente, sin cortesía. `start` vuelve a lanzar el proceso inicial de un contenedor parado, conservando su capa de escritura; `restart` equivale a parar y arrancar. `rm` solo borra contenedores parados, salvo que se fuerce con `-f`.

Una diferencia importante: `start` no admite cambios de configuración. No se puede añadir un puerto o una variable a un contenedor existente. Los contenedores son inmutables en sus características; para cambiar algo se crea otro con `run`.

## Sistemas de archivos: el contenedor no es la imagen

Lo que el proceso escribe va a una capa de escritura propia, montada sobre las capas de solo lectura de la imagen. Esa capa sobrevive al parado y al reinicio, pero desaparece con el contenedor. Dos contenedores de la misma imagen no comparten lo que cada uno escriba.

```bash
docker diff web
docker ps -s
```

`diff` muestra qué cambió en el sistema de archivos del contenedor; `ps -s` muestra el tamaño de su capa de escritura y el virtual de las capas compartidas. Para datos que deben sobrevivir hay volúmenes, que se tratan aparte.

## Ejecutar procesos dentro

```bash
docker exec -it web sh
docker exec web env
docker exec -u 0 web id
```

`exec` no crea un contenedor: lanza un proceso adicional en uno que ya está en marcha. Sirve para abrir un shell, comprobar variables, lanzar una consulta o inspeccionar ficheros. Si la imagen no tiene shell —cada vez más imágenes lo omiten por seguridad y tamaño— el comando falla; en ese caso se usan binarios concretos o se depura desde fuera.

## Publicar puertos

Un contenedor tiene su propia interfaz de red y su propia IP. El puerto que abre pertenece al contenedor, no al anfitrión. Para alcanzarlo desde fuera hay que publicarlo:

```bash
docker run -d -p 8080:80 nginx
docker run -d -p 127.0.0.1:8080:80 nginx
docker run -d -P nginx
```

El formato es `ip-anfitrión:puerto-anfitrión:puerto-contenedor`. Limitar la publicación a `127.0.0.1` evita exponer el servicio a la red local, algo imprescindible para bases de datos y paneles de administración. `-P` publica en puertos aleatorios los puertos declarados con `EXPOSE` en la imagen.

Dos contenedores pueden escuchar en su mismo puerto 80 sin conflicto, porque cada uno tiene su espacio de red. El conflicto aparece si ambos intentan publicarse en el mismo puerto del anfitrión. Y desde dentro de un contenedor, `localhost` es el propio contenedor, nunca el anfitrión ni otro contenedor.

## Borrar imágenes

```bash
docker rmi nginx
docker rmi nginx:stable
docker rmi <id>
docker image prune
```

`rmi` con un nombre o etiqueta elimina esa referencia; si la imagen tiene otra etiqueta o un contenedor en marcha la usa, el resultado es `Untagged` y el contenido sigue en disco. Con el identificador se elimina la imagen física, pero solo si no hay contenedores en marcha que la usen; los parados se pueden forzar con `-f`. En Podman, `rmi -f` sobre un identificador también elimina los contenedores que la usan, así que conviene leer dos veces antes de teclear.

Las imágenes colgantes (`<none>:<none>`) son versiones antiguas que perdieron su etiqueta al reconstruir. Se limpian con `docker image prune`, y `-a` elimina además las que no tienen contenedores asociados.

## Resumen del ciclo

```bash
docker pull nginx            # traer
docker run -d --name web ... # crear y arrancar
docker ps                    # comprobar
docker logs -f web           # seguir la salida
docker exec -it web sh       # entrar
docker stop web              # parar
docker rm web                # borrar
```

El orden importa: no se borra una imagen que un contenedor en marcha necesita, y no se borra un contenedor sin aceptar que su capa de escritura se pierde. Los datos que importan van a un volumen antes de que eso ocurra.
