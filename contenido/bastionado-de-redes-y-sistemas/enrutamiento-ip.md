# IP y enrutamiento

La capa de red es el servicio de correos que mueve paquetes entre ciudades. No sabe en qué mesa acabará la carta, pero sí a qué oficina debe llegar y cuál es el siguiente tramo. Si alguien puede cambiar las instrucciones de reparto, el paquete llega a otro sitio sin que el remitente lo note.

IP proporciona direccionamiento lógico y entrega de datagramas entre redes. Es un servicio sin conexión y de mejor esfuerzo: no garantiza que el paquete llegue ni que llegue en orden. Esa falta de garantías es una decisión de diseño, no un defecto; las garantías se añaden en capas superiores o en la aplicación.

## Qué decide la capa 3

Un host compara la dirección de destino con su prefijo. Si el destino está en su misma subred, entrega la trama en el enlace local; si está fuera, la envía a su puerta de enlace. A partir de ahí, cada router consulta su tabla y reenvía hacia el siguiente salto.

Las direcciones IP de origen y destino describen la conversación extremo a extremo. Las direcciones MAC corresponden al enlace local y cambian en cada salto. Confundir ambas cosas lleva a buscar un problema de encaminamiento donde hay una resolución de vecino, o al contrario.

## La tabla de rutas y su confianza

Una tabla de rutas puede contener:

- **Rutas directamente conectadas**, creadas al configurar una interfaz.
- **Rutas estáticas**, añadidas a mano.
- **Rutas dinámicas**, aprendidas de otros routers.
- **Una ruta por defecto**, que se usa cuando no coincide otra más específica.

Cada tipo tiene una superficie distinta. Una ruta estática es predecible, pero si nadie la revisa puede enviar tráfico a un sitio que ya no existe. Una ruta dinámica se adapta, pero acepta información de los vecinos: si un router no autorizado inyecta rutas, puede desviar tráfico o absorberlo.

Por eso, en una red bastionada, los protocolos de enrutamiento se autentican y se limita qué routers pueden participar. La pregunta no es solo «¿llega el paquete?», sino «¿quién decidió que llegara por ahí?».

## Filtrar en el borde

La tabla de rutas decide el camino; las listas de control de acceso y el cortafuegos deciden si el paquete tiene derecho a pasar. Son decisiones complementarias:

- El router encamina lo que su tabla permite.
- La ACL filtra por origen, destino, protocolo y puerto, y se evalúa de arriba abajo: la primera coincidencia decide.
- El cortafuegos añade estado y, según el modelo, inspección de aplicación.

Una red con rutas correctas y sin filtrado sigue siendo una red plana a efectos de seguridad. La separación de subredes no bloquea nada por sí sola; el bloqueo aparece cuando una regla lo ordena. El detalle de ACL, NAT y su lógica está en [Enrutamiento avanzado, ACL y seguridad de la red](../redes/enrutamiento-acl-y-seguridad.md).

## ICMP y el diagnóstico

ICMP comunica errores y mensajes de control: destino inalcanzable, tiempo excedido, eco para comprobar si un equipo responde. Es útil para diagnosticar y también para descubrir una red. Bloquearlo por completo rompe funciones legítimas —el descubrimiento de MTU, por ejemplo—; permitirlo sin límites facilita el reconocimiento.

La decisión razonable es permitir los tipos necesarios y restringir el resto según la zona. Un equipo de usuario no necesita responder a todo lo que le pregunten desde Internet.

## IPv6: las mismas preguntas, otras reglas

IPv6 usa direcciones de 128 bits, cabecera base de longitud fija y cabeceras de extensión. No emplea difusión: usa multicast y el descubrimiento de vecinos, parte de ICMPv6, para encontrar equipos y routers. Los routers IPv6 no fragmentan en tránsito; si hace falta fragmentar, lo hace el origen.

Para el bastionado, dos consecuencias:

- El descubrimiento de vecinos cumple el papel de ARP. Un equipo que responde por otro puede redirigir el tráfico, igual que en IPv4.
- Los anuncios de router configuran la puerta de enlace de los clientes. Si un equipo no autorizado los envía, puede colocarse en medio. Hay que controlar quién puede anunciar.

IPv6 no es «IPv4 con más números». Tiene sus propios mecanismos y sus propias comprobaciones.

## MTU y fragmentación

La MTU es el tamaño máximo que un enlace transporta sin fragmentar. IPv4 permite fragmentar y marca con campos si se autoriza y en qué posición va cada trozo. La fragmentación innecesaria complica el filtrado y consume recursos; conviene ajustar la MTU del camino.

Un cortafuegos que descarta todos los fragmentos puede romper tráfico legítimo, y uno que los acepta sin analizar deja pasar partes de un ataque troceado. La política se decide, no se improvisa.

## Procedimiento para seguir un paquete

1. Compara la dirección de destino con el prefijo local.
2. Si está en la misma subred, entrega en el enlace local; resuelve la MAC con ARP o NDP.
3. Si está fuera, entrega a la MAC de la puerta de enlace.
4. En cada router, consulta la tabla y elige la ruta más específica.
5. Comprueba qué ACL o regla de cortafuegos actúa en ese tramo.
6. Repite hasta la red de destino y anota dónde cambia el camino.

## Ejemplo

Un equipo `10.1.2.15/24` quiere llegar a `10.1.3.40`. No pertenece a su subred, así que envía la trama a su router. El router tiene una ruta hacia `10.1.3.0/24` por la interfaz correcta y una regla que permite el puerto solicitado. El paquete llega. Si la regla no existiera, el router seguiría sabiendo el camino, pero el tráfico se descartaría: la conectividad y el permiso son cosas distintas.

## Errores que se repiten

- Creer que una ruta correcta implica permiso para pasar.
- Aceptar rutas dinámicas de cualquier vecino.
- Bloquear todo ICMP y romper el diagnóstico y el descubrimiento de MTU.
- Ignorar los anuncios de router en IPv6.
- Filtrar por dirección MAC en lugar de por identidad.
- Revisar la tabla de rutas y no revisar el orden de las ACL.

## Fuentes

- RFC 791 (IPv4), RFC 8200 (IPv6), RFC 1812 (requisitos de routers IPv4), RFC 4861 (descubrimiento de vecinos), RFC 826 (ARP) y RFC 792 (ICMP).
- IEEE 802.1Q para el contexto de segmentación local.
