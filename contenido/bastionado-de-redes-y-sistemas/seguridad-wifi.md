# Seguridad en redes inalámbricas

Una red sin cables no tiene puerta: la señal sale del edificio y llega a la calle, al portal de enfrente y al coche aparcado. Por eso, cuando alguien dice que su wifi es segura porque el nombre no aparece, la respuesta es que el nombre no es una cerradura. Lo que separa a un invitado de un empleado es el cifrado y la forma de autenticarse.

La configuración de WPA2-Enterprise, 802.1X y la separación de invitados también aparece en [El acceso a la red](../seguridad-y-alta-disponibilidad/acceso-a-la-red.md). Este apunte se ocupa de lo propio del aire: tramas, cifrados, WPS y ataques.

## Nombres y estructura

| Término | Qué es |
|---|---|
| SSID | Nombre de la red que el punto de acceso anuncia |
| BSSID | Dirección MAC del punto de acceso |
| ESSID | Nombre de la red extendida con varios puntos de acceso |
| BSS | Un punto de acceso con sus clientes |
| ESS | Varios puntos de acceso coordinados, como en un aeropuerto |

Esconder el SSID no impide que un analizador lo descubra: los clientes lo mencionan al asociarse. La medida da tranquilidad, no seguridad.

Hay dos formas de organizar la red. En **infraestructura**, un punto de acceso centraliza las conexiones; es el esquema de una casa, una oficina o una ciudad. En **ad-hoc**, los dispositivos se hablan directamente sin punto de acceso; hoy es un caso residual.

Las **tramas** se agrupan en gestión, control y datos. Las de gestión —beacon, sondeo, asociación— anuncian el nombre, el cifrado, el canal, la MAC y el fabricante sin pedir credenciales. Con ellas basta para inventariar lo que hay alrededor.

Las **bandas** no son equivalentes. La de 2,4 GHz atraviesa más paredes y ofrece menos velocidad; la de 5 GHz hace lo contrario; la de 6 GHz suma espectro y reduce interferencias. Los canales se reparten para que no se pisen.

## La debilidad del medio

En una red cableada, para escuchar hay que estar dentro del edificio. En una wifi, basta una antena y algo de paciencia. El intruso puede capturar, intentar asociarse y, en muchos casos, pasar desapercibido. A eso se añade que muchos equipos salen de fábrica sin cifrado o con una clave común para todos.

El filtrado por MAC se salta cambiando la dirección de la tarjeta. Sirve para ordenar un inventario, no para decidir quién entra.

## Cifrados

| Protocolo | Año | Cifrado | Estado |
|---|---:|---|---|
| WEP | 1999 | RC4 con IV corto | Roto; se rompe con paquetes capturados |
| WPA | 2003 | TKIP | Obsoleto; puente hacia WPA2 |
| WPA2 | 2004 | AES-CCMP (802.11i) | Aceptable si se desactiva TKIP |
| WPA3 | 2018 | AES-CCMP con SAE | Recomendado |

WEP no exige fuerza bruta: acumulando tráfico, la clave acaba saliendo. WPA sustituyó la clave fija por una por paquete mediante TKIP, pero el diseño arrastraba los defectos de WEP y hoy no se recomienda. WPA2 con AES es el mínimo defendible. WPA3 introduce SAE, que impide el ataque de diccionario sin conexión contra el handshake, y obliga a proteger las tramas de gestión, lo que dificulta la desautenticación.

WPA3 no es una simple revisión de WPA2. WPA2 tuvo KRACK en 2017, corregido en la mayoría de equipos, y WPA3 ha tenido fallos de implementación que también se han corregido. La elección sensata es WPA3 donde el parque lo soporte y WPA2-AES sin TKIP donde no.

## WPS

WPS permite conectar un equipo con un PIN de ocho dígitos en vez de escribir la contraseña. El PIN se comprueba en dos mitades, así que el espacio real de búsqueda se reduce a unas once mil combinaciones: unas horas de prueba. En chips vulnerables, el ataque *Pixie Dust* lo resuelve aún más rápido. No hay configuración segura de WPS: se desactiva.

## Ataques y defensas

| Ataque | En qué consiste | Defensa |
|---|---|---|
| Punto de acceso falso (*evil twin*) | Se anuncia un SSID igual al legítimo para capturar credenciales | Certificados en enterprise, PMF, formación, WIPS |
| Desautenticación | Se expulsa a los clientes con tramas falsas para capturar el handshake | PMF (WPA3), monitorización |
| Hombre en el medio | El atacante se coloca entre cliente y red | Cifrado de extremo a extremo, no solo wifi |
| Suplantación de DHCP | Se entrega una puerta de enlace falsa | DHCP snooping, control de puertos |
| Denegación de servicio | Se satura el espectro o el punto de acceso | Cobertura redundante, detección |

## Empresa e invitados

Una organización no debería repartir una clave única entre toda la plantilla. El modelo es **WPA-Enterprise**: cada persona se autentica con su cuenta por 802.1X contra un servidor RADIUS, y la sesión usa una clave distinta. Se gana identificación individual y la posibilidad de revocar a una persona sin cambiar la wifi a todos. El coste es un servidor, certificados y configuración en los clientes.

Las visitas necesitan otra red, sin acceso a la interna, con portal cautivo y caducidad. Mezclarlas con los empleados convierte una visita en un miembro más de la red.

## Qué comprobar

- ¿WPA3 o WPA2-AES, sin TKIP ni WEP?
- ¿WPS desactivado en todos los puntos de acceso?
- ¿La red de invitados está separada de la corporativa?
- ¿La administración del punto de acceso no es accesible por wifi y usa contraseña propia?
- ¿El firmware está actualizado y se revisa?
- ¿Se mira el registro del punto de acceso para detectar clientes desconocidos?

## Errores que se repiten

- Confiar en ocultar el SSID o en una lista de MAC.
- Mantener WPS por comodidad para conectar la impresora.
- Repartir una sola clave y llamarlo red corporativa.
- Publicar la administración del punto de acceso en la misma wifi.
- Auditar una red ajena sin autorización y llamarlo prueba de seguridad.

## Fuentes

- IEEE 802.11i y Wi-Fi Alliance: WPA2 y WPA3.
- OWASP. *Wireless Security Cheat Sheet*.
- INCIBE. Guías y seminarios de seguridad wifi.
- RFC 3227, *Guidelines for Evidence Collection and Archiving*.
