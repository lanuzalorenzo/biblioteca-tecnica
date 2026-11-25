# Contenedores

Un contenedor empaqueta una aplicación con las bibliotecas, el entorno y la configuración que necesita, y la ejecuta aislada del resto del sistema. La imagen resultante se transporta igual entre un portátil, un servidor de pruebas y producción, y arranca en menos de un segundo porque comparte el kernel del anfitrión. Esa es la diferencia con una máquina virtual y también su límite: el aislamiento es de proceso, no de hardware.

Docker ordenó el ecosistema con una interfaz de línea de comandos, un formato de imagen y un registro público, y sigue siendo la referencia. Podman ejecuta las mismas imágenes OCI sin demonio y, por defecto, sin privilegios, con una línea de comandos casi idéntica. Lo aprendido en una herramienta sirve en la otra salvo en los detalles que se señalan. Alrededor de ambas están las piezas que convierten un contenedor suelto en un servicio: capas y caché, volúmenes para lo que debe sobrevivir, redes con nombre propio, Compose para coordinar varios procesos, registros para distribuir y controles de seguridad para no cambiar comodidad por exposición.

## Contenido

| Apunte | Qué responde |
|---|---|
| [Contenedores y máquinas virtuales](contenedores-y-maquinas-virtuales.md) | Qué se ejecuta, qué se guarda y en qué se diferencia de una VM |
| [Instalación y primeros pasos](instalacion-y-primeros-pasos.md) | Qué instalar, cómo comprobar que funciona y qué objetos hay |
| [Imágenes y ciclo de vida](imagenes-y-ciclo-de-vida.md) | Cómo se descarga, arranca, inspecciona y borra |
| [Construir imágenes](construir-imagenes.md) | Cómo se describe una imagen y cómo se construye |
| [Persistencia y volúmenes](persistencia-y-volumenes.md) | Dónde viven los datos que no pueden perderse |
| [Etiquetas, registros y multiarquitectura](etiquetas-registros-y-multiarquitectura.md) | Cómo se nombra, publica y fija una imagen |
| [Compose](compose.md) | Cómo se describe una aplicación y se separa por entornos |
| [Compose multicontenedor](compose-multicontenedor.md) | Cómo se coordinan servicios, dependencias y escala |
| [Redes](redes.md) | Cómo se ven y se exponen los contenedores |
| [Contextos y acceso remoto](contextos-y-acceso-remoto.md) | Cómo se gobierna un motor local o remoto |
| [Compilar y probar con contenedores](compilar-y-probar-con-contenedores.md) | Cómo usar el contenedor como cadena de herramientas |
| [Contenedores Windows](contenedores-windows.md) | Qué cambia cuando el kernel es Windows |
| [Depurar contenedores](depurar-contenedores.md) | Qué mirar cuando un contenedor no arranca o falla |
| [Dev containers](dev-containers.md) | Cómo se desarrolla dentro de un contenedor sin perder el editor |

Los ejemplos usan `docker`; `podman` acepta el mismo comando en casi todos los casos. Nombres, contraseñas y direcciones son marcadores: la configuración real se inyecta desde el entorno o desde un gestor de secretos.
