# Ethernet y conmutación

Un switch es el portero de un edificio con muchas puertas. No pregunta quién eres, solo mira el nombre del sobre y lo lleva a la mesa correspondiente. Esa eficacia es también su punto débil: si alguien puede escribir el nombre que quiera en el sobre, el portero lo entregará donde diga.

En capa 2 se decide qué equipo recibe cada trama dentro del segmento local. El aprendizaje y el reenvío se explican en [Ethernet, conmutación, STP y VLAN](../redes/ethernet-conmutacion-y-vlan.md). Este apunte se queda con lo que hay que cerrar para que esa entrega no se convierta en una puerta abierta.

## Qué decisiones toma el switch

Cuando entra una trama, el switch aprende la MAC de origen en ese puerto y consulta la de destino. Si la conoce por otro puerto, reenvía solo por él; si la conoce por el mismo, filtra; si es desconocida o de difusión, inunda los puertos permitidos menos el de entrada.

Tres consecuencias para el bastionado:

- La tabla de direcciones se construye observando el tráfico. Un equipo puede anunciar una MAC que no le pertenece y desviar respuestas hacia su puerto.
- La inundación es normal, pero también es la vía por la que un atacante ve tráfico que no iba dirigido a él.
- Las entradas caducan. Una tabla vacía o en aprendizaje se comporta distinto de una consolidada, y eso explica resultados que parecen aleatorios.

## Riesgos del enlace local

- **Suplantación de MAC.** Cambiar la dirección de la tarjeta es inmediato. Sirve para ocupar el sitio de otro equipo, saltarse un filtro que solo mira la MAC o provocar que el switch reenvíe hacia el atacante.
- **Saturación de la tabla.** Si se generan más direcciones de las que caben, el switch puede inundar por necesidad y el tráfico deja de estar contenido.
- **Bucles.** Un enlace redundante mal controlado multiplica tramas y difusiones hasta saturar la red. STP bloquea los enlaces sobrantes para mantener una topología sin ciclos, pero también se puede manipular para cambiar quién es la raíz.
- **Salto de VLAN.** Un puerto mal configurado o un troncal demasiado permisivo puede permitir que una trama etiquetada termine en una VLAN que no le corresponde.
- **Servicios falsos.** Un equipo puede declararse servidor DHCP o responder por ARP en lugar de la puerta de enlace real.

Las VLAN separan dominios de difusión, pero no cifran ni autentican. Un portátil conectado a la VLAN de invitados sigue siendo un portátil desconocido. La separación lógica y el control de acceso son dos capas distintas: la primera ordena, la segunda decide.

## Cerrar el puerto

Tres controles convierten una boca de switch en algo defendible. Su configuración concreta se desarrolla en [El acceso a la red](../seguridad-y-alta-disponibilidad/acceso-a-la-red.md).

- **Seguridad de puerto.** Limita cuántas MAC se aprenden y cuáles se aceptan. Ante una violación puede descartar tramas, avisar o apagar el puerto. Frena el cambio de equipo y la conexión de un switch no autorizado.
- **DHCP snooping.** Solo el servidor legítimo puede repartir direcciones; el resto de puertos no pueden ofrecer DHCP. Evita que un equipo se declare servidor y entregue una puerta de enlace falsa.
- **Inspección de ARP.** Comprueba que las respuestas ARP corresponden a una asignación legítima. Sin esto, envenenar la tabla ARP de la red es trivial.

Ninguno sustituye a los otros. La seguridad de puerto sin DHCP snooping deja pasar un servidor falso por un puerto autorizado; el snooping sin inspección de ARP no impide responder por un equipo que ya tiene dirección.

## Troncales y VLAN de gestión

El troncal transporta varias VLAN a la vez. Es el punto donde un error de configuración tiene más alcance:

- La **VLAN nativa** viaja sin etiquetar. Si se deja la de gestión o la de usuarios, una trama sin etiqueta puede acabar donde no debe. Se cambia por una VLAN sin uso y no se emplea para tráfico real.
- La lista de VLAN permitidas en el troncal debe ser explícita. Permitir todas «por si acaso» convierte cualquier equipo conectado en candidato a recibir redes que no necesita.
- Los puertos **dinámicos** negocian su modo con el vecino. En una red bastionada se fijan a acceso o troncal; el modo automático amplía la superficie sin aportar nada.
- La VLAN de **gestión** se separa del tráfico de usuarios. Compartir puerto con un puesto de trabajo pone la administración del switch al alcance de ese puesto.

Los puertos que no se usan se desactivan. Un latiguillo olvidado en una sala accesible es una entrada libre, y el inventario de qué equipo entra por cada boca es tan útil como la propia configuración.

## Bucles y STP

STP evita ciclos, pero la protección no termina en activarlo. Un equipo que se declara raíz puede reorganizar la topología a su favor, y un puerto de usuario que recibe BPDU puede introducir información de spanning tree donde no corresponde. Las defensas habituales son limitar los BPDU en los puertos de acceso y fijar la raíz en un switch controlado.

El objetivo no es solo que la red no se caiga: es que la topología no la decida un equipo no autorizado.

## Inventario y cambios

La configuración del switch caduca como cualquier otra. Un puerto que se abrió para una sustitución, una VLAN que se creó para una prueba y una regla que se añadió para un evento se quedan si nadie las retira.

Conviene guardar la configuración, versionarla y revisar los cambios con la misma disciplina que el resto de la infraestructura. Saber qué equipo entra por cada boca no es una curiosidad: es lo que permite detectar un dispositivo desconocido y explicar por qué un puerto está en una VLAN concreta.

## Lo que se comprueba

- Cada puerto de acceso pertenece a una sola VLAN y tiene un propósito documentado.
- Los puertos sin uso están desactivados.
- La seguridad de puerto está activa donde hay equipos finales, con un número de MAC coherente con el puesto.
- DHCP snooping e inspección de ARP funcionan en las VLAN de usuarios.
- El troncal solo permite las VLAN declaradas y la nativa no es de gestión ni de usuarios.
- La administración del switch está en una VLAN separada, con acceso restringido y registro.
- El firmware está actualizado y la configuración se guarda y se versiona.

## Errores que se repiten

- Creer que una VLAN aísla por sí sola y no poner reglas entre segmentos.
- Dejar la VLAN 1 para todo, incluida la gestión.
- Conectar un switch no previsto a un puerto de acceso y arrastrar todas las VLAN.
- Filtrar por MAC y llamarlo autenticación.
- Tener STP activo y dar por hecho que nadie puede influir en la topología.
- No revisar los puertos que se dieron de alta para una sustitución y quedaron abiertos.

## Fuentes

- IEEE 802.3 (Ethernet), IEEE 802.1Q (VLAN y etiquetado) e IEEE 802.1D (STP).
- Documentación de seguridad de puerto, DHCP snooping e inspección de ARP de los fabricantes de conmutación.
