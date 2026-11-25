# Git: control de código fuente para programadores

Git es un sistema de control de versiones distribuido: guarda el histórico completo de un proyecto y permite volver a cualquier punto del pasado, comparar dos momentos y trabajar en paralelo sin pisar los cambios de otros. Lo creó Linus Torvalds en 2005 para el desarrollo del kernel de Linux y hoy es la herramienta de referencia en casi cualquier proyecto de software.

## El problema que resuelve

Guardar copias de los archivos antes de tocarlos —`proyecto_v2`, `proyecto_final`, `proyecto_final_bueno`— multiplica el espacio y no deja claro qué cambió ni quién lo cambió. Un control de versiones sustituye ese apaño por un histórico ordenado: cada cambio queda registrado con su autor, su fecha y su mensaje, y se puede recuperar un archivo suelto o el proyecto entero en el estado que tenía.

## Cómo trabaja Git

Git no guarda una lista de diferencias: guarda instantáneas del proyecto. Cada confirmación (*commit*) es una foto completa con un identificador propio, y las ramas son punteros a esas fotos, no copias del proyecto. Por eso crear una rama es instantáneo y cambiar de una a otra no duplica nada.

El trabajo diario pasa por tres zonas:

- El **directorio de trabajo**, con los archivos tal como están ahora.
- El **área de preparación** (*staging*), donde se eligen los cambios que entran en la siguiente confirmación.
- El **repositorio**, donde quedan las confirmaciones ya guardadas.

## El flujo de trabajo

El día a día se resume en cuatro pasos: `git status` para ver qué ha cambiado, `git add` para elegir qué entra, `git commit` para guardar la instantánea y `git push` para publicarla en el remoto. En sentido contrario, `git pull` trae lo que otros han subido. Con eso ya se trabaja; el resto de Git son ramas, historia y herramientas para los casos que se salen de lo habitual.

## Ramas y remotos

Una rama es solo un puntero a una confirmación. Al cambiar de rama, Git mueve el puntero y actualiza el directorio de trabajo, sin duplicar el proyecto. Los repositorios remotos añaden una copia compartida: se descargan sus confirmaciones, se suben las propias y se sincronizan las ramas. Ahí es donde aparecen las fusiones, los conflictos y las estrategias para resolverlos.
