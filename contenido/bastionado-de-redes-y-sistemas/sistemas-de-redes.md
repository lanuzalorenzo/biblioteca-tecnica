# Los sistemas de redes

Una red se parece al sistema de reparto de una ciudad: hay calles locales que unen edificios cercanos, vías rápidas que conectan barrios y normas comunes para que un paquete no se pierda ni llegue dos veces. Cambian la escala y el medio, pero la idea es la misma: poner en contacto puntos que, sin esa infraestructura, estarían aislados.

Para bastionar hay que saber qué pieza toma cada decisión. No se protege igual un puerto de switch que una ruta, un nombre de dominio o una sesión de aplicación. Este apunte sirve de mapa; el detalle de conmutación y de direccionamiento está en [Redes y conmutación](../redes/README.md).

## Capas: dónde se puede poner un control

La comunicación se organiza por capas. Cada una usa los servicios de la inferior y ofrece algo a la superior, y al enviar se añade información de control. Esa separación no es solo didáctica: indica dónde actúa cada medida.

- En el **enlace**, la trama y la dirección MAC resuelven la entrega dentro del mismo segmento. Aquí viven la seguridad de puerto, las VLAN y la protección contra bucles.
- En **red**, el paquete IP y la tabla de rutas deciden por dónde sale y hacia qué siguiente salto. Aquí se filtran zonas y se controla el encaminamiento.
- En **transporte**, TCP o UDP ponen puertos y estado a la conversación. Aquí se decide qué servicio está expuesto.
- En **aplicación** viven DNS, DHCP, HTTP y el resto. Aquí se autentica de verdad al usuario y se registra qué hizo.

Una debilidad en cualquiera de las capas afecta al conjunto. Cifrar una web no arregla un switch con todos los puertos abiertos, y una VLAN bien hecha no impide que una aplicación tenga una contraseña por defecto.

## Tipos de red y exposición

Según su alcance se distingue entre red personal, local, metropolitana y amplia. La clasificación sirve para hablar, pero la decisión de seguridad es otra: qué atraviesa el límite y quién lo controla.

- Una **LAN** suele estar bajo administración propia; su riesgo principal es el acceso físico y el equipo que se conecta sin control.
- Una **WAN** o una conexión a Internet depende de terceros; el riesgo incluye cortes, latencia y la confianza que se deposita en el proveedor.
- Una red **inalámbrica** no tiene puerta física: el canal llega a la calle y el control empieza por el cifrado y la autenticación.
- Una red **virtual** o en la nube traslada parte del control a una plataforma ajena; hay que saber qué se configura allí y qué se da por supuesto.

## Medios y errores de transmisión

El par trenzado reduce interferencias, el coaxial usa un conductor central y una malla, y la fibra transmite luz. La elección afecta a distancia, inmunidad al ruido y coste, no solo a velocidad.

En el enlace se detectan errores con paridad, sumas de comprobación o CRC. Detectar no es corregir: el mecanismo avisa de que la trama llegó mal y la descarta, pero no reconstruye el dato. Por eso las capas superiores necesitan retransmisión o tolerancia al fallo.

## Direcciones y reenvío

Una dirección puede ser unicast, broadcast o multicast. La diferencia importa al analizar tráfico: una difusión llega a todos los equipos del dominio y puede multiplicar el efecto de un fallo o de un ataque.

El switch decide dentro del segmento con su tabla de direcciones; el router decide entre redes con su tabla de rutas. Confundir ambos planos lleva a buscar un problema de seguridad en el sitio equivocado: un equipo que no alcanza un servidor puede tener la ruta bien y el puerto de switch mal, o al revés.

## Transporte y servicios de aplicación

TCP ofrece una conversación ordenada, con confirmaciones y retransmisión; UDP no garantiza entrega, orden ni ausencia de duplicados. La aplicación decide si necesita esas garantías o si prefiere implementar las suyas.

Los puertos asocian tráfico con procesos. Algunos servicios son especialmente relevantes para el bastionado:

| Servicio | Función | Puerto habitual |
|---|---|---|
| DNS | Resuelve nombres en direcciones y otros datos | 53, UDP o TCP según la consulta |
| DHCP | Reparte configuración de red a los clientes | 67 en el servidor y 68 en el cliente |
| HTTP | Intercambio web sin cifrar | 80 |
| HTTPS | HTTP protegido con TLS | 443 |

Los puertos son convenciones: un servicio puede escuchar en otro. Por eso una revisión no consiste en buscar números conocidos, sino en comprobar qué proceso escucha, si necesita hacerlo y desde dónde se puede alcanzar.

**Un puerto abierto no es una vulnerabilidad por sí mismo.** Lo que decide es la necesidad del servicio, su exposición, su configuración y los controles que lo rodean. Cerrar todo lo que no se entiende también rompe servicios; el trabajo es justificar cada apertura.

## Procedimiento para leer una comunicación

1. Identifica la aplicación que origina o recibe los datos.
2. Sitúa el transporte: TCP o UDP, y qué puertos usa.
3. Comprueba si el destino está en la misma subred o en otra.
4. Si está fuera, sigue la ruta hasta la puerta de enlace y el siguiente salto.
5. Distingue la entrega local de la trama del encaminamiento del paquete.
6. Anota qué control actúa en cada tramo: puerto, VLAN, regla de cortafuegos, autenticación.

## Ejemplo

Un puesto consulta una web alojada en otra red. Resuelve el nombre por DNS, ve que la dirección no pertenece a su subred y entrega el paquete a su puerta de enlace. En el enlace local, la trama va dirigida a la MAC del router; el paquete conserva la dirección del servidor como destino. El router lo reenvía y, al final, TCP transporta la petición HTTPS. Si algo falla, el punto de mira se estrecha: nombre, ruta, puerto, certificado o aplicación.

## Errores que se repiten

- Suponer que una red segmentada está automáticamente protegida.
- Creer que un puerto conocido implica un servicio concreto.
- Buscar un fallo de aplicación en la tabla de rutas.
- Ignorar los servicios de nombres y de configuración automática, que son objetivos habituales.
- Confundir detección de errores con corrección.

## Fuentes

- IEEE 802.3 (Ethernet).
- RFC 791 (IPv4), RFC 8200 (IPv6), RFC 9293 (TCP), RFC 768 (UDP), RFC 1035 (DNS), RFC 2131 (DHCP) y RFC 9110 (HTTP).
