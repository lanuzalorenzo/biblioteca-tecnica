# Guía para agentes: visor-temario

Visor local del contenido IT de los cursos. Repositorio privado: no se enlaza ni se copia desde repos públicos. Sin CI: la barrera de secretos es el hook local de Gitleaks, obligatorio en cada clon.

## Propósito y límites

- Lee las fuentes configuradas y genera un sitio navegable en `dist/`. No guarda contenido propio ni versiona contenido; `dist/` es una copia local de los recursos que se regenera.
- La portada es un índice de contenido, no un catálogo de cursos: cada módulo es un item, con su categoría, sus apuntes y sus guías. El curso solo identifica la fuente.
- No publica, no sirve fuera de `127.0.0.1` y no usa red, CDN ni telemetría.
- Este repo es el dueño del visor que vivía en `curso-ciberseguridad/sitio/` y `scripts/sitio.py`. Mientras la fase 2 no esté cerrada, el curso conserva una copia pendiente de retirar; no se mantiene como segunda fuente de verdad.
- Quedan fuera las fuentes que no son contenido de estudio.

## Estructura

```
config/fuentes.toml     fuentes por etiqueta, presentación y categorías
scripts/visor.py        build, servidor, vigilancia y composición
scripts/verificar.py    verificación de módulos, búsqueda y dist/
sitio/                  plantilla, estilos y guion del navegador
dist/                   salida generada; no se versiona
```

Cada fuente se resuelve por etiqueta con `privatenotes/scripts/repos.py` y `workspace/rutas.env`. No escribas una ruta de repo en el código ni en la configuración: añade o cambia la fila del registro.

## Fuentes y estructura de los cursos

- `ciclo-asir`: módulos en `primer-curso/` y `segundo-curso/`, con `teoria/` y `ejercicios/`. Se esperan 11 módulos, 43 apuntes y 32 guías.
- `curso-ciberseguridad`: módulos `5021`–`5026` en la raíz, con `teoria/` y `ejercicios/`. Se esperan 6 módulos.
- La configuración declara `estructura` (`curso` o `asir`), las raíces de los módulos, los conteos esperados y las categorías de las tarjetas. Un curso nuevo se añade por configuración; no se crea contenido para rellenar el visor.
- Los prefijos numéricos de los módulos del curso son internos: no se muestran en la navegación ni en las tarjetas.

## Comandos

```bash
python3 scripts/visor.py build
python3 scripts/visor.py serve [--puerto 8001] [--vigilar] [--abrir]
python3 scripts/verificar.py
```

El servicio de usuario es `visor-temario` y escucha en `127.0.0.1:8001`. El `8000` pertenece al visor antiguo del curso hasta que se retire.

## Verificación

Antes de dar un lote por cerrado:

```bash
python3 scripts/verificar.py

CHECK_LINKS="$(python3 ~/Repositorios/privatenotes/scripts/repos.py campo core ruta)/actions/check-links/check_links.py"
python3 "$CHECK_LINKS" . --skip dist --skip sitio
python3 "$CHECK_LINKS" dist

~/Repositorios/privatenotes/scripts/instalar-hooks.sh --check visor-temario
```

`verificar.py` exige los conteos de las fuentes, que la búsqueda encuentre un apunte y una guía de cada curso, que `dist/` sea reproducible, que los enlaces internos resuelvan y que `dist/` no esté versionado. `check-links` revisa los enlaces relativos del repositorio y los del HTML generado. Si falla un conteo, no cambies el número de la configuración: revisa la fuente.

## Privacidad y licencia

- No hay contenido versionado de los cursos; `dist/` se reconstruye desde las fuentes.
- No enlaces este repositorio desde contenido público ni copies sus rutas o configuración a un repo público.
- Licencia MIT, copyright 2026 Lorenzo Lanuza Arellano. El titular se mantiene igual en `LICENSE`, `README.md` y este archivo.

## Scopes de commit

`visor`, `config`, `servicio`, `repo`. Formato: `type(scope): imperative summary in English`. Commit y push requieren autorización explícita por lote.
