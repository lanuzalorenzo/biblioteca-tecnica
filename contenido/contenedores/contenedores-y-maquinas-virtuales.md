# Contenedores y máquinas virtuales

Un contenedor es un proceso normal al que el kernel le ha dado una vista privada del sistema: su propio árbol de procesos, sus interfaces de red, sus puntos de montaje y sus límites de CPU y memoria. No hay un sistema operativo invitado ni un hipervisor de por medio; el proceso se ejecuta de forma nativa sobre el kernel del anfitrión, encerrado en un espacio de nombres. De ahí que arranque en milisegundos y ocupe lo que ocupe la aplicación, no lo que ocupa un ordenador completo.

## La comparación con una máquina virtual

Una máquina virtual simula hardware y arranca un kernel propio. Eso le da un aislamiento fuerte —está pensada para que un fallo dentro no alcance al anfitrión— y le permite ejecutar otro sistema operativo, a cambio de segundos de arranque, gigabytes de disco y una capa de virtualización que hay que administrar. Un contenedor comparte el kernel y solo aísla procesos; es más ligero y denso, pero también más frágil como frontera de seguridad.

| | Máquina virtual | Contenedor |
|---|---|---|
| Qué ejecuta | Un sistema operativo completo con su kernel | Un proceso y sus dependencias |
| Arranque | Decenas de segundos | Menos de un segundo |
| Tamaño | Gigabytes | Decenas o cientos de megabytes |
| Densidad | Pocas por máquina | Decenas por máquina |
| Aislamiento | Fuerte, por hardware emulado | De proceso, sobre el mismo kernel |
| Sistema operativo | Cualquiera compatible con el hipervisor | El del kernel del anfitrión |

Esa última fila explica por qué Linux ejecuta contenedores Linux y Windows ejecuta contenedores Windows. En macOS y Windows, Docker Desktop y Podman crean una máquina virtual Linux ligera para poder ejecutar contenedores Linux; el usuario no la administra, pero está ahí y condiciona cosas como la IP interna o el rendimiento del sistema de archivos.

## Qué problema resuelve el empaquetado

Publicar una aplicación suele dejar fuera piezas que el servidor de destino debe tener: el runtime, una versión concreta de una biblioteca compartida, un servidor web, variables de entorno. Cuando dos aplicaciones en el mismo host necesitan versiones distintas de la misma dependencia, actualizar una puede romper la otra. La imagen corta esa dependencia: lleva el sistema de archivos base, las bibliotecas y el código, y no espera nada del host salvo un motor de contenedores.

La consecuencia es que el artefacto que se prueba es el que se despliega. Lo que cambia entre entornos es la configuración —direcciones, credenciales, niveles de registro—, no el contenido de la imagen. Ese es el motivo de que la configuración se saque fuera y se inyecte al arrancar.

## Imagen y contenedor

La imagen es la plantilla de solo lectura: un sistema de archivos por capas más unos metadatos de configuración (comando inicial, variables, puertos declarados, usuario). El contenedor es una imagen en ejecución, con una capa de escritura propia encima. La relación es la de una clase y un objeto: de una imagen se crean tantos contenedores como haga falta, y cada uno tiene su ciclo de vida.

Una imagen no se modifica. Cambiar una aplicación significa construir otra imagen y crear contenedores nuevos; el contenedor existente conserva la que tenía. Esa inmutabilidad es lo que permite reproducir un despliegue y volver atrás: la versión anterior sigue siendo un identificador que se puede volver a ejecutar.

## Las piezas de Docker

Docker es una arquitectura cliente-servidor:

- **CLI** (`docker`): interpreta el comando y habla con el motor.
- **Demonio** (`dockerd`): recibe la petición, construye imágenes, crea redes y volúmenes.
- **containerd**: gestiona el ciclo de vida de los contenedores.
- **runc**: crea el proceso aislado según la especificación OCI.
- **BuildKit**: construye imágenes; es el motor que hay detrás de `docker build`.

El cliente y el demonio se comunican por un socket Unix (`/var/run/docker.sock`) o por una tubería con nombre en Windows. Pueden estar en máquinas distintas, que es la base de los contextos y del acceso remoto. También implican un riesgo: quien puede escribir en ese socket puede crear un contenedor privilegiado y montar el sistema de archivos del anfitrión, así que el socket equivale a root.

**Docker Engine** es el motor para Linux, sin interfaz gráfica. **Docker Desktop** es un producto que empaqueta el motor con una máquina virtual, una interfaz y utilidades para macOS y Windows, y también existe para Linux. Al crear y administrar contenedores se comportan igual; la diferencia está en dónde se ejecuta el demonio.

## OCI y las alternativas

La Open Container Initiative define el formato de imagen y el de ejecución. Gracias a ello, una imagen construida por una herramienta se ejecuta con otra:

- **Podman**: mismo modelo, sin demonio central y con modo rootless por defecto. Añade pods, que agrupan contenedores que comparten red.
- **Buildah**: construye imágenes OCI sin demonio; Podman lo usa por debajo.
- **nerdctl**: cliente de containerd con una CLI muy parecida a la de Docker.
- **Kaniko**: construye imágenes dentro de un clúster, pensado para CI.

rkt, la primera alternativa relevante, quedó abandonada. Docker sigue siendo el estándar de facto, pero el formato ya no pertenece a una sola empresa.

## Contenedores y microservicios

Los contenedores encajan con los microservicios porque permiten desplegar y actualizar cada pieza por separado, pero no los exigen: un monolito también se beneficia de un empaquetado reproducible. Y se pueden construir microservicios sin contenedores. La arquitectura y la tecnología de despliegue son decisiones distintas.

## Lo que un contenedor no es

No es una máquina virtual, no aísla del kernel y no sustituye a un orquestador. Tampoco garantiza que una aplicación sea segura: si el proceso dentro corre como root y el motor también, un fallo puede alcanzar al anfitrión. Esas dos ideas —que comparte kernel y que el límite es de procesos— gobiernan todo lo que viene después: la persistencia, las redes, los límites de recursos y la forma de depurar.
