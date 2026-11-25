# Firma electrónica y blockchain

Una firma manuscrita dice quién firma y cuándo, y el gesto se ve. En un entorno electrónico esa confianza no se ve: hay que construirla con criptografía, certificados y reglas, y comprobar después que el documento no cambió. Lo que se gana en comodidad se paga en verificación.

## Identificar no es autenticar

La identificación responde a «¿quién dice ser?». La autenticación responde a «¿puede demostrarlo?». Se apoya en tres factores: algo que se sabe —una contraseña o un PIN—, algo que se tiene —una tarjeta o una clave criptográfica— y algo que se es —biometría—. Combinar factores reduce el riesgo; usar uno solo lo concentra.

## Qué garantiza cada mecanismo

| Mecanismo | Garantiza |
|---|---|
| Firma electrónica | Autenticidad de origen e integridad del documento |
| Cifrado de confidencialidad | Que solo el destinatario lea el contenido |
| Tercero de confianza | No repudio: el firmante no puede negar haber firmado |

La firma no oculta el contenido; el cifrado no demuestra quién envió. Son funciones distintas y se combinan cuando hacen falta ambas. Un documento puede ir firmado y legible, o cifrado y sin firma; cada elección responde a una pregunta diferente.

## Criptografía y firma

La criptografía simétrica usa la misma clave para cifrar y descifrar. Es rápida, pero exige compartir la clave por un canal seguro. La asimétrica usa dos claves relacionadas: lo que se cifra con una se descifra con la otra. La pública se reparte; la privada no sale del firmante.

Para firmar, el emisor calcula un resumen —un *hash*— del documento, lo firma con su clave privada y adjunta el resultado. El receptor recalcula el hash, verifica la firma con la clave pública y compara. Si coincide, la firma corresponde al firmante y al documento, y el documento no ha cambiado desde que se firmó.

El hash no es el documento: es una huella de tamaño fijo que representa su contenido. La verificación se hace sobre el valor completo y sobre el documento, no sobre una parte ni sobre el aspecto del fichero.

## Certificados y sellos de tiempo

La clave pública resuelve la comprobación, pero no dice a quién pertenece. De eso se encargan las autoridades de certificación, que emiten certificados firmados por ellas, y las autoridades de registro, que comprueban la identidad del solicitante antes de emitirlos.

El sello de tiempo añade la dimensión temporal: un prestador de confianza certifica con su firma la fecha y hora. Una marca de tiempo sin esa firma es solo una referencia. En documentos XML, los formatos XAdES añaden capas sucesivas de evidencia; XAdES-T incorpora el sello de tiempo.

Un código seguro de verificación permite cotejar una copia impresa o en PDF con el documento autenticado que guarda el organismo. Los certificados de servidor identifican servidores y permiten cifrar la comunicación; la firma de software identifica al editor de una aplicación.

Un certificado tiene un ciclo de vida: se emite, se usa y se comprueba. La verificación no termina en la firma del documento; alcanza a la cadena que sostiene el certificado y al momento en que se usó.

## Confidencialidad y recuperación de claves

Para cifrar un mensaje se usa la clave pública del destinatario; solo su clave privada lo descifra. Si esa clave se pierde, la información se pierde con ella. Por eso algunas organizaciones contratan servicios de depósito de claves, que añaden una copia de recuperación y, con ella, un riesgo que debe gobernarse.

Ese riesgo se parece al de la llave maestra de un edificio: resuelve la emergencia y, a la vez, concentra el acceso. El depósito exige controles propios y un registro de quién recupera qué.

## Tres niveles de firma

El Reglamento eIDAS y la Ley 6/2020 ordenan las firmas en tres niveles:

| Tipo | Qué es | Valor práctico |
|---|---|---|
| Simple | Datos electrónicos asociados al documento, como una contraseña | Fácil de usar, pero débil: la conoce quien proporciona el medio y se puede robar |
| Avanzada | Vinculada de forma única al firmante, lo identifica, se crea bajo su control exclusivo y cualquier cambio posterior es detectable | Identifica y protege la integridad |
| Cualificada | Avanzada creada con un dispositivo cualificado y basada en un certificado cualificado | Equivale jurídicamente a la firma manuscrita |

Una firma electrónica no puede rechazarse como prueba por el mero hecho de no ser cualificada. La firma la usan personas físicas; el sello electrónico lo usan personas jurídicas y actúa de forma automatizada.

Los prestadores de servicios de confianza emiten certificados, validan firmas, sellan el tiempo y prestan entrega certificada. Los cualificados deben verificar la identidad del solicitante y cumplir requisitos técnicos y jurídicos; disponen de una política y de una declaración de prácticas que explican para qué sirve cada certificado y qué valor tiene la firma que respalda.

Elegir prestador no es elegir marca. La política y la declaración de prácticas dicen qué se comprueba al emitir, qué se conserva y qué se puede verificar después; son la letra pequeña que decide el valor de la firma.

## Blockchain

Una blockchain es una base de datos distribuida con dos propiedades: la información se comparte entre nodos mediante técnicas entre pares y forma una cadena de bloques cuyo hash enlaza cada bloque con el anterior. Cambiar un bloque obliga a recalcular todos los siguientes, de modo que la manipulación se detecta.

En redes públicas, cualquiera puede ser nodo y competir por cerrar bloques; en privadas, un administrador decide quién participa. Los algoritmos de consenso —prueba de trabajo, prueba de participación y prueba de autoridad— mantienen a los nodos de acuerdo. Un actor con más de la mitad de los recursos de consenso podría imponer su versión: es el ataque del 51 %.

Bitcoin es un criptoactivo sobre una blockchain pública. La minería premia al nodo que cierra un bloque, y la recompensa se reduce a la mitad aproximadamente cada cuatro años. La prueba de trabajo limita la emisión y sirve de barrera frente a la manipulación.

La cadena registra el orden y la integridad de lo que se escribió. Su valor para la prueba documental depende de que el dato inicial esté bien definido y de que el registro se pueda consultar cuando haga falta.

## Un contrato que hay que probar años después

Una empresa firma un contrato con un ayuntamiento. El documento se firma con certificado cualificado de la persona apoderada y se sella el tiempo con un prestador de confianza. Años después, una auditoría puede comprobar que el contenido no cambió y que la firma se produjo antes de una fecha concreta, sin depender de la memoria de quienes lo firmaron.

La prueba no está en el aspecto del PDF, sino en la cadena de certificados, sellos y verificaciones que lo acompañan. Si esa cadena se rompe, el documento sigue siendo legible, pero deja de probar lo que se esperaba.

## Fuentes

- Reglamento (UE) 910/2014 (eIDAS).
- Ley 6/2020, de 11 de noviembre, de servicios electrónicos de confianza.
- Reglamento de Ejecución (UE) 2015/1502, sobre niveles de garantía de identificación.
- ETSI, especificaciones XAdES.
- Documentación de Bitcoin sobre la reducción de la recompensa por bloque.
