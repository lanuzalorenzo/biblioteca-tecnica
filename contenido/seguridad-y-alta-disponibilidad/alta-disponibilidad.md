# Alta disponibilidad: clústeres, balanceo y replicación

Un servicio disponible no es el que nunca falla, sino el que sigue respondiendo cuando algo falla. La diferencia es de diseño: tener repuesto, detectar el fallo y cambiar de pieza antes de que el usuario lo note.


## La cuenta de la disponibilidad

La disponibilidad es la proporción del tiempo en que el servicio responde. Se suele expresar en «nueves»: 99,9 % admite unas 8 horas y 46 minutos de caída al año; 99,99 %, unos 52 minutos; 99,999 %, unos 5 minutos. Cada nueve cuesta más que el anterior, y por eso se elige el objetivo antes de comprar la redundancia.

La cuenta se apoya en dos tiempos: el **MTBF**, tiempo medio entre fallos, y el **MTTR**, tiempo medio de reparación. La disponibilidad aproximada es MTBF / (MTBF + MTTR). Se mejora con componentes más fiables o con una recuperación más rápida; en la práctica, el MTTR es lo que más se controla, porque depende de la detección, el repuesto y el procedimiento.

No es lo mismo disponibilidad que continuidad. El **RTO** dice cuánto puede tardar el servicio en volver tras un desastre; el **RPO**, cuánto dato se puede perder. Esos dos valores deciden la réplica y las copias, no la simpatía por una herramienta.

Antes de duplicar nada hay que buscar el **punto único de fallo** (SPOF): una sola fuente de alimentación, un solo conmutador, un solo DNS, un solo almacenamiento o una sola persona que sepa arrancarlo. La redundancia que no se prueba es decoración.

## Clústeres

Un clúster es un conjunto de nodos que ofrecen un servicio como si fueran uno. Hay dos modelos:

- **Activo-pasivo (failover).** Un nodo atiende y el otro espera. Cuando el activo falla, el recurso —la IP, el volumen, el servicio— se traslada al pasivo. Es sencillo y fácil de razonar; a cambio, la capacidad del pasivo se desaprovecha.
- **Activo-activo.** Los dos atienden a la vez. Exige una aplicación sin estado o con sesiones compartidas, y dimensionar cada nodo para que absorba la carga del otro cuando uno caiga.

El **quórum** es el número de votos necesario para decidir quién manda. Con un número par de nodos y una partición de red, los dos lados pueden creer que son el primario: es el **split-brain**, y suele terminar con datos divergentes. Se evita con un testigo que desempate y, sobre todo, con **fencing** o STONITH: antes de promover al secundario se aísla o se apaga el primario. Sin fencing, la conmutación automática no es segura.

En Linux, la combinación habitual es Pacemaker con Corosync; en Windows, el clúster de conmutación por error. La IP virtual se anuncia con ARP gratuito para que el conmutador actualice su tabla MAC y no siga enviando al nodo caído.

## Balanceo de carga

El balanceador reparte peticiones entre varios servidores. En **capa 4** decide por dirección y puerto TCP o UDP; en **capa 7** entiende HTTP y puede enrutar por host, ruta, cabecera o cookie, además de terminar TLS.

Los algoritmos habituales son round robin, menos conexiones, hash por origen o por cookie y ponderado. La elección depende de si las sesiones son pegajosas y de la capacidad de cada nodo.

La **comprobación de salud** puede ser activa —un sondeo periódico a una ruta— o pasiva —observar los errores reales—. Un backend que falla sale del reparto; hay que evitar el rebote que provoca reintroducirlo demasiado pronto.

HAProxy y nginx son las piezas libres más usadas. La IP virtual se mantiene con keepalived y VRRP (RFC 5798): el nodo maestro la posee y el respaldo la reclama si deja de oír sus anuncios. Terminar TLS en el balanceador simplifica los certificados, pero el tramo hasta el backend debe cifrarse o quedar confinado a una red de confianza.

## Replicación

Replicar es copiar datos entre nodos para que el secundario pueda sustituir al primario.

- **Síncrona.** La escritura se confirma cuando el secundario también la tiene. El RPO se acerca a cero, pero añade latencia y depende de la red.
- **Asíncrona.** Se confirma en el primario y se envía después. No penaliza la escritura; si el primario cae, se pierde lo que no llegó a enviarse.

En bases de datos, PostgreSQL usa replicación por WAL (*streaming*); MySQL y MariaDB, el registro binario con GTID. Promover el secundario es una operación con decisiones: comprobar el retraso, cerrar escrituras y cambiar la referencia de los clientes.

A nivel de bloque, DRBD replica un dispositivo entre dos nodos; es la alternativa al almacenamiento compartido de una SAN. El almacenamiento compartido no evita el fallo lógico: un borrado o un cifrado por ransomware se ve en ambos nodos. Y `rsync` no es replicación de alta disponibilidad, porque no es continuo ni garantiza el orden.

Replicar no es hacer copias: la réplica propaga el borrado. Se necesitan las dos cosas, con la copia fuera del alcance de la cuenta comprometida.

## Comprobar que funciona

Un clúster sin pruebas de fallo es una hipótesis. Se prueba en una ventana de mantenimiento: parar el servicio, apagar un nodo, cortar la red y llenar el disco. Se mide el tiempo de conmutación, se verifica el dato y se anota el resultado.

La monitorización debe cubrir disponibilidad, latencia, errores y retraso de replicación. Se alerta por retraso, no solo por caída, porque un secundario retrasado no sirve para cumplir el RPO. El mantenimiento también se prueba: actualizar un nodo sin cortar el servicio exige capacidad y drenar antes.

## Lo que ha cambiado desde 2015

Los conceptos siguen siendo los mismos: quórum, fencing, comprobación de salud, RPO y RTO. Las herramientas de entonces también aguantan: keepalived, HAProxy, Pacemaker y DRBD continúan vigentes.

Lo que cambió es el envoltorio. Hay balanceadores gestionados, bases de datos con réplica y conmutación como servicio, y Kubernetes, que aporta réplicas, sondas y actualizaciones progresivas. La nube no elimina el split-brain ni el punto único de fallo: los mueve de sitio y añade una dependencia nueva, la red entre zonas.

## Fuentes

- RFC 5798, VRRP versión 3.
- ISO/IEC 25010, modelo de calidad del producto: fiabilidad y disponibilidad.
- Documentación oficial de Pacemaker y Corosync (ClusterLabs).
- Documentación oficial de HAProxy, de nginx y de keepalived.
- Documentación oficial de Microsoft, clústeres de conmutación por error de Windows Server.
- Documentación oficial de PostgreSQL, replicación por *streaming*.
- Documentación oficial de MySQL y MariaDB, replicación con GTID.
- Documentación oficial de DRBD.
- Documentación oficial de Kubernetes, sondas y despliegues.
