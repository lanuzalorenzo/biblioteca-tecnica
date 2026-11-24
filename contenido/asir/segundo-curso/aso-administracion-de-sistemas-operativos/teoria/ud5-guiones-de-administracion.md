# UD5. Guiones de administración

Un administrador que repite la misma secuencia de órdenes cinco veces al día no está trabajando: está copiando. El guion convierte esa secuencia en algo que se ejecuta igual, se revisa una vez y deja rastro de lo que hizo; la diferencia entre un cambio reproducible y uno que solo funcionó en la máquina de quien lo escribió.

> **Módulo:** ASO. Administración de sistemas operativos

## Para qué un guion

- **Repetir sin variación** una tarea: crear usuarios, revisar discos, rotar registros, comprobar servicios.
- **Documentar el procedimiento** en el propio código: lo que hace y en qué orden.
- **Reducir el error manual**: una orden mal escrita en una consola se olvida; en un guion, se corrige para siempre.
- **Automatizar la comprobación**: no solo ejecutar, también verificar el resultado.

Un guion no sustituye a entender la tarea. Si no se sabe hacer a mano, el guion solo automatiza el error.

## Bash y PowerShell

En Linux, **Bash** es el intérprete habitual; en Windows, **PowerShell**. La sintaxis básica, el esqueleto y el tratamiento de errores están en ISO, UD5; aquí se añade lo que necesita la administración diaria. Los dos comparten ideas:

- Entrada y salida: argumentos, código de salida, salida estándar y de error.
- Estructuras: variables, condicionales, bucles, funciones.
- Tratamiento de errores: detenerse o continuar según el fallo.

En Bash conviene empezar con `set -euo pipefail`: detenerse ante un error, tratar variables no definidas como error y no ocultar fallos en una tubería. En PowerShell, `$ErrorActionPreference = "Stop"` cumple un papel parecido. El código de salida importa: `0` es éxito; cualquier otro valor, fallo.

## Estructura

Un guion legible tiene:

```bash
#!/usr/bin/env bash
set -euo pipefail

uso() {
  echo "Uso: $0 <directorio> [días]" >&2
  exit 1
}

principal() {
  local destino="${1:-}"
  local dias="${2:-7}"
  [[ -d "$destino" ]] || uso
  find "$destino" -type f -mtime "+$dias" -print
}

principal "$@"
```

- **Cabecera** con intérprete y modo estricto.
- **Funciones** con nombre y variables locales.
- **Validación** de argumentos antes de tocar nada.
- **Mensajes de uso** por la salida de error.
- **Una función principal** que ordena el flujo.

Las variables se citan siempre entre comillas dobles; un espacio en un nombre de archivo rompe el guion que no lo hace.

## Errores, registro y limpieza

Un guion que falla a mitad puede dejar un archivo temporal, un bloqueo o un servicio parado. `trap` permite ejecutar una limpieza al salir —con éxito o con error—. El registro debe decir qué se hizo, cuándo y con qué resultado: fecha, nivel y mensaje, no un `echo` suelto.

La salida de error se separa de la normal para que un cron o un sistema de monitorización pueda distinguirlas. Y el guion no debe imprimir contraseñas ni tokens aunque falle.

## Idempotencia

Un guion idempotente se puede ejecutar dos veces con el mismo resultado: comprueba antes de crear, actualiza si falta y no duplica. Es la diferencia entre un despliegue repetible y uno que la segunda vez rompe.

La idempotencia se apoya en comprobaciones: ¿existe el usuario?, ¿está el servicio activo?, ¿la configuración ya tiene el valor? Si no se puede comprobar, se documenta que el guion no es seguro de repetir.

## Programación

- **cron:** expresión de cinco campos; el entorno es mínimo y las rutas deben ser absolutas.
- **systemd timers:** unidad de servicio más temporizador, con registro en el journal y dependencias.
- **Programador de tareas de Windows:** disparadores, condiciones y cuenta de ejecución.

En los tres casos hay que evitar solapes: un `flock` o un bloqueo equivalente impide que dos ejecuciones se pisen. Y el registro debe permitir saber si la tarea corrió y qué devolvió.

## Secretos y revisión

Las credenciales no se escriben en el guion ni se pasan por línea de órdenes —quedan en el historial y en la lista de procesos—. Se leen de un archivo con permisos restringidos, de variables de entorno controladas o de un gestor de secretos.

El guion se versiona y se revisa como el resto del código. Herramientas como `shellcheck` o `PSScriptAnalyzer` detectan errores antes de ejecutar; una prueba en seco —`--dry-run`— permite ver qué haría sin tocar el sistema.

## Lo que se comprueba

Que el guion valida argumentos y devuelve código de salida; que se detiene ante el error y limpia lo que deja; que registra qué hizo; que se puede ejecutar dos veces sin duplicar; que no expone secretos; que la programación evita solapes; y que se ha probado en un entorno distinto del de producción.

## Fuentes

- GNU Bash Reference Manual.
- Documentación de Microsoft PowerShell.
- `systemd.timer` y `cron(5)`.
- ShellCheck y PSScriptAnalyzer.
- Orden EDU/392/2010, de 20 de enero, currículo del ciclo de ASIR (BOE-A-2010-3028), módulo 0374.
