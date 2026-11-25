# Git en el editor y en la terminal

Un editor moderno muestra el estado del repositorio, permite preparar cambios y resolver un conflicto sin escribir un comando. La terminal sigue siendo necesaria para lo que el editor no cubre bien: reescribir historia, recuperar lo perdido y automatizar. La nota separa lo uno de lo otro para que no se baile entre dos herramientas sin saber cuál manda.

## Lo que el editor hace bien

El panel de control de código fuente de Visual Studio Code, o su equivalente en otros entornos, cubre el ciclo diario:

- Ver qué archivos cambiaron y en qué línea.
- Preparar un archivo o un fragmento concreto.
- Confirmar con un mensaje y enviar al remoto.
- Crear, cambiar y mezclar ramas.
- Comparar dos versiones de un archivo y recorrer el histórico.

Ese ciclo no necesita terminal. Trabajar con el ratón no cambia el resultado: los mismos objetos y las mismas referencias se escriben en `.git`.

## Lo que sigue pidiendo terminal

Hay operaciones que el editor esconde o no ofrece:

- **Reescribir historia:** `rebase -i`, `commit --amend` sobre varios commits, `filter-repo`.
- **Recuperar:** `reflog`, que es la red de seguridad cuando una rama parece perdida.
- **Automatizar:** hooks, scripts de comprobación y tareas de CI que se ejecutan solas.
- **Diagnosticar:** `fsck`, `cat-file`, `rev-parse` y el estado real de las referencias.
- **Trabajar con submódulos y LFS**, donde la interfaz suele quedarse corta.

Un conflicto se puede resolver en el editor, y suele ser más cómodo. Lo que no se hace desde el editor es decidir qué commits se reescriben sin entender el grafo.

## Extensiones de Visual Studio Code

El panel nativo trae lo básico. Estas extensiones cubren lo que falta:

- **GitLens** añade el histórico por línea, la comparación entre ramas y la búsqueda en el historial.
- **Git Graph** dibuja el grafo con todas las ramas y permite actuar sobre una rama o un commit.
- **Gitignore** da soporte de sintaxis y edición para `.gitignore`.
- **GitHub Pull Requests and Issues** revisa pull requests e issues de GitHub sin salir del editor.

## Práctica

Con el repositorio de prueba, haz el recorrido completo desde el editor: prepara un archivo, confirma, crea una rama, cambia a ella, mezcla y abre el histórico. Después repite el mismo recorrido desde la terminal y compara:

- ¿En qué paso el editor muestra menos información?
- ¿Qué comando te habría gustado tener a mano?
- ¿Dónde te habría ayudado ver el grafo antes de mezclar?

El objetivo no es elegir una herramienta, sino saber cuál usar en cada momento y no depender de que el editor lo permita.

## Criterio

El editor es una vista del repositorio, no el repositorio. Cuando una operación cambia la historia o recupera algo perdido, se hace desde la terminal y se comprueba el resultado con `git log --graph --oneline` y `git status`. Cuando solo se prepara, confirma o compara, el editor ahorra tiempo y errores de tecleo.
