# Guía para agentes: biblioteca-tecnica

Visor local del contenido IT de los cursos. Repositorio privado: no se enlaza ni se copia desde repos públicos. Sin CI: la barrera de secretos es el hook local de Gitleaks, obligatorio en cada clon.

## Propósito y límites

- Lee las fuentes configuradas y genera un sitio navegable en `dist/`. No guarda contenido propio ni versiona contenido; `dist/` es una copia local de los recursos que se regenera.
- La portada es un índice de contenido, no un catálogo de cursos: cada módulo es un item, con su categoría, sus apuntes y sus guías. El lateral agrupa por categorías plegables, con icono de categoría y de módulo. El curso solo identifica la fuente.
- No publica, no sirve fuera de `127.0.0.1` y no usa red, CDN ni telemetría.
- Este repo es el dueño del visor que vivía en `curso-ciberseguridad/sitio/` y `scripts/sitio.py`; el curso ya no conserva plantilla, estilos ni lógica del visor.
- Quedan fuera las fuentes que no son contenido de estudio.

## Estructura

```
config/fuentes.toml     fuentes por etiqueta, presentación y categorías
scripts/visor.py        build, servidor, vigilancia y composición
scripts/verificar.py    verificación de módulos, búsqueda y dist/
sitio/                  plantilla, estilos propios, iconos y guion
_identidad/             paquete de identidad consumido; no se retoca
servicio/               unidad de usuario de systemd
dist/                   salida generada; no se versiona
```

Cada fuente se resuelve por etiqueta con `privatenotes/scripts/repos.py` y `workspace/rutas.env`. No escribas una ruta de repo en el código ni en la configuración: añade o cambia la fila del registro.

`_identidad/` es la copia del paquete de la web personal, traída por etiqueta y comprobada con sus huellas en `verificar.py`; se copia entera a `dist/_identidad/` porque la copia es la distribución. `identidad.css`, la cabecera, el pie y la pestaña vienen de ahí: en `sitio/estilo.css` solo queda la distribución del visor —marco fijo, lateral, contenido, TOC— y el nombre `--estado-*` como alias de los tokens del paquete. Un color nuevo no se escribe aquí: se sube al paquete. La única excepción es el bloque `@media print`, que cambia a papel con sus propios valores. El shell mantiene su margen de 24 px y su pie de móvil de 56 px sin «Volver arriba»: es distribución, no piel.

## Fuentes y estructura de los cursos

- `ciclo-asir`: módulos en `primer-curso/` y `segundo-curso/`, con `teoria/` y `ejercicios/`. Se esperan 12 módulos, 58 apuntes y 36 guías.
- `curso-ciberseguridad`: módulos `5021`–`5026` en la raíz, con `teoria/` y `ejercicios/`. Se esperan 6 módulos.
- `apuntes`: módulos por carpeta con `README.md` y los apuntes al mismo nivel; `Azure` agrupa nueve módulos. Se esperan 14 módulos y 72 apuntes.
- La configuración declara `estructura` (`curso`, `asir` o `apuntes`), las raíces de los módulos, los conteos esperados, el nombre corto de cada módulo (`nombres`) y las categorías de las tarjetas. Un curso nuevo se añade por configuración; no se crea contenido para rellenar el visor.
- Las fuentes que no viven en el contenedor se declaran con `local` y se resuelven en `$XDG_CONFIG_HOME/privatenotes/fuentes.locales`, que no se versiona. La raíz del contenido no se escribe en la configuración y el contenido no se copia al repositorio.
- Los prefijos numéricos de los módulos del curso son internos: no se muestran en la navegación ni en las tarjetas.
- El `README.md` de cada módulo es la introducción al tema y se publica como `index.html`: contenido propio, no un índice de enlaces. El índice de módulos ya está en el lateral.
- No se reproduce material del curso: ni portada, ni logotipo, ni aviso legal, ni datos del profesorado, ni el nombre de la plataforma que lo imparte. Las figuras se incluyen solo cuando explican algo; una imagen de relleno o promocional no entra.

## Comandos

```bash
python3 scripts/visor.py build
python3 scripts/visor.py serve [--puerto 8001] [--vigilar] [--abrir]
python3 scripts/verificar.py

mkdir -p ~/.config/systemd/user
cp servicio/biblioteca-tecnica.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now biblioteca-tecnica
```

El servicio de usuario es `biblioteca-tecnica` y escucha en `127.0.0.1:8001`. El `8000` no lo usa ningún visor.

## Verificación

Antes de dar un lote por cerrado:

```bash
python3 scripts/verificar.py

CHECK_LINKS="$(python3 ~/Repositorios/privatenotes/scripts/repos.py campo core ruta)/actions/check-links/check_links.py"
python3 "$CHECK_LINKS" . --skip dist --skip sitio
python3 "$CHECK_LINKS" dist

~/Repositorios/privatenotes/scripts/instalar-hooks.sh --check biblioteca-tecnica
```

`verificar.py` exige los conteos de las fuentes, que las fuentes no citen al proveedor del curso ni conserven cabeceras de curso, que la búsqueda encuentre un apunte de cada fuente y una guía donde la haya, que `dist/` sea reproducible, que los enlaces internos resuelvan y que `dist/` no esté versionado. `check-links` revisa los enlaces relativos del repositorio y los del HTML generado. Si falla un conteo, no cambies el número de la configuración: revisa la fuente.

## Privacidad y licencia

- No hay contenido versionado de los cursos; `dist/` se reconstruye desde las fuentes.
- No enlaces este repositorio desde contenido público ni copies sus rutas o configuración a un repo público.
- Licencia MIT, copyright 2026 Lorenzo Lanuza Arellano. El titular se mantiene igual en `LICENSE`, `README.md` y este archivo.

## Scopes de commit

`visor`, `config`, `servicio`, `repo`. Formato: `type(scope): imperative summary in English`. Commit y push requieren autorización explícita por lote.
