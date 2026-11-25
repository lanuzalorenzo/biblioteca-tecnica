# Ethernet y conmutación

Un switch es el portero de un edificio con muchas puertas. No pregunta quién eres, solo mira el nombre del sobre y lo lleva a la mesa correspondiente. Esa eficacia es también su punto débil: si alguien puede escribir el nombre que quiera en el sobre, el portero lo entregará donde diga.

El funcionamiento del enlace —tramas, aprendizaje, inundación y STP— se explica en [Ethernet, conmutación, STP y VLAN](../redes/ethernet-conmutacion-y-vlan.md). Este apunte se queda con lo que hay que cerrar para que esa entrega no se convierta en una puerta abierta.

## Dónde está el riesgo

- **Suplantación de MAC.** Cambiar la dirección de la tarjeta es inmediato. Sirve para ocupar el sitio de otro equipo, saltarse un filtro que solo mira la MAC o desviar respuestas hacia el atacante.
- **Saturación de la tabla.** Si se generan más direcciones de las que caben, el switch inunda por necesidad y el tráfico deja de estar contenido.
- **Bucles.** Un enlace redundante mal controlado multiplica tramas y difusiones hasta saturar la red. Además, quien consigue influir en la topología puede colocarse en el camino del tráfico.
- **Salto de VLAN.** Un puerto mal configurado o un troncal demasiado permisivo puede permitir que una trama etiquetada termine en una VLAN que no le corresponde.
- **Servicios falsos.** Un equipo puede declararse servidor DHCP o responder por ARP en lugar de la puerta de enlace real.

Ninguno se resuelve mirando solo la tabla de direcciones. Son riesgos de configuración y de confianza en el puerto.

## Lo que la VLAN no resuelve

Las VLAN separan dominios de difusión, pero no cifran ni autentican. Un portátil conectado a la VLAN de invitados sigue siendo un portátil desconocido. La separación lógica y el control de acceso son dos capas distintas: la primera ordena, la segunda decide.

Por eso una VLAN de invitados sin reglas hacia la red interna no protege nada. Y una VLAN de gestión que comparte puerto con un puesto de trabajo pone la administración del switch al alcance de ese puesto.

## Cerrar el puerto

Tres controles convierten una boca de switch en algo defendible. Su configuración concreta se desarrolla en [El acceso a la red](../seguridad-y-alta-disponibilidad/acceso-a-la-red.md).

- **Seguridad de puerto.** Limita cuántas MAC se aprenden y cuáles se aceptan. Ante una violación puede descartar tramas, avisar o apagar el puerto. Frena el cambio de equipo y la conexión de un switch no autorizado.
- **DHCP snooping.** Solo el servidor legítimo puede repartir direcciones; el resto de puertos no pueden ofrecer DHCP. Evita que un equipo se declare servidor y entregue una puerta de enlace falsa.
- **Inspección de ARP.** Comprueba que las respuestas ARP corresponden a una asignación legítima. Sin esto, envenenar la tabla ARP de la red es trivial.

Ninguno sustituye a los otros. La seguridad de puerto sin DHCP snooping deja pasar un servidor falso por un puerto autorizado; el snooping sin inspección de ARP no impide responder por un equipo que ya tiene dirección.

## Troncales y gestión

El troncal transporta varias VLAN a la vez y es donde un error de configuración tiene más alcance:

- La **VLAN nativa** viaja sin etiquetar. Si se deja la de gestión o la de usuarios, una trama sin etiqueta puede acabar donde no debe. Se cambia por una VLAN sin uso y no se emplea para tráfico real.
- La lista de VLAN permitidas debe ser explícita. Permitir todas «por si acaso» convierte cualquier equipo conectado en candidato a recibir redes que no necesita.
- Los puertos **dinámicos** negocian su modo con el vecino. En una red bastionada se fijan a acceso o troncal; el modo automático amplía la superficie sin aportar nada.
- La VLAN de **gestión** se separa del tráfico de usuarios. Compartir puerto con un puesto de trabajo pone la administración del switch al alcance de ese puesto.

Los puertos que no se usan se desactivan. Un latiguillo olvidado en una sala accesible es una entrada libre.

## Físico y cambios

La configuración no lo es todo. El switch vive en un armario que debe estar cerrado y fuera del alcance de quien no administra; un puerto al que se accede con la mano es un control que se puede saltar sin tocar la interfaz de gestión.

La configuración también caduca. Un puerto que se abrió para una sustitución, una VLAN que se creó para una prueba y una regla que se añadió para un evento se quedan si nadie las retira. Conviene guardar la configuración, versionarla y revisar los cambios con la misma disciplina que el resto de la infraestructura.

Saber qué equipo entra por cada boca no es una curiosidad: permite detectar un dispositivo desconocido y explicar por qué un puerto está en una VLAN concreta.

## Auditoría del switch

1. Contrasta el inventario de puertos con lo que hay conectado.
2. Comprueba que los puertos sin uso están desactivados y que no hay latiguillos olvidados.
3. Revisa la configuración de seguridad de puerto y el número de MAC permitido por boca.
4. Verifica DHCP snooping e inspección de ARP en las VLAN de usuarios.
5. Mira el troncal: VLAN permitidas, VLAN nativa y puertos dinámicos.
6. Confirma que la gestión está en una VLAN separada y con acceso restringido.
7. Revisa firmware, copia de configuración y registro de cambios.

## Qué comprobar

- Cada puerto de acceso pertenece a una sola VLAN y tiene un propósito documentado.
- Los puertos sin uso están desactivados.
- La seguridad de puerto está activa donde hay equipos finales.
- DHCP snooping e inspección de ARP funcionan en las VLAN de usuarios.
- El troncal solo permite las VLAN declaradas y la nativa no es de gestión ni de usuarios.
- La administración del switch está separada, restringida y registrada.

## Errores que se repiten

- Creer que una VLAN aísla por sí sola y no poner reglas entre segmentos.
- Dejar la VLAN 1 para todo, incluida la gestión.
- Conectar un switch no previsto a un puerto de acceso y arrastrar todas las VLAN.
- Filtrar por MAC y llamarlo autenticación.
- No revisar los puertos que se dieron de alta para una sustitución y quedaron abiertos.

## Fuentes

- IEEE 802.3 (Ethernet), IEEE 802.1Q (VLAN y etiquetado) e IEEE 802.1D (STP).
- Documentación de seguridad de puerto, DHCP snooping e inspección de ARP de los fabricantes de conmutación.
