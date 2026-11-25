# Almacenamiento y copias de seguridad

Un RAID es como llevar dos ruedas de repuesto en el mismo coche: si una se pincha, sigues. Pero si el coche se cae por un barranco, las de repuesto se van con él. Redundancia y copia de seguridad resuelven problemas distintos, y confundirlas es la causa más común de perder datos para siempre.


## RAID: disponibilidad, no respaldo

RAID combina varios discos en una unidad lógica. Lo que aporta es que el fallo de un disco no detenga el servicio, y en algunos niveles, más velocidad o más capacidad.

| Nivel | Qué hace | Tolera | Capacidad útil | Lectura / escritura |
|---|---|---|---|---|
| 0 | Reparte los datos entre discos | Ningún fallo | 100 % | Muy rápida |
| 1 | Espejo por parejas | Un disco por pareja | 50 % | Lectura rápida, escritura igual |
| 5 | Reparte datos y paridad | Un disco | n−1 discos | Lectura rápida, escritura penalizada |
| 6 | Doble paridad | Dos discos | n−2 discos | Igual, con más coste |
| 10 | Espejo de grupos en franjas | Un disco por grupo | 50 % | La mejor para escritura |

El RAID 5 con discos grandes tiene un problema práctico: al reconstruir hay que leer todos los discos y un solo error de lectura no recuperable —del orden de uno cada 10<sup>14</sup> bits en discos de consumo y 10<sup>15</sup> en discos empresariales— deja el conjunto irrecuperable, justo cuando más se necesita. Por eso, con discos de varios terabytes, se prefiere RAID 6 o RAID 10.

RAID **no** protege de un borrado accidental, de un cifrado por ransomware, de un fallo del controlador ni del robo del servidor: replica el error junto con los datos.

## Dónde vive el almacenamiento

- **DAS:** discos conectados directamente al servidor. Simple y barato; su disponibilidad es la del servidor.
- **NAS:** aparato en red que comparte ficheros por SMB o NFS. Fácil de usar y de copiar; el protocolo de ficheros impone latencia.
- **SAN:** red dedicada que ofrece bloques de disco, normalmente por fibra o iSCSI. Es lo que usan los sistemas que necesitan rendimiento y clusters.
- **Objeto:** almacenamiento por API (S3 y compatibles), pensado para volumen, versionado y retención. Es donde han ido a parar las copias que antes ocupaban cinta.

Un **clúster** es un conjunto de máquinas que trabajan como una sola para dar servicio; pertenece a la parte de alta disponibilidad, no al almacenamiento.

## Copias: cinco decisiones

1. **Qué se copia.** Datos, configuración y, aparte, el sistema. Identificar antes qué es irrecuperable.
2. **Cada cuánto.** Lo marca el RPO: cuánto dato se puede perder. Una copia diaria de una base de datos que cambia cada minuto pierde un día entero.
3. **Cómo.** Completa, incremental o diferencial.
4. **Dónde.** Nunca en el mismo soporte, ni en el mismo servidor, ni con las mismas credenciales.
5. **Cómo se restaura.** Y si esa restauración se ha probado.

### Tipos de copia

- **Completa:** todo, cada vez. Restaurar es copiar y ya; ocupa y tarda más.
- **Diferencial:** lo que ha cambiado desde la última completa. Para restaurar hacen falta la completa y la última diferencial. Crece con los días.
- **Incremental:** lo que ha cambiado desde la última copia, sea del tipo que sea. Ocupa menos y es más rápida, pero restaurar exige encadenar todas las piezas desde la última completa: un eslabón roto rompe la cadena.

### La regla 3-2-1

Tres copias, en dos medios distintos, con una fuera de la instalación. La variante que se usa contra el ransomware añade una copia **desconectada o inmutable** y una **verificación** de que se puede restaurar: 3-2-1-1-0. La regla es una práctica extendida, no una norma; su valor está en obligar a separar las copias del original.

## Consistencia

Copiar un fichero que se está escribiendo produce una copia que parece válida y no lo es. En bases de datos se hace un volcado lógico o se usa el mecanismo de copia en caliente del motor; en sistemas de ficheros, una instantánea coherente. En Windows, el servicio de instantáneas de volumen (VSS) coordina aplicaciones y disco para que la copia represente un instante único.

## Lo que no es una copia de seguridad

- **Una instantánea** (*snapshot*): vive en el mismo almacenamiento y con las mismas credenciales. Sirve para volver atrás cinco minutos; si el volumen se corrompe o lo cifran, se va con él.
- **Una imagen del sistema** tomada una vez: restaura el equipo como estaba, no los datos de ayer.
- **Un RAID:** ya visto.
- **Una carpeta sincronizada en la nube:** si el ransomware cifra el original, la sincronización propaga el cifrado. Solo cuenta si tiene versionado e historial independiente.

## Protección frente a ransomware y borrado

La copia tiene que ser inalcanzable desde la cuenta que se ve comprometida:

- **Inmutabilidad** (*object lock*, WORM): durante un plazo, nadie puede modificar ni borrar, ni con privilegios de administrador.
- **Air gap:** el medio se conecta solo durante la copia y se retira.
- **Cuentas separadas:** la credencial de copia no puede borrar su propio destino.
- **Retención definida:** cuántos días, semanas y meses se guarda. Se fija antes del incidente, no durante.

## Restaurar: la prueba que casi nadie hace

Una copia sin restauración probada es una hipótesis. Un plan razonable define qué se prueba, cada cuánto y cuánto tarda:

- Restaurar un fichero suelto y una base de datos completa.
- Medir el tiempo real y compararlo con el RTO comprometido.
- Verificar integridad con suma de comprobación, no solo que el fichero exista.
- Hacerlo con la persona que no participó en montar la copia, que es quien descubrirá la documentación que falta.

Si las copias van cifradas —deben ir—, la clave se guarda aparte. Una copia cifrada cuya clave está en el mismo servidor es una copia perdida.

## Lo que ha cambiado

Hasta hace unos años se discutía cintas, copias a DVD y servicios de primera generación. Las piezas que siguen son las mismas —completa, incremental, diferencial, 3-2-1, prueba de restauración—; lo que ha cambiado es el destino: almacenamiento de objeto con versionado e inmutabilidad, deduplicación y compresión para no multiplicar el espacio, y la nube como segunda ubicación en lugar del disco externo que nadie se lleva a casa.

## Fuentes

- ISO/IEC 27001:2022, control de copias de seguridad (A.8.13).
- NIST SP 800-34, guía de contingencias para sistemas de información.
- Especificaciones de tasa de error de lectura no recuperable de los fabricantes de discos.
- Documentación oficial de almacenamiento de objeto (versionado e inmutabilidad).
