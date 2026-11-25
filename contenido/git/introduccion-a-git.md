# Introducción a Git y al control de código fuente

Un control de versiones guarda el histórico de un proyecto para poder volver atrás, comparar dos momentos y trabajar en paralelo sin pisar el trabajo de otros. Git es hoy la herramienta de referencia, pero antes de usarla conviene entender qué problema resuelve y por qué su modelo es distinto al de los sistemas que lo precedieron.

## El problema de las copias

Cuando un proyecto no tiene control de versiones, la carpeta acaba llena de copias: `proyecto_v2`, `proyecto_final`, `proyecto_final_bueno`, `proyecto_final_bueno_2`. Cada copia ocupa espacio, ninguna dice qué cambió ni quién lo cambió, y comparar dos versiones se convierte en un ejercicio manual.

Un control de versiones sustituye ese apaño por un histórico ordenado. Cada cambio queda registrado con su autor, su fecha y su mensaje. Se puede recuperar un archivo suelto, volver el proyecto entero a una fecha anterior y saber qué se tocó entre dos puntos. También permite que varias personas trabajen a la vez sobre el mismo código sin sobrescribirse.

## Tipos de control de versiones

Hay tres modelos, y la diferencia está en dónde vive el histórico.

| Modelo | Dónde vive el histórico | Qué implica |
|---|---|---|
| Local | En la propia máquina | Sirve para un proyecto pequeño; no hay copia ni trabajo en equipo |
| Centralizado | En un servidor único | Todos dependen de la red y del servidor; si cae, nadie trabaja |
| Distribuido | En cada clon | Cada persona tiene el histórico completo; se trabaja sin conexión y se sincroniza cuando conviene |

Los sistemas locales quedaron atrás. Los centralizados, como CVS o Subversion, resolvieron el trabajo en equipo pero arrastran un punto único de fallo. Los distribuidos, como Mercurial o Git, replican el repositorio en cada clon: se puede trabajar sin red, comparar y confirmar en local, y usar el servidor solo para compartir y respaldar.

## De BitKeeper a Git

El kernel de Linux estuvo años gestionándose con parches y correos. En 2002 pasó a BitKeeper, un sistema distribuido, pero era software comercial y la relación con su creador se rompió en 2005. Linus Torvalds necesitaba algo que no dependiera de un tercero y escribió Git en unos días, con una premisa clara: gestionar el kernel, que ya era un proyecto enorme, sin perder velocidad.

De ahí salen las decisiones que aún definen Git: las ramas son baratas, las operaciones locales son rápidas y la integridad se comprueba en cada paso. La primera versión estuvo lista en una semana y el kernel empezó a usarla casi de inmediato. El resto de la industria la adoptó después por las mismas razones.

## Cómo modela Git el histórico

La diferencia de fondo con un sistema centralizado no es el servidor, sino qué se guarda. Un VCS tradicional registra diferencias entre versiones; Git guarda **instantáneas** del proyecto. Cada confirmación (*commit*) es una foto completa del árbol, con un identificador propio, y las ramas son punteros a esas fotos, no copias del proyecto.

Ese modelo explica por qué crear una rama es instantáneo y por qué cambiar de una a otra no duplica archivos. También explica el identificador: Git calcula un *hash* del contenido de cada objeto y lo usa como nombre. Si un archivo se corrompe o se altera en tránsito, el *hash* deja de cuadrar y Git lo detecta. La integridad no es un extra; está en el diseño.

## Los tres estados de un archivo

Trabajar con Git es mover archivos entre tres estados:

- **Modificado**: el archivo cambió en el directorio de trabajo, pero todavía no se ha preparado.
- **Preparado** (*staged*): el cambio está en el área de preparación y entrará en la próxima confirmación.
- **Confirmado** (*committed*): la instantánea está guardada en el repositorio.

Y esos estados se corresponden con tres zonas:

| Zona | Qué contiene |
|---|---|
| Directorio de trabajo | Los archivos tal como están ahora |
| Área de preparación (`index`) | Lo que se ha elegido para el próximo *commit* |
| Repositorio (`.git`) | Las confirmaciones ya guardadas y sus objetos |

El área de preparación es lo que más despista al principio, porque otros sistemas no la tienen. Su utilidad es separar “lo que he cambiado” de “lo que quiero confirmar”: permite dividir un trabajo grande en varios *commits* coherentes y revisar antes de guardar.

## El flujo diario

El ciclo básico tiene cuatro pasos:

```bash
git status          # qué ha cambiado
git add archivo     # qué entra en la próxima confirmación
git commit -m "..." # guardar la instantánea
git push            # publicar en el remoto
```

En sentido contrario, `git pull` trae lo que otros han subido y lo integra. Con estos cuatro comandos se trabaja el día a día; el resto de Git —ramas, fusiones, rebase, etiquetas— cubre los casos que se salen de lo habitual.

## Instalación

Git se instala con el gestor de paquetes de cada sistema o con el instalador oficial.

- **Windows**: el instalador de `git-scm.com` añade Git al `PATH`, la línea de comandos y Git Bash. Las opciones por defecto sirven; solo hay que elegir el editor si se quiere otro.
- **macOS**: Homebrew lo mantiene actualizado con `brew install git`.
- **Linux**: el paquete de la distribución. En Debian y Ubuntu, `sudo apt install git`; en Fedora, `sudo dnf install git`.

Al terminar, `git --version` confirma la instalación. Antes del primer *commit* conviene configurar la identidad:

```bash
git config --global user.name "Nombre"
git config --global user.email "correo@ejemplo.com"
```

## Para practicar

1. Instala Git y comprueba la versión con `git --version`.
2. Crea una carpeta vacía, ejecuta `git init` y mira qué aparece en `.git`.
3. Crea un archivo, ejecuta `git status`, prepáralo con `git add` y confírmalo con `git commit`.
4. Vuelve a cambiar el archivo y observa cómo `git status` lo marca como modificado.

Con eso quedan claros los tres conceptos que aparecerán en todos los módulos: qué es un *commit*, qué es una rama y qué es un repositorio.
