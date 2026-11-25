# Compose

Compose describe una aplicación en un fichero YAML y la levanta con un comando. Cada servicio declara qué imagen usa, qué puertos publica, qué variables recibe y qué volúmenes monta; Compose crea la red, los contenedores y el orden mínimo entre ellos. Su valor no está en hacer cosas que Docker no pueda hacer, sino en dejar escrita la configuración y repetirla igual.

## El fichero

```yaml
services:
  api:
    image: miempresa/api:1.0
    ports:
      - "8080:3000"
    environment:
      LOG_LEVEL: info
      DATABASE_URL: postgres://app@db:5432/app
    depends_on:
      - db

  db:
    image: postgres:16
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?define POSTGRES_PASSWORD}
    volumes:
      - datos:/var/lib/postgresql/data

volumes:
  datos:
```

El nombre por defecto es `compose.yaml` —también se acepta `docker-compose.yml`— y se puede cambiar con `-f`. **No se usan tabulaciones**: YAML exige espacios y una indentación coherente. El campo `version` que aparece en ejemplos antiguos está obsoleto y se ignora; si se incluye, Compose avisa.

## Las claves que se usan a diario

| Clave | Qué hace |
|---|---|
| `image` | Imagen del servicio |
| `build` | Construye la imagen desde un contexto y un Dockerfile |
| `ports` | Publica puertos en el anfitrión |
| `expose` | Declara puertos internos sin publicarlos |
| `environment` | Variables de entorno |
| `env_file` | Fichero con variables |
| `volumes` | Volúmenes y *bind mounts* |
| `depends_on` | Orden de arranque y, con condición, de salud |
| `command` | Sustituye el comando de la imagen |
| `working_dir` | Directorio de trabajo |
| `restart` | Política de reinicio |
| `healthcheck` | Comprobación de salud |
| `profiles` | Agrupa servicios opcionales |
| `networks` | Redes a las que se conecta |

`build` admite contexto y fichero:

```yaml
services:
  api:
    build:
      context: .
      dockerfile: docker/Dockerfile
      args:
        NODE_VERSION: "22"
    image: miempresa/api:dev
```

Si se declaran `build` e `image`, Compose construye y etiqueta con ese nombre. Sin `image`, genera un nombre derivado del proyecto y del servicio, poco útil para publicar.

## Órdenes

```bash
docker compose up
docker compose up -d
docker compose up --build
docker compose ps
docker compose logs -f api
docker compose exec api sh
docker compose down
docker compose down -v
```

`up` construye lo que falte, crea la red y arranca. Sin `-d` queda en primer plano y muestra la salida mezclada de todos los servicios; con `-d` devuelve el control. `--build` fuerza la reconstrucción. `ps`, `logs` y `exec` funcionan por nombre de servicio, no por nombre de contenedor. `down` para y elimina contenedores y red, pero conserva los volúmenes nombrados; `-v` los borra también y es el comando que hay que evitar en un entorno con datos.

`docker compose config` valida el fichero y muestra el resultado final, incluida la combinación de varios ficheros. Es la primera comprobación cuando algo no arranca como se espera.

## Configuración fuera de la imagen

Un fichero de configuración dentro de la imagen obliga a tener una imagen por entorno. La alternativa es inyectarlo:

- **Variables de entorno** para valores simples; es la forma preferida.
- **`env_file`** para un conjunto de variables, con una línea `CLAVE=valor` por variable.
- **Volumen o *bind mount*** para ficheros que la aplicación exige en una ruta fija, como un `web.config` o un certificado.
- **Secretos** de Compose u orquestador para credenciales, montados como ficheros en lugar de variables.

La precedencia tiene dos niveles. Para interpolar `${VARIABLE}` en el fichero, manda el entorno del shell, después `.env` y por último el valor por defecto. Para lo que recibe el contenedor, un valor escrito en `environment` gana sobre `env_file`, y este sobre el `ENV` de la imagen. `.env` se lee automáticamente del directorio del proyecto y no debe versionarse si contiene secretos.

```yaml
environment:
  PORT: "${PORT:-3000}"
```

Ese `:-` da un valor por defecto cuando la variable no existe o está vacía. `:?` aborta con un mensaje si falta, lo que evita arrancar con una credencial vacía.

## Entornos

La forma limpia de separar entornos es un fichero base con la definición y otro por entorno con lo que cambia:

```yaml
# compose.yaml
services:
  api:
    image: miempresa/api:1.0
```

```yaml
# compose.dev.yaml
services:
  api:
    ports:
      - "8080:3000"
    environment:
      LOG_LEVEL: debug
    volumes:
      - ./src:/app
```

```bash
docker compose -f compose.yaml -f compose.dev.yaml up
```

Compose combina los ficheros en memoria: las listas se suman, los mapas se fusionan y los valores escalares del último fichero ganan. No se genera un fichero combinado; `config` lo muestra. Si no se pasa `-f`, se usan `compose.yaml` y, si existe, `compose.override.yaml`, que es el nombre convencional para los ajustes locales de desarrollo.

Mantener la imagen y los servicios solo en el fichero base evita cambiar el nombre de la imagen en cinco sitios cuando se publica una versión.

## Perfiles

Los perfiles arrancan un subconjunto de servicios sin crear ficheros distintos:

```yaml
services:
  api:
    image: miempresa/api:1.0

  admin:
    image: adminer
    profiles: ["debug"]

  worker:
    image: miempresa/worker:1.0
    profiles: ["jobs"]
```

```bash
docker compose --profile debug up
docker compose --profile debug --profile jobs up
```

Un servicio sin perfil se arranca siempre; uno con perfil solo se arranca si ese perfil está activo. Es útil para herramientas de administración, tareas puntuales y depuración, sin obligar a mantener un fichero por combinación.

## Construir con Compose

```bash
docker compose build
docker compose build --no-cache api
docker compose pull
```

Compose construye todos los servicios con `build` y reutiliza la caché de capas como `docker build`. En un proyecto con varias imágenes, un solo comando evita recordar el orden y los contextos. `pull` actualiza las imágenes que no se construyen; conviene ejecutarlo antes de un `up` en un entorno que depende de etiquetas.

## Límites

Compose no es un orquestador. No reparte contenedores entre máquinas, no reinicia un servicio caído en otro nodo ni hace balanceo real. Para eso están Kubernetes, Swarm u otros sistemas. Compose es una herramienta de desarrollo y de despliegue pequeño en un único host; usarla para lo que no es ahorra problemas.
