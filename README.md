<img src="assets/iconos/biblioteca-tecnica.svg" width="64" alt="Biblioteca técnica">

# Biblioteca técnica

Biblioteca personal de apuntes de informática: módulos de sistemas, redes, datos, desarrollo, seguridad, empleo y Azure, con notas de Git, Angular, ASP.NET, contenedores y testing que voy completando, convertidos en un sitio navegable con búsqueda, filtros por materia, migas y un árbol de módulos. El contenido lo escribo yo; el visor lo convierte a HTML estático sin red, sin CDN y sin telemetría.

**Sitio:** pendiente de publicación. El destino previsto es <https://lanuzalorenzo.github.io/biblioteca-tecnica/>.

## Contenido

- **12 módulos y 58 apuntes** de sistemas, redes, datos, desarrollo, seguridad y empleo.
- **Azure:** 12 módulos y 12 notas.
- **Git:** 1 módulo y 9 notas.
- **Angular:** 1 módulo y 12 notas.
- **ASP.NET Core MVC:** 1 módulo y 41 notas.
- **Contenedores:** 1 módulo y 14 notas.
- **Testing .NET:** 1 módulo y 14 notas.

En total, 29 módulos y 160 apuntes. Cada módulo es una carpeta de `contenido/` con su `README.md` y sus notas.

Solo entra material propio y publicable. Quedan fuera los enunciados y las prácticas de los cursos, el seguimiento de entregas y los datos de acceso a las plataformas del centro. No se reproduce material de terceros: ni portadas, ni logotipos, ni avisos legales, ni datos del profesorado.

## Uso

```bash
python3 scripts/visor.py build          # genera dist/
python3 scripts/visor.py serve          # sirve en http://127.0.0.1:8001/
python3 scripts/visor.py serve --vigilar --abrir
```

- Solo usa la biblioteca estándar de Python 3.11 o posterior.
- `serve --vigilar` reconstruye al detectar cambios en cualquier `.md`, en la plantilla, en los estilos, en el guion o en la configuración.
- `build` termina con error si un enlace interno no resuelve.

## Estructura

| Ruta | Para qué |
|---|---|
| `contenido/` | Un módulo por carpeta con su README, sus notas y sus recursos; es la fuente de verdad |
| `config/fuentes.toml` | Fuente única, presentación y categorías |
| `scripts/visor.py` | Build, servidor, vigilancia y composición del contenido |
| `scripts/verificar.py` | Verificación de módulos, búsqueda, enlaces y `dist/` |
| `sitio/plantilla.html` | Esqueleto de cada página; marcadores `{{...}}` |
| `sitio/estilo.css` | Distribución del visor: marco fijo, lateral, contenido y TOC |
| `sitio/app.js` | Progreso, búsqueda, filtros y navegación |
| `_identidad/` | Paquete de identidad consumido: CSS y tile; no se retoca |
| `sitio/iconos/` | Iconos de categorías y módulos |
| `dist/` | Salida generada; ignorada por Git |

`dist/index.html` es la portada del contenido. Cada módulo vive en `dist/<modulo>/` y comparte el lateral, la búsqueda, los filtros y los recursos de `dist/_sitio/`; la cabecera y el pie se componen en `sitio/plantilla.html`, y los estilos y el tile vienen de `dist/_identidad/`.

## Publicación

El repositorio sigue privado mientras se termina la adaptación del contenido. Cuando esté listo, el sitio se publicará con GitHub Pages desde un workflow: el build se ejecutará en CI y se subirá el artefacto de `dist/`. El sitio será estático y no tendrá autenticación ni contenido privado. GitHub Pages fija las cabeceras HTTP de respuesta, incluida `Server`; por eso no se presenta el ocultado de cabeceras como un control propio.

## Verificación

```bash
python3 scripts/verificar.py
```

Comprueba que no bajen de 29 módulos y 160 apuntes —hoy 12/58 de la base, 12/12 de Azure, 1/9 de Git, 1/12 de Angular, 1/41 de ASP.NET, 1/14 de contenedores y 1/14 de testing—, que la búsqueda encuentra un apunte, que `dist/` se regenera igual, que los enlaces internos resuelven y que `dist/` no se versiona. Al publicar, el CI añadirá Gitleaks sobre el historial completo y la comprobación de enlaces relativos del repositorio y del HTML generado.

## Línea base

Cuando el repositorio pase a público, todo cambio entrará por rama y pull request, con `main` protegida y los checks obligatorios. La línea base se aplicará al publicar: permisos mínimos en cada workflow, Gitleaks sobre el historial completo y Dependabot para GitHub Actions, con auto-merge de parche y minor cuando los checks pasen.

## Licencia

MIT. Copyright (c) 2026 Lorenzo Lanuza Arellano. El texto está en [`LICENSE`](LICENSE).
