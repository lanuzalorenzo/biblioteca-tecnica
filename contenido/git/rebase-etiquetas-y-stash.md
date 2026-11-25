# Rebase, etiquetas y stash

Hay tres herramientas que aparecen cuando el trabajo se complica: `rebase` para ordenar la historia antes de integrarla, las etiquetas para marcar versiones y `stash` para aparcar cambios sin confirmarlos. Ninguna es obligatoria para empezar, pero las tres ahorran disgustos en cuanto el repositorio tiene varias ramas.

## Rebase

`git rebase` reaplica las confirmaciones de una rama sobre otra base. Se usa desde la rama que se quiere mover:

```bash
git switch feature
git rebase main
```

Git toma cada confirmación de `feature` que no está en `main`, la vuelve a aplicar sobre la punta de `main` y mueve el puntero. El resultado es una historia lineal, como si el trabajo se hubiera hecho después de la última confirmación de `main`.

La diferencia con `merge`:

- **Merge** conserva la bifurcación y crea una confirmación con dos padres. La historia es la real, pero el grafo se llena de cruces.
- **Rebase** reescribe los identificadores de las confirmaciones reaplicadas. La historia queda limpia y lineal, pero deja de ser la original.

Por eso hay una regla que evita casi todos los problemas: **no se hace rebase sobre commits publicados**. Si otra persona ya descargó esos commits, reescribirlos le obliga a recolocar su rama y a forzar el `push`. En local, sobre lo que aún no se ha compartido, es una herramienta excelente.

### Resolver un rebase

Si una confirmación choca con la nueva base, el rebase se detiene y deja el conflicto en el archivo. Se resuelve como en una fusión:

```bash
git status
# editar los archivos y quitar las marcas
git add archivo
git rebase --continue
```

`git rebase --abort` vuelve al estado anterior; `git rebase --skip` descarta la confirmación que no se quiere reaplicar.

### Rebase interactivo

`git rebase -i HEAD~4` abre una lista de las últimas cuatro confirmaciones con una acción por línea:

- `pick`: conservar la confirmación.
- `reword`: cambiar el mensaje.
- `edit`: detener para modificar el contenido.
- `squash`: unir con la anterior y editar el mensaje.
- `fixup`: unir con la anterior y quedarse con su mensaje.
- `drop`: eliminar la confirmación.

Es la forma de dejar una rama con commits coherentes antes de abrir una pull request. Cambia los identificadores, así que se hace sobre trabajo local.

## Etiquetas

Una etiqueta marca una confirmación con un nombre, normalmente una versión. No se mueve como una rama: queda fija en ese commit.

Hay dos tipos:

```bash
git tag v1.0.0                          # ligera: solo un puntero
git tag -a v1.0.0 -m "Primera versión"   # anotada: guarda autor, fecha y mensaje
```

La anotada es la recomendada para versiones publicadas, porque incluye metadatos y se puede firmar. La ligera sirve para marcas temporales.

```bash
git tag                     # listar
git tag -l "v1.*"           # filtrar
git show v1.0.0             # ver la confirmación y el mensaje
git tag -d v1.0.0           # borrar en local
git push origin v1.0.0      # publicar una etiqueta
git push --tags             # publicar todas
git fetch --tags            # traer las del remoto
```

Borrar una etiqueta publicada requiere `git push origin :refs/tags/v1.0.0`; conviene hacerlo solo si nadie la usa.

Para saber en qué etiqueta está un commit, `git describe --tags` devuelve algo como `v1.0.0-3-gabc123`: tres confirmaciones después de `v1.0.0`, en el commit `abc123`.

## Stash

`git stash` guarda los cambios sin confirmar en una pila aparte y deja el directorio de trabajo limpio. Sirve para cambiar de rama a resolver algo urgente sin confirmar trabajo a medias.

```bash
git stash push -m "formulario a medias"
git stash push -u          # incluye archivos sin seguimiento
git stash list
git stash show -p stash@{0}
git stash apply            # recuperar y mantener en la pila
git stash pop              # recuperar y sacar de la pila
git stash drop stash@{0}   # borrar una entrada
git stash clear            # vaciar la pila
```

`apply` es más seguro que `pop`: si hay conflictos, la entrada sigue en la pila y se puede reintentar. Los stash son locales; no se suben al remoto.

Si el trabajo aparcado se ha convertido en una rama, `git stash branch nueva-rama` crea la rama desde el commit donde se guardó y aplica el stash allí.

## Para practicar

1. Crea una rama, añade dos confirmaciones y haz `git rebase main`; comprueba el grafo antes y después.
2. Provoca un conflicto durante el rebase, resuélvelo y termina con `--continue`; prueba también `--abort`.
3. Usa `git rebase -i HEAD~3` para unir dos confirmaciones con `squash` y cambiar un mensaje con `reword`.
4. Crea una etiqueta anotada, publícala, bórrala en local y vuelve a descargarla con `git fetch --tags`.
5. Guarda un cambio con `git stash`, cambia de rama, vuelve y recupéralo con `pop`; comprueba la pila con `git stash list`.
