# DHCP: direcciones sin intervención

Configurar una dirección IP a mano en cada equipo funciona con tres; con trescientos es una fábrica de errores: dos equipos con la misma dirección, una puerta de enlace mal escrita, un portátil que se lleva la configuración de la oficina a casa. DHCP existe para que la red entregue la configuración y la retire cuando ya no hace falta.


## Qué entrega y a quién

Un servidor DHCP entrega a cada cliente, como mínimo, una dirección IP, la máscara, la puerta de enlace y uno o varios servidores DNS. Puede añadir el dominio de búsqueda, servidores NTP, la duración del alquiler y opciones específicas del fabricante.

El cliente no siempre es un ordenador: también piden configuración impresoras, teléfonos IP, puntos de acceso, cámaras y hasta máquinas virtuales. Cada tipo puede necesitar opciones distintas, y eso se resuelve con **clases** o con reservas.

## El intercambio DORA

La asignación tiene cuatro mensajes:

1. **Discover:** el cliente, sin dirección, pregunta en difusión si hay algún servidor.
2. **Offer:** el servidor propone una dirección y su configuración.
3. **Request:** el cliente pide formalmente esa oferta.
4. **Ack:** el servidor confirma el alquiler.

El alquiler tiene un plazo —la *lease*— y se renueva a la mitad y a las siete octavas partes del plazo (T1 y T2). Si el cliente desaparece, la dirección vuelve al conjunto cuando caduca. Por eso no se reserva una dirección «para siempre» sin motivo: se agota el ámbito y aparecen clientes sin red.

## Ámbito, exclusiones y reservas

El **ámbito** o *scope* es el rango de direcciones que el servidor puede repartir en una subred, con su máscara, puerta de enlace y DNS. Dentro se definen:

- **Exclusiones:** direcciones que no se reparten porque están asignadas a routers, servidores, impresoras o equipos de administración.
- **Reservas:** una dirección fija para un cliente concreto, identificado por su dirección MAC o por su identificador de cliente. Es la forma de dar IP estable a un servidor sin configurarla a mano.
- **Concesiones:** el tiempo de alquiler. Corto en redes con muchos equipos itinerantes; más largo en una red estable.

La reserva no es una configuración estática: el cliente sigue pidiendo por DHCP y el servidor le devuelve siempre la misma dirección. Si el cliente cambia de tarjeta de red, cambia la MAC y la reserva deja de aplicarse.

## Varios segmentos: el relay

DHCP usa difusión, y la difusión no cruza un router. En una red con varias subredes, el router actúa como **relay** (DHCP relay o helper): recibe la petición del cliente, la reenvía al servidor indicando de qué subred viene, y devuelve la respuesta. El servidor tiene un ámbito por subred y elige el adecuado por la dirección de origen del relay.

Sin relay, cada subred necesitaría su propio servidor. Con relay, un solo servidor —o dos en alta disponibilidad— atiende toda la organización.

## Seguridad

DHCP no autentica al cliente ni al servidor por defecto. Eso abre dos riesgos:

- **Servidor pirata:** alguien conecta un servidor DHCP falso y reparte una puerta de enlace propia para interceptar el tráfico. Se combate con **DHCP snooping** en el conmutador: solo los puertos autorizados pueden enviar ofertas.
- **Cliente que se hace pasar por otro:** agota el ámbito o pide una reserva ajena. El snooping y la inspección de ARP ayudan; la reserva por MAC no es una autenticación fuerte.

También conviene registrar las concesiones y alertar cuando el ámbito se llena: un ámbito agotado deja a los clientes nuevos sin red y suele avisar de un problema mayor.

## IPv6

IPv6 puede funcionar sin DHCP: los equipos se autoconfiguran con **SLAAC** a partir de los anuncios del router. DHCPv6 sigue siendo útil para repartir DNS, dominio y direcciones concretas. En una red mixta hay que decidir qué se entrega por router y qué por DHCPv6 para no duplicar ni contradecir la configuración.

## Diagnóstico

Cuando un cliente no obtiene dirección: comprobar que el ámbito tiene libres, que la exclusión no cubre su MAC, que el relay apunta al servidor correcto y que el cortafuegos deja pasar el puerto 67/68. En el cliente, renovar la concesión y mirar los registros del servidor. Un «no tengo red» que se arregla al reconectar suele ser un ámbito agotado o un relay mal configurado.

## Lo que se comprueba

Que el ámbito no reparte direcciones reservadas; que las reservas coinciden con los equipos que deben tener IP fija; que el tiempo de alquiler es razonable; que hay relay en las subredes remotas; que el snooping está activo en los puertos de usuario; y que el registro de concesiones permite saber quién tenía qué dirección y cuándo.

## Fuentes

- RFC 2131, Dynamic Host Configuration Protocol.
- RFC 8415, Dynamic Host Configuration Protocol for IPv6.
- Documentación de ISC DHCP y Kea, y de Microsoft Windows Server DHCP.
- Orden EDU/392/2010, de 20 de enero (BOE-A-2010-3028).
