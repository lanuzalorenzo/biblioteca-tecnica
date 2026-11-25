# Criptografía y firma digital

Un candado abierto que se reparte por la calle no sirve de nada si cualquiera puede cerrarlo, pero funciona si solo el dueño tiene la llave: lo que se envía dentro queda a la vista de todos y solo se abre con una pieza que nunca salió de casa. Eso es la criptografía asimétrica, y de ahí cuelga casi todo lo que hoy sostiene la confianza en una red.


## Qué resuelve cada pieza

- **Confidencialidad:** cifrado simétrico o asimétrico.
- **Integridad:** funciones resumen (*hash*) y códigos de autenticación de mensaje.
- **Autenticidad y no repudio:** firma digital.
- **Confianza en las claves:** infraestructura de clave pública.

## Cifrado simétrico

Una sola clave cifra y descifra. Es rápido, barato y el que se usa para el volumen: AES en sus modos autenticados —GCM, o CCM en entornos restringidos— es el estándar de facto. Su problema es el reparto: si emisor y receptor están en extremos distintos de Internet, ¿cómo se pasan la clave sin que nadie la vea? De ahí nace todo lo demás.

DES y 3DES están retirados; RC4, prohibido. Una clave de 256 bits en AES es lo habitual hoy.

## Cifrado asimétrico

Dos claves matemáticamente ligadas: lo que cifra una, solo lo descifra la otra. Se reparte la **pública** —de ahí el nombre— y se guarda la **privada**. Es de tres a cuatro órdenes de magnitud más lento que el simétrico, así que no se usa para cifrar mensajes largos.

Familias vigentes:

- **RSA**, con 2048 bits como mínimo y 3072 recomendado.
- **Curvas elípticas:** ECDSA y EdDSA (Ed25519) para firma; ECDH y X25519 para acuerdo de claves. Con 256 bits dan la seguridad de RSA-3072 con mucha menos carga.

## El esquema híbrido: así funciona de verdad

En la práctica se combinan. En TLS 1.3, el cliente y el servidor acuerdan una clave de sesión con un intercambio asimétrico (X25519 o similar) y a partir de ahí todo el tráfico va cifrado con simétrico. El asimétrico resuelve el reparto; el simétrico, la velocidad.

## Integridad: el hash

Una función resumen convierte cualquier entrada en una huella de tamaño fijo. No es cifrado —no se descifra— y sirve para detectar cambios: si un byte cambia, la huella cambia por completo.

- **SHA-256 y SHA-3** son las opciones vigentes.
- **MD5 y SHA-1** están rotos para colisiones. SHA-1 aparece todavía en certificados antiguos y en configuraciones heredadas: cuando se encuentra, es un hallazgo, no una curiosidad. Es exactamente lo que pasaba con la entidad certificadora que se montó en la práctica de 2015, que emitía con SHA-1.
- **HMAC** combina un hash con una clave secreta para autenticar mensajes cuando ambas partes comparten esa clave.

## Firma digital

Firmar es una operación con la clave privada sobre el resumen del documento: en RSA clásico equivale a cifrar ese resumen, y en los esquemas modernos —RSA-PSS, ECDSA, EdDSA— es un cálculo distinto que cumple la misma función. Cualquiera con la clave pública correspondiente comprueba tres cosas a la vez: que el documento no ha cambiado, que lo firmó quien dice y que no puede negarlo. La firma de GPG que se practicó entonces —`--detach-sign` para firma separada, `--clearsign` para firma legible, `--verify` para comprobarla— es exactamente este mecanismo.

No confundir la firma **digital**, que es una operación criptográfica, con la firma **electrónica**, que es una figura jurídica. El Reglamento eIDAS distingue firma electrónica simple, avanzada y cualificada; solo la cualificada tiene el mismo valor que la manuscrita ante cualquier administración. Un PDF firmado con GPG puede ser una firma avanzada si cumple los requisitos; un «firmado, yo» en un correo no es nada.

## Infraestructura de clave pública

El problema que queda es: ¿cómo sé que esa clave pública pertenece a quien dice? Lo resuelve una **autoridad de certificación** (CA) que firma un **certificado** en el que consta la identidad y su clave pública.

- **X.509 v3** es el formato: sujeto, emisor, periodo de validez, clave pública, extensiones —usos de la clave, nombres alternativos, restricciones— y la firma de la CA.
- **Cadena de confianza:** el certificado del servidor lo firma una CA intermedia, que a su vez firma la raíz, que está en el almacén de confianza del sistema. Si un eslabón falta, el navegador avisa.
- **Revocación:** un certificado puede dejar de ser válido antes de caducar. Se publica en listas CRL o se consulta por OCSP. Una CA comprometida revoca y emite de nuevo.
- **ACME** (RFC 8555) automatizó la emisión para servicios públicos: es lo que hay detrás de Let's Encrypt y hoy de la mayoría de los certificados de servidor web.

Una práctica habitual es montar una CA propia, emitir un certificado al servidor web y configurar el proxy para inspeccionar con él. El procedimiento es correcto; las piezas, no: Windows Server 2008 salió de soporte en enero de 2020, la CA emitía con SHA-1 y el reparto manual del certificado raíz a cada cliente no escala. Hoy eso se hace con una CA interna gestionada —servicios de CA de Windows Server vigente, `step-ca` o Vault— y con ACME y SHA-256 para lo público.

## Errores que se repiten

- Aceptar el aviso de certificado no válido «solo esta vez». Enseña a la gente a ignorar la única señal que distingue un sitio legítimo de una suplantación.
- Reutilizar el par de claves de una CA para todo.
- Guardar la clave privada sin contraseña, en un directorio compartido o en el mismo servidor que firma.
- Confundir hash con cifrado y publicar el hash creyendo que protege el dato.
- Cifrar sin autenticar: un modo sin MAC permite alterar el texto cifrado sin detectarlo.

## Ciclo de vida de una clave y de un certificado

Una clave no se genera y se olvida. El recorrido tiene cinco pasos y cada uno se puede hacer mal:

1. **Generación** en el equipo donde se va a usar, con una contraseña que la proteja. Generarla en un servidor ajeno y enviarla por correo anula lo demás.
2. **Solicitud y emisión:** se pide a la CA con los datos correctos —nombre, usos, nombres alternativos del servidor—. Un certificado emitido para `intranet.local` no vale para `www`.
3. **Distribución:** la privada no se mueve; la pública y el certificado raíz sí, por un canal con integridad.
4. **Uso:** con la versión de TLS y los cifrados permitidos, y renovando antes de caducar. Un certificado caducado tumba un servicio igual que un fallo de disco, y avisa menos.
5. **Retirada:** revocar si la clave se ha podido ver, archivar el certificado por si hay que verificar firmas antiguas y destruir la privada.

La automatización es lo que evita el paso 4 fallando: ACME renueva sin intervención y deja registro de cada emisión. La alternativa —una hoja de cálculo con fechas— funciona hasta que se olvida.

## Fuentes

- NIST FIPS 197 (AES) y FIPS 186-5 (firmas digitales).
- RFC 5280: certificados X.509 y listas de revocación.
- RFC 8446 (TLS 1.3) y RFC 8996, que retira TLS 1.0 y 1.1.
- RFC 8555: protocolo ACME.
- Reglamento (UE) 910/2014 (eIDAS) y su modificación de 2024.
