# UD2. Compartir ficheros y correo

Dos servicios que parecen simples y son los que más incidencias generan: compartir ficheros y entregar correo. El primero porque los permisos nunca son los que uno cree; el segundo porque depende de una cadena de nombres, registros y reputación que no controla el servidor.

> **Módulo:** SRI. Servicios de red e internet

## FTP: el protocolo y sus sombras

FTP transfiere ficheros con dos conexiones: una de control en el puerto 21 y otra de datos que se abre aparte. Ese diseño antiguo tiene dos consecuencias incómodas: funciona mal detrás de cortafuegos y **mueve las credenciales sin cifrar**.

- **Modo activo y pasivo:** en el activo, el servidor abre la conexión de datos hacia el cliente, lo que casi nunca atraviesa un cortafuegos; en el pasivo es el cliente quien conecta a un puerto del servidor, y hay que acotar el rango de puertos en la configuración.
- **FTPS** añade TLS a FTP. **SFTP** no es FTP con cifrado: es el protocolo de transferencia de SSH, otro servicio, otro puerto y otra configuración. Confundirlos es el error más habitual en una entrega.

Una instalación razonable: usuario por persona, directorio encerrado en su *chroot*, escritura solo donde toca, sin acceso anónimo y con FTPS o SFTP obligatorio. Y una pregunta previa: si lo que se necesita es compartir con el navegador, quizá el servicio correcto no sea FTP sino un recurso web o un servicio de ficheros en red.

## Correo: cuatro protocolos y una cadena

Enviar y recibir correo son dos caminos distintos:

| Función | Protocolo | Puertos habituales |
|---|---|---|
| Enviar desde el cliente | SMTP de envío | 587 con TLS obligatorio |
| Entregar entre servidores | SMTP | 25 |
| Recibir en el cliente | IMAP | 143, o 993 con TLS |
| Recibir y borrar del servidor | POP3 | 110, o 995 con TLS |

Enviar usa SMTP; leer usa IMAP o POP3 —hoy, IMAP casi siempre, porque mantiene el buzón sincronizado en varios dispositivos—. Un servidor que solo recibe no sirve de nada si no puede entregar a otros, y para eso necesita un nombre resoluble, una dirección inversa coherente y no estar en una lista negra.

## Que el correo llegue

Tres mecanismos deciden si un mensaje entra o se marca como sospechoso:

- **SPF:** declara qué servidores pueden enviar en nombre del dominio, en un registro de texto del DNS.
- **DKIM:** firma el mensaje con una clave cuya parte pública está publicada, de modo que el receptor comprueba que no se ha alterado.
- **DMARC:** dice qué hacer cuando SPF o DKIM fallan y da un informe. Es la política, no la autenticación.

Configurar los tres sin comprobarlos no basta: se publica un mensaje de prueba a un buzón externo y se leen las cabeceras para ver qué ha evaluado el receptor. Es la única forma de saber que la cadena funciona.

## Buzones y antispam

- **Un buzón por persona**, con cuota. Las cuentas compartidas hacen imposible saber quién leyó qué.
- **Alias y listas** para direcciones funcionales; el alias no tiene buzón propio.
- **Filtro antispam y antivirus** en el servidor, con cuarentena revisable: un filtro que borra sin avisar pierde facturas.
- **Registro** de entrega y de rechazo, con retención suficiente para investigar un envío perdido.
- **Relay abierto**: el error clásico y grave. Un servidor que reenvía correo de cualquiera se convierte en pocas horas en herramienta de spam y acaba en listas negras.

## Lo que se comprueba

Que un usuario no sale de su directorio en FTP y que el anónimo está cerrado; que el envío por el puerto de sumisión exige TLS y autenticación; que el relay abierto está cerrado —probándolo desde fuera—; que SPF, DKIM y DMARC están publicados y evaluados; que las cuotas funcionan; y que los buzones con alias no se confunden.

## Errores que se repiten

- FTP sin cifrar «porque es una red interna».
- Confundir SFTP con FTPS.
- Publicar SPF pero no DMARC, y preguntarse por qué el correo cae en spam.
- Dejar el relay abierto y descubrirlo por una factura de tráfico.
- Un solo registro del servidor de correo, sin retención, con los registros rotando a diario.

## Fuentes

- RFC 5321 (SMTP), RFC 3501 (IMAP) y RFC 1939 (POP3).
- RFC 7208 (SPF), RFC 6376 (DKIM) y RFC 7489 (DMARC).
- Documentación oficial de vsftpd, Postfix y Dovecot.
