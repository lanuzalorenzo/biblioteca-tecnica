# Comunicación inalámbrica

Una red cableada empieza en una puerta: para escuchar hay que entrar y conectar algo. Una red Wi-Fi no tiene esa puerta, porque la señal atraviesa paredes y llega a la calle, y cualquiera con una antena recibe lo que se transmite a su alrededor. Por eso empiezo toda auditoría inalámbrica por el medio y no por la contraseña: lo que no se puede cerrar con una puerta hay que protegerlo dentro del paquete.

## El aire es un medio compartido

En Ethernet cada equipo tiene su cable hasta el conmutador y la señal viaja por un medio que alguien tendría que tocar para escuchar. En Wi-Fi el medio es el aire y lo comparten todos los dispositivos de la zona: cuando una radio transmite, cualquier receptor a su alcance recibe la señal, sea o no el destinatario. Escuchar no emite nada, así que nadie puede saber que hay un observador.

Esa diferencia explica casi todo lo demás. La red cableada puede defender el acceso físico; la inalámbrica no, y debe defender el contenido y la identidad de los participantes con criptografía.

Compartir el aire obliga además a ordenar quién habla. En radio no se detecta una colisión mientras se transmite, porque la propia señal tapa la de los demás. De ahí que Wi-Fi use CSMA/CA (*Carrier Sense Multiple Access with Collision Avoidance*): se escucha el canal, se espera un tiempo aleatorio si está ocupado y se pide confirmación de cada trama. Dos consecuencias prácticas: el rendimiento real queda por debajo del nominal, y un observador también oye confirmaciones y tiempos de espera.

## Bandas, canales y generaciones

Wi-Fi es el nombre comercial de la familia IEEE 802.11. La banda de 2,4 GHz tiene más alcance y penetra mejor las paredes, pero el número de canales sin solapar depende del país: en el plan de EE. UU. son tres (1, 6 y 11) y en España, con 13 canales, el plan habitual es 1, 5, 9 y 13. Además comparte espectro con microondas, Bluetooth y otros equipos. La de 5 GHz ofrece más canales y menos interferencias, con menos alcance, y parte de ella exige ceder el canal si se detecta un radar (DFS, *Dynamic Frequency Selection*). La de 6 GHz llegó con Wi-Fi 6E. Canales y potencias dependen del país: no se configura lo mismo en cualquier dominio regulatorio.

| Estándar | Nombre comercial | Bandas | Año aprox. | Rasgo |
|---|---|---|---|---|
| 802.11b | — | 2,4 GHz | 1999 | Hasta 11 Mb/s; nació con WEP |
| 802.11a | — | 5 GHz | 1999 | Poco extendido entonces |
| 802.11g | — | 2,4 GHz | 2003 | Hasta 54 Mb/s |
| 802.11n | Wi-Fi 4 | 2,4 y 5 GHz | 2009 | Introduce MIMO |
| 802.11ac | Wi-Fi 5 | 5 GHz | 2013 | Más velocidad por usuario |
| 802.11ax | Wi-Fi 6 y 6E | 2,4, 5 y 6 GHz | 2019 y 2021 | Eficiencia en entornos densos |
| 802.11be | Wi-Fi 7 | 2,4, 5 y 6 GHz | 2024 | Canales muy anchos |

La velocidad del estándar y la seguridad configurada son cosas distintas. Un punto de acceso Wi-Fi 6 puede estar mal protegido y un equipo 802.11g puede ir con WPA2. La seguridad se negocia al asociarse, no la impone la generación del hardware.

## Elegir canal no es elegir seguridad

El canal y el ancho de banda dicen cómo se reparte el espectro, no cuánto se protege lo que viaja por él. En 2,4 GHz, el plan de canales de 20 MHz que no se pisan depende del dominio regulatorio: 1, 6 y 11 en EE. UU.; 1, 5, 9 y 13 en España. Conviene fijarlo en lugar de dejar que los equipos se solapen. En 5 GHz hay más margen, pero los canales anchos de 80 y 160 MHz ocupan más espectro, sufren más interferencia y tardan más en ceder ante un radar. Un plan de canales ordenado mejora disponibilidad y rendimiento; ninguna combinación de canales sustituye al cifrado.

## Vocabulario de una red de infraestructura

En una red de infraestructura las estaciones se conectan a través de un punto de acceso. El conjunto de un AP y sus estaciones es un BSS, y su identificador es el BSSID, que en la práctica es la MAC de la radio del AP. El nombre que ve el usuario es el SSID. Varios AP con el mismo SSID y la misma red cableada forman un ESS, que permite moverse por el edificio cambiando de AP (*roaming*) sin perder la conexión.

| Término | Qué es | Por qué importa en una auditoría |
|---|---|---|
| STA (estación) | Dispositivo con radio Wi-Fi | Objetivo de los ataques dirigidos al cliente |
| AP (punto de acceso) | Equipo que une las estaciones con la red cableada | Pieza que se suplanta o se ataca |
| BSSID | Identificador de 48 bits del AP; su MAC de radio | Identifica el equipo, y se puede falsear |
| SSID | Nombre legible de la red, hasta 32 octetos | No autentica: dos AP pueden llamarse igual |
| ESS | Varios AP con el mismo SSID | Base del roaming y de la suplantación |
| Canal | Frecuencia que usa la red | Un capturador escucha uno cada vez |

El SSID no es único ni autentica: cualquiera puede emitir un AP con el nombre que quiera. Ocultarlo o filtrar por MAC tampoco son medidas de seguridad. El nombre reaparece cuando un cliente legítimo se conecta y las MAC viajan en claro, así que un observador paciente aprende cuáles están autorizadas y puede imitarlas. Un SSID oculto, además, obliga a los móviles a preguntar por él en todas partes y revela qué redes conocen.

## Qué ocurre cuando un dispositivo se conecta

Las tramas 802.11 se agrupan en gestión (anunciar, asociarse, desconectarse), control (confirmaciones y reservas de canal) y datos. Solo se cifra la carga útil de las de datos, y ni siquiera entera: la cabecera con las MAC, la duración y el número de secuencia va siempre en claro, porque la radio necesita leerla antes de descifrar.

La secuencia habitual es esta:

1. El AP emite un beacon cada 102,4 ms aproximadamente con su SSID, canal, velocidades y el elemento de seguridad (RSN). Un equipo puede escuchar beacons (escaneo pasivo) o enviar una petición de sondeo y recibir respuesta (escaneo activo).
2. La estación elige la red y hace la autenticación 802.11. En las redes modernas de clave compartida esta fase es un trámite sin valor criptográfico; en WPA3 transporta el intercambio SAE.
3. Sigue la asociación: la estación declara qué cifrados soporta y el AP le asigna un identificador.
4. Si la red está protegida, se negocia la clave: el handshake de cuatro mensajes en WPA y WPA2, o el intercambio SAE en WPA3. Los detalles están en [Protocolos de seguridad Wi-Fi](protocolos-de-seguridad-wifi.md).
5. Los datos viajan cifrados hasta que una de las partes envía una desasociación o desautenticación.

| Tipo | Ejemplos | ¿Se cifra? | Qué revela |
|---|---|---|---|
| Gestión | Beacon, sondeo, autenticación, asociación, desautenticación | No, salvo con PMF y solo en parte | Redes presentes, seguridad configurada, quién se conecta |
| Control | ACK, RTS, CTS | No | Quién recibe tráfico y cuánto |
| Datos | Tráfico IP y tramas EAPOL del handshake | Carga útil sí; cabecera no | Metadatos siempre; contenido solo con la clave |

De la tabla salen dos ideas. Primera: aunque no se lea el contenido, un observador ve metadatos —qué equipos hay, con quién hablan, en qué horario, cuánto tráfico mueven y qué seguridad usa cada red—, que es el material del [reconocimiento](fases-de-un-ataque.md) pasivo. Segunda: como las tramas de gestión no están autenticadas, cualquiera puede fabricar una desautenticación con la dirección del AP o del cliente y el receptor la obedece. Eso expulsa a un cliente y, lo que interesa más, lo obliga a reconectarse y repetir el handshake mientras se escucha.

La defensa es la enmienda 802.11w o PMF (*Protected Management Frames*), que protege las tramas de gestión robustas una vez establecida la asociación. En WPA2 es opcional; en WPA3 es obligatoria. Los beacons anteriores a la asociación quedan fuera, aunque revisiones posteriores añaden su protección.

## Un caso: la terraza de la esquina

Una cafetería ficticia ofrece dos redes: «Bar Ejemplo» con WPA2 y «Bar Ejemplo Invitados» abierta. Desde la acera, con la tarjeta en modo monitor y sin enviar nada, se ven los dos BSSID, sus canales y su potencia, los clientes asociados y las desautenticaciones que ocurren. No hace falta contraseña para saber cuántos equipos hay, a qué hora llega el personal ni qué red usa cada uno. Si la red principal no usa PMF, además se puede expulsar a un cliente y esperar a que se reconecte para capturar el handshake. La defensa no es esconder el nombre: es PMF, una contraseña larga, WPA3 si el equipo lo permite y separar la red de invitados de la de gestión.

## Por qué importa a quien defiende

- **Inventario.** Un mapa de SSID, BSSID, canal, seguridad y potencia permite detectar AP no autorizados y equipos que anuncian una seguridad peor que la del resto.
- **AP falsos.** Un SSID legítimo emitido desde un equipo ajeno es indistinguible para el usuario; solo el BSSID y la configuración esperada permiten notarlo.
- **Desautenticaciones.** Si la red no usa PMF, un tercero puede cortar conexiones a voluntad. Conviene tratarlo como riesgo real y no como molestia.
- **Canales.** Un plan de canales sensato evita solapamientos y deja menos margen a la interferencia maliciosa.
- **Controles que no son controles.** Ocultar el SSID y filtrar por MAC no protegen; si aparecen como medida en un informe, hay que corregir la recomendación.
- **Metadatos.** El cifrado no oculta la existencia ni los patrones de la comunicación. Si eso importa, se protege en capas superiores.

## Errores frecuentes

- Creer que ocultar el SSID o filtrar por MAC protege la red.
- Confundir la velocidad del estándar con la seguridad configurada.
- Pensar que el cifrado oculta también la existencia y los metadatos de la comunicación.
- Suponer que un SSID identifica a un AP: lo que lo identifica es el BSSID.
- Olvidar que un capturador escucha un solo canal cada vez.
- Interpretar una desautenticación como fallo del cliente sin mirar si la red usa PMF.

## Glosario

| Término | Definición |
|---|---|
| CSMA/CA | Acceso al medio que escucha antes de transmitir y evita colisiones con esperas y confirmaciones. |
| BSS | Conjunto formado por un punto de acceso y sus estaciones. |
| BSSID | Identificador del BSS; en la práctica, la MAC de la radio del punto de acceso. |
| SSID | Nombre de la red que ve el usuario. |
| ESS | Varios BSS con el mismo SSID sobre la misma red cableada. |
| MIMO | Uso de varias antenas para transmitir y recibir a la vez. |
| DFS | Mecanismo que obliga a ceder el canal si se detecta un radar. |
| Beacon | Trama periódica con la que el punto de acceso anuncia la red. |
| PMF | Protección de las tramas de gestión (802.11w). |
| RSN | Conjunto de capacidades de seguridad que anuncia la red; en WPA2, el elemento que declara el cifrado y la autenticación. |
| SAE | Intercambio de autenticación simultánea de WPA3, que sustituye al handshake de contraseña. |
| RTS/CTS | Intercambio que reserva el medio antes de una transmisión. |

## Fuentes

- IEEE 802.11 y enmienda 802.11w, tramas de gestión protegidas.
- Wi-Fi Alliance, documentación pública de generaciones y certificación.
