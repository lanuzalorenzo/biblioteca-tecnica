# Icono del repositorio

Un solo icono, el de la cabecera del `README.md`.

Formato: 64×64, `rx=16`, fondo navy con degradado (`#07131e` → `#0e2a47`), borde cian sólido de 2 px (`#38bdf8`) y glifo blanco relleno (`#f8fafc`) en una caja de 44×44. El icono lleva su propio fondo, así que se lee igual sobre una barra clara y sobre una oscura. Sin texto y sin color por repositorio: la distinción va en el dibujo.

| Archivo | Dibujo |
|---|---|
| `apuntes.svg` | Hoja con líneas |

## El glifo

La hoja dice «apuntes» sin rodeos: una página con la esquina doblada y dos líneas de texto recortadas en la silueta. Se dibuja rellena, con las líneas en negativo, para que el trazo no desaparezca al reducir.

A 32 px sigue leyéndose como página y no se confunde con el libro abierto de otros repositorios de la familia: la hoja tiene el borde derecho recto, la esquina superior derecha cortada y las líneas dentro; el libro abre dos páginas en uve. En escala de grises mantiene la misma silueta, porque la forma no depende del color.

## Uso

En la cabecera del `README.md`, antes del título:

```html
<img src="assets/iconos/apuntes.svg" width="64" alt="Icono del repositorio Apuntes">
```

El icono está pensado para leerse a partir de 32 px; por debajo, el dibujo pierde detalle.

## Contraste del borde

Medido sobre el raster a 32, 64 y 128 px, componiendo el icono sobre la meseta (`#0d2740`) y sobre la caída del halo (`#0b2034`). El borde cae en píxel entero en los tres tamaños, así que el valor es el mismo:

| Tamaño | Meseta, color | Meseta, gris (Rec. 601) | Caída, color | Caída, gris (Rec. 601) |
|---|---|---|---|---|
| 32 px | 7,10:1 | 5,80:1 | 7,72:1 | 6,21:1 |
| 64 px | 7,10:1 | 5,80:1 | 7,72:1 | 6,21:1 |
| 128 px | 7,10:1 | 5,80:1 | 7,72:1 | 6,21:1 |

Los doce valores superan el mínimo de 3:1. En los tramos rectos, el borde sale `#38bdf8` puro en los tres tamaños, sin fundirse con el fondo; en los arcos de esquina el píxel es parcial por el redondeo, no por el grosor del borde.

## Origen y licencia

El glifo procede de [Material Design Icons](https://pictogrammers.com/library/mdi/) (Pictogrammers), con licencia [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0). Se ha recoloreado y compuesto; la geometría no se ha modificado.
