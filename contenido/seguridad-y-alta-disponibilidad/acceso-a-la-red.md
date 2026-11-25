# Seguridad activa: el acceso a la red

Una red plana es un pasillo único: quien entra por cualquier puerta llega a todas las habitaciones. Segmentar es poner puertas intermedias y decidir quién tiene llave de cada una; sin eso, comprometer un puesto de trabajo es comprometer el servidor que está al lado.


## La red cableada

El diseño de partida es en estrella: cada equipo se conecta a un puerto del switch, y el switch decide por dónde reenvía cada trama. Eso concentra el control en un solo punto y también el riesgo.

- **Protección física del switch:** armario cerrado, fuera del alcance de quien no administra.
- **Protección lógica:** solo el administrador accede a su configuración; el resto, por una VLAN de gestión separada y con contraseña.
- **Control de puertos:** saber qué equipo entra por cada boca y desactivar las que no se usan. Un latiguillo olvidado en una sala de espera es una entrada libre.

## VLAN

Una VLAN divide un switch en varias redes lógicas independientes. Los equipos de la misma VLAN se hablan sin restricción; los de VLAN distintas, solo si algo enruta entre ellas.

- **Puerto de acceso:** pertenece a una sola VLAN y sirve a un equipo final.
- **Puerto troncal:** transporta varias VLAN a la vez. En IEEE 802.1Q, cada trama lleva una etiqueta de 4 bytes con el identificador de VLAN; el margen utilizable es 1–4094.
- **VLAN nativa:** la que viaja sin etiquetar en el troncal. Cambiarla por defecto y no usarla para tráfico de usuarios evita que una trama sin etiqueta termine donde no debe.

Segmentar reduce el dominio de difusión —menos tráfico, menos alcance de un fallo— y permite restringir qué VLAN se habla con cuál en el router. Lo que **no** hace es cifrar ni autenticar: un portátil conectado a la VLAN de invitados sigue siendo un portátil desconocido.

En 2015 se practicó con VTP, el protocolo de Cisco que propaga la lista de VLAN entre switches. Sigue existiendo, pero un VTP mal configurado propaga también los borrados: hoy se prefiere configuración declarativa por equipo o herramientas de gestión central.

## Control de acceso al puerto

Tres medidas convierten un puerto en algo defendible:

- **Seguridad de puerto:** limita cuántas MAC se aprenden por boca y qué MAC se aceptan; la violación puede descartar tramas, avisar o apagar el puerto. Frena el cambio de equipo y la conexión de un switch no autorizado.
- **DHCP snooping:** solo el servidor legítimo puede repartir direcciones; el resto de puertos no pueden ofrecer DHCP. Evita que un equipo se declare servidor y reparta una puerta de enlace falsa.
- **Inspección de ARP:** valida que las respuestas ARP correspondan a una asignación DHCP legítima. Sin esto, envenenar la tabla ARP de la red es trivial.

## 802.1X: la red que pide identidad

En lugar de confiar en el puerto, se pide autenticación antes de dar acceso:

1. **Suplicante:** el equipo que quiere entrar, con un cliente 802.1X.
2. **Autenticador:** el switch o el punto de acceso, que no deja pasar tráfico hasta que alguien le autorice.
3. **Servidor de autenticación:** normalmente RADIUS, que valida contra un directorio.

Los métodos de EAP más usados son **EAP-TLS**, con certificado en el cliente y en el servidor —el más sólido y el que exige más administración—, **PEAP** y **EAP-TTLS**, que montan un túnel TLS y validan usuario y contraseña dentro. La práctica del módulo montó un servidor RADIUS con wifi y un Windows 7 como cliente: el esquema es el correcto, las versiones no —hoy se hace con FreeRADIUS o NPS vigente y con certificados SHA-256.

## Wifi

- **WPA2-Enterprise** con 802.1X y CCMP/AES es el mínimo aceptable en una organización: cada usuario con su credencial y su registro.
- **WPA2-Personal** comparte una única contraseña; sirve para casa, no para una empresa donde no se puede saber quién entró.
- **WPA3** sustituye el intercambio de la contraseña por SAE, que impide el ataque de diccionario sobre la clave de red, y añade cifrado de tramas en redes abiertas.
- **WEP y TKIP están roídos** —uno por diseño, el otro por ataques prácticos—. Encontrar una red con WEP es un hallazgo, no una configuración.
- **Ocultar el SSID no protege nada:** el nombre viaja en cada respuesta de los clientes y cualquier analizador lo ve. Filtra la falsa sensación de seguridad, no el acceso.

## El proxy

Un proxy intermedio tiene dos usos distintos y conviene no confundirlos:

- **Proxy directo:** los clientes le piden a él las páginas y él las descarga. Permite autenticar, filtrar por categoría, cachear y registrar quién visitó qué. Es el que se montó en el módulo con Squid sobre Ubuntu.
- **Proxy inverso:** está delante de los servidores propios, reparte carga, termina TLS y protege la aplicación del exterior.

El registro del proxy es a la vez control y problema: guarda hábitos de navegación de personas identificadas, así que su retención y acceso se deciden con criterio jurídico, no solo técnico.

## Segmentación que sí sirve

Un diseño razonable separa, como mínimo: la **VLAN de gestión** de los dispositivos de red, los **servidores**, los **puestos de trabajo**, los **invitados** —sin acceso a la red interna— y una **DMZ** para lo que se publica hacia Internet. Lo que se publica no debe compartir segmento con lo que se protege.

## Lo que se comprueba

Que un equipo de invitados no alcanza ningún recurso interno aunque su puerto esté activo; que un equipo sin credenciales 802.1X no obtiene dirección; que el troncal entre switches solo transporta las VLAN declaradas; y que el proxy registra la salida con el usuario autenticado, no con la IP a secas.

## Errores que se repiten

- Creer que ocultar el SSID o filtrar por MAC protege la wifi: las dos cosas se saltan en minutos.
- Dejar la VLAN de gestión compartiendo puerto con usuarios.
- Poner el proxy sin autenticación y creer que el registro identifica a alguien.
- Publicar un servicio en la misma red que los servidores internos en lugar de en una DMZ.

## Fuentes

- IEEE 802.1Q (VLAN y etiquetado) y 802.1X (control de acceso a la red).
- IEEE 802.11i (WPA2) y la enmienda de WPA3.
- RFC 2865 y 2866 (RADIUS).
- Documentación oficial de Squid y de FreeRADIUS.
