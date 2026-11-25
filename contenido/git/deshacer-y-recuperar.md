# Deshacer y recuperar

Casi todo lo que se hace en Git se puede deshacer, pero no todo con el mismo comando. La diferencia está en dos cosas: si el cambio llegó a publicarse y si interesa conservarlo. Un archivo mal editado, un *commit* con el mensaje equivocado o una rama que se borró por error se arreglan en segundos si se elige la herramienta correcta; elegir la equivocada convierte un susto en una pérdida.

## Dos preguntas antes de tocar nada

La primera: ¿el *commit* está publicado? Lo que solo existe en el equipo se puede reescribir sin consecuencias. Lo que ya está en el remoto lo puede tener otra persona, y reescribirlo obliga a forzar el *push* y rompe el historial de quien lo descargó.

La segunda: ¿quieres conservar los cambios? Un `git reset --hard` no pregunta; borra el trabajo del directorio. Si hay algo que merece la pena, se guarda antes con un *commit* o con un *stash*.

## Las tres zonas

Git guarda el trabajo en tres sitios: el **directorio de trabajo**, con los archivos tal como están; el **área de preparación** o *index*, con lo que entrará en el próximo *commit*; y el **repositorio**, con los *commits* ya cerrados. Cada comando de recuperación mueve una, dos o las tres.

De ahí sale el detalle que más confunde: `git restore archivo` copia desde el *index*, no desde el último *commit*. Si el archivo ya estaba añadido, restaurarlo devuelve la versión preparada, no la confirmada.

## Descartar cambios en un archivo

```bash
git restore notas.md
```

Devuelve el archivo tal como estaba en el *index*. Si quieres la versión del último *commit* y además sacarlo del *index*, se indica el origen y las dos zonas:

```bash
git restore --source=HEAD --staged --worktree notas.md
```

Las dos órdenes destruyen lo no confirmado de ese archivo. No hay papelera: lo que se va, se va.

## Sacar un archivo del próximo commit

```bash
git restore --staged .env
```

Quita el archivo del *index* y deja intacto su contenido. Es lo que se hace cuando se añadió algo que no debía entrar. Ojo con lo que no arregla: si el archivo ya se confirmó antes, el secreto sigue en el historial y este comando no lo toca.

## Deshacer el último commit

`git reset` mueve la rama a otro *commit* y decide qué pasa con lo demás. Tiene tres modos y conviene saber cuál se está usando:

```bash
git reset --soft HEAD~1
```

Deshace el *commit* y deja sus cambios en el *index*, listos para confirmarlos otra vez. Es lo habitual para corregir un mensaje o juntar dos *commits*.

```bash
git reset HEAD~1
```

Es el modo por defecto (`--mixed`): deshace el *commit* y deja los cambios en el directorio, sin preparar. Útil cuando hay que reorganizar qué entra en cada *commit*.

```bash
git reset --hard HEAD~1
```

Deshace el *commit* y borra además los cambios del directorio. La salida es el *reflog*, que se ve más abajo.

## Deshacer un commit publicado

Aquí no se reescribe: se añade. `git revert` crea un *commit* nuevo que aplica lo contrario del indicado.

```bash
git revert a1b2c3d
```

El historial conserva el error y su corrección, que es lo que necesita un repositorio compartido: nadie tiene que descargar de nuevo ni forzar nada. Si el *commit* que se revierte es una mezcla, hay que decir cuál de sus padres se toma como referencia:

```bash
git revert -m 1 <commit-de-mezcla>
```

## Guardar el trabajo a medias

Cuando hay que cambiar de rama y no toca confirmar, el *stash* aparta los cambios sin ensuciar el historial.

```bash
git stash push -m "formulario a medias"
git stash list
git stash apply stash@{0}
git stash pop
```

`apply` recupera y conserva la entrada; `pop` recupera y la borra. El *stash* es local: no se sube ni lo ve nadie más.

## Recuperar lo que parece perdido

Cada movimiento de `HEAD` y de las ramas queda anotado en el *reflog*, un registro local. Ahí está la salida de un `reset --hard` equivocado o de una rama borrada.

```bash
git reflog
git reset --hard HEAD@{1}
```

`HEAD@{1}` es la posición anterior de `HEAD`: justo donde estaba antes del último movimiento. Se puede apuntar a cualquier línea del *reflog*. Dos límites: es local y no viaja al remoto; y se poda solo, a los 90 días las entradas alcanzables y a los 30 las que ya no lo están, según los valores por defecto de `gc.reflogExpire` y `gc.reflogExpireUnreachable`.

## Mover un commit a otra rama

Si se confirmó en `main` por error, el *commit* no se pierde: se crea la rama en ese punto y después se retrocede `main`.

```bash
git branch trabajo
git reset --hard HEAD~1
git switch trabajo
```

La rama nueva conserva el *commit*; `main` vuelve al anterior. Sin `push` de por medio, nadie lo nota.

## El caso que no arreglan estos comandos

Un secreto confirmado y publicado no se deshace con `restore` ni con `reset`. El primer paso es siempre **rotar la credencial**: a partir de ese momento, lo que esté en el historial ya no sirve. Después, si el repositorio es público o se comparte, se reescribe el historial con `git filter-repo`, se fuerza el *push* con el equipo avisado y se documenta la exposición. Un `force-push` sobre una rama protegida se prepara antes, no se improvisa.

## Para practicar

Crea un repositorio de prueba con tres *commits* y rompe cosas a propósito: descarta un archivo modificado, saca otro del *index* y deshaz el último *commit* con los tres modos de `reset`. Provoca un `reset --hard` y recupéralo con `git reflog`. Ejecuta un `git revert` y compara el historial con el de un `reset`. Al terminar, borra el repositorio: no queda nada que conservar.
