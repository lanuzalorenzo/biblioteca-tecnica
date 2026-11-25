# Compose multicontenedor

Con un solo contenedor, Compose ahorra tecleo. Con varios, resuelve el problema que hace inviable el enfoque manual: las direcciones IP cambian en cada arranque y no se pueden escribir en un fichero de configuración. Compose crea una red propia, un DNS interno y un nombre por servicio, de modo que una API llama a `db` y no a una IP que ya no existe.

## Nombres y red

Cada proyecto de Compose crea una red con el nombre del directorio —o el que se indique con `-p`— y conecta a ella todos sus servicios. En esa red, el nombre del servicio resuelve a la IP del contenedor:

```yaml
services:
  api:
    image: miempresa/api:1.0
    environment:
      DATABASE_URL: postgres://app@db:5432/app
  db:
    image: postgres:16
```

Desde `api`, `db` es un nombre válido; desde el anfitrión, no. El DNS de Compose es interno y no se publica. Si se necesita un alias adicional, se declara con `networks.aliases`.

El nombre del contenedor sigue el patrón `proyecto-servicio-1`. Ese nombre es cómodo para `docker logs`, pero no se debe usar como dirección: al escalar o recrear cambia el número. La dirección estable es el nombre del servicio.

## Dependencias y salud

`depends_on` garantiza el orden de arranque, no que el servicio esté listo:

```yaml
services:
  api:
    depends_on:
      db:
        condition: service_healthy
  db:
    image: postgres:16
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 5s
      timeout: 3s
      retries: 10
```

Sin la condición, Compose arranca `api` cuando el contenedor de `db` existe, aunque la base todavía esté inicializando. Con `service_healthy`, espera a que el healthcheck pase. Esa espera no sustituye a la tolerancia a fallos de la aplicación: un servicio puede caerse después, y la aplicación debe reintentar.

`depends_on` tampoco crea dependencias en el apagado ni reinicia el servicio dependiente si el otro se cae. Para eso hace falta un orquestador o lógica en la aplicación.

## Escalar

```bash
docker compose up -d --scale worker=4
```

Levanta cuatro contenedores del servicio `worker`. Dos restricciones aparecen de inmediato:

- Un puerto fijo del anfitrión no se puede publicar cuatro veces. Hay que quitar `ports` o dejar solo el puerto del contenedor para que Docker asigne uno aleatorio.
- `container_name` impide escalar, porque obliga a un nombre único. Se elimina y se usan los nombres generados.

Los contenedores escalados comparten el nombre del servicio en el DNS y Compose devuelve todas sus IP en orden variable. **No hay balanceo real**: no hay comprobación de carga, ni sesiones pegajosas, ni reparto round-robin garantizado. Cada cliente elige una IP según su resolvedor. Para balanceo de verdad hace falta un proxy delante —Traefik, nginx, HAProxy— o un orquestador.

## Sesiones interactivas

Compose está pensado para mostrar la salida de varios contenedores en una consola, así que no se puede abrir una sesión interactiva con `up`. Para un servicio que lee de la entrada estándar:

```yaml
services:
  consola:
    image: miimagen/consola
    stdin_open: true
    tty: true
```

```bash
docker compose up -d
docker attach proyecto-consola-1
```

`stdin_open` y `tty` son equivalentes a `-i` y `-t` en `docker run`. `attach` enlaza la consola al contenedor; para salir sin pararlo se usa la secuencia de escape (`Ctrl-P`, `Ctrl-Q`). Para un shell de diagnóstico, `docker compose exec servicio sh` es más simple y no requiere esas opciones.

## Un caso completo

Una API necesita una base de datos, una caché y una herramienta de administración. El fichero:

```yaml
services:
  db:
    image: mcr.microsoft.com/mssql/server:2022-latest
    environment:
      ACCEPT_EULA: "Y"
      MSSQL_SA_PASSWORD: "${MSSQL_SA_PASSWORD:?define MSSQL_SA_PASSWORD}"
    ports:
      - "127.0.0.1:1433:1433"
    volumes:
      - datos-db:/var/opt/mssql
    healthcheck:
      test:
        - CMD-SHELL
        - /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "$$MSSQL_SA_PASSWORD" -C -Q "SELECT 1" || exit 1
      interval: 10s
      timeout: 5s
      retries: 10

  cache:
    image: redis:7-alpine
    ports:
      - "127.0.0.1:6379:6379"

  admin:
    image: adminer:latest
    ports:
      - "127.0.0.1:8080:8080"
    depends_on:
      db:
        condition: service_healthy

volumes:
  datos-db:
```

Cada decisión responde a un problema:

- `depends_on` con `service_healthy` evita que la interfaz arranque antes de que la base acepte consultas.
- El volumen `datos-db` conserva la base al recrear contenedores.
- Los puertos se publican en `127.0.0.1`, no en todas las interfaces: el servicio queda en el equipo y no en la red local.
- La contraseña se toma del entorno y el healthcheck la referencia con `$$`, que Compose convierte en `$` para que la expanda el shell del contenedor.

`adminer:latest` no es una buena elección para producción; se usa aquí porque es una herramienta de desarrollo. En un despliegue real se fija una versión.

## Comprobar que funciona

```bash
docker compose up -d
docker compose ps
docker compose logs -f db
curl -I http://localhost:8080
```

`ps` debe mostrar `db` como `healthy` y el resto en marcha. Cuando la base tarda, `logs` explica si está inicializando o si ha rechazado la contraseña por no cumplir la política. La interfaz responde con un `200` o un `302` hacia el formulario de acceso.

Para comprobar que el volumen hace su trabajo, se cargan las variables del fichero `.env` en el shell —Compose ya las lee, pero el comando `exec` las expande el anfitrión— y se ejecutan las consultas:

```bash
set -a; . ./.env; set +a
docker compose exec db /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P "$MSSQL_SA_PASSWORD" -C \
  -Q "CREATE DATABASE pedidos;"
docker compose down
docker compose up -d
docker compose exec db /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P "$MSSQL_SA_PASSWORD" -C \
  -Q "SELECT name FROM sys.databases WHERE name = 'pedidos';"
```

`down` elimina los contenedores pero no el volumen, así que la base sigue ahí. `down -v` borra también el volumen y es el comando para empezar de cero, no para reiniciar.

## El patrón que se repite

Un servicio por pieza, una dependencia explícita, un volumen para lo que debe sobrevivir y un healthcheck para lo que tarda en arrancar. Cambiar SQL Server por PostgreSQL o Redis por otro almacén no cambia la forma: cambia la imagen, el comando de salud y la cadena de conexión. Lo que no se hace es publicar la base a internet ni guardar credenciales en el fichero que se versiona.

Podman puede ejecutar ficheros de Compose con `podman compose`, que delega en un proveedor externo, o interpretar manifiestos de Kubernetes con `podman kube play`. La sintaxis de Compose no es un estándar de Podman, así que conviene probarla antes de dar por hecho que funciona igual.
