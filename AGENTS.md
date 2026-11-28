# Guía para agentes: biblioteca-tecnica

Biblioteca técnica: el contenido versionado en `contenido/` y el visor que lo convierte en un sitio estático. El repositorio es público desde el 2026-11-25; es dueño del contenido publicable y no lee fuentes externas.

## Propósito y límites

- `contenido/` es la fuente de verdad. El visor genera `dist/` y no se versiona.
- Solo entra material propio y publicable: teoría y notas reescritas. Quedan fuera los enunciados y prácticas de los cursos, el seguimiento de entregas, los datos de acceso a plataformas del centro y cualquier dato personal o de terceros.
- No se reproduce material de terceros: ni portada, ni logotipo, ni aviso legal, ni datos del profesorado, ni el nombre de la plataforma que imparte el curso.
- El destino es un sitio público y estático: solo se publica material adaptado.
- No usa red, CDN ni telemetría en el build ni en el sitio.

## Estructura

```
contenido/<modulo>/     README, notas y recursos del módulo
config/fuentes.toml     fuente única, presentación y categorías
scripts/visor.py        build, servidor, vigilancia y composición
scripts/verificar.py    verificación de módulos, búsqueda, enlaces y dist/
sitio/                  estilos propios, iconos y guion
_identidad/             paquete de identidad consumido; no se retoca
dist/                   salida generada; no se versiona
```

La fuente es `contenido/`; no hay rutas del equipo ni etiquetas externas.

El esqueleto de página —documento, cabecera, pie y navegación— sale de `_identidad/`; el visor solo aporta el cuerpo, los metadatos, la sección activa (`biblioteca`) y los scripts. `sitio/` no lleva plantilla propia ni enlaces de nav.

## Contenido

- Cada módulo vive en `contenido/<modulo>/` con su `README.md` y sus notas. Hoy hay módulos de sistemas, redes, datos, desarrollo, seguridad, empleo y Azure, con Git, Angular, ASP.NET, .NET MAUI, contenedores y testing; las prácticas y el material de curso sin adaptar quedan fuera.
- Los módulos no declaran estado de artefacto; el README dice el alcance y lo pendiente. El estado del trabajo vive fuera del repositorio.
- No hay fuentes por curso: la única fuente es `contenido/` y la categoría la pone el visor en las tarjetas y en el lateral.
- El material de curso que aún no está adaptado se queda fuera; entra módulo a módulo cuando esté cerrado.
- Los prefijos numéricos de los módulos son internos: no se muestran en la navegación ni en las tarjetas.
- El `README.md` de cada módulo es la introducción al tema y se publica como `index.html`.
- Si un enlace apunta a material que no se publica, se desenvuelve en la copia: se conserva el texto y se retira el enlace. Un enlace roto no se publica.

## Comandos

```bash
python3 scripts/visor.py build
python3 scripts/visor.py serve [--puerto 8001] [--vigilar] [--abrir]
python3 scripts/verificar.py
scripts/actualizar-identidad.sh   # solo si hay que subir de versión el paquete
```

## Verificación

Antes de dar un lote por cerrado:

```bash
python3 scripts/verificar.py
```

`verificar.py` exige un mínimo de 34 módulos y 208 apuntes, que la búsqueda encuentre un apunte, que `dist/` sea reproducible, que los enlaces internos resuelvan y que `dist/` no esté versionado. El mínimo es del total: añadir módulos no obliga a tocar la configuración, y el desglose por grupo no lo comprueba el script. El CI añade Gitleaks sobre el historial completo y `check-links` sobre el repositorio —sin `sitio/`, que no tiene HTML publicado— y sobre `dist/`. Si falla un conteo, no cambies el número: revisa el contenido.

## Publicación

- El sitio se sirve con GitHub Pages desde `.github/workflows/sitio.yml`: build en CI y artefacto de `dist/`.
- GitHub Pages fija las cabeceras de respuesta, incluida `Server`; no se presenta como control propio.
- Todo cambio entra por rama y pull request, con `main` protegida y los checks obligatorios.
- La línea base: permisos mínimos en cada workflow, Gitleaks sobre el historial completo y Dependabot para GitHub Actions, con auto-merge de parche y minor cuando los checks pasen.
- Un lote de más de un archivo, o que toque reglas, CI, seguridad o publicación, pasa por el revisor de cambios antes de commitear.
- El CI comprueba que `_identidad/VERSION` es la última etiqueta `identidad-v*` y falla si la copia está atrasada; el trabajo `identidad` abre la PR de actualización cada semana.

## Licencia

MIT, copyright 2026 Lorenzo Lanuza Arellano. El titular se mantiene igual en `LICENSE`, `README.md` y este archivo.

## Scopes de commit

`visor`, `config`, `content`, `site`, `ci`, `repo`. Formato: `type(scope): imperative summary in English`. Commit y push requieren autorización explícita por lote.
