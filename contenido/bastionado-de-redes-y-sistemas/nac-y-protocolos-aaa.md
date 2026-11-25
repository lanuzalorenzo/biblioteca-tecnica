# Control de acceso a la red: NAC y protocolos AAA

Un proveedor entra con su portátil, pide la wifi para consultar el correo y acaba viendo la carpeta de contabilidad porque la red solo distingue entre «conectado» y «no conectado». El control de acceso a la red añade una pregunta previa: qué es este dispositivo, quién lo usa, cumple las condiciones y a qué zona debe ir. La respuesta se da antes de entregar una dirección IP.

La parte de VLAN, 802.1X y autenticación de puerto desde el switch está en [El acceso a la red](../seguridad-y-alta-disponibilidad/acceso-a-la-red.md). Aquí se desarrolla la decisión de admisión y los protocolos que la transportan.

## Cuatro preguntas antes de admitir

Para cada equipo que se conecta, un sistema de control de acceso a la red responde:

1. Si se le permite entrar.
2. Quién es: el usuario, el equipo o ambos.
3. Si cumple las condiciones: sistema actualizado, antivirus activo, disco cifrado.
4. En qué segmento queda y con qué políticas.

No es un cortafuegos. El cortafuegos filtra tráfico entre zonas; NAC decide a qué zona pertenece el dispositivo. Tampoco se resuelve solo con VLAN: una VLAN mal asignada sigue dando acceso.

## El flujo de admisión

| Papel | Quién es | Qué hace |
|---|---|---|
| Suplicante | El dispositivo que se conecta | Envía credenciales o certificado por EAP |
| Autenticador | El switch o el punto de acceso | Bloquea el puerto hasta que el servidor responde |
| Servidor de autenticación | Normalmente RADIUS | Verifica y devuelve la decisión y la VLAN |

Hasta que hay respuesta, el puerto solo transporta lo imprescindible para autenticarse. Los equipos que no pueden ejecutar un suplicante —impresoras, cámaras, sensores— se identifican por MAC. Es cómodo y flojo: la dirección se falsifica en un minuto. La mitigación pasa por una VLAN propia y por limitar a qué pueden hablar.

## Dónde se nota

- **IoT.** Aparatos que el fabricante no diseñó con seguridad y que no se actualizan. La política los deja hablar solo con su servidor.
- **BYOD.** Equipos personales dentro de la red de la empresa; se les da Internet y poco más.
- **Visitas y terceros.** Acceso separado, con fecha de caducidad y sin visión de la red interna.
- **OT.** Redes industriales donde un escaneo no planificado detiene la producción; NAC separa y aplica políticas por célula.

Hay soluciones libres como PacketFence y FreeNAC, y los fabricantes de red integran la suya. En una pyme sin equipo dedicado, el coste de operación suele pesar más que la licencia: un NAC mal mantenido acaba en modo abierto.

## Los tres servicios AAA

- **Autenticación:** comprobar quién es.
- **Autorización:** decidir qué puede hacer.
- **Contabilidad (*accounting*):** registrar qué hizo.

Mezclarlas produce diseños incompletos: se autentica bien y no se registra nada, o se autoriza por comodidad y se pierde la trazabilidad.

## RADIUS

RADIUS nació en 1991 y sigue siendo el estándar para autenticar accesos a red. Su arquitectura tiene tres piezas:

| Pieza | Función |
|---|---|
| Suplicante | El equipo que pide entrar; no habla con el servidor |
| NAS (*Network Access Server*) | Intermediario; es el cliente de RADIUS y quien habla con el servidor |
| Servidor RADIUS | Verifica y autoriza; devuelve la configuración de acceso |

En un portal cautivo, el cliente abre la wifi y cae en una página de acceso; allí teclea sus credenciales, el NAS las traslada al servidor y, si la respuesta es afirmativa, aplica la VLAN y las reglas.

### Lo que arrastra

- Viaja sobre **UDP**, sin conexión: se puede falsear el origen y no hay confirmación de entrega.
- Solo protege la **contraseña**; el resto de atributos va en claro.
- El ocultamiento usa **MD5** con el secreto compartido y un identificador de petición, un diseño de 1991 que hoy no se considera robusto.

Las salidas actuales son encapsular RADIUS en TLS (**RadSec**), usar IPsec o mantenerlo en una red de gestión. RADIUS por Internet sin protección no es aceptable.

## Diameter

Se diseñó para corregir esos defectos: transporte fiable sobre TCP o SCTP, seguridad de transporte con TLS o IPsec, notificación de errores, modelos con y sin estado y compatibilidad transitoria con RADIUS. Su compatibilidad con la itinerancia lo hizo estándar en telefonía móvil.

## TACACS+

Es el protocolo de AAA pensado para administrar dispositivos de red. Surgió en Cisco y arrastra fama de propietario, aunque su especificación es pública desde 2020 y hay implementaciones de otras marcas y de proyectos libres.

Sus diferencias con RADIUS explican cuándo se elige:

| Criterio | RADIUS | TACACS+ |
|---|---|---|
| Transporte | UDP | TCP, puerto 49 |
| Cifrado | Solo la contraseña | Todo el cuerpo del paquete |
| AAA | Autenticación y autorización juntas | Los tres servicios separados |
| Autorización por comando | No de forma nativa | Sí, comando a comando |
| Uso típico | Acceso de usuarios a la red | Administración de routers y switches |

La autorización comando a comando explica su uso en administración: un técnico puede consultar el estado del router con `show` sin poder entrar en `configure`.

## Qué comprobar

- ¿Los puertos de acceso tienen 802.1X o están abiertos a cualquiera?
- ¿Las visitas caen en una VLAN separada con caducidad?
- ¿Los dispositivos sin suplicante están aislados o mezclados con los puestos?
- ¿RADIUS viaja cifrado o en claro por la red de gestión?
- ¿La administración de switches y routers usa TACACS+ con autorización por comando?
- ¿Hay registro de las decisiones de admisión y de los cambios de VLAN?

## Errores que se repiten

- Llamar NAC a tener VLAN de invitados sin autenticación.
- Autenticar al usuario y no comprobar el estado del equipo.
- Dejar impresoras y cámaras en la VLAN de usuarios.
- Enviar RADIUS en claro «porque está en la red interna».
- Administrar routers con una cuenta compartida por todo el equipo.

## Fuentes

- IEEE 802.1X-2020, *Port-Based Network Access Control*.
- RFC 2865 (RADIUS), RFC 6614 (RadSec), RFC 6733 (Diameter) y RFC 8907 (TACACS+).
- PacketFence e INCIBE: documentación de despliegue de NAC.
