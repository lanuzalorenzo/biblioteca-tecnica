# PKI y firma electrónica

Una web de reservas mostraba el candado y el dueño daba por hecho que estaba protegida. El candado decía que la conexión iba cifrada, pero el certificado estaba emitido para otro dominio y el navegador lo aceptaba porque alguien había instalado una autoridad de confianza sin control. Un certificado no es un adorno: es la pieza que permite comprobar con quién se habla y acordar una clave de sesión. Sin esa comprobación, el candado solo indica que hay cifrado, no que el interlocutor sea quien dice.

La criptografía, el hash y la firma digital se explican en [Criptografía y firma digital](../seguridad-y-alta-disponibilidad/criptografia-y-firma-digital.md). Este apunte se ocupa de la infraestructura que emite y valida certificados, de su ciclo de vida y del valor jurídico de una firma.

## Qué resuelve

Una PKI reúne roles, políticas, equipos, programas y procedimientos para crear, distribuir, usar, almacenar y revocar certificados digitales.

Se apoya en criptografía asimétrica: cada titular tiene un par de claves, una privada que no se comparte y una pública que se distribuye. Lo cifrado con una se descifra con la otra. De ahí salen dos operaciones diferentes:

- **Cifrar**, para que solo el titular de la clave privada pueda leer.
- **Firmar**, para que cualquiera con la clave pública compruebe autoría e integridad.

## Los cuatro papeles

| Actor | Función |
|---|---|
| Autoridad de certificación (CA) | Emite y firma los certificados; responde de su contenido |
| Autoridad de registro (RA) | Comprueba la identidad del solicitante antes de que la CA firme |
| Titular | La persona o el servicio a quien se emite el certificado |
| Tercero que confía | Quien valida el certificado sin haber participado en su emisión |

En España, la Fábrica Nacional de Moneda y Timbre actúa como CA y, en muchos trámites, la autoridad de registro es otra entidad. Un certificado de web pública suele ser de validación de dominio: la CA comprueba solo que el solicitante controla el dominio. Las validaciones de organización y extendida añaden una comprobación de identidad y son minoría.

## Qué se mira en un certificado

Un certificado X.509 une una clave pública con una identidad y lo firma una CA. Los campos que importan en la práctica:

- **Titular** y **nombre alternativo del servidor**, que es lo que el navegador compara con la dirección.
- **Emisor**, la CA que lo firmó.
- **Clave pública** y algoritmo de firma.
- **Periodo de validez**, con fecha de inicio y fin.
- **Extensiones**, como los usos permitidos o si sirve para autenticar clientes.

Un titular con el nombre de una organización no garantiza honestidad; acredita el control del dominio y que una CA lo comprobó. Un certificado acredita que el dominio es el que se dice, no que su dueño sea de fiar.

## El camino de confianza

El navegador no conoce a todas las CA del mundo: tiene un almacén de certificados raíz. La raíz firma un certificado intermedio y el intermedio firma el del servidor. El cliente recorre la cadena hasta una raíz que tenga instalada y considere de confianza.

De ahí dos situaciones habituales:

- Un certificado **autofirmado** no llega a una raíz conocida; el navegador avisa. No implica malicia: implica que nadie externo responde por él.
- Un certificado **caducado** rompe la validación aunque la firma sea correcta. La caducidad es la causa más frecuente de incidencias y la que más se olvida renovar.

## Emitir, usar, retirar

Un certificado se solicita, se valida, se emite, se usa y se revoca. La revocación se pide a la CA cuando la clave privada se compromete o el titular pierde el derecho al certificado.

Hay dos mecanismos para consultarla:

- **CRL:** la CA publica una lista de certificados revocados y el cliente la descarga. Puede estar desactualizada.
- **OCSP:** el cliente pregunta por un certificado concreto y recibe una respuesta inmediata.

La revocación evita la suplantación y después se emite un certificado nuevo. Conviene no pedirle a la PKI más de lo que da: certifica mientras el certificado sea válido; si roban la clave privada, el atacante puede firmar hasta que se revoque. Esa revocación no es instantánea en todos los clientes, y de ahí los plazos cortos y mecanismos como la fijación de clave pública.

## Para qué se usan

| Uso | Qué aporta |
|---|---|
| TLS en web y APIs | Cifrado de la sesión y autenticación del servidor |
| Firma de documentos | Autoría, integridad y no repudio |
| Cifrado de correo y ficheros | Solo el destinatario puede leer |
| Autenticación de clientes | El servidor comprueba el certificado del usuario |
| Acceso a la Administración | Sustituye usuario y contraseña por certificado |

## Firma electrónica

La firma electrónica es una figura jurídica, no solo una operación técnica: da fe de la voluntad del firmante. Técnicamente es un conjunto de datos vinculado al documento que identifica al autor y permite detectar cambios.

El Reglamento eIDAS distingue tres niveles:

| Tipo | Qué garantiza |
|---|---|
| Simple | Datos en formato electrónico asociados a un documento; por sí sola, poca cosa |
| Avanzada | Vinculada al firmante, permite detectar cambios y está bajo su control exclusivo |
| Cualificada | Avanzada con certificado cualificado y dispositivo cualificado; equivale a la firma manuscrita |

La Ley 6/2020 recoge en España los servicios electrónicos de confianza y sitúa esa escala dentro del marco europeo. En el DNI electrónico, el certificado puede leerse, pero la clave privada no se puede exportar: permanece en el chip y se activa con un PIN. De ahí que sirva para firmar, no solo para identificarse.

En banca conviven tres mecanismos: una clave pactada, la biometría del teléfono —que autoriza una clave sin salir del dispositivo— y una clave criptográfica privada. Ninguno envía la clave privada; se envía la prueba de que se utilizó.

## Errores que se repiten

- Confundir cifrado con autenticidad: HTTPS con un certificado no válido no protege de una suplantación.
- Dejar caducar un certificado por no tener inventario ni alertas.
- Instalar la CA interna en todos los equipos «para que no dé avisos» sin controlar quién puede emitir.
- Usar un certificado de servidor como certificado de usuario, o al revés, cuando las extensiones no lo permiten.
- Guardar la clave privada sin contraseña o en el mismo servidor que firma.

## Qué comprobar

- ¿Hay inventario de certificados con titular, uso, caducidad y responsable?
- ¿La renovación está automatizada o depende de que alguien se acuerde?
- ¿La CA interna está protegida y su clave privada no vive en un servidor de aplicaciones?
- ¿Los clientes validan cadena y revocación, o aceptan cualquier certificado?
- ¿La firma usada tiene el nivel jurídico que exige el trámite?

## Fuentes

- Reglamento (UE) 910/2014 (eIDAS), artículos 25 y 26.
- Ley 6/2020, de 11 de noviembre, de servicios electrónicos de confianza.
- RFC 5280, *Internet X.509 Public Key Infrastructure Certificate and CRL Profile*.
- INCIBE. Guías de certificados y firma electrónica.
