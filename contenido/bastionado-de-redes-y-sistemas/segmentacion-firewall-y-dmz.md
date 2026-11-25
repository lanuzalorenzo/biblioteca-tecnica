# Segmentación, cortafuegos y DMZ

Un edificio de oficinas con una única entrada y sin tabiques interiores deja que cualquiera que pase el portal llegue a todas las plantas. Una red plana funciona igual: el visitante que conecta un portátil alcanza el servidor de nóminas. Segmentar es levantar tabiques y colocar puertas con llave; el cortafuegos decide quién pasa y la DMZ es el vestíbulo donde se atiende a quien viene de la calle.

La separación por VLAN y la autenticación de puerto están en [El acceso a la red](../seguridad-y-alta-disponibilidad/acceso-a-la-red.md), y la lógica de las ACL en [Enrutamiento avanzado, ACL y seguridad de la red](../redes/enrutamiento-acl-y-seguridad.md). Aquí se combinan para diseñar el filtrado y la exposición.

## VLAN

Una VLAN crea redes lógicas independientes sobre el mismo cableado. Se obtienen cuatro cosas:

- **Segmentación.** Cada VLAN agrupa equipos en una subred.
- **Flexibilidad.** Un equipo cambia de VLAN por configuración, sin mover cables.
- **Rendimiento.** Menos equipos comparten dominio de difusión.
- **Seguridad.** Las VLAN se aíslan y el paso entre ellas se permite o se deniega con una regla.

Una VLAN no habla con otra por sí sola. Para cruzar hay que subir a capa 3, con un router o con un switch que tenga una interfaz por VLAN. El permiso se concreta en listas de control de acceso o en el cortafuegos.

### Cómo se configura un puerto

| Modo | Qué hace | Uso |
|---|---|---|
| Acceso | Pertenece a una VLAN, sin etiqueta | Equipos finales: PC, impresora, cámara |
| Troncal | Transporta varias VLAN etiquetadas | Enlace entre switches o hacia el router |
| Dinámico | Decide acceso o troncal según la trama | Poco recomendable: amplía la superficie |

El modo dinámico negocia con el vecino y puede permitir que un equipo se haga pasar por un switch para recibir varias VLAN. En una red bastionada, cada puerto se fija a acceso o troncal y el troncal solo se habilita donde hace falta.

### Fallos que cuestan caros

- Usar la VLAN 1, la de gestión por defecto, para usuarios y para el troncal.
- Llevar un puerto de acceso a un switch no previsto y arrastrar todas las VLAN.
- Autorizar en el troncal VLAN que nadie utiliza.
- Enrutar entre VLAN sin ACL y confiar en que la separación lógica basta.

## Cortafuegos

Un cortafuegos permite o rechaza tráfico según reglas. Se sitúa donde cambia la confianza: entre la red interna e Internet, entre la interna y la DMZ, y entre segmentos que no deben hablarse.

No todos miran lo mismo:

| Tipo | Qué mira | Límite |
|---|---|---|
| De paquetes | Cabeceras: IP, puerto y protocolo | No entiende el contexto de la conexión |
| De estado | Añade el estado de la conexión | No inspecciona el contenido de la aplicación |
| Proxy o pasarela de aplicación | Protocolo de aplicación | Más coste y más puntos de fallo |
| NGFW | Inspección profunda, aplicación e identidad | Configuración compleja; no sustituye al resto |

La política debe empezar por denegar y abrir solo lo necesario, con el mínimo origen, destino y puerto. Si se permite «todo desde dentro», el cortafuegos deja de servir: el malware que ya está en la red sale sin encontrar obstáculo.

El orden también importa. La primera regla que coincide decide, así que una regla amplia situada arriba deja sin efecto las específicas que vienen después.

Las ACL de un router hacen un filtrado sin estado y por interfaz. Sirven para separar VLAN y para aprender la lógica; un cortafuegos de borde cubre más, pero la ACL sigue siendo la herramienta del switch y del router.

## DMZ

La DMZ es una red aparte para los servicios que deben verse desde Internet: web, correo, proxy inverso. Se coloca entre fuera y dentro, de forma que un fallo en uno de esos servicios no abra la red interna.

Lo habitual es usar dos cortafuegos o uno con tres interfaces: Internet, DMZ y red interna. Las reglas dejan entrar a los servicios publicados y limitan lo que la DMZ puede iniciar hacia dentro. La red interna no se publica.

Lo que aporta:

- Aísla los servicios expuestos y reduce el alcance de una intrusión.
- Permite apagar en el servidor publicado lo que no se usa.
- Deja claro qué debe ser accesible desde fuera.

Lo que puede fallar:

- Una DMZ mal configurada que permite tráfico libre hacia la red interna pierde todo el aislamiento.
- Un servicio publicado con credenciales internas traslada el problema, no lo resuelve.
- La DMZ no detiene a quien ya está dentro ni corrige un fallo de la aplicación.

## Publicar un servidor

Cada servidor publicado es un objetivo permanente. Si un atacante lo compromete y comparte red con otros equipos, lo usa como trampolín. Las medidas que acompañan a la DMZ son separar el servidor, actualizarlo, retirar servicios y cuentas que no se usan, revisar los registros y limitar por regla lo que puede alcanzar.

## Qué comprobar

- Cada VLAN tiene una subred y un propósito; no hay equipos sueltos en la VLAN de gestión.
- Los puertos de acceso llevan una sola VLAN y los troncales solo las necesarias.
- El paso entre VLAN está permitido por una regla explícita, no por defecto.
- La política del cortafuegos empieza por denegar y cada permiso justifica origen, destino y puerto.
- La DMZ solo publica lo que debe ser público y no inicia tráfico hacia dentro salvo lo imprescindible.
- Las reglas y las ACL se revisan, y las obsoletas se retiran.

## Errores que se repiten

- Suponer que la VLAN de invitados protege sin reglas entre segmentos.
- Poner una regla de permiso total «para que funcione».
- Publicar en la misma red los servicios de Internet y los internos.
- Abrir un puerto para una prueba y olvidar cerrarlo.
- Acumular reglas durante años y no atreverse a borrar ninguna.

## Fuentes

- IEEE 802.1Q (VLAN y etiquetado de tramas).
- NIST SP 800-41 Rev. 1, *Guidelines on Firewalls and Firewall Policy*.
- NIST SP 800-125B, *Secure Virtual Network Configuration for Virtual Machine Protection*.
