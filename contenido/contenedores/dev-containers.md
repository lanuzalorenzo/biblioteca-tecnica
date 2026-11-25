# Dev containers

Un *dev container* es un contenedor contra el que el editor se conecta. El código sigue en el anfitrión, montado con un *bind mount*, pero el intérprete, las dependencias, el SDK y las herramientas viven dentro del contenedor. El resultado es un entorno de desarrollo reproducible —el mismo en cualquier equipo— sin renunciar al editor de siempre.

## Cómo funciona

Visual Studio Code, con la extensión **Dev Containers**, lee un fichero `devcontainer.json`, construye o descarga la imagen, arranca el contenedor, monta el espacio de trabajo y ejecuta un servidor del editor dentro. Las extensiones se instalan en ese servidor, no en el anfitrión. La terminal integrada es una sesión dentro del contenedor.

```json
{
  "name": "api",
  "image": "mcr.microsoft.com/devcontainers/javascript-node:22",
  "forwardPorts": [3000],
  "postCreateCommand": "npm ci",
  "customizations": {
    "vscode": {
      "extensions": ["dbaeumer.vscode-eslint", "esbenp.prettier-vscode"]
    }
  }
}
```

- `image` parte de una imagen preparada; `build` usa un Dockerfile propio.
- `features` añade herramientas —git, Docker CLI, lenguajes— sobre la base.
- `forwardPorts` publica puertos para el navegador del anfitrión.
- `mounts` añade volúmenes, por ejemplo para cachés de paquetes.
- `postCreateCommand` se ejecuta una vez, al crear el contenedor.
- `postStartCommand` se ejecuta en cada arranque.

El fichero vive en `.devcontainer/devcontainer.json` dentro del repositorio, de modo que viaja con el proyecto.

## Con Compose

Si el proyecto ya tiene un fichero de Compose, el contenedor de desarrollo puede ser uno de sus servicios:

```json
{
  "name": "api + db",
  "dockerComposeFile": "../compose.yaml",
  "service": "api",
  "workspaceFolder": "/app",
  "shutdownAction": "stopCompose"
}
```

Así se levanta la base de datos y la API juntas, con la red y el DNS que ya define Compose. El editor se conecta al servicio `api`; los demás siguen funcionando en segundo plano. Es la forma de reproducir un entorno con dependencias sin duplicar la configuración.

## Ciclo de vida

Al abrir el proyecto, el editor ofrece «Reopen in Container». La primera vez construye la imagen, instala las extensiones y ejecuta los comandos de creación; las siguientes reutiliza el contenedor si no cambió la definición. Cambiar `devcontainer.json`, el Dockerfile o las dependencias del sistema exige **Rebuild Container**, que recrea el contenedor y conserva el código del anfitrión.

Los cambios en el código se ven al instante porque el directorio está montado. Los cambios en herramientas o variables de entorno requieren reconstruir. Esa separación —código montado, entorno inmutable— es la misma que se usa en producción.

## Límites y cuidados

- **Rendimiento**: en macOS y Windows, montar muchos ficheros pequeños desde el anfitrión es más lento que tenerlos dentro de la máquina virtual. Los proyectos grandes lo notan.
- **Permisos**: el usuario del contenedor debe poder escribir en el espacio de trabajo. Las imágenes de desarrollo suelen crear un usuario con el UID del anfitrión; si no, aparecen ficheros propiedad de root.
- **Secretos**: las variables del contenedor de desarrollo no deben contener credenciales reales en el fichero versionado. Se usan variables del entorno o un fichero local ignorado.
- **Producción**: un dev container es un entorno de desarrollo, no una imagen de despliegue. Suele incluir shell, herramientas y permisos que no deben llegar a producción.
- **Dependencia del motor**: sin Docker o Podman en marcha, el editor no puede abrir el contenedor. El código sigue accesible, pero el entorno no.

La idea no es exclusiva de Visual Studio Code: JetBrains, DevPod y otras herramientas permiten desarrollar contra un contenedor. El fichero de definición y el principio son los mismos: describir el entorno una vez y compartirlo.
