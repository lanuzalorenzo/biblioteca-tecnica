# TCP: conexiones y banderas

Abrir una conexión TCP se parece a concertar una cita por carta: primero se pregunta si el otro está y acepta, luego se confirma la cita y, cuando termina, cada parte avisa de que se marcha. Las banderas de la cabecera son esas frases hechas; los estados, el registro de en qué punto de la cita está cada uno.

Mirar una captura sin entender esa secuencia es como leer solo las palabras sueltas de una conversación. Lo que informa es el orden y la repetición: un saludo suelto no dice nada, pero cien saludos desde el mismo sitio en un minuto cuentan otra historia.

## Las banderas activas

| Bandera | Nombre | Para qué sirve | Detalle |
|---|---|---|---|
| SYN | *Synchronize* | Pedir la apertura y anunciar la secuencia inicial | Aparece en los dos primeros segmentos y gasta un número de secuencia |
| ACK | *Acknowledge* | Indicar que el campo de confirmación es válido | Acompaña casi todo el tráfico posterior al saludo |
| FIN | *Finish* | Anunciar que un extremo no enviará más datos | Cada sentido se cierra por separado y también gasta secuencia |
| RST | *Reset* | Cortar la conexión sin negociación | Se usa para rechazar, abortar o atacar una sesión |
| ECE | *ECN-Echo* | Comunicar que se ha visto una marca de congestión | Solo tiene sentido con notificación explícita habilitada |
| CWR | *Congestion Window Reduced* | Confirmar que se redujo la ventana por congestión | Responde a la marca anterior |

ECE y CWR dependen de que la notificación de congestión esté configurada en los extremos y en los equipos intermedios. Sin ella, viajan a cero y no aportan nada al análisis.

## Las que quedaron atrás

**PSH** pedía entregar los datos a la aplicación sin esperar a llenar el búfer. La decisión de trocear el flujo corresponde a la pila del emisor, y las implementaciones actuales entregan cuando toca. Se estudia por su intención, no porque sirva para diagnosticar.

**URG** señalaba que el puntero de datos urgentes era válido. La interpretación de ese mecanismo nunca fue homogénea y la propia especificación posterior desaconseja confiar en él. Hoy los datos urgentes se gestionan en la aplicación.

En la cabecera queda además un bit reservado que se usó en una propuesta experimental de congestión. Está retirado y no se considera una bandera operativa.

## El saludo de tres pasos

1. El cliente manda **SYN** con su secuencia inicial y queda en `SYN_SENT`.
2. El servidor responde **SYN+ACK**: confirma la del cliente, anuncia la suya y acepta. Queda en `SYN_RECEIVED`.
3. El cliente manda **ACK** y confirma la del servidor. Los dos extremos pasan a `ESTABLISHED`.

Después, los segmentos de datos llevan ACK activa aunque la herramienta muestre solo la otra bandera cuando la hay. Por eso decir que «el receptor confirma con un ACK» vale para el saludo y no describe toda la conversación.

El servidor reserva una entrada para cada conexión a medio abrir. Si el tercer paso no llega, la entrada espera hasta caducar. Esa espera es el recurso que agota la inundación de SYN, y la razón de que existan las *SYN cookies*.

## La despedida de cuatro pasos

1. Un extremo manda **FIN** y pasa a `FIN_WAIT_1`.
2. El otro responde **ACK** y queda en `CLOSE_WAIT`, pero todavía puede enviar datos.
3. Cuando termina, manda su propio **FIN**.
4. El primero responde **ACK** y espera en `TIME_WAIT` antes de liberar la conexión.

Un FIN cierra una dirección, no la conversación entera. Y `TIME_WAIT` no es un fallo: es el tiempo que evita confundir segmentos retrasados con una conexión nueva.

El corte brusco es **RST**. Sirve para rechazar una conexión a un puerto cerrado, para abortar ante un error y también como arma: un RST colocado a tiempo tumba una sesión sin que las partes sepan por qué.

| Estado | Lectura práctica |
|---|---|
| `LISTEN` | Hay un servicio esperando; el puerto está abierto |
| `SYN_SENT` | El cliente aguarda respuesta; si se repite, el destino no contesta |
| `ESTABLISHED` | La conexión está en curso |
| `CLOSE_WAIT` | La aplicación local no cerró su parte; muchos acumulados delatan un fallo de programa |
| `TIME_WAIT` | Cierre normal en espera; solo duele si agota los puertos efímeros |

## Lo que enseña al bastionado

- **Las banderas no son un control de acceso.** El estado lo guarda el cortafuegos, no los bits que llegan. Fabricar paquetes con la combinación deseada está al alcance de cualquiera.
- **Los escaneos silenciosos explotan esa ambigüedad.** Mandan combinaciones poco habituales —solo FIN, ninguna bandera, FIN+PSH+URG— y deducen del silencio o del RST si el puerto está abierto. Ocultar el RST no protege: lo que protege es no tener el puerto expuesto.
- **Los estados sí delatan anomalías.** Una acumulación de `SYN_RECEIVED`, muchos `SYN_SENT` hacia el mismo destino o RST en sesiones establecidas son señales que merecen mirada.
- **Ninguna bandera identifica a una persona.** La autenticación pertenece a la aplicación.

## Cómo interpretar una captura

1. Identifica el par de direcciones y puertos y decide quién hace de cliente.
2. Mira el primer segmento: `SYN` sin `ACK` indica un intento de apertura.
3. Comprueba si hay `SYN+ACK`; sin él no existe conexión establecida, por mucho tráfico que se vea.
4. Revisa el estado de cada extremo para distinguir un cierre ordenado de un corte.
5. Fíjate en las repeticiones: el patrón pesa más que el segmento aislado.
6. Contrasta con el servicio: un `LISTEN` que nadie justifica es un hallazgo.

## Ejemplo

Un cliente conversa con un servidor web y, de repente, la sesión muere. En la captura aparecen `SYN`, `SYN+ACK`, `ACK`, varios segmentos con `ACK` y, sin `FIN` antes, un `RST` enviado por el servidor. No hubo despedida: algo dentro del servidor perdió el estado —un servicio que se reinició, un cortafuegos que descartó la entrada o un equipo intermedio—. Lo relevante no es el RST en sí, sino que el cliente seguía creyendo en una conversación que el otro lado ya había olvidado.

## Errores que se repiten

- Aprender las banderas de memoria sin asociarlas a estados.
- Tomar un ACK aislado por una conexión completa.
- Leer `TIME_WAIT` como un problema de rendimiento.
- Creer que esconder el RST hace invisible un puerto.
- Suponer que el puerto de origen identifica al usuario.

## Fuentes

- RFC 9293, *Transmission Control Protocol (TCP)* (2022), que sustituye al RFC 793 de 1981.
- RFC 3168 (2001), notificación explícita de congestión y origen de ECE y CWR.
- RFC 6093 (2011), revisión del mecanismo de datos urgentes.
