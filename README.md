# Biblioteca técnica

Visor local del contenido IT que he ido estudiando y documentando. Lee los Markdown de los repositorios de cursos y genera un sitio navegable con un solo árbol de módulos, búsqueda global, filtros por materia, migas y enlaces a apuntes y guías. La composición sigue el lenguaje editorial de la web personal, adaptado a la lectura y a la navegación del visor. No guarda contenido propio: cada build lee las fuentes y `dist/` es una copia local de los recursos que se regenera.

**Privado.** No se publica. La salida (`dist/`) no se versiona. **Licencia:** MIT, copyright 2026 Lorenzo Lanuza Arellano; el texto está en [`LICENSE`](LICENSE).

## Fuentes

| Etiqueta | Qué aporta |
|---|---|
| `ciclo-asir` | 11 módulos, 43 apuntes y 32 guías |
| `curso-ciberseguridad` | 6 módulos |

Las rutas no están en el código: `config/fuentes.toml` nombra cada fuente por etiqueta y el visor pide su raíz a `privatenotes/scripts/repos.py`, que lee `workspace/rutas.env`. Añadir otro curso es añadir una fila en la configuración y su etiqueta en el registro; no se inventa contenido.

La portada no separa por cursos: cada módulo es un item, con su categoría, sus apuntes y sus guías. El lateral agrupa por categorías plegables, con icono de categoría y de módulo. Quedan fuera las fuentes que no son contenido de estudio.

## Uso

```bash
python3 scripts/visor.py build          # genera dist/
python3 scripts/visor.py serve          # genera y sirve en http://127.0.0.1:8001/
python3 scripts/visor.py serve --vigilar --abrir
```

- El servicio de usuario `biblioteca-tecnica` sirve en `http://127.0.0.1:8001/`. No hay un segundo visor: el `8000` quedó libre al retirar el antiguo.
- `serve --vigilar` reconstruye al detectar cambios en cualquier `.md` de las fuentes configuradas, en la plantilla, en los estilos, en el guion o en la configuración.
- Solo usa la biblioteca estándar de Python 3.11 o posterior. Sin CDN, sin telemetría y sin red.
- `build` termina con error si un enlace interno no resuelve.

## Estructura

| Ruta | Para qué |
|---|---|
| `config/fuentes.toml` | Fuentes por etiqueta, presentación y categorías |
| `scripts/visor.py` | Build, servidor, vigilancia y composición del contenido |
| `scripts/verificar.py` | Verificación de módulos, búsqueda, enlaces y `dist/` |
| `sitio/plantilla.html` | Esqueleto de cada página; marcadores `{{...}}` |
| `sitio/estilo.css` | Estilos y tokens de la identidad |
| `sitio/app.js` | Progreso, búsqueda, filtros, navegación y plazos |
| `sitio/marca.svg`, `sitio/marca-tile.svg` | Marca personal del visor |
| `sitio/iconos/` | Iconos de categorías y módulos |
| `servicio/biblioteca-tecnica.service` | Unidad de usuario del servicio |
| `dist/` | Salida generada; ignorada por Git |

`dist/index.html` es la portada del contenido. Cada módulo vive en `dist/<fuente>/<modulo>/` y comparte el lateral, la búsqueda, los filtros y los recursos de `dist/_sitio/`.

## Verificación

```bash
python3 scripts/verificar.py

CHECK_LINKS="$(python3 ~/Repositorios/privatenotes/scripts/repos.py campo core ruta)/actions/check-links/check_links.py"
python3 "$CHECK_LINKS" . --skip dist --skip sitio
python3 "$CHECK_LINKS" dist
```

`verificar.py` comprueba los 11 módulos, 43 apuntes y 32 guías de ASIR, los 6 módulos del curso, que la búsqueda encuentra un apunte y una guía de cada fuente, que `dist/` se regenera igual, que los enlaces internos resuelven y que `dist/` no se versiona.

El repositorio es privado y no tiene CI. La barrera de secretos es el hook local de Gitleaks:

```bash
~/Repositorios/privatenotes/scripts/instalar-hooks.sh --apply biblioteca-tecnica
~/Repositorios/privatenotes/scripts/instalar-hooks.sh --check biblioteca-tecnica
```

## Servicio

```bash
mkdir -p ~/.config/systemd/user
cp servicio/biblioteca-tecnica.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now biblioteca-tecnica
```

```bash
systemctl --user status biblioteca-tecnica
systemctl --user restart biblioteca-tecnica
journalctl --user -u biblioteca-tecnica -n 20
```

## Licencia

MIT. Copyright (c) 2026 Lorenzo Lanuza Arellano. El texto está en [`LICENSE`](LICENSE).
