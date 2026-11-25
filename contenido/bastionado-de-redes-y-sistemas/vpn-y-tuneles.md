# VPN y túneles

Una oficina nueva a 23 kilómetros necesita usar el sistema de pedidos como si estuviera en el edificio central. La red privada virtual resuelve el transporte sin contratar un cable dedicado. Lo que no resuelve es la confianza: cada persona conectada pasa a formar parte de la red corporativa, y una credencial robada abre esa puerta desde cualquier punto del planeta.

Las familias de VPN y su papel en el control del tráfico se presentan en [Control de la red](../seguridad-y-alta-disponibilidad/control-y-monitorizacion.md). Este apunte se centra en las decisiones de diseño: qué se protege, qué no, y qué hay que revisar antes de confiar en un túnel.

## Qué se gana y qué no

Una VPN levanta una red privada encima de otra que no está bajo su control. Lo privado no es el camino, sino el envoltorio que lo recorre: los paquetes siguen pasando por Internet, pero envueltos y cifrados entre dos puntos.

Cuando alguien dice que la comunicación es segura «porque el canal es privado», confunde el medio con la protección. El medio es Internet. Lo que defiende son el cifrado y la autenticación de los extremos; el resto sigue expuesto a cortes, latencia y ataques contra el servicio.

## Dos extremos, dos modelos

| Modo | Qué conecta | Uso típico |
|---|---|---|
| Cliente a red (acceso remoto) | Un equipo con una red corporativa | Teletrabajo, soporte, viajes |
| Red a red (sitio a sitio) | Dos sedes o una sede y una nube | Unir oficinas sin línea dedicada |

En el modo cliente a red, el cliente recibe una dirección de la red interna y pasa a ser un equipo más, con sus permisos. En el modo red a red, los routers de cada extremo encapsulan el tráfico de toda la red; no hay cliente por usuario.

## El paquete dentro del paquete

Un túnel envuelve un paquete en otro: pone delante una cabecera que permite atravesar la red pública y la quita al llegar al destino. Ese envoltorio lo definen los extremos y el protocolo elegido.

La primera decisión, por tanto, es qué se cifra, qué se autentica y en qué capa se hace.

## IPsec, en corto

IPsec opera en la capa de red. Esa posición le permite cubrir TCP, UDP e ICMP sin pedir nada a la aplicación; TLS y SSH, en cambio, necesitan que el programa los implemente.

| Pieza | Qué aporta |
|---|---|
| AH (*Authentication Header*) | Integridad y autenticación del origen, sin cifrado |
| ESP (*Encapsulating Security Payload*) | Confidencialidad, integridad y autenticación |
| Modo transporte | Protege la carga y deja visible la cabecera IP original; se usa entre hosts |
| Modo túnel | Protege el paquete entero y añade una cabecera; es el de sitio a sitio |

El intercambio de claves lo hace IKE, en su versión 2 en los despliegues actuales. En IPv6, IPsec fue obligatorio en el diseño original y pasó a recomendable con la revisión de 2011.

## Otras familias

- **VPN sobre TLS.** Reutiliza el TLS de la web con un portal o un cliente. Su ventaja es que cruza proxies y cortafuegos con facilidad porque viaja por el puerto 443.
- **WireGuard.** Un protocolo reciente, de código corto y auditado, presente en el núcleo Linux desde la versión 5.6. Gana en velocidad y sencillez, y pierde en funciones de gestión frente a las suites IPsec empresariales.

## El coste oculto

| A favor | En contra |
|---|---|
| Usa Internet en vez de una línea dedicada | La disponibilidad y el caudal dependen del proveedor |
| El remoto trabaja con las mismas políticas que en la oficina | La gestión de claves y certificados es la parte más frágil |
| Se llega desde cualquier sitio con conexión | Cifrar y encapsular consume recursos en el cliente |
| Sirve para sedes, proveedores y consultores con alcance definido | Entrega red, no aplicación: el usuario comprometido puede moverse |

## Lo que sigue expuesto

- **Acceso de red, no de aplicación.** La VPN da conectividad; si el usuario comprometido entra, puede moverse lateralmente. La alternativa que se impone es el acceso por aplicación con verificación continua, que no entrega la red entera.
- **El dispositivo VPN es un objetivo.** Los appliances expuestos acumulan vulnerabilidades críticas; hay que parchearlos como cualquier servidor frontera y exigir MFA.
- **Túnel partido (*split tunneling*).** Si el tráfico personal sale por la conexión local y el corporativo por la VPN, se mezclan dos mundos y se pierde visibilidad.

## Qué comprobar

- ¿La VPN exige MFA o solo usuario y contraseña?
- ¿El appliance está actualizado y con las vulnerabilidades conocidas revisadas?
- ¿Se registra quién se conecta, cuándo y desde dónde?
- ¿El túnel es completo o partido, y está justificado?
- ¿Los certificados y claves tienen inventario, caducidad y plan de renovación?
- ¿La VPN aplica el mínimo privilegio o entrega la red completa a cualquiera que se conecte?

## Errores que se repiten

- Tratar la VPN como una frontera de confianza y no segmentar por dentro.
- Compartir un certificado de cliente entre varios usuarios.
- Dejar el appliance sin parchear porque «solo lo usa el personal».
- Activar túnel partido sin control y perder la visibilidad del tráfico.
- Creer que una VPN cifra el extremo final: solo protege el trayecto.

## Fuentes

- RFC 4301 (arquitectura IPsec), RFC 7296 (IKEv2) y RFC 6434 (IPv6).
- WireGuard: documentación oficial del proyecto.
- NIST SP 800-77, *Guide to IPsec VPNs*.
- INCIBE. Recomendaciones de seguridad en VPN.
