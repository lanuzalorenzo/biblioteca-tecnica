# Compilar y probar con contenedores

El contenedor no solo ejecuta aplicaciones: también puede ser la cadena de herramientas. Un proyecto se compila con la imagen que trae el SDK, sin instalar ese SDK en el equipo, y el resultado se extrae a un directorio del anfitrión. Con una construcción multi-etapa, el mismo fichero compila, prueba y genera una imagen final que solo lleva el runtime.

## Compilar sin instalar el SDK

La primera idea es una imagen con el SDK y el código copiado:

```dockerfile
FROM mcr.microsoft.com/dotnet/sdk:10.0
WORKDIR /src
COPY . .
ENTRYPOINT ["dotnet", "publish", "-o", "out"]
```

Funciona, pero los binarios quedan dentro del contenedor y no hay forma cómoda de sacarlos. El arreglo es montar un directorio del anfitrión sobre la salida:

```bash
docker run --rm \
  -v "$PWD:/src" \
  -v "$PWD/out:/src/out" \
  -w /src \
  mcr.microsoft.com/dotnet/sdk:10.0 \
  dotnet publish -o out
```

Ahora el código fuente y el resultado están en el anfitrión. Ni siquiera hace falta una imagen propia: se usa la del SDK y se redefine el comando al ejecutar. Si el proyecto tiene dependencias que deben descargarse en cada compilación, la caché de NuGet se puede montar aparte para no repetir la descarga.

En Node el equivalente es una imagen `node` con `npm ci`; en Go, `golang` con `go build`; en Rust, `rust` con `cargo build`. La imagen aporta el compilador y las bibliotecas del sistema, y el *bind mount* aporta el código.

## Multi-stage build

Una construcción multi-etapa usa varias instrucciones `FROM`. Cada una abre una etapa con su propia imagen base, y la última es la que se conserva salvo que se indique otra:

```dockerfile
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src
COPY . .
RUN dotnet publish -o /app

FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS final
WORKDIR /app
COPY --from=build /app .
EXPOSE 8080
USER app
ENTRYPOINT ["dotnet", "MiApi.dll"]
```

La primera etapa compila con el SDK; la segunda parte solo del runtime y copia el resultado con `COPY --from=build`. El SDK, los fuentes y las herramientas de compilación no llegan a la imagen final. El tamaño baja de gigabytes a decenas o cientos de megabytes, y la superficie de ataque se reduce.

Las etapas se pueden nombrar y encadenar:

```dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS base
WORKDIR /app
EXPOSE 8080

FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src
COPY . .
RUN dotnet publish -o /app

FROM base AS final
COPY --from=build /app .
ENTRYPOINT ["dotnet", "MiApi.dll"]
```

`--target` construye solo hasta una etapa intermedia:

```bash
docker build --target build -t mi-api-build .
```

Eso permite tener una imagen de compilación reutilizable, con SDK y dependencias, sin construir la final. Es la técnica que usan los IDE para depurar dentro de un contenedor: construyen la etapa con herramientas, montan el código y conectan el depurador.

## Pruebas dentro de la construcción

Una etapa adicional ejecuta las pruebas y hace fallar el build si no pasan:

```dockerfile
FROM node:22-alpine AS test
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm test

FROM node:22-alpine AS runtime
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
COPY --from=test /app/src ./src
CMD ["node", "src/server.js"]
```

`docker build` se detiene en la etapa `test` si el comando devuelve un código distinto de cero. En una tubería de integración continua, eso convierte la construcción en la puerta de calidad: no se publica una imagen si las pruebas fallan. Para ejecutar solo las pruebas sin producir la imagen final, se usa `--target test`.

En Rust, `cargo test`; en Go, `go test ./...`; en .NET, `dotnet test`. El patrón es siempre el mismo: una etapa con herramientas y pruebas, otra con el artefacto y el runtime mínimo.

## Ordenar las capas para la caché

Cada instrucción genera una capa y se guarda en caché. La caché se invalida cuando cambia la propia instrucción o cualquier anterior. Por eso las instrucciones se ordenan de lo más estable a lo más volátil:

```dockerfile
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm test
```

Si se copiara todo el código antes de `npm ci`, cualquier cambio en un fichero invalidaría la instalación de dependencias. Separando el manifiesto, un cambio de código solo rehace las capas posteriores. La misma idea se aplica a `.csproj` con `dotnet restore`, a `go.mod` con `go mod download` y a `Cargo.toml`.

Para dependencias que no cambian entre construcciones, BuildKit permite cachés persistentes:

```dockerfile
RUN --mount=type=cache,target=/root/.npm npm ci
```

La caché no forma parte de la imagen; se reutiliza entre construcciones. `--no-cache` desactiva la caché de capas cuando se sospecha que una capa antigua oculta un problema.

## El contexto y .dockerignore

El contexto es el directorio que se envía al motor. Si incluye `node_modules`, `.git` o binarios, cada construcción transfiere y copia datos que no hacen falta. `.dockerignore` los excluye:

```gitignore
.git
node_modules
bin
obj
out
*.log
.env
```

Las reglas se leen en orden y `!` recupera una excepción:

```gitignore
*.md
!README.md
```

El orden importa: la última regla que afecta a un fichero decide. Para incluir solo una parte del contexto se empieza excluyendo todo y se abre lo necesario:

```gitignore
*
!Dockerfile
!src
!package.json
!package-lock.json
```

El `Dockerfile` y el propio `.dockerignore` se envían siempre al contexto de construcción, aunque el `.dockerignore` los excluya; lo que no se puede es copiarlos a la imagen. Las rutas de `COPY` son relativas a la raíz del contexto, no a la ubicación del Dockerfile, y nunca pueden salir con `..`.

Un contexto más ancho que el Dockerfile permite compartir código entre proyectos:

```
/src
  compose.yaml
  common/
  api/
    Dockerfile
  worker/
    Dockerfile
```

Con `context: .` y `dockerfile: api/Dockerfile`, el Dockerfile copia `common` y `api` desde la raíz. Es habitual en soluciones .NET con varios proyectos, en monorepos de Node y en proyectos con cabeceras compartidas.

## Construir dentro de un contenedor

Un servidor de integración continua que corre en un contenedor necesita crear imágenes. Hay dos formas:

- **Docker-in-Docker**: un contenedor privilegiado ejecuta su propio demonio. Es potente y problemático: requiere `--privileged`, mezcla sistemas de archivos y puede corromper datos.
- **Montar el socket**: el contenedor recibe `/var/run/docker.sock` y usa el demonio del anfitrión.

```bash
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock docker:cli ps
```

La segunda opción es la habitual en CI y evita el demonio anidado, pero concede al contenedor el control total del motor. Solo se monta en herramientas de confianza y nunca en un contenedor que ejecute código de terceros sin aislar. La alternativa moderna es un builder sin privilegios —BuildKit en modo rootless, Kaniko, Buildah— que construye imágenes sin acceso al demonio.

## Del código a la imagen

El flujo completo queda así:

```bash
docker build --target test -t mi-api:test .
docker build -t mi-api:1.0 .
docker run --rm -p 8080:8080 mi-api:1.0
```

La primera orden valida; la segunda produce la imagen final; la tercera la ejecuta. En una tubería se añade `docker push` y el despliegue consume la etiqueta o el digest. Lo importante es que el mismo fichero que compila y prueba es el que genera el artefacto: no hay un entorno de CI distinto del de producción.
