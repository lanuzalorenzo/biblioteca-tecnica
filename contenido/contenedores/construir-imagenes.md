# Construir imágenes

Una imagen se describe en un fichero de texto, el `Dockerfile`, y se construye con `docker build`. Cada instrucción de ese fichero produce una capa o un cambio de configuración; el resultado es una imagen identificada por un hash. El mismo fichero, con el mismo contexto y las mismas entradas, produce la misma imagen, que es lo que hace reproducible un despliegue.

## El contexto de construcción

```bash
docker build -t miapp:1.0 .
```

El punto final no es decorativo: es el **contexto**, el directorio que el cliente comprime y envía al motor. El demonio no ve el resto del disco, así que todo lo que una instrucción `COPY` necesite debe estar dentro de ese árbol. El `Dockerfile` se busca en la raíz del contexto salvo que se indique otra ruta con `-f`.

Enviar un contexto enorme —un `node_modules`, un `.git`, binarios de compilación— ralentiza cada construcción y puede filtrar ficheros que no deben entrar en la imagen. `.dockerignore`, en la raíz del contexto, excluye rutas con la misma sintaxis que `.gitignore`. Se detalla en [compilar y probar con contenedores](compilar-y-probar-con-contenedores.md).

## La primera línea: de qué se parte

```dockerfile
FROM node:22-alpine
```

`FROM` fija la imagen base y abre cada etapa; es obligatoria en todas. La elección de la base decide tamaño, superficie de ataque y disponibilidad de herramientas:

- **Imagen oficial completa**: trae todo lo habitual, pesa más.
- **Variante `slim` o `alpine`**: menos paquetes y menos vulnerabilidades; Alpine usa musl en lugar de glibc, lo que puede romper binarios precompilados.
- **Distroless**: sin shell ni gestor de paquetes; muy pequeña, difícil de depurar dentro.
- **Imagen de una tecnología concreta**: por ejemplo, `mcr.microsoft.com/dotnet/aspnet` para ejecutar y `sdk` para compilar.

Conviene fijar una versión concreta y, en producción, un digest. `latest` cambia sin avisar y convierte una reconstrucción en una actualización silenciosa.

## Las instrucciones que importan

| Instrucción | Para qué |
|---|---|
| `WORKDIR` | Directorio de trabajo de las instrucciones siguientes |
| `COPY` | Copia ficheros del contexto a la imagen |
| `ADD` | Como `COPY`, pero admite URLs y desempaqueta tar; se evita salvo necesidad |
| `RUN` | Ejecuta un comando durante la construcción y guarda el resultado |
| `ENV` | Variable de entorno permanente en la imagen |
| `ARG` | Valor de construcción, disponible solo durante el build |
| `EXPOSE` | Documenta el puerto que la aplicación escucha |
| `USER` | Usuario con el que corre el proceso |
| `VOLUME` | Declara un punto de montaje persistente |
| `HEALTHCHECK` | Comando que decide si el contenedor está sano |
| `CMD` / `ENTRYPOINT` | Proceso inicial del contenedor |
| `LABEL` | Metadatos de la imagen |

`COPY` conserva rutas relativas al contexto. Las rutas absolutas y los `..` que salen del contexto no funcionan. `ADD` con una URL no verifica integridad y con un tar lo desempaqueta, dos comportamientos que sorprenden; para lo normal, `COPY` es predecible.

`RUN` en forma *shell* (`RUN apt-get update && apt-get install -y curl`) se ejecuta con `/bin/sh -c`; en forma *exec* (`RUN ["apt-get", "install", "-y", "curl"]`) no pasa por shell. Encadenar actualización, instalación y limpieza en una sola instrucción evita dejar en la capa anterior listas de paquetes y cachés que solo ocupan espacio.

## Variables: ARG y ENV

`ARG` existe durante la construcción y no queda en la imagen final; `ENV` queda en la configuración y la heredan los contenedores. Un `ARG` sin valor por defecto puede romper el build:

```dockerfile
ARG NODE_VERSION=22
FROM node:${NODE_VERSION}-alpine
```

```bash
docker build --build-arg NODE_VERSION=20 -t miapp .
```

Un `ARG` no toma el valor de una variable de entorno del anfitrión por el simple hecho de llamarse igual: hay que pasarlo con `--build-arg` o declararlo con valor por defecto. No se usan `ARG` ni `ENV` para secretos: ambos quedan en el historial o en la configuración de la imagen.

## El proceso inicial: CMD y ENTRYPOINT

Ambas instrucciones definen qué se ejecuta al arrancar el contenedor, y ambas admiten forma *shell* y forma *exec*:

```dockerfile
CMD ["node", "server.js"]          # exec: node es el PID 1
CMD node server.js                 # shell: /bin/sh -c "node server.js"
ENTRYPOINT ["node", "server.js"]
```

La forma *exec* es la recomendada. En la forma *shell*, el PID 1 es el shell, que no propaga bien las señales: un `SIGTERM` enviado por `docker stop` puede no llegar al proceso real y el contenedor termina por `SIGKILL` tras el plazo. Además, si la imagen no tiene shell, la forma *shell* no funciona.

La diferencia real entre ambas es quién puede redefinir el comando:

- `docker run miapp otro-comando` sustituye `CMD`.
- `docker run --entrypoint otro-comando miapp` sustituye `ENTRYPOINT`.

Por eso `ENTRYPOINT` se usa cuando el contenedor es una herramienta con un verbo fijo, y `CMD` cuando es razonable que quien lo lanza cambie el comando. Si se declaran los dos, `CMD` pasa a ser la lista de argumentos por defecto de `ENTRYPOINT`, y solo funciona si `ENTRYPOINT` está en forma *exec*.

## Puertos y salud

`EXPOSE` no abre nada: documenta la intención y permite que otras herramientas lean el puerto. La publicación real se hace con `-p` al ejecutar o con `ports` en Compose. Aun así, declararlo es útil y no cuesta nada.

```dockerfile
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD wget -qO- http://localhost:3000/salud || exit 1
```

`HEALTHCHECK` no reinicia el contenedor por sí solo. Marca el estado como `healthy` o `unhealthy`, y ese estado es el que puede usar Compose con `depends_on` o un orquestador para decidir si envía tráfico.

## Usuario y permisos

Por defecto, el proceso corre como root dentro del contenedor. Si el motor también corre como root, ese root es el del anfitrión. Crear un usuario sin privilegios y usarlo es una de las mejoras más baratas:

```dockerfile
RUN addgroup -S app && adduser -S app -G app
USER app
```

El usuario debe existir en la imagen y tener permiso sobre los directorios que la aplicación escribe. En imágenes basadas en Debian o Ubuntu se usa `useradd`; en Alpine, `adduser`. Los ficheros copiados con `COPY --chown=app:app` evitan un `chown` posterior que duplicaría capas.

## Un Dockerfile completo

```dockerfile
FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --omit=dev

COPY . .

ENV NODE_ENV=production
EXPOSE 3000
USER node

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget -qO- http://localhost:3000/salud || exit 1

CMD ["node", "server.js"]
```

El orden no es casual: primero el manifiesto de dependencias y su instalación, después el código. Así, un cambio en el código no invalida la capa de `npm ci`, que es la lenta. Esa regla se desarrolla en [compilar y probar con contenedores](compilar-y-probar-con-contenedores.md).

## Construir y comprobar

```bash
docker build -t miapp:1.0 .
docker build --no-cache -t miapp:1.0 .
docker build --progress=plain -t miapp:1.0 .
docker run --rm -p 3000:3000 miapp:1.0
```

`--no-cache` reconstruye todas las capas; `--progress=plain` muestra la salida completa, útil cuando una instalación falla y el modo compacto la oculta. El resultado se puede etiquetar, publicar y ejecutar como cualquier otra imagen.

La construcción no es magia: el motor crea un contenedor temporal a partir de la base, ejecuta cada instrucción y guarda el sistema de archivos resultante. Por eso una instrucción que falla deja las anteriores en caché y por eso el orden de las instrucciones decide cuánto tarda la siguiente construcción.
