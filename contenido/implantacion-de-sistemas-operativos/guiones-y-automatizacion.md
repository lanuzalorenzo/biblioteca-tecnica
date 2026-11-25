# Guiones: ficheros por lotes y shell

Un administrador que repite una tarea a mano tres veces ya ha tardado demasiado en escribirla como guion. El guion no es un adorno de programador: es la forma de que la tarea se ejecute igual mañana, la ejecute quien la ejecute y quede registro de que se hizo.


## Tres lenguajes, una idea

En un sistema Windows se empieza con **ficheros por lotes** (`.bat`) y se termina en **PowerShell**. En Linux, con **Bash**. Los tres comparten lo esencial: variables, condiciones, bucles, salida por pantalla, código de retorno y encadenamiento de órdenes.

Un fichero por lotes de 2015 típico —menú de opciones con `set /p` y `goto`— enseña algo que sigue siendo cierto: la estructura importa más que la sintaxis. Si el flujo está claro, el lenguaje se consulta.

## Piezas que se usan siempre

- **Variables:** `set VAR=valor` y `%VAR%` en lotes; `$VAR` en Bash; `$var` en PowerShell.
- **Condiciones:** `if exist`, `if errorlevel`; en Bash, `[ -f fichero ]` y `if [ "$a" -eq 1 ]`.
- **Bucles:** `for %%f in (*.txt) do` en lotes; `for f in *.txt; do` en Bash.
- **Código de retorno:** cada orden devuelve 0 si fue bien. Permite encadenar y abortar.
- **Redirección:** `>`, `>>` y `2>` separan salida normal y errores; `|` conecta la salida de una orden con la entrada de la siguiente.

## Bash con criterio

Cuatro hábitos convierten un guion frágil en uno fiable:

```bash
#!/usr/bin/env bash
set -euo pipefail     # aborta al fallar, con variables sin definir y en tuberías
```

- `-e`: si una orden falla, el guion para. Sin esto, un borrado fallido sigue adelante y borra otra cosa.
- `-u`: usar una variable vacía es un error, no una cadena vacía silenciosa.
- `-o pipefail`: un fallo en mitad de una tubería no se pierde.
- **Comillas** alrededor de las variables: sin ellas, un nombre de fichero con espacios parte el comando en dos.

Y lo que no se hace nunca: pasar datos de usuario directamente a `eval`, concatenar para construir órdenes de borrado sin comprobar la ruta, o dejar `sudo` dentro de un guion que cualquiera puede editar.

## Programación de tareas

- **Windows:** el Programador de tareas, con condiciones de red, usuario y credenciales de ejecución.
- **Linux:** `cron` con `crontab -e`, o un temporizador de systemd, que además registra la ejecución en journald.

Lo que se programa se documenta: qué hace, cuándo, con qué cuenta y qué deja si falla. Un cron olvidado que envía correo cada hora llena el buzón y nadie sabe de dónde sale.

## Cuándo un guion no basta

Un guion sirve para una tarea acotada en un equipo. Cuando hay que mantener veinte equipos en el mismo estado, el guion deja de ser la herramienta: hace falta configuración declarativa, que comprueba antes de aplicar. El guion empuja; la herramienta converge.

## Lo que se comprueba

Que el guion hace lo mismo ejecutado dos veces; que falla de forma visible cuando algo no está, en lugar de continuar; que no imprime credenciales en la salida; que deja un registro de lo que hizo; y que se puede ejecutar con otro usuario sin sorpresas de permisos.

## Errores que se repiten

- Guiones sin `set -e`, que siguen tras el primer error.
- Rutas relativas que dependen del directorio desde el que se lanza.
- Comprobar el éxito por el texto de la salida en lugar del código de retorno.
- Programar tareas con la contraseña escrita dentro del fichero.

## Esqueleto de un guion útil

```bash
#!/usr/bin/env bash
set -euo pipefail

destino="${1:?falta el directorio de destino}"
[[ -d "$destino" ]] || { echo "no existe: $destino" >&2; exit 1; }

for f in /var/log/*.log; do
  [[ -f "$f" ]] || continue
  cp --preserve=timestamps "$f" "$destino/"
done

echo "copiados $(ls -1 "$destino" | wc -l) ficheros"
```

En Windows, el equivalente mínimo con PowerShell es `$ErrorActionPreference = "Stop"` y un `try/catch`; en un fichero por lotes, comprobar `if errorlevel 1` después de cada orden que importe.

## Fuentes

- Manual de Bash y guía de estilo de Google para shell.
- Documentación de PowerShell y del Programador de tareas.
- Páginas de manual de `cron` y `systemd.timer`.
