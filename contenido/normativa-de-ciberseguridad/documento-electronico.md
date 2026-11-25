# El documento electrónico

Un documento en papel se explica solo: se ve el soporte, la firma y la fecha. Un fichero no; fuera de su sistema, es una secuencia de bytes que cualquiera puede cambiar sin dejar una marca visible. Lo que lo convierte en prueba es el conjunto: contenido, contexto y garantías de integridad.

## Qué convierte algo en documento

La definición clásica distingue tres elementos: información, soporte y forma de expresión —gráfica, sonora o en imagen—. El soporte puede ser material o electrónico; lo que no cambia es la función: fijar y comunicar información, servir de prueba, permitir el ejercicio de un derecho y, en algunos casos, actuar como título.

Hay dos lecturas del término. La amplia acepta cualquier objeto material capaz de representar un hecho. La estricta exige que el hecho tenga trascendencia jurídica y que el objeto reúna características que le den valor probatorio. Un borrador sin firma puede ser documento en sentido amplio, pero no prueba lo mismo que un contrato firmado.

La diferencia importa en la práctica: un expediente puede contener documentos de los dos tipos, y no todos pesan igual ante un auditor o un juez. Saber cuál es cuál evita atribuir a una copia la fuerza de un original.

## Tres generaciones de sistemas

Los sistemas orientados a datos automatizaron la contabilidad y trajeron, con ella, la protección de datos personales. Los orientados a documentos añadieron editores, correo y flujos de trabajo, y con ellos nacieron los conceptos jurídicos de firma, documento y expediente electrónicos. Los orientados al conocimiento incorporan inteligencia artificial y decisiones automatizadas, que plantean si una máquina puede adoptar una decisión jurídicamente relevante.

La historia no es un adorno: explica por qué el documento electrónico se regula a la vez como soporte técnico y como institución jurídica. Un PDF no es un documento por su extensión, sino por lo que se puede demostrar sobre él.

## La definición legal

El Reglamento eIDAS define el documento electrónico como todo contenido almacenado en formato electrónico, en particular texto o registro sonoro, visual o audiovisual. No exige que el original sea nativo digital: un registro analógico digitalizado y almacenado en formato electrónico sí es un documento electrónico.

Lo decisivo no es el soporte, sino que el contenido se conserve y se pueda asociar a su origen. Esa asociación es el punto débil. En papel, el contexto se percibe —quién entrega, en qué mesa, con qué sello—. En un sistema informático, el contexto no se ve y hay que hacerlo explícito. De ahí los metadatos.

## Metadatos: el contexto hecho datos

Los metadatos son información complementaria, independiente del documento, que permite clasificarlo y situar sus contenidos en su contexto. Sin ellos, un PDF es un fichero; con ellos, se sabe quién dice haberlo emitido, cuándo, para qué procedimiento y con qué estado de elaboración. La prueba de autoría requiere además firma o sello.

La Ley 39/2015, del procedimiento administrativo común, exige que los documentos electrónicos administrativos incorporen los metadatos mínimos exigidos. La norma técnica que los fija es la Norma Técnica de Interoperabilidad de Documento Electrónico, y el esquema de referencia habitual es el Esquema de Metadatos para la Gestión del Documento Electrónico.

| Metadato | Pregunta que responde |
|---|---|
| Identificador | ¿Qué documento es y a qué expediente pertenece? |
| Fecha de captura | ¿Cuándo entró en el sistema? |
| Origen | ¿Quién lo emitió o lo aportó? |
| Estado de elaboración | ¿Es un borrador, un original o una copia? |
| Nombre de formato | ¿Con qué especificación se guardó? |
| Tipo documental | ¿Qué clase de documento es? |
| Evidencias y firma | ¿Qué garantías lo acompañan? |

Los metadatos no son un adorno técnico. Son lo que permite buscar, conservar y volver a presentar el documento años después, cuando ya no queda nadie que recuerde el trámite. Un identificador sin expediente o una fecha sin zona horaria convierten la búsqueda en una conjetura.

## Presentación y significado

Un documento puede describir cómo se ve o qué significa. El marcado de presentación, como HTML, mezcla estructura y apariencia: etiquetas de color, centrado o tipografía conviven con el contenido. HTML5 añade etiquetas semánticas y CSS separa la presentación.

El marcado descriptivo o semántico, como XML, indica significado: esto es una cotización, esto su nombre, esto su fecha. XML es un metalenguaje: no define etiquetas concretas, sino las reglas sintácticas para construir dialectos adaptados a cada sector. SGML estableció las bases generales de las que descienden ambos.

Sobre XML se han construido formatos de intercambio como XBRL para información financiera o LegalXML para documentación jurídica. La estructura habitual separa metadatos y contenido, y una hoja de estilos XSL transforma el contenido para el usuario, de modo que el mismo dato se presente en pantalla, en papel o en otro sistema sin duplicar la información.

La separación tiene una consecuencia práctica: el dato se mantiene una vez y se presenta de varias formas. Si el contenido y la apariencia viven en el mismo sitio, cualquier cambio de formato obliga a rehacer el documento y abre la puerta a versiones que dicen cosas distintas.

## Cómo revisar un documento electrónico

1. Identifica el contenido y el soporte: qué información contiene y dónde está almacenada.
2. Comprueba los metadatos: identificador, fecha, origen, estado, formato y tipo documental.
3. Verifica la integridad: hay firma o sello que permita detectar cambios.
4. Revisa el formato: es un estándar abierto o un formato propietario que dificulta la conservación.
5. Comprueba la trazabilidad: se puede reconstruir quién lo creó, quién lo modificó y cuándo.

La revisión no termina en el fichero. Un documento puede estar impecable y pertenecer a un expediente incompleto; en ese caso, la prueba se discute en el conjunto, no en la página.

## Errores frecuentes

**Confundir el fichero con el documento.** Un PDF sin metadatos ni firma puede ser una copia; no prueba por sí solo quién lo emitió.

**Suponer que el formato lo dice todo.** El tipo de archivo indica cómo se abre, no si el contenido es auténtico.

**Descuidar la conservación.** Un formato propietario puede dejar de abrirse; un estándar abierto y documentado facilita la lectura a largo plazo.

**Mezclar presentación y significado.** En HTML clásico, la apariencia y el contenido van juntos; si el dato no está etiquetado, se pierde al reutilizarlo.

**Olvidar la trazabilidad.** Sin registro de versiones no se sabe qué documento se revisó, quién lo aprobó ni cuándo.

## Una licencia en PDF

Un ayuntamiento publica una licencia de obra en PDF. El fichero incluye el texto del acuerdo, pero sin metadatos no se sabe si es el documento original o una copia, ni a qué expediente pertenece. Si además lleva un código seguro de verificación, cualquier persona puede cotejarlo con el documento autenticado del archivo municipal. El PDF deja de ser una imagen y pasa a ser una prueba verificable.

La diferencia no está en el aspecto del fichero, que puede ser idéntico, sino en lo que se puede comprobar desde fuera. Ese es el criterio que separa una copia útil de un documento con valor probatorio.

## Fuentes

- Reglamento (UE) 910/2014 (eIDAS), artículo 3.35.
- Ley 39/2015, de 1 de octubre, del procedimiento administrativo común de las Administraciones Públicas, artículo 26.2.
- Norma Técnica de Interoperabilidad de Documento Electrónico y esquema de metadatos para la gestión del documento electrónico.
- W3C, *Extensible Markup Language (XML)* y *Extensible Stylesheet Language (XSL)*.
- XBRL International y OASIS, para los formatos de intercambio citados.
