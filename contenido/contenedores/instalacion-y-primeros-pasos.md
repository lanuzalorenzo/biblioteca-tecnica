# Instalación y primeros pasos

Antes de instalar conviene saber qué pieza se necesita. En Linux, el motor es **Docker Engine**, que se instala desde los repositorios de la distribución o desde el repositorio oficial de Docker y se ejecuta como servicio de systemd. En macOS y Windows no existe ese motor nativo: se instala **Docker Desktop**, que crea una máquina virtual Linux —en Windows con WSL 2 como opción recomendada— y expone su demonio a la CLI. **Podman** se instala como un único binario y, en macOS y Windows, necesita una máquina (`podman machine`) porque los contenedores siguen siendo Linux.

Los requisitos reales son modestos: un sistema de 64 bits con virtualización activada si hace falta la máquina auxiliar, kernel reciente con namespaces y cgroups, y permisos para administrar el servicio. En Linux conviene comprobar que el almacenamiento y la red del motor funcionan con la configuración del sistema; en equipos antiguos con cgroups v1 o con un cortafuegos propio, los primeros fallos suelen venir de ahí.

## Comprobar que responde

```bash
docker --version
docker version
docker info
```

`--version` muestra la versión del cliente; `version` separa cliente y servidor y confirma que se hablan; `info` resume el estado del motor: almacenamiento, cgroups, red, número de contenedores. Si `version` falla en la parte del servidor, el problema no es la aplicación: el demonio no está arrancado o el usuario no tiene acceso al socket.

En Podman el equivalente es:

```bash
podman --version
podman info
```

La primera ejecución de una imagen pequeña confirma el circuito completo:

```bash
docker run --rm hello-world
```

Si aparece el mensaje de bienvenida, el motor descarga, crea, ejecuta y elimina un contenedor. Podman descarga una imagen distinta para ese nombre porque aplica su propio fichero de alias de nombres cortos; el resto del flujo es idéntico.

## Permisos del socket

En Linux, el demonio escucha en `/var/run/docker.sock`, que pertenece a `root` y al grupo `docker`. Un usuario normal recibe un error de permiso denegado hasta que se le añade al grupo:

```bash
sudo usermod -aG docker "$USER"
```

El cambio se aplica al cerrar y abrir la sesión. Pertenecer a `docker` equivale a tener root de facto, porque permite montar el sistema de archivos del anfitrión dentro de un contenedor. En equipos compartidos, la alternativa es el modo **rootless**, que ejecuta el demonio y los contenedores con el usuario, o usar Podman, que funciona así por defecto. En Windows, el acceso al named pipe del motor lo controla el grupo `docker-users`.

## Los objetos que se administran

| Objeto | Qué representa | Se crea con |
|---|---|---|
| Imagen | Plantilla de solo lectura | `build`, `pull`, `commit` |
| Contenedor | Imagen en ejecución con capa propia | `run`, `create`, Compose |
| Volumen | Almacenamiento persistente gestionado por el motor | `volume create` |
| Red | Segmento virtual con DNS opcional | `network create` |
| Contexto | Conexión a un demonio local o remoto | `context create` |

El resto de la CLI son operaciones sobre esos cinco objetos: listar, inspeccionar, etiquetar, conectar, borrar.

## Un primer servicio

```bash
docker run -d --name web -p 8080:80 nginx
docker ps
curl -I http://localhost:8080
```

`-d` deja el contenedor en segundo plano, `--name` le da un nombre legible y `-p 8080:80` publica el puerto 80 del contenedor en el 8080 del anfitrión. Sin ese mapeo, el servicio existe pero no es alcanzable desde fuera. `docker ps` muestra el identificador, la imagen, el comando, el estado y los puertos.

Para entrar, mirar y limpiar:

```bash
docker exec -it web sh
docker logs --tail 50 web
docker stop web
docker rm web
```

`exec` lanza un proceso nuevo dentro del contenedor en marcha; `logs` lee lo que el proceso escribió por la salida estándar y de error; `stop` envía una señal de terminación y espera; `rm` borra el contenedor y su capa de escritura.

## Dónde está cada cosa

En Linux, las imágenes, los volúmenes y la configuración viven bajo `/var/lib/docker`. No conviene editar esos ficheros a mano: el motor mantiene su propio índice y cualquier cambio externo lo deja inconsistente. La vía es siempre la CLI o la API. En Docker Desktop y en Podman con máquina, ese directorio está dentro de la máquina virtual, no en el sistema de archivos del usuario.

El cliente guarda sus credenciales de registro y su configuración en el directorio del usuario (`~/.docker/config.json` en Docker; Podman usa el directorio de configuración de contenedores). Ese fichero sí es del usuario, pero también puede contener credenciales: no se versiona ni se comparte.

## Podman en macOS y Windows

```bash
podman machine init
podman machine start
podman machine ssh
```

La máquina se crea con los valores por defecto y se administra con `machine`. En Windows se apoya en WSL 2; en macOS y Linux, en QEMU. `podman machine set --rootful` cambia el modo de la máquina, y `podman machine stop` la apaga. Sin ella, la CLI no tiene dónde ejecutar contenedores Linux.

Con el motor en marcha, el resto del trabajo es el mismo que en Docker: descargar, ejecutar, exponer, persistir y componer. Las diferencias aparecen en los permisos, en la red rootless y en la ausencia de demonio, y se tratan en las notas siguientes.
