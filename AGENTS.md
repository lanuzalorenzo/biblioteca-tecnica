# Guía para agentes: biblioteca-tecnica

Biblioteca técnica: el contenido versionado en `contenido/` y el visor que lo convierte en un sitio estático. El repositorio es privado por ahora y se prepara para publicarse; es dueño del contenido publicable y no lee fuentes externas.

## Propósito y límites

- `contenido/` es la fuente de verdad. El visor genera `dist/` y no se versiona.
- Solo entra material propio y publicable: teoría y notas reescritas. Quedan fuera los enunciados y prácticas de los cursos, el seguimiento de entregas, los datos de acceso a plataformas del centro y cualquier dato personal o de terceros.
- No se reproduce material de terceros: ni portada, ni logotipo, ni aviso legal, ni datos del profesorado, ni el nombre de la plataforma que imparte el curso.
- El destino es un sitio público y estático. Mientras el repositorio sea privado no hay despliegue, y el contenido no debe salir de él hasta estar adaptado.
- No usa red, CDN ni telemetría en el build ni en el sitio.

## Estructura

```
contenido/              Markdown y recursos publicados, por fuente
config/fuentes.toml     fuentes dentro del repositorio, presentación y categorías
scripts/visor.py        build, servidor, vigilancia y composición
scripts/verificar.py    verificación de módulos, búsqueda, enlaces y dist/
sitio/                  plantilla, estilos propios, iconos y guion
_identidad/             paquete de identidad consumido; no se retoca
dist/                   salida generada; no se versiona
```

Cada fuente declara su `ruta` relativa al repositorio. No se escriben rutas del equipo ni se resuelven etiquetas externas.

## Contenido

- `asir` publica teoría y el README de cada módulo; las prácticas quedan fuera.
- `apuntes` publica los doce módulos de Azure, con su README y su nota.
- El curso de especialización se incorpora módulo a módulo cuando el material esté cerrado; mientras tanto, su material vivo no entra.
- Los prefijos numéricos de los módulos son internos: no se muestran en la navegación ni en las tarjetas.
- El `README.md` de cada módulo es la introducción al tema y se publica como `index.html`.
- Si un enlace apunta a material que no se publica, se desenvuelve en la copia: se conserva el texto y se retira el enlace. Un enlace roto no se publica.

## Comandos

```bash
python3 scripts/visor.py build
python3 scripts/visor.py serve [--puerto 8001] [--vigilar] [--abrir]
python3 scripts/verificar.py
```

## Verificación

Antes de dar un lote por cerrado:

```bash
python3 scripts/verificar.py
```

`verificar.py` exige los conteos de las fuentes, que la búsqueda encuentre un apunte de cada fuente, que `dist/` sea reproducible, que los enlaces internos resuelvan y que `dist/` no esté versionado. El CI añade Gitleaks sobre el historial completo y `check-links` sobre el repositorio —sin `sitio/`, que es plantilla— y sobre `dist/`. Si falla un conteo, no cambies el número: revisa el contenido o el alcance de la fuente.

## Publicación

- El sitio se publica con GitHub Pages desde el workflow: build en CI y artefacto de `dist/`.
- GitHub Pages fija las cabeceras de respuesta, incluida `Server`; no se presenta como control propio.
- Cuando el repositorio sea público, todo cambio entrará por rama y pull request, con `main` protegida y los checks obligatorios. Mientras sea privado, el flujo es el de un repositorio privado.
- Permisos mínimos en cada workflow. Gitleaks sobre el historial completo. Dependabot para GitHub Actions, con auto-merge de parche y minor cuando los checks pasan.
- Un lote de más de un archivo, o que toque reglas, CI, seguridad o publicación, pasa por el revisor de cambios antes de commitear.

## Licencia

MIT, copyright 2026 Lorenzo Lanuza Arellano. El titular se mantiene igual en `LICENSE`, `README.md` y este archivo.

## Scopes de commit

`visor`, `config`, `content`, `ci`, `repo`. Formato: `type(scope): imperative summary in English`. Commit y push requieren autorización explícita por lote.
