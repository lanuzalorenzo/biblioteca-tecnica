# Mensajería, audio y vídeo

La mensajería y el vídeo se parecen al correo en que llevan información de una persona a otra, pero se diferencian en lo que exige la red: el correo tolera minutos de retraso; una llamada, no. Montar estos servicios es decidir qué se necesita en tiempo real y qué se puede empaquetar y enviar después.


## Mensajería en tiempo real

El correo es almacenamiento y reenvío: el mensaje se guarda hasta que el destinatario lo recoge. La mensajería instantánea mantiene una conexión abierta y entrega en el momento, con presencia —quién está conectado— e indicadores de lectura.

Dos familias de protocolo abierto:

- **XMPP:** estándar, federado —un servidor puede hablar con otro— y extensible. Se apoya en XML sobre TCP y tiene extensiones para cifrado, archivos y audio. Servidores como Prosody o ejabberd lo implementan.
- **Matrix:** protocolo de salas con replicación entre servidores, pensado para historial distribuido y cifrado de extremo a extremo. Synapse es su implementación de referencia.

Frente a ello, las aplicaciones cerradas —WhatsApp, Telegram, Slack— ofrecen menos control y más comodidad. En una empresa, la elección depende de si se necesita federación, historial propio, cumplimiento y cifrado gestionado por la organización.

## Cifrado y confianza

El cifrado de extremo a extremo protege el contenido, pero no los metadatos —quién habla con quién y cuándo— ni las copias del servidor si se guardan. En una implantación propia hay que decidir: cifrado en tránsito con TLS, cifrado de extremo a extremo con OMEMO o MLS, y política de retención. Las conversaciones de trabajo pueden ser prueba de un acuerdo; borrarlas sin criterio también crea problemas.

## Audio y vídeo: dos planos

Una videollamada tiene dos planos:

- **Señalización:** cómo se encuentran las partes y se negocian códecs y direcciones. SIP es el estándar clásico; WebRTC lo resuelve en el navegador con señalización propia.
- **Transporte de medios:** RTP lleva el audio y el vídeo, y RTCP informa de pérdida, retardo y jitter. Los códecs habituales son Opus para voz y VP8, VP9 o AV1 para vídeo.

En una red local, el **multicast** permite enviar una sola vez a muchos receptores; en Internet no se usa y se sustituye por servidores de distribución. Un aula o una sala de reuniones puede usar multicast; una empresa con teletrabajo, no.

## Streaming

El vídeo en directo o bajo demanda tiene dos modelos:

- **RTSP/RTP:** control de una cámara o un reproductor, con baja latencia y estado. Es el modelo de las cámaras IP y de algunos reproductores.
- **HLS y DASH:** el vídeo se corta en segmentos y se sirve por HTTP; el reproductor descarga el manifiesto y elige calidad. Escala bien con CDN y atraviesa cortafuegos, a cambio de más latencia.

La elección depende del caso: una cámara de seguridad quiere baja latencia y RTSP; una clase grabada o una retransmisión pública quieren HLS o DASH. Servir vídeo desde el mismo servidor web que la aplicación funciona para pocos usuarios; con muchos, el ancho de banda se come el resto.

## Capacidad y calidad

Los medios consumen ancho de banda constante y sensible al retardo. Antes de montar el servicio hay que calcular: cuántas sesiones simultáneas, con qué códec y a qué calidad. Una llamada de voz ronda decenas de kbps; un vídeo HD, varios Mbps. La **QoS** marca el tráfico de voz y vídeo para que no compita con una copia de seguridad.

El **jitter** —variación del retardo— se corrige con un búfer pequeño; si es grande, la conversación se corta aunque haya ancho de banda. La pérdida de paquetes se nota antes en voz que en datos.

## Seguridad y cumplimiento

- **Autenticación** de usuarios y, si hay invitados, cuentas temporales.
- **TLS** en la señalización y en el transporte; certificados válidos.
- **Control de acceso** a salas y grabaciones.
- **Consentimiento** para grabar audio o vídeo, y política de conservación.
- **Registro** de accesos sin guardar el contenido más de lo necesario.

Una cámara IP con la contraseña por defecto es una puerta abierta a la red; una sala de vídeo pública sin contraseña, una reunión a la que entra cualquiera.

## Lo que se comprueba

Que el protocolo elegido encaja con el uso —mensajería, llamada, cámara o emisión—; que el cifrado está en tránsito y, si se requiere, de extremo a extremo; que el ancho de banda y la QoS están dimensionados; que las grabaciones tienen consentimiento y retención; y que las cuentas y salas tienen control de acceso.

## Fuentes

- RFC 6120, XMPP Core; RFC 6121, XMPP Instant Messaging and Presence.
- RFC 3261, SIP; RFC 3550, RTP; RFC 3711, SRTP.
- RFC 8216, HTTP Live Streaming; ISO/IEC 23009-1, MPEG-DASH.
- W3C, WebRTC 1.0.
- Orden EDU/392/2010, de 20 de enero (BOE-A-2010-3028).
