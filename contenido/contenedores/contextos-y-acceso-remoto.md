# Contextos y acceso remoto

Docker separa cliente y motor, así que la CLI puede gobernar un demonio que no está en la misma máquina. Al principio eso se hacía con la variable `DOCKER_HOST`; hoy se hace con **contextos**, que guardan la dirección, las credenciales y el certificado de cada destino. Podman, sin demonio local, resuelve el mismo problema con conexiones SSH a un servicio remoto.

## El socket y DOCKER_HOST

Por defecto, la CLI habla con un socket Unix local:

```bash
export DOCKER_HOST=unix:///var/run/docker.sock
```

También admite TCP y SSH:

```bash
export DOCKER_HOST=ssh://usuario@servidor
export DOCKER_HOST=tcp://192.0.2.10:2375
```

La variante SSH arranca una sesión y se conecta al socket remoto; el servidor debe tener Docker y aceptar la clave. La variante TCP funciona, pero si el puerto no está protegido con TLS y autenticación, cualquiera con acceso a la red puede crear contenedores privilegiados en esa máquina. **Un demonio Docker expuesto sin TLS equivale a un servidor comprometido**; no se publica a internet.

`DOCKER_HOST` es útil para un comando puntual, pero no guarda configuración ni permite cambiar de destino sin exportar variables. Para eso están los contextos.

## Contextos de Docker

```bash
docker context ls
docker context use produccion
docker context create staging --docker host=ssh://usuario@staging
docker context inspect staging
docker context rm staging
```

`ls` marca con un asterisco el contexto activo. `use` cambia el destino de todos los comandos siguientes. `--context` permite usar otro solo para una orden:

```bash
docker --context produccion ps
```

Cada contexto es un entorno distinto: sus imágenes, contenedores, volúmenes y redes son independientes. Un `docker context use` no "mueve" nada; cambia de servidor. Por eso es fácil crear un contenedor en el entorno equivocado si no se mira el asterisco.

Docker Desktop añade su propio contexto (`desktop-linux`) y deja el `default` para el motor nativo si existe. En Linux con ambos instalados hay dos almacenes separados y dos contextos; los contenedores de uno no se ven desde el otro.

Los contextos se pueden exportar e importar para replicar la configuración entre equipos:

```bash
docker context export produccion
docker context import produccion produccion.dockercontext
```

El fichero puede contener credenciales y certificados. Se trata como un secreto y no se versiona.

## Contextos y buildx

Cada contexto de Docker es también un *builder* de `buildx` con driver `docker`. Si hay tres contextos, `docker buildx ls` muestra tres constructores. Eso permite construir en el motor remoto sin cambiar de contexto:

```bash
docker buildx build --builder remoto -t usuario/api:1.0 --push .
```

No se debe confundir `docker context use`, que cambia el motor, con `docker buildx use`, que cambia el constructor dentro del motor activo.

## Podman sin demonio

Podman no necesita un servicio para funcionar en local: la propia CLI crea los contenedores. Por eso en Linux no hay contextos por defecto ni hace falta configurarlos. El acceso remoto existe, pero es opcional y se implementa con un servicio que escucha en `podman.sock`, normalmente sobre SSH.

En macOS y Windows sí es obligatorio, porque los contenedores Linux necesitan una máquina. `podman machine` la crea y la administra:

```bash
podman machine init
podman machine start
podman machine list
podman machine ssh
podman machine stop
podman machine set --rootful
```

En Windows la máquina es una distribución WSL 2; en macOS y Linux, una VM con QEMU. `set --rootful` cambia entre modo root y rootless dentro de la máquina y requiere reiniciarla.

## Conexiones remotas de Podman

Una conexión remota se declara con `system connection add`, que crea a la vez un contexto:

```bash
podman system connection add produccion \
  --identity ~/.ssh/id_ed25519 \
  usuario@servidor:/run/user/1000/podman/podman.sock
podman system connection ls
podman context ls
```

Sin `--identity`, la conexión pide la contraseña en cada comando. Con una clave SSH configurada en el servidor, la autenticación es transparente. El comando `podman context create` existe por compatibilidad con la CLI de Docker, pero la gestión real se hace con `system connection`; crear o borrar uno crea o borra el otro.

El modificador `--remote` decide si el comando va al motor local o al contexto remoto:

```bash
podman --remote ps
podman --remote run -d nginx
```

En Linux, sin `--remote`, Podman sigue trabajando en local aunque haya un contexto configurado. Esa es la diferencia de comportamiento que más confunde al venir de Docker: el contexto no cambia el destino por sí solo.

## Elegir destino

| Necesidad | Docker | Podman |
|---|---|---|
| Motor local | Contexto `default` | Sin contexto |
| Cambiar de motor | `docker context use` | `podman context use` + `--remote` |
| Comando puntual | `--context` | `--remote` con contexto activo |
| Crear máquina | Docker Desktop la gestiona | `podman machine` |
| Autenticación remota | Contexto con TLS o SSH | `system connection` con clave SSH |

En ambos casos, la regla de seguridad es la misma: el acceso al motor permite crear contenedores con privilegios, así que se protege con TLS mutuo o SSH, se limita por red y no se comparte la credencial. Un contexto es una llave maestra, no un alias de conveniencia.
