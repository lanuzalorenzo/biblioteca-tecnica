# Datos en Azure

Un almacén de datos se define por tres decisiones que se toman antes del primer byte: dónde se guarda, cuántas copias se mantienen y quién puede leer. Todo lo demás —rendimiento, índices, consultas— se puede cambiar después. Estas tres, no.

## Almacenamiento de blobs

**Azure Storage** guarda cuatro cosas distintas bajo una misma cuenta: objetos (blobs), ficheros compartidos, colas y tablas. La cuenta de almacenamiento es la unidad de configuración: redundancia, red, claves y cifrado se definen en ella.

La **redundancia** decide cuántas copias hay y dónde:

| Opción | Copias | Alcance |
|---|---|---|
| Local | Tres, en un centro de datos | Un edificio |
| Por zona | Tres, repartidas entre zonas | Una región |
| Geográfica | Seis, en dos regiones | Una pareja de regiones |
| Geográfica con lectura | Las mismas, con lectura en la secundaria | Pareja de regiones |

Los **niveles de acceso** —frecuente, esporádico, frío y archivo— cambian el coste de guardar por el coste de leer. Archivar abarata el almacenamiento y encarece la recuperación, que además tarda horas. Poner ahí lo que se consulta cada semana es una forma silenciosa de perder dinero.

El acceso se decide entre la **clave de la cuenta**, que da control total y no se puede limitar, y **Microsoft Entra ID con roles de datos**, que identifica a la persona o a la identidad administrada. Las firmas de acceso compartido sirven para delegar un acceso temporal, pero una firma de cuenta o de servicio se firma con la clave y hereda su riesgo; la delegación de usuario, en cambio, se firma con credenciales de Entra ID y se puede revocar.

En las cuentas nuevas, el acceso público anónimo viene desactivado. Conviene que siga así y que la red se limite a las subredes o al punto de conexión privado.

## Ficheros compartidos

Azure Files expone un recurso compartido por SMB o NFS. Es la opción para levantar una aplicación antigua que escribe en una unidad de red o para compartir archivos entre varias máquinas. El recurso compartido se monta como una carpeta y la aplicación no cambia.

El límite importa: un recurso compartido estándar llega a 5 TiB; con recursos compartidos grandes, a 100 TiB. La identidad se resuelve con Entra ID o con servicios de dominio, no con la clave de la cuenta. NFS solo está en el nivel premium y no admite todas las combinaciones de redundancia.

## Colas

Azure Queue Storage guarda mensajes de hasta 64 KB durante un máximo de siete días. El consumidor toma un mensaje, lo procesa y lo borra; si no lo borra, el mensaje vuelve a estar visible tras el tiempo de visibilidad. Esa reaparición es la que obliga a que el consumidor sea idempotente.

La cola no garantiza orden ni entrega única. Para orden, sesiones o mensajes mayores está Service Bus. Para trabajos simples y baratos, la cola de Storage sobra.

## Tablas

Table Storage guarda pares clave-valor con dos claves: partición y fila. La partición agrupa lo que se consulta junto y es la que decide el rendimiento; una consulta que cruza particiones es más lenta y más cara.

Es una opción barata para datos sencillos y voluminosos, como estados o registros. No tiene consultas relacionales, ni transacciones fuera de una partición, ni índices secundarios. Cuando eso hace falta, Cosmos DB o una base relacional.

## Firmas de acceso compartido

Una SAS delega un acceso temporal a un recurso concreto, con permisos y caducidad. Hay tres tipos: de cuenta, de servicio y de delegación de usuario. Los dos primeros se firman con la clave de la cuenta y heredan su riesgo: quien obtiene la clave puede firmar cualquier cosa.

La delegación de usuario se firma con credenciales de Entra ID, se puede revocar y es la que conviene usar desde una aplicación. Para emitir SAS de servicio sin repartir la clave, se apoya en una política de acceso almacenada, que permite revocar las firmas emitidas.

Una SAS sin caducidad o con permiso de escritura sobre todo el contenedor es una credencial permanente en una URL. Se limita el recurso, el permiso y el tiempo.

## Ciclo de vida

Las reglas de ciclo de vida mueven un blob de nivel o lo borran según su antigüedad o su último acceso. Son la forma de que el archivo no se quede en frecuente pagando de más.

Una regla típica mueve a esporádico a los 30 días, a frío a los 90 y a archivo al año; otra borra las versiones anteriores a los 30 días. Cada regla se prueba sobre una etiqueta antes de aplicarla al contenedor entero. Mover a archivo lo que se consulta cada semana cuesta más en recuperación de lo que ahorra.

## Bases de datos relacionales

**Azure SQL** separa el servidor lógico de la base de datos. El servidor es la puerta: cortafuegos, administración de identidades y reglas de auditoría. La base de datos es donde viven los datos y donde se elige la potencia, que puede ser fija o elástica entre varias bases.

Dos ajustes se revisan siempre. El primero, la regla de cortafuegos que permite el acceso desde servicios de Azure: abre la puerta a cualquier recurso de la plataforma y mucha gente la usa para no configurar red privada. El segundo, la autenticación: con Entra ID, los usuarios y las identidades administradas entran sin contraseña de base de datos.

El cifrado en reposo viene activo y la clave la gestiona la plataforma; se puede sustituir por una clave propia en Key Vault, con el coste de tener que administrarla. La copia de seguridad automática permite restaurar a un punto en el tiempo dentro de una ventana de días configurable. Esa ventana es el objetivo de recuperación real, no lo que diga el diseño.

## Bases de datos distribuidas

**Cosmos DB** guarda documentos, pares clave-valor, grafos o tablas con replicación entre regiones. El coste se mide en unidades de petición por segundo, que resumen lectura, escritura y almacenamiento en un solo número.

La **clave de partición** es la decisión que no se puede corregir barata: tiene que repartir el volumen y las consultas. Si todas las escrituras caen en la misma partición, el rendimiento se limita aunque sobre capacidad.

La **consistencia** es un ajuste explícito con cinco niveles, del más fuerte al más débil. Cuanto más fuerte, más latencia y menos disponibilidad en la escritura; cuanto más débil, más rápido pero con riesgo de leer algo desactualizado.

## Copia, retención y borrado

Tener replicación no es tener copia de seguridad: un borrado o una corrupción se replica igual. Lo que protege es otra cosa —restauración a un punto en el tiempo, versiones anteriores de un blob, retención inmutable, borrado suave— y cada una cubre un escenario distinto.

La prueba que importa no es que la copia exista, sino que se haya restaurado alguna vez y se sepa cuánto tarda. Un plan de recuperación sin ensayo es una hipótesis.

## Qué revisar

- ¿Cada almacén tiene la redundancia que pide su criticidad?
- ¿Hay datos en el nivel de archivo que se consultan a menudo?
- ¿El acceso es por identidad o por clave compartida?
- ¿Queda algún contenedor con acceso anónimo o con cortafuegos abierto a la plataforma?
- ¿La copia se prueba y se sabe el tiempo de restauración?
- ¿La clave de partición reparte de verdad?
