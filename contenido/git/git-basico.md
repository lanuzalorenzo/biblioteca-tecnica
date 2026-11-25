# Git básico: la línea de comandos

Con Git instalado, el trabajo diario se hace con un puñado de comandos. Este módulo cubre el ciclo completo: crear o clonar un repositorio, preparar cambios, confirmarlos, leer el histórico, ignorar archivos y sincronizar con un remoto.

## Antes de empezar

Conviene comprobar la versión y dejar configurada la identidad, porque cada confirmación lleva autor y correo:

```bash
git --version
git config --global user.name "Nombre"
git config --global user.email "correo@ejemplo.com"
git config --global init.defaultBranch main
```

`git config --list` muestra la configuración efectiva; `git config --global --edit` abre el archivo global. La ayuda está en `git help comando` y en `git comando -h` para el resumen rápido.

## Crear un repositorio

`git init` convierte una carpeta en repositorio: crea `.git`, donde viven los objetos, las referencias y la configuración local.

```bash
mkdir proyecto
cd proyecto
git init
```

`git clone` hace lo mismo a partir de uno existente y añade el remoto `origin`:

```bash
git clone https://ejemplo.com/repo.git
git clone https://ejemplo.com/repo.git carpeta-local
```

El clon trae la historia, la rama por defecto y las referencias remotas. No trae las ramas locales de otras personas: esas se crean al hacer *checkout* sobre la referencia remota.

## Leer el estado

`git status` es el comando que más se usa. Distingue tres grupos:

- **Sin seguimiento**: archivos nuevos que Git aún no conoce.
- **Modificados**: archivos ya versionados con cambios sin preparar.
- **Preparados**: cambios que entrarán en la próxima confirmación.

La versión corta, `git status -s`, usa dos columnas: la izquierda es el área de preparación y la derecha el directorio de trabajo. `M ` significa preparado; ` M`, modificado sin preparar; `??`, sin seguimiento.

## Preparar y confirmar

El ciclo básico es `add` y `commit`:

```bash
git add archivo.txt
git add carpeta/
git add -A          # todo: altas, cambios y borrados
git add -u          # solo archivos ya versionados
git add -p          # por fragmentos, para revisar qué entra
```

Antes de confirmar, `git diff` muestra lo que no está preparado y `git diff --staged` lo que sí. `git diff HEAD` compara el directorio de trabajo con la última confirmación.

```bash
git commit -m "feat: add the first page"
```

`git commit -am "..."` prepara y confirma solo archivos ya versionados; no añade archivos nuevos. `git commit --amend` reescribe la última confirmación: sirve para corregir el mensaje o añadir un archivo olvidado, pero no debe usarse sobre una confirmación ya publicada y compartida.

Para deshacer un `add` sin tocar el archivo:

```bash
git restore --staged archivo.txt
# equivalente clásico: git reset HEAD archivo.txt
```

## Leer el histórico

```bash
git log --oneline --graph --decorate --all
git log -5 --stat
git show <commit>
git log -p -- archivo.txt
```

`--oneline` resume cada confirmación; `--graph` dibuja las ramas; `--decorate` muestra etiquetas y referencias; `--all` incluye todas las ramas. `git show` enseña una confirmación concreta con su diferencia, y `git log -p -- archivo` sigue la historia de un archivo.

Los alias ahorran tecleo y se guardan en la configuración global:

```bash
git config --global alias.lg "log --oneline --graph --decorate --all"
git lg
```

## Ignorar archivos

`.gitignore` se escribe en la raíz del repositorio y contiene patrones, uno por línea. Las rutas son relativas a la carpeta donde está el archivo; `#` abre un comentario; `!` niega un patrón anterior.

```gitignore
# Build y dependencias
bin/
obj/
node_modules/

# Configuración local y secretos
.env
*.local

# Temporales
*.log
*.tmp
```

`git check-ignore -v ruta` dice qué regla ignora un archivo. Los archivos ya versionados no dejan de estarlo por añadirlos a `.gitignore`: hay que sacarlos con `git rm --cached`. Una carpeta vacía no existe para Git; si hace falta conservarla, se usa un `.gitkeep` vacío.

Nunca se ignoran secretos que ya están en el histórico: si una credencial se confirmó, hay que rotarla y limpiar la historia; añadirla a `.gitignore` solo evita el siguiente commit.

## Remotos

Un remoto es un repositorio con el que se sincroniza el local. `origin` es el nombre convencional del principal.

```bash
git remote -v
git remote add origin https://ejemplo.com/repo.git
git remote set-url origin git@ejemplo.com:usuario/repo.git
```

La diferencia entre `fetch` y `pull` es importante:

- `git fetch` descarga las referencias y los objetos, pero no toca el directorio de trabajo. Deja los cambios en `origin/main` para revisarlos.
- `git pull` hace `fetch` y después integra: por defecto con una fusión, o con `--rebase` si se quiere la historia lineal.

```bash
git fetch origin
git log HEAD..origin/main --oneline   # qué hay en el remoto que no tengo
git pull --rebase
git push -u origin main
```

`-u` deja la rama local enlazada con la remota, así los siguientes `push` y `pull` no necesitan argumentos. `git branch -vv` muestra el enlace y si hay commits por delante o por detrás.

Para practicar sin un servidor, se puede crear un repositorio desnudo, que solo guarda objetos y referencias:

```bash
git init --bare remoto.git
git remote add origin ../remoto.git
git push -u origin main
```

Un repositorio desnudo no tiene directorio de trabajo ni `.git` interno; es el equivalente a lo que hay en un servidor.

## Resumen del flujo

```bash
git status                 # ver dónde estoy
git add -A                 # elegir qué entra
git commit -m "..."        # guardar
git fetch                  # mirar qué hay fuera
git pull --rebase          # integrar
git push                   # publicar
```

## Para practicar

1. Crea un repositorio con `git init`, añade dos archivos y confirma cada uno en un *commit* distinto.
2. Modifica un archivo, prepáralo y comprueba la diferencia entre `git diff` y `git diff --staged`.
3. Añade un `.gitignore` que excluya un archivo temporal y comprueba con `git check-ignore -v`.
4. Crea un repositorio desnudo, añádelo como `origin` y sube la rama con `git push -u origin main`.
5. Haz un cambio en otra copia, tráelo con `git fetch` y revísalo antes de integrarlo con `git pull`.
