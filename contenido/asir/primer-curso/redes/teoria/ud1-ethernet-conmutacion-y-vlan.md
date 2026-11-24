# UD1. Ethernet, conmutación, STP y VLAN

Cuando dos equipos hablan por un switch, alguien tiene que decidir por qué puerto sale cada trama y, sobre todo, evitar que una trama dé vueltas para siempre. Esa decisión —aprender direcciones, reenviar solo por donde toca y cortar los bucles— es toda la conmutación, y sin entenderla no se entiende ninguna red segmentada.

> **Módulo:** Redes

## La trama Ethernet

Un equipo envía una **trama** con la MAC de destino, la de origen, el tipo de protocolo, los datos y una comprobación final. La MAC es un número de 48 bits, con la parte del fabricante y la del equipo; no se parece a una dirección IP y no se enruta.

El tamaño útil máximo es de 1500 bytes (MTU). Por debajo, el mínimo de 64 bytes sirve para que las colisiones se detecten a tiempo: en una red half-duplex, un equipo que transmite debe enterarse de que otro lo pisa.

## Hub y switch: dominio de colisión

- **Con un hub**, todos los equipos comparten el mismo medio: lo que transmite uno lo reciben todos y dos transmisiones a la vez chocan. Ese es el **dominio de colisión**.
- **Con un switch**, cada puerto es su propio dominio de colisión. El equipo solo recibe lo que va dirigido a él, salvo difusión (*broadcast*), que sigue llegando a todos.

El **dominio de difusión** es otra cosa: abarca todo lo que recibe una trama de difusión. Un switch lo mantiene entero; un router o una VLAN lo cortan.

## Cómo aprende un switch

1. **Aprende** la MAC de origen de cada trama y la asocia al puerto por el que entró.
2. **Reenvía** si la MAC de destino está en su tabla: solo por ese puerto.
3. **Inunda** si no la conoce: la manda por todos los puertos menos el de entrada.
4. **Envejece** las entradas que dejan de usarse, unos cinco minutos por defecto.

Editar la tabla a mano se hace para fijar un equipo a un puerto, y es la base de la seguridad de puerto: si una MAC aparece por otro puerto, algo ha cambiado.

## Bucles y STP

Dos switches conectados por dos cables forman un bucle: una difusión se replica y vuelve, y la red se cae en segundos. Redundar el cableado es bueno; dejar el bucle abierto, no.

El **protocolo de árbol de expansión** (STP, IEEE 802.1D) resuelve esto eligiendo un camino y bloqueando el resto:

- Se elige un **puente raíz** por prioridad, y a igualdad, por la MAC más baja. La prioridad por defecto es 32768.
- Cada switch elige un **puerto raíz** (el de menor coste hacia la raíz); en cada segmento, un **puerto designado** que reenvía.
- El resto queda **bloqueado**: no reenvía tráfico, pero sigue escuchando para detectar cambios.
- Los estados pasan de bloqueo a escucha, aprendizaje y reenvío, con tiempos que suman unos 30 segundos de convergencia.

Ese medio minuto es demasiado en una red de acceso, y de ahí vienen las mejoras: **RSTP** (802.1w) reduce la convergencia a segundos y añade roles alternativos, y **MSTP** (802.1s) permite un árbol por grupo de VLAN. En los puertos de usuario se activa además **PortFast**, que evita la espera al conectarse, con **BPDU guard** para apagarlos si alguien cuelga un switch.

## VLAN

Una VLAN separa un switch en varias redes lógicas. Los equipos de la misma VLAN se hablan sin más; los de VLAN distintas necesitan un router o un switch de capa 3.

- **Enlace de acceso:** un puerto, una VLAN, un equipo.
- **Enlace troncal:** transporta varias VLAN entre switches o hacia el router. Con IEEE 802.1Q, cada trama lleva una etiqueta con su VLAN; los identificadores utilizables van del 1 al 4094.
- **Enrutamiento entre VLAN:** una interfaz por VLAN en el router, o una subinterfaz troncal que atiende a todas.

El ejercicio del módulo practicó los tres casos —enlaces de acceso, troncales y VTP— sobre Packet Tracer. **VTP** propaga la lista de VLAN entre switches en tres modos: servidor, cliente y transparente. Funciona, y por eso mismo es peligroso: un switch añadido con la revisión más alta puede borrar las VLAN del resto. Hoy la lista se declara por configuración o se gestiona desde un sistema central.

## Lo que se comprueba en una práctica

Que cada VLAN tiene su rango de direcciones y no se solapa; que los troncales llevan solo las VLAN que deben; que la VLAN nativa no transporta usuarios; que el árbol de expansión tiene una raíz previsible y no la que ganó por MAC; y que desconectar el cable redundante no deja la red sin servicio.

Órdenes que responden a esas preguntas, en un switch de configuración habitual: `show vlan brief` para la lista de VLAN y sus puertos, `show interfaces trunk` para los troncales y su VLAN nativa, `show spanning-tree` para la raíz y los roles, `show mac address-table` para qué MAC hay en cada puerto.

## Seguridad de puerto

Un puerto de acceso admite por defecto cualquier equipo que se enchufe. Limitarlo es barato y evita sorpresas:

- **Número máximo de MAC** por puerto, con la primera aprendida como fija (*sticky*).
- **Modo de violación:** proteger descarta las tramas nuevas, restringir avisa y descarta, apagar deja el puerto en error y exige intervención. El último es el único que se entera uno de que algo pasa.
- **Puertos sin uso, apagados** y fuera de cualquier VLAN de usuarios.

Con eso, mover un equipo de sitio deja de ser transparente: hay que tocar la configuración, y eso deja rastro.

## Errores que se repiten

- Dejar la VLAN 1 como nativa y con usuarios dentro.
- Marcar un troncal como acceso, o al revés, y pasar media hora buscando por qué no hay conectividad.
- Confiar en que el árbol de expansión elige la raíz correcta: la gana el switch con menor prioridad y, a igualdad, la MAC más baja, que casi nunca es el core.
- Activar PortFast en un puerto que conecta a otro switch: convierte un bucle en una tormenta de difusión instantánea.

## Fuentes

- IEEE 802.3 (Ethernet), 802.1D (STP), 802.1w (RSTP), 802.1s (MSTP) y 802.1Q (VLAN).
- Documentación oficial de configuración de switches.
