# Iconos del visor

Glifos de categoría y de módulo que no trae su repositorio de origen.

Formato: 64×64, `rx=16`, fondo navy con degradado (`#07131e` → `#0e2a47`), borde cian sólido de 2 px (`#38bdf8`) y glifo blanco relleno (`#f8fafc`) en una caja de 44×44, igual que los iconos de los módulos del curso y del ciclo.

La geometría es la de Material Design Icons (Apache 2.0) y coincide con la del tema de iconos de la marca y con la de los iconos de módulo de los repositorios de los cursos: el mismo dibujo se repite en el escritorio, en los README y en el visor, sin variantes por superficie.

El dibujo se mide por su caja de tinta, no por la rejilla. Todos los glifos ocupan 20 de las 24 unidades de la rejilla —el 83 % de la caja de 44— en su lado mayor, estén dibujados sobre la rejilla de 24 o más pequeños, y quedan centrados en ella. La corrección va en un grupo interno con `translate` y `scale` propio de cada icono, de modo que la receta externa sigue siendo la misma para todos y el glifo se lee del grupo sin perderla. Los dos que se dibujan a línea y no rellenos, `identidad` y `red`, compensan en ese grupo el `stroke-width` para que el trazo conserve las 2,5 y 2 unidades con que se dibujaron.

## Uso

- **Baldosa completa desde 32 px.** En las tarjetas y en la portada se usa el SVG tal cual.
- **Glifo a una tinta por debajo de 32 px.** El árbol y los filtros no muestran la baldosa: el visor extrae el dibujo del grupo escalado y lo pinta con el color del texto en un `viewBox` de 24, como los iconos simbólicos del tema. Así el icono se lee a 16-20 px y cambia con el tema claro u oscuro.

Un icono de módulo del repositorio de origen tiene prioridad sobre estos glifos. El orden es: `<fuente>/assets/iconos/<clave>.svg`, `<fuente>/assets/iconos/<prefijo>.svg` (lo que hay antes del primer guion, como `5021` o `sad`), el glifo de `ICONOS_MODULO` para la clave o, si no, para ese prefijo y, como último recurso, `documento.svg`.

Para cambiar la receta común —fondo, borde, tamaño del glifo— se editan todos los archivos a la vez.
