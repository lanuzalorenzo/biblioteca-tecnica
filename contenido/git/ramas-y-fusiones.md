# Ramas y fusiones

Una rama en Git es un puntero a una confirmación. No es una copia del proyecto ni una carpeta aparte: es una etiqueta móvil que avanza cuando se confirma. Esa idea, tan simple, es lo que permite trabajar en varias líneas a la vez sin duplicar nada y fusionarlas después.

## Qué es una rama

En un repositorio recién creado hay una sola rama, normalmente `main`. Cada confirmación crea un objeto nuevo y mueve el puntero de la rama actual:

```text
A --- B --- C   main
```

Si se crea una rama a partir de `C`, las dos apuntan al mismo commit. Al confirmar en la nueva, solo avanza ese puntero:

```text
A --- B --- C   main
              \
               D --- E   feature
```

El histórico no se copia: se comparte. Por eso crear una rama es instantáneo aunque el proyecto tenga años de historia.

## HEAD y las referencias

`HEAD` indica la rama o el commit en el que se está trabajando. Normalmente apunta a una rama, y esa rama apunta a un commit. Al cambiar de rama, Git mueve `HEAD` y actualiza el directorio de trabajo para que coincida con la instantánea de esa rama.

Hay dos formas de nombrar un commit:

- **Absoluta**: su identificador, los primeros caracteres del *hash* (`a1b2c3d`).
- **Relativa**: desde otro commit. `HEAD~1` es el padre, `HEAD~3` el tercer ancestro; `HEAD^1` es el primer padre de una fusión y `HEAD^2` el segundo.

`git log --oneline --graph --decorate --all` dibuja el grafo y muestra dónde está cada puntero. Es la forma más rápida de entender una historia con ramas.

## Crear y cambiar de rama

```bash
git branch                 # ramas locales; la actual lleva *
git branch feature         # crear sin cambiar
git switch feature         # cambiar a la rama
git switch -c feature      # crear y cambiar en un paso
git branch -d feature      # borrar si ya está fusionada
git branch -D feature      # borrar a la fuerza, sin comprobar
```

El comando clásico es `git checkout feature`; `git switch` se añadió para separar el cambio de rama del de archivos. `git checkout -b feature` sigue siendo válido y equivale a `git switch -c`.

Al cambiar de rama, Git solo toca los archivos que difieren entre las dos instantáneas. Si hay cambios sin confirmar que entrarían en conflicto con el cambio, se niega y pide confirmarlos o guardarlos.

## Fusionar ramas

La fusión integra el trabajo de una rama en otra. Se hace desde la rama que recibe:

```bash
git switch main
git merge feature
```

Hay dos casos:

- **Avance rápido** (*fast-forward*): `main` no ha avanzado desde que nació `feature`, así que basta con mover el puntero. No se crea una confirmación de fusión.
- **Fusión a tres bandas** (*three-way merge*): las dos ramas han avanzado. Git busca el ancestro común y combina los cambios; si no hay conflictos, crea una confirmación de fusión con dos padres.

Para forzar una confirmación de fusión incluso cuando cabría el avance rápido:

```bash
git merge --no-ff feature
```

Así queda explícito en el histórico que hubo una rama y una integración, lo que ayuda a leer el proyecto.

## Conflictos

Un conflicto aparece cuando las dos ramas modifican la misma zona del mismo archivo y Git no puede decidir qué versión vale. No es un error: es una pausa para que lo resuelva una persona.

```bash
git status                 # archivos en conflicto
git diff --name-only --diff-filter=U
```

En el archivo aparecen marcas:

```text
<<<<<<< HEAD
lo que hay en la rama actual
=======
lo que trae la otra rama
>>>>>>> feature
```

Se elige el resultado, se borran las marcas y se prepara el archivo:

```bash
git add archivo
git commit                 # cierra la fusión
```

Si la fusión se complica, `git merge --abort` vuelve al estado anterior. Para ver qué cambió cada lado antes de decidir, `git log --merge -p archivo` y `git diff` ayudan; también se puede usar `git mergetool` si hay una herramienta gráfica configurada.

## Rebase frente a merge

`git rebase` reaplica las confirmaciones de una rama sobre otra base. El resultado es una historia lineal, sin confirmación de fusión:

```bash
git switch feature
git rebase main
```

La diferencia práctica:

- **Merge** conserva la historia real, con la bifurcación y la fusión. Es seguro en ramas compartidas.
- **Rebase** reescribe los identificadores de las confirmaciones reaplicadas. Deja una historia más limpia, pero no debe usarse sobre commits que ya están publicados y que otras personas han descargado.

La regla que evita sustos: rebase en local sobre lo que aún no se ha compartido; merge para integrar lo que ya está en el remoto.

## Para practicar

1. Crea un repositorio con tres confirmaciones y una rama `feature`.
2. Añade dos confirmaciones en `feature` y vuelve a `main`; comprueba el grafo con `git log --graph --all`.
3. Fusiona con avance rápido y repite el ejercicio con `--no-ff` para ver la diferencia.
4. Provoca un conflicto modificando la misma línea en las dos ramas, resuélvelo y cierra la fusión.
5. Borra la rama con `git branch -d` y comprueba que el histórico sigue ahí.
