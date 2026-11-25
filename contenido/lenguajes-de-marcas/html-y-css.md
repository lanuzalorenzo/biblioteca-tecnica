# HTML y CSS: estructura y presentación

Una página web es un documento con etiquetas que dicen qué es cada cosa, y una hoja de estilos que decide cómo se ve. Separar las dos partes no es una moda: es lo que permite que el mismo contenido se lea en un móvil, se imprima o lo entienda un lector de pantalla.


## La estructura

HTML describe **qué es** cada fragmento. Una cabecera es una cabecera, no un texto grande; una lista es una lista, no una serie de guiones.

```html
<!DOCTYPE html>
<html lang="es">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Inventario</title>
    <link rel="stylesheet" href="estilo.css">
  </head>
  <body>
    <header><h1>Inventario</h1></header>
    <main>
      <table>
        <caption>Equipos del laboratorio</caption>
        <thead><tr><th>Equipo</th><th>Estado</th></tr></thead>
        <tbody><tr><td>PC-01</td><td>Activo</td></tr></tbody>
      </table>
    </main>
    <footer><p>Curso 2015/2016</p></footer>
  </body>
</html>
```

Las etiquetas semánticas —`header`, `nav`, `main`, `article`, `aside`, `footer`— existen para que el documento se entienda sin la hoja de estilos. Un lector de pantalla, un buscador y una impresora dependen de eso.

Y de la cabecera, dos líneas que se olvidan: `charset` declara la codificación —sin ella, las tildes se rompen— y `viewport` hace que el móvil no reduzca la página a un cuarto de pantalla.

## De la tabla al diseño

En 2015 todavía se encontraban maquetaciones con tablas anidadas. Hoy eso es un error: la tabla es para datos tabulares, y el diseño se hace con CSS.

El modelo de caja explica casi todo lo que descoloca al principio: cada elemento ocupa un rectángulo con contenido, relleno, borde y margen. Sumar anchos sin contar relleno y borde es la razón de que «no me cabe» tres párrafos seguidos de depuración.

```css
:root { --acento: #0369a1; }

main { max-width: 70ch; margin: 0 auto; padding: 1rem; }
table { border-collapse: collapse; width: 100%; }
th, td { border: 1px solid #cbd5e1; padding: .5rem; text-align: left; }
caption { font-weight: 600; text-align: left; }
```

Tres piezas de CSS que conviene dominar antes que los trucos:

- **Selector y especificidad:** un `id` pesa más que una clase, y una clase más que una etiqueta. Los `!important` repartidos por una hoja son la señal de que la especificidad se perdió.
- **Modelo de caja y `box-sizing`:** con `border-box`, el ancho incluye relleno y borde, que es lo que uno espera al dibujar.
- **Disposición:** `flex` para alinear en una dirección, `grid` para una rejilla. Las dos resuelven lo que antes se hacía con flotantes y parches.

## Accesibilidad: lo que se rompe sin querer

- Contraste suficiente entre texto y fondo; un gris claro sobre blanco no se lee al sol.
- Alternativa en las imágenes que aportan información y vacía en las decorativas.
- Etiquetas asociadas a los campos de formulario; un `placeholder` no es una etiqueta.
- Navegación con teclado y foco visible: quien no usa ratón necesita ver dónde está.
- Texto que no depende solo del color: «en rojo» no comunica si no se distingue el rojo.

## Lo que se comprueba

Que el documento valida; que sin la hoja de estilos se entiende; que se lee a 320 px de ancho; que la tabla tiene cabeceras declaradas; que los formularios tienen etiquetas; y que el contraste pasa la comprobación automática.

## Errores que se repiten

- Usar `div` con clases para todo y perder la semántica.
- Medir en píxeles absolutos y romper el diseño en el móvil.
- Poner texto alternativo genérico en todas las imágenes.
- Mezclar contenido y presentación con estilos en línea repartidos.

## Formularios: la puerta de entrada

Un formulario es la parte del documento que envía datos, y por eso es donde se concentran los errores. Tres reglas que no dependen del diseño:

- Cada campo lleva su `label` asociada con `for` e `id`. El texto de ayuda dentro del campo desaparece al escribir y no lo lee un lector de pantalla.
- El método se elige por el efecto: `GET` para consultar —los parámetros quedan en la dirección y en el historial—, `POST` para cambiar algo.
- La validación del navegador (`required`, `type="email"`) mejora la experiencia y **no sustituye** la del servidor: cualquiera puede enviar la petición sin pasar por el formulario.

Un formulario que borra un registro con un enlace es un fallo de diseño, no una comodidad: el enlace se puede precargar o repetir sin que el usuario lo decida.

## Fuentes

- Especificaciones del W3C y del WHATWG para HTML y CSS.
- Pautas de accesibilidad para el contenido web (WCAG) del W3C.
