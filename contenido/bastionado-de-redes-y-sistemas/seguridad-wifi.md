# Seguridad en redes inalámbricas

Una red sin cables no tiene puerta: la señal sale del edificio y llega a la calle, al portal de enfrente y al coche aparcado. Por eso, cuando alguien dice que su wifi es segura porque el nombre no aparece, la respuesta es que el nombre no es una cerradura. Lo que separa a un invitado de un empleado es el cifrado y la forma de autenticarse.

Los cifrados, las tramas y los ataques habituales se explican en [El acceso a la red](../seguridad-y-alta-disponibilidad/acceso-a-la-red.md). El detalle ofensivo, con el handshake, PMKID y la captura, está en [Protocolos de seguridad Wi-Fi](../hacking-etico/protocolos-de-seguridad-wifi.md) y [Comunicación inalámbrica](../hacking-etico/comunicacion-inalambrica.md). Este apunte se queda con la configuración defendible: qué se exige, qué se separa y qué se revisa.

## El mínimo aceptable

- **WPA3** donde el parque lo soporte; **WPA2-AES** sin TKIP donde no.
- **WEP y WPA/TKIP** no son una opción: se consideran roídos y su presencia es un hallazgo.
- **WPS desactivado** en todos los puntos de acceso.
- **Protección de tramas de gestión** (PMF) activa donde esté disponible.
- **Firmware actualizado** y administración fuera de la red wifi.
- **Contraseña de administración propia**, distinta de la clave de la red.

Una red que cumple esto sigue siendo vulnerable a un punto de acceso falso, pero al menos no entrega la clave a quien pase por la calle.

## Decisiones de diseño

| Decisión | Opción defendible | Motivo |
|---|---|---|
| Autenticación de empleados | WPA-Enterprise con 802.1X y RADIUS | Identidad individual y revocación por persona |
| Red de invitados | VLAN separada, portal cautivo y caducidad | Sin acceso a la red interna |
| Administración del AP | VLAN de gestión y acceso restringido | La wifi no debe ser la puerta de la administración |
| Ubicación de los AP | Cobertura hacia dentro, no hacia la calle | Menos exposición innecesaria |
| Inventario | Un registro por AP, con dueño y ubicación | Sin inventario no hay revisión posible |

WPA-Enterprise no es solo «más seguro»: es lo que permite saber quién entró. Una clave compartida para toda la plantilla da comodidad y elimina la trazabilidad.

## Riesgos que no se arreglan con cifrado

- **Punto de acceso falso.** Alguien anuncia el mismo nombre de red y los clientes se conectan. La defensa pasa por certificados en enterprise, PMF, formación y detección de AP no autorizados.
- **Desautenticación.** Tramas falsas expulsan a los clientes para capturar el handshake. PMF y monitorización reducen el margen.
- **Suplantación de DHCP.** Un equipo entrega una puerta de enlace falsa; DHCP snooping y control de puertos lo frenan.
- **Filtrado por MAC.** Se salta cambiando la dirección de la tarjeta; sirve para inventario, no para autenticar.
- **Ocultar el SSID.** El nombre viaja en las tramas de los clientes; no protege.

El cifrado protege el contenido del enlace, no la identidad del punto de acceso ni la del cliente.

## Auditoría autorizada

Comprobar una wifi ajena sin permiso no es una prueba de seguridad: es una intromisión. La auditoría se hace sobre redes propias o con autorización escrita y alcance definido.

Dentro de ese alcance, la revisión mínima:

1. Inventariar los AP y comprobar que todos están en la lista.
2. Verificar cifrado, WPS y PMF en cada uno.
3. Comprobar que la red de invitados no alcanza la interna.
4. Revisar la administración: VLAN, contraseña y acceso.
5. Buscar AP no autorizados o SSID parecidos al corporativo.
6. Revisar registros de asociación y clientes desconocidos.

## Operación

La wifi cambia con el firmware y con las personas. Un AP que se instaló para una feria y se quedó encendido es una puerta que nadie recuerda. El inventario, la revisión de firmware y la retirada de configuraciones antiguas forman parte del control.

También conviene revisar la rotación de la clave de invitados y la caducidad de sus accesos. Una red de visitas con la misma contraseña durante años deja de ser una red de visitas.

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

- IEEE 802.11 (tramas de gestión y control), IEEE 802.11i (WPA2) y Wi-Fi Alliance (WPA3).
- OWASP. *Wireless Security Cheat Sheet*.
- INCIBE. Guías y seminarios de seguridad wifi.
