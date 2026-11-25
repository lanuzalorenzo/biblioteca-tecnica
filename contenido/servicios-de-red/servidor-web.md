# Publicar un servidor web

Un servidor web es la puerta de entrada de casi todo lo que una empresa publica: la web, la intranet, la aplicación de gestión, el panel de correo. Configurarlo mal no solo tumba un servicio, deja a la vista de cualquiera lo que hay detrás.


## Qué hace el servidor

Recibe una petición HTTP, decide qué contenido corresponde y la devuelve con su código de estado. Debajo hay tres decisiones que se toman al instalarlo:

- **Qué escucha y dónde:** una dirección y un puerto por servicio. Escuchar en todas las interfaces cuando solo hace falta local es abrir una puerta sin necesidad.
- **Con qué usuario corre:** un usuario propio, sin privilegios, con lectura del código y escritura solo en lo que lo necesite. El servidor escucha con privilegios y después los cede.
- **Qué se registra:** acceso y errores, con retención y rotación. Sin registro no hay diagnóstico ni prueba.

## Varios sitios en una máquina

Un servidor puede atender muchos nombres con una sola dirección IP: es lo que hacen los **hosts virtuales**.

```apache
<VirtualHost *:443>
    ServerName intranet.empresa.test
    DocumentRoot /srv/www/intranet
    SSLEngine on
    SSLCertificateFile    /etc/ssl/certs/intranet.crt
    SSLCertificateKeyFile /etc/ssl/private/intranet.key
    ErrorLog  ${APACHE_LOG_DIR}/intranet-error.log
    CustomLog ${APACHE_LOG_DIR}/intranet-access.log combined
    <Directory /srv/www/intranet>
        Require all granted
        Options -Indexes
    </Directory>
</VirtualHost>
```

En Nginx la idea es la misma con `server_name` y `root`. Tres detalles que rompen una configuración: el nombre debe resolver al servidor por DNS o por el fichero de hosts; el primero que coincide gana, y si no coincide ninguno, se aplica el sitio por defecto; y `Options -Indexes` evita que se liste el contenido de un directorio sin índice, que es un regalo para quien busca ficheros olvidados.

## TLS

Sin cifrado, cada credencial que se introduzca viaja legible por cualquier punto intermedio. El certificado se obtiene de una autoridad y hoy se automatiza con el protocolo de emisión correspondiente (ACME).

- **Renovación automática** y comprobación de que la renovación ocurre: un certificado caducado deja la web inaccesible con un aviso que el usuario interpreta como un ataque.
- **Redirección de HTTP a HTTPS** y cabecera de transporte seguro para que el navegador no vuelva al texto plano.
- **Cifrados y versiones:** TLS 1.2 como mínimo y 1.3 si el cliente lo permite. Las versiones antiguas están retiradas por norma.
- **Cabeceras:** política de contenido, tipo de contenido, marco y referente. Cuestan una línea y evitan clases enteras de problema.
- **La versión del servidor no se anuncia.** Es información gratis para quien busca un fallo conocido.

## Contenido dinámico

Cuando el sitio ejecuta código, el servidor web pasa la petición al intérprete o hace de **proxy inverso** delante del proceso de la aplicación. En ese segundo caso el servidor termina TLS, sirve lo estático y deja la aplicación detrás: así se puede reiniciar la aplicación sin cortar el servicio y queda una única puerta vigilada.

Los permisos del directorio de subida merecen un párrafo aparte: si un directorio donde el usuario sube ficheros permite ejecutar código, un fichero subido se convierte en un programa que corre en el servidor. Se sube a un directorio sin ejecución y se sirve como descarga.

## Lo que se comprueba

Que el sitio responde por su nombre y no solo por IP; que un nombre desconocido no cae en otro sitio; que la redirección a HTTPS funciona y el certificado se renueva; que no hay listado de directorios; que la versión no se anuncia; que los registros se escriben y rotan; y que la ruta de subida no ejecuta código.

## Errores que se repiten

- Un directorio con permisos de escritura para el usuario del servidor web.
- Certificado manual y hoja de cálculo con fechas: se olvida y caduca.
- Dejar el sitio de ejemplo accesible después de publicar.
- Registrar todo sin rotación hasta llenar la partición.
- Probar con la IP y dar por bueno el nombre.

El servidor negocia también la versión de HTTP: HTTP/2 multiplexa peticiones sobre una conexión y HTTP/3 lo hace sobre QUIC. Activarlo depende del proxy y del cliente, y se comprueba en la respuesta, no se supone.

## Fuentes

- Documentación oficial de Apache HTTP Server y de Nginx.
- RFC 8446 (TLS 1.3) y RFC 8996, que retira las versiones anteriores.
- RFC 8555 (ACME) y guía de cabeceras de seguridad de OWASP.
