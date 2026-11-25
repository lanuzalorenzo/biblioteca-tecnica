# Remotos y alojamiento

Un remoto es otro repositorio con el que se sincroniza el local. No es un servidor especial: suele ser un repositorio desnudo, sin directorio de trabajo, que sirve para coordinar al equipo y como copia de seguridad. Entender cómo se nombran, cómo se sincronizan y cómo se autentican evita la mayor parte de los sustos al trabajar con GitHub, GitLab o un servidor propio.

## Ramas remotas

Cuando se clona un repositorio, Git crea una rama local y una referencia remota:

```text
origin/main   ->  última confirmación conocida del remoto
main          ->  rama local, que puede ir por delante o por detrás
```

`git branch -r` lista las ramas remotas; `git branch -vv` muestra la rama local, su remoto y si hay commits pendientes de subir o bajar. `git fetch` actualiza las referencias `origin/*` sin tocar el directorio de trabajo.

Una rama local puede seguir a una remota:

```bash
git switch --track origin/feature
# o, si ya existe la local:
git branch --set-upstream-to=origin/main main
```

Con el seguimiento configurado, `git pull` y `git push` saben contra qué rama trabajar sin argumentos.

## Sincronizar

```bash
git fetch origin          # descargar sin integrar
git pull --rebase         # descargar e integrar sobre la punta local
git push origin main      # subir la rama local
git push -u origin main   # subir y dejar el seguimiento configurado
```

`pull` es `fetch` más una integración. La integración puede ser una fusión o un rebase; en ramas de trabajo personales, `--rebase` deja una historia más limpia y evita la confirmación de fusión. En ramas compartidas, la fusión es más segura.

Si el `push` se rechaza porque el remoto tiene commits nuevos, no se fuerza: se hace `pull`, se resuelven los conflictos y se vuelve a subir.

## Gestionar remotos

```bash
git remote -v
git remote add upstream https://ejemplo.com/original.git
git remote rename origin viejo
git remote set-url origin git@ejemplo.com:usuario/repo.git
git remote remove upstream
```

Tener varios remotos es normal en un fork: `origin` apunta a la copia propia y `upstream` al repositorio original. Se descarga del original y se sube a la copia:

```bash
git fetch upstream
git switch main
git merge upstream/main
git push origin main
```

Los `push` y `pull` aceptan el remoto y la rama como argumentos, así que se puede elegir cada vez.

## Credenciales

Hay dos formas de autenticarse:

- **HTTPS**: usuario y un token de acceso personal. La contraseña de la cuenta no sirve en GitHub, GitLab ni Bitbucket. El token se guarda con un ayudante de credenciales (`git config --global credential.helper store` o el gestor del sistema). Nunca se escribe el token en la URL ni en un archivo versionado.
- **SSH**: una clave pública registrada en el servicio y la privada en el equipo. Se genera con `ssh-keygen -t ed25519 -C "correo"`, se añade la pública al servicio y se prueba con `ssh -T git@github.com`. El agente (`ssh-add`) evita repetir la frase de paso.

SSH es cómodo para uso diario; HTTPS con token es útil en entornos donde no se pueden gestionar claves. En ambos casos, el secreto no se versiona.

## Migrar un repositorio de un servicio a otro

La forma completa conserva ramas, etiquetas y referencias:

```bash
git clone --mirror https://origen/repo.git
cd repo.git
git remote set-url origin https://destino/repo.git
git push --mirror
```

`--mirror` copia todas las referencias, incluidas las ramas remotas y las etiquetas. Si solo se quieren las ramas y las etiquetas normales:

```bash
git remote add destino https://destino/repo.git
git push destino --all
git push destino --tags
```

Después se actualiza el remoto del clon de trabajo y se comprueba que el histórico y las etiquetas coinciden.

## Git LFS

Git guarda instantáneas completas de cada versión. Con archivos binarios grandes —diseños, grabaciones, modelos— el repositorio crece muy rápido. Git LFS (Large File Storage) sustituye el archivo por un puntero y guarda el contenido en un almacenamiento aparte.

```bash
git lfs install
git lfs track "*.psd"
git add .gitattributes
git add diseño.psd
git commit -m "docs: add the design source"
git push
```

`git lfs track` escribe una regla en `.gitattributes`; esa regla sí se versiona. `git lfs ls-files` lista los archivos gestionados. Al clonar, hace falta `git lfs install` para que los archivos se descarguen; sin él, se obtienen los punteros.

Los servicios suelen cobrar por el almacenamiento y el ancho de banda de LFS. No se usa para texto ni para binarios pequeños: añade complejidad y dependencia del servicio. Para archivos que cambian mucho y no necesitan histórico, a veces es mejor un almacenamiento externo.

### Bloqueos

LFS permite bloquear un archivo para que nadie más lo edite a la vez:

```bash
git lfs lock diseño.psd
git lfs locks
git lfs unlock diseño.psd
```

Es útil en binarios que no se pueden fusionar, como un archivo de diseño o una hoja de cálculo.

## Para practicar

1. Clona un repositorio, añade un remoto `upstream` y comprueba `git remote -v`.
2. Crea una rama local que siga a una remota y sube un cambio con `push`.
3. Fuerza un rechazo de `push` desde otra copia, resuelve con `pull --rebase` y vuelve a subir.
4. Migra un repositorio de prueba con `clone --mirror` y `push --mirror`; comprueba ramas y etiquetas.
5. Instala Git LFS, rastrea un tipo de archivo, confirma y comprueba con `git lfs ls-files`.
