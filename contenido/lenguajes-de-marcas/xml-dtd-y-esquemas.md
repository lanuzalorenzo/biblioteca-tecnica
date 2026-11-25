# XML: estructura, DTD y esquemas

XML no sirve para que un programa pinte una pantalla: sirve para que dos programas se pasen datos y se entiendan. Por eso su valor no está en el formato, sino en la posibilidad de **comprobar** que el fichero cumple lo pactado antes de leerlo.


## Un documento bien formado

Bien formado significa que el documento se puede leer sin ambigüedad. Las reglas son pocas y no admiten interpretación:

- Un solo elemento raíz.
- Toda etiqueta abierta se cierra, en el orden correcto.
- Los nombres distinguen mayúsculas y no admiten espacios.
- Los atributos van entrecomillados y no se repiten en el mismo elemento.
- Los caracteres especiales se escapan: `&lt;`, `&gt;`, `&amp;`.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<equipos>
  <equipo id="PC-01">
    <nombre>Aula 12</nombre>
    <estado>activo</estado>
  </equipo>
</equipos>
```

## Bien formado no es válido

Un documento puede cumplir todas las reglas anteriores y aun así no ser el que esperaba el sistema: falta un campo obligatorio, el estado tiene un valor que no existe, el identificador se repite.

Ahí entran las dos formas de describir el contrato:

| | DTD | Esquema XSD |
|---|---|---|
| Sintaxis | Propia, heredada de SGML | XML |
| Tipos de datos | No | Sí: fechas, enteros, decimales, enumeraciones |
| Cardinalidad | Vaga | Precisa (`minOccurs`, `maxOccurs`) |
| Espacios de nombres | No | Sí |
| Uso actual | Legado | Preferente |

La DTD se escribió mucho y se sigue leyendo en sistemas antiguos; para trabajo nuevo se usa XSD, porque permite decir que un campo es una fecha y que un estado solo admite tres valores.

```xml
<xs:element name="estado">
  <xs:simpleType>
    <xs:restriction base="xs:string">
      <xs:enumeration value="activo"/>
      <xs:enumeration value="reparacion"/>
      <xs:enumeration value="baja"/>
    </xs:restriction>
  </xs:simpleType>
</xs:element>
```

## Espacios de nombres

Cuando un documento mezcla vocabularios —un inventario propio con direcciones postales de otro estándar— los nombres chocan. El **espacio de nombres** prefija cada elemento con un identificador único:

```xml
<inv:equipo xmlns:inv="urn:empresa:inventario"
            xmlns:dir="urn:empresa:direccion">
  <inv:nombre>Aula 12</inv:nombre>
  <dir:calle>Calle Mayor 1</dir:calle>
</inv:equipo>
```

El prefijo es solo un alias: lo que identifica es la URI, no el texto `inv`. Cambiar el prefijo no cambia el documento.

## Validar y procesar

La validación se hace con una herramienta —`xmllint` en línea de órdenes— y en el código con un analizador que recibe el esquema:

```bash
xmllint --noout --schema inventario.xsd inventario.xml
xmllint --noout --dtdvalid inventario.dtd inventario.xml
```

Y una advertencia que se aprende con un susto: **nunca** analizar XML con entidades externas habilitadas cuando el documento viene de fuera. Es la vía clásica de leer ficheros locales del servidor. Los analizadores modernos lo desactivan por defecto; las configuraciones heredadas, no.

## Cuándo XML y cuándo otra cosa

XML es verboso y explícito: bueno para documentos, contratos e intercambio entre sistemas distintos, donde la precisión compensa el tamaño. Para una API entre dos sistemas del mismo equipo, JSON ocupa menos y se procesa igual de bien. La decisión se toma por el caso, no por preferencia.

## Lo que se comprueba

Que el documento está bien formado; que valida contra su esquema o DTD; que los valores enumerados son los pactados; que los espacios de nombres están declarados; y que el analizador del código rechaza un fichero inválido en lugar de tragárselo.

## Errores que se repiten

- Validar solo el primer fichero de una importación y dar el resto por bueno.
- Cambiar el esquema sin avisar a quien lo consume.
- Usar DTD para datos nuevos cuando el tipo importa.
- Habilitar entidades externas «para que funcione» un documento ajeno.

## Leer el documento desde el código

En la práctica, el XML se procesa con un analizador, y hay dos familias con consecuencias distintas:

- **Árbol en memoria** (DOM): carga el documento entero y permite recorrerlo y modificarlo. Cómodo con ficheros pequeños; con uno de doscientos megabytes, el servidor se queda sin memoria.
- **Por eventos** (SAX y los analizadores de flujo): lee y avisa, sin guardar el árbol. Sirve para ficheros grandes y para importaciones por lotes.

La elección se hace por tamaño y por necesidad de modificar, no por preferencia. Y en los dos casos se declara el esquema antes de leer: validar al principio evita procesar tres mil filas para descubrir en la última que el fichero no era el esperado.

## Fuentes

- Recomendación XML del W3C y especificación de esquemas XML (XSD).
- Especificación de espacios de nombres en XML.
- Documentación de `xmllint` y de los analizadores de referencia.
