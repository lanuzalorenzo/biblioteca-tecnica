# VPN y túneles

Una oficina nueva a 23 kilómetros necesita usar el sistema de pedidos como si estuviera en el edificio central. La red privada virtual resuelve el transporte sin contratar un cable dedicado. Lo que no resuelve es la confianza: cada persona conectada pasa a formar parte de la red corporativa, y una credencial robada abre esa puerta desde cualquier punto del planeta.

Las familias de VPN, sus protocolos y su papel en el control del tráfico se explican en [Control de la red](../seguridad-y-alta-disponibilidad/control-y-monitorizacion.md). Este apunte se queda con las decisiones de despliegue: qué se entrega, qué se exige y qué se revisa.

## La decisión: qué se entrega

Una VPN entrega conectividad. El usuario conectado puede alcanzar todo lo que las reglas le permitan, no solo la aplicación que necesita. Esa diferencia es la que separa una VPN de un acceso por aplicación con verificación continua, que no entrega la red entera.

Antes de elegir producto hay que responder:

- ¿El usuario necesita la red completa o solo una aplicación?
- ¿El acceso es permanente o para una tarea concreta?
- ¿Se puede verificar el estado del dispositivo, no solo la identidad?
- ¿Qué pasa si la credencial se roba?

Si la respuesta es «solo una aplicación», una VPN de red es más de lo necesario. Si es «la red completa», hay que asumir que un equipo comprometido puede moverse lateralmente y compensarlo con segmentación.

## Criterios de elección

| Escenario | Familia | Motivo |
|---|---|---|
| Unir dos sedes de forma permanente | IPsec sitio a sitio | Interoperabilidad y despliegue en routers y cortafuegos |
| Acceso remoto que debe cruzar redes restrictivas | VPN sobre TLS | Viaja por el puerto 443 y atraviesa mejor los filtros |
| Enlace moderno con configuración mínima | WireGuard | Código pequeño, rápido y fácil de auditar |

La elección no es solo técnica: depende del parque de clientes, de la capacidad del equipo y de las obligaciones del entorno. Un protocolo moderno no compensa una gestión de claves descuidada.

## Riesgos de despliegue

- **El appliance es un objetivo.** Los equipos VPN expuestos acumulan vulnerabilidades críticas; hay que parchearlos como cualquier servidor frontera.
- **MFA no es opcional.** Usuario y contraseña solos convierten una filtración en un acceso remoto.
- **Gestión de claves y certificados.** Es la parte que más falla: inventario, caducidad, revocación y renovación.
- **Túnel partido.** Si el tráfico personal sale por la conexión local y el corporativo por la VPN, se pierde visibilidad y se mezclan dos mundos.
- **Movimiento lateral.** Una VPN no segmenta por dentro; el usuario comprometido puede intentar alcanzar otros sistemas.
- **Registro.** Sin saber quién se conecta, cuándo y desde dónde, un incidente remoto se investiga a ciegas.

## Lo que una VPN no hace

- No autentica al usuario por sí sola: eso lo hace el mecanismo de acceso.
- No limita a qué puede acceder una vez dentro: eso lo hace la segmentación.
- No cifra el extremo final: protege el trayecto entre los dos extremos.
- No sustituye a un EDR ni a la monitorización del dispositivo.
- No reemplaza a la gestión de identidades ni a la autenticación multifactor.
- No convierte una red plana en una red segmentada.

## Operación

Un despliegue de VPN necesita las mismas rutinas que cualquier servicio expuesto:

1. Inventario de certificados, claves y dispositivos.
2. Renovación antes de la caducidad, con alertas.
3. Revisión de vulnerabilidades del appliance y del cliente.
4. Registro de conexiones y de intentos fallidos.
5. Revisión periódica de quién tiene acceso y a qué.
6. Procedimiento de revocación cuando alguien se marcha o pierde un equipo.

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

- NIST SP 800-77, *Guide to IPsec VPNs*.
- WireGuard: documentación oficial del proyecto.
- INCIBE. Recomendaciones de seguridad en VPN.
