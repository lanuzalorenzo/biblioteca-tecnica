# Iconos

Un icono para el repositorio y, en el encabezado de su `README.md`, uno por módulo. De momento solo tienen icono el repositorio y SAD; los demás módulos usan el título sin imagen hasta que se dibujen.

Formato: 64×64, `rx=16`, fondo navy con degradado (`#07131e` → `#0e2a47`), borde cian sólido de 2 px (`#38bdf8`) y glifo blanco relleno (`#f8fafc`) en una caja de 44×44. El icono lleva su propio fondo, así que se lee igual sobre una barra clara y sobre una oscura. Sin texto y sin color por módulo: todos son navy y cian, y se distinguen por el dibujo.

| Archivo | Dibujo |
|---|---|
| `ciclo-asir.svg` | Libro abierto |
| `sad.svg` | Candado |

## Uso

En el `README.md` de un módulo —está dos carpetas por debajo de la raíz—, antes del título:

```html
<img src="../../assets/iconos/sad.svg" width="64" alt="Icono del módulo SAD">
```

El icono está pensado para leerse a partir de 32 px; por debajo, el dibujo pierde detalle.

## Origen y licencia

Dibujo propio sobre una rejilla de 24 unidades, con la geometría de la marca del autor: mismo lienzo, mismo degradado y mismo borde que el resto de la identidad. Sin glifos de terceros.
