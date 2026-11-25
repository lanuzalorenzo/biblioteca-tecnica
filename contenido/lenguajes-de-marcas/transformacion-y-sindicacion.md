# Transformar y publicar contenidos

Un mismo dato se publica en una web, se envía en un lector de noticias y se guarda para consultarlo después. Escribirlo tres veces garantiza que las tres versiones se contradigan; transformarlo desde una sola fuente es lo que hace que el contenido sea el mismo en todas partes.


## XPath: elegir partes del documento

Antes de transformar hay que saber **seleccionar**. XPath recorre el árbol y devuelve los nodos que cumplen una ruta.

| Expresión | Qué selecciona |
|---|---|
| `/equipos/equipo` | Todos los equipos del raíz |
| `//equipo[@estado='activo']` | Los activos, estén donde estén |
| `//equipo[1]` | El primero de cada grupo |
| `//equipo/nombre/text()` | El texto del nombre |

Es la misma idea que un selector de CSS aplicado a datos, y sirve también para consultar XML desde código.

## XSLT: convertir un XML en otro documento

Una hoja XSLT es un documento XML que describe la transformación. Se compone de **plantillas** que se aplican a los nodos seleccionados:

```xml
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="/">
    <html><body>
      <h1>Equipos</h1>
      <ul>
        <xsl:for-each select="//equipo[@estado='activo']">
          <li><xsl:value-of select="nombre"/></li>
        </xsl:for-each>
      </ul>
    </body></html>
  </xsl:template>
</xsl:stylesheet>
```

La versión 1.0 es la que implementan los navegadores; la 3.0 es la actual y aporta funciones y procesamiento en streaming, pero se ejecuta fuera del navegador, con un procesador.

Un uso práctico que se sigue viendo: recibir un XML de un proveedor y publicar el catálogo en HTML sin tocar el original. Se cambia la hoja, no los datos.

## Sindicación: RSS y Atom

La sindicación permite que un sitio publique una lista de novedades y que otros la lean sin visitarlo. **RSS 2.0** y **Atom** son los dos formatos en uso; Atom es más estricto y tiene especificación formal.

Un canal mínimo lleva título, enlace, descripción e ítems con su fecha. Tres errores que rompen los lectores: fechas en formato local en lugar de ISO 8601, enlaces relativos —el lector no sabe respecto a qué— y contenido HTML sin escapar.

```xml
<rss version="2.0">
  <channel>
    <title>Novedades del centro</title>
    <link>https://ejemplo.local/</link>
    <description>Cambios en el inventario</description>
    <item>
      <title>Nuevo equipo PC-07</title>
      <link>https://ejemplo.local/pc-07</link>
      <pubDate>Mon, 02 Nov 2015 09:00:00 +0100</pubDate>
    </item>
  </channel>
</rss>
```

## Publicar sin romper nada

- **Codificación:** UTF-8 declarado en el documento y en la cabecera del servidor. Si no coinciden, aparecen símbolos donde había tildes.
- **Validación antes de publicar:** el canal y la transformación se comprueban con la misma herramienta que el resto del XML.
- **Enlaces absolutos** en lo que se sindica o se envía: fuera del sitio, un enlace relativo no apunta a nada.
- **Caché y actualización:** un lector consulta cada cierto tiempo; si el canal tarda una hora en regenerarse, las novedades llegan tarde.

## Lo que se comprueba

Que la transformación produce un documento válido; que XPath selecciona lo que se espera antes de escribir la plantilla; que el canal tiene fechas en formato correcto y enlaces absolutos; y que el mismo contenido sale igual en la web y en el lector.

## Errores que se repiten

- Escribir la plantilla antes de probar la expresión XPath.
- Publicar un canal con fechas locales que cada lector interpreta a su manera.
- Transformar en el servidor en cada visita lo que podría generarse una vez.
- Cambiar la estructura del XML de origen sin revisar las hojas que lo consumen.

## Generar el canal desde los datos

El canal no se escribe a mano: se genera desde la fuente que ya tiene el contenido. Un proceso programado consulta las novedades del periodo, compone el XML y lo deja en la ruta pública; la transformación a HTML se hace con la misma hoja para la web y para el lector.

Tres comprobaciones antes de dar el canal por publicado: que el XML resultante valida contra su esquema, que las fechas van en UTC y que el orden de los ítems es el que se espera. Un canal que lista las novedades del más antiguo al más reciente técnicamente funciona y nadie lo lee.

Y si el canal se genera cada hora, conviene que el proceso deje registro de la última ejecución y avise si falla dos veces seguidas: un canal congelado no da error, simplemente deja de recibir novedades.

## Fuentes

- Especificación XSLT 3.0 y XPath del W3C.
- Especificación RSS 2.0 y RFC 4287 (Atom).
- Norma ISO 8601 para fechas y horas.
