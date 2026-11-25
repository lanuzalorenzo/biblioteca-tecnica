# Herramientas visuales

Git se aprende en la terminal porque ahí se entiende qué pasa de verdad. En el trabajo diario, en cambio, casi todo el mundo usa un cliente gráfico que muestra el estado, los diffs y los conflictos sin escribir comandos. Conviene conocer ambos: la terminal para entender y desatascar, el cliente para no pelearse con lo rutinario.

## Qué aporta un cliente gráfico

Un buen cliente cubre el ciclo diario:

- Ver qué archivos han cambiado y qué líneas.
- Preparar un archivo o un fragmento concreto.
- Confirmar con un mensaje y subir al remoto.
- Crear y cambiar de rama.
- Dibujar el grafo de commits y las ramas.
- Resolver conflictos con un editor de tres paneles.

Lo que no suele cubrir bien es la historia reescrita: `rebase` interactivo, `reset`, `reflog` y recuperaciones. Para eso se vuelve a la terminal.

## Git GUI

Es el cliente que viene con Git para Windows. Es minimalista: muestra el estado, permite preparar y confirmar, y dibuja el grafo. Sirve para lo básico, pero se queda corto en comparación con las herramientas específicas.

## GitHub Desktop

Cliente oficial de GitHub para Windows y macOS. Integra la cuenta, los repositorios remotos y las pull requests; el flujo de clonar, cambiar de rama, confirmar y subir es muy directo. Es la opción más sencilla si todo el trabajo vive en GitHub, y la que menos fricción añade a quien empieza.

## SourceTree

Cliente de Atlassian para Windows y macOS. Su punto fuerte es la vista del grafo y la gestión de ramas, con opciones para hacer `rebase`, `cherry-pick` y `stash` desde menús. Integra Bitbucket y GitHub. Es más completo que GitHub Desktop, y también más pesado.

## TortoiseGit

Se integra en el explorador de Windows: las operaciones aparecen en el menú contextual de la carpeta. Es cómodo para quien trabaja con archivos y no quiere abrir otra aplicación. Su editor de conflictos muestra las tres versiones —base, local y remota— y permite elegir por bloques.

Los iconos superpuestos del explorador indican el estado de cada archivo; si no se ven, suele ser porque el explorador tiene la caché de iconos desactualizada o porque otra aplicación los ocupa.

## Criterio

No hay una herramienta mejor para todos. La elección depende del sistema, del remoto y de si el equipo ya usa una. Lo que sí conviene:

- Aprender el ciclo básico en la terminal antes de depender de los botones.
- Usar el cliente para revisar diffs y conflictos, que es donde ahorra más tiempo.
- Volver a la terminal para reescribir historia y recuperar.

## Para practicar

1. Abre el repositorio de práctica en un cliente gráfico y localiza el grafo, el estado y el diff de un archivo.
2. Prepara un archivo y confírmalo desde el cliente; comprueba el resultado con `git log` en la terminal.
3. Crea una rama, cambia a ella y provoca un conflicto; resuélvelo en el editor del cliente.
4. Haz el mismo cambio de rama con `git switch` y compara lo que muestra el cliente.
