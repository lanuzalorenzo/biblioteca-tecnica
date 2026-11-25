# Conceptos avanzados

Con el ciclo básico y las ramas controladas, quedan las operaciones que reescriben historia, mueven commits entre ramas y automatizan comprobaciones. Son las que separan un uso superficial de Git de un uso con criterio.

## Amend: corregir el último commit

`git commit --amend` reemplaza la última confirmación por una nueva. Sirve para corregir el mensaje o añadir un archivo que se olvidó:

```bash
git add archivo-olvidado
git commit --amend --no-edit      # conserva el mensaje
git commit --amend -m "Mensaje nuevo"
```

El commit original deja de existir y aparece otro con un identificador distinto. Por eso solo se hace sobre commits locales que nadie ha descargado. Si ya está publicado, la alternativa segura es `git revert`.

## Revert: deshacer sin borrar historia

`git revert <commit>` crea una confirmación nueva que aplica el cambio inverso. La historia se conserva y el resultado es seguro en ramas compartidas:

```bash
git revert a1b2c3d
git revert --no-commit a1b2c3d    # prepara el cambio sin confirmar
```

Si el cambio revertido choca con cambios posteriores, Git pide resolver el conflicto como en una fusión. `git revert --abort` cancela.

La diferencia con `reset` es la clave: `revert` añade, `reset` borra. En una rama publicada, `revert` es la herramienta correcta.

## Reset: mover la rama y decidir qué se conserva

`git reset` mueve el puntero de la rama a otra confirmación. Lo que ocurre con el índice y el directorio de trabajo depende del modo:

| Modo | Rama | Índice | Directorio de trabajo |
|---|---|---|---|
| `--soft` | Se mueve | Se conserva | Se conserva |
| `--mixed` (por defecto) | Se mueve | Se reinicia | Se conserva |
| `--hard` | Se mueve | Se reinicia | Se reinicia |

```bash
git reset --soft HEAD~1    # deshacer el commit y dejar los cambios preparados
git reset HEAD~1           # deshacer el commit y dejar los cambios sin preparar
git reset --hard HEAD~1    # deshacer el commit y borrar los cambios
```

`--hard` no pregunta y puede destruir trabajo. Antes de usarlo, comprobar `git status` y, si hay dudas, guardar con un `stash` o una rama temporal.

Si el commit ya se envió al remoto, no se hace `reset`: se hace `revert`. Forzar el `push` después de un `reset` obliga a los demás a recolocar su historia y puede perder trabajo.

### Recuperar después de un reset

`git reflog` guarda durante un tiempo los movimientos de `HEAD`, incluidas las confirmaciones que un `reset` dejó fuera de la rama. Desde ahí se puede volver:

```bash
git reflog
git reset --hard HEAD@{2}
```

El módulo de deshacer y recuperar desarrolla estos casos con más detalle.

## Cherry-pick: llevar un commit a otra rama

`git cherry-pick <commit>` aplica los cambios de una confirmación concreta sobre la rama actual, creando una confirmación nueva:

```bash
git switch release
git cherry-pick a1b2c3d
git cherry-pick a1b2c3d..e4f5g6h    # un rango
git cherry-pick --no-commit a1b2c3d
```

Se usa para llevar un arreglo puntual de una rama a otra sin fusionar todo. No sustituye a una fusión: si se repite mucho, el historial se llena de copias y los conflictos se multiplican.

## Hooks

Los hooks son scripts que Git ejecuta en momentos concretos. Viven en `.git/hooks/` y no se versionan por defecto; para compartirlos se configura un directorio común con `core.hooksPath` o se usa una herramienta que los instale.

Los más útiles:

- `pre-commit`: se ejecuta antes de crear la confirmación. Sirve para lint, formato y pruebas rápidas; si sale con error, el commit se cancela.
- `commit-msg`: valida el formato del mensaje.
- `pre-push`: se ejecuta antes de subir. Sirve para pruebas algo más lentas o para comprobar que no se sube un secreto.
- `post-checkout`: se ejecuta al cambiar de rama; útil para reinstalar dependencias o regenerar archivos.

Un `pre-commit` mínimo:

```bash
#!/bin/sh
set -e
npm test -- --runInBand
```

Se guarda en `.git/hooks/pre-commit`, se hace ejecutable con `chmod +x` y se prueba con un commit. `git commit --no-verify` salta los hooks: sirve para una urgencia, no como costumbre.

## GitFlow

GitFlow es un modelo de ramas para productos con versiones y soporte. Define ramas con un papel:

- `main` o `master`: solo versiones publicadas; cada confirmación lleva una etiqueta.
- `develop`: integración del trabajo que se está preparando.
- `feature/*`: una por funcionalidad; sale de `develop` y vuelve a `develop`.
- `release/*`: cierra una versión; sale de `develop`, recibe solo arreglos y se fusiona en `main` y `develop`.
- `hotfix/*`: arreglo urgente sobre `main`; se fusiona en `main` y en `develop`.

El flujo es más pesado que trabajar con una sola rama principal y ramas cortas. Tiene sentido cuando hay versiones que mantener y varias personas; en un proyecto pequeño, la sobrecarga no compensa.

## Para practicar

1. Corrige el mensaje de la última confirmación con `--amend` y comprueba el cambio de identificador.
2. Revierte una confirmación publicada con `git revert` y observa la nueva confirmación.
3. Deshaz un commit local con `--soft`, `--mixed` y `--hard` en una rama de prueba; compara qué queda en cada zona.
4. Recupera con `git reflog` el commit que borró un `reset --hard`.
5. Lleva un arreglo de `main` a una rama de versión con `cherry-pick`.
6. Escribe un `pre-commit` que ejecute las pruebas y comprueba que bloquea un commit fallido.
