# Higiene y ciclo de vida

La higiene digital es el conjunto de medidas mínimas que se aplican antes de que ocurra nada: parches, copias, contraseñas, configuración. El ciclo de vida es lo que se activa cuando, a pesar de todo, algo ocurre. Uno reduce la probabilidad; el otro reduce el daño y permite volver a operar.

## El decálogo como lista mínima

El Centro Criptológico Nacional publica y actualiza un decálogo de principios generales de ciberseguridad. Resume las medidas que no deberían faltar en ninguna organización:

1. **Cultura y concienciación.** La concienciación del empleado es uno de los pilares de la seguridad.
2. **Correo.** No abrir enlaces ni descargar adjuntos con indicios fuera de lo habitual.
3. **Herramientas de seguridad.** Antivirus, antimalware, cortafuegos personal y borrado seguro son irrenunciables.
4. **Superficie de exposición.** No basta con proteger el acceso: hay que dejar solo los servicios estrictamente necesarios.
5. **Cifrado.** Cifrar la información sensible y revisar el mecanismo para usar el más fuerte disponible.
6. **Contraseñas.** Adaptadas a la función, con doble o múltiple factor. La recomendación tradicional de renovarlas con frecuencia ha quedado atrás: la práctica actual, recogida en NIST SP 800-63B, desaconseja la rotación periódica sin indicios y prioriza longitud, unicidad y MFA.
7. **Borrado seguro.** Eliminar la información cuando ya no se necesita o se retira el soporte.
8. **Copias de seguridad.** Periódicas, con varias réplicas y cuidadas para no respaldar también el malware.
9. **Actualizaciones.** Mantener aplicaciones y sistema operativo al día es la mejor forma de protegerse de lo conocido.
10. **Configuración.** Revisar periódicamente la configuración de seguridad, los permisos y las opciones.

El decálogo no es una lista para memorizar sin entender. Cada punto responde a una de las tres reglas: la cultura y el correo son concienciación; las herramientas, la superficie, el cifrado, las contraseñas, el borrado, las actualizaciones y la configuración son prevención; las copias sostienen la respuesta y la recuperación.

## Las tres reglas detrás del decálogo

La prevención cubre lo que ya se conoce: una vulnerabilidad publicada, un tipo de malware documentado, una configuración insegura. La concienciación cubre lo que no se puede enumerar de antemano: un correo raro, una llamada que pide credenciales, un mensaje que mete prisa. La respuesta cubre el peor caso: el incidente que ninguna de las dos anteriores evitó.

Las tres se necesitan. Una organización con parches al día pero sin personas formadas sigue siendo vulnerable al engaño. Una organización concienciada pero sin copias probadas puede perder semanas de trabajo. Y una organización con un plan de respuesta que nadie ha leído tiene un documento, no una capacidad.

## El ciclo de vida de un incidente

El ciclo ordena lo que ocurre desde antes del incidente hasta después:

1. **Prevención inicial.** Medidas previas: inventario, parches, permisos, formación.
2. **Detección.** IDS, IPS, SIEM, analistas y cualquier persona que advierte algo raro.
3. **Mitigación.** Evitar que el incidente se expanda mientras se averigua qué pasa.
4. **Contención.** Aislar cuando ya se sabe qué ha pasado y por dónde ha entrado.
5. **Erradicación.** Eliminar la causa: el malware, la cuenta comprometida, la vulnerabilidad explotada.
6. **Recuperación.** Volver a poner el servicio en marcha con el plan de continuidad y el plan de recuperación ante desastres.
7. **Protección y mejora.** Corregir, documentar y actualizar el plan de respuesta para la próxima vez.

Mitigación y contención no son lo mismo. La mitigación frena el daño con lo que se sabe en ese momento; la contención aísla de forma deliberada cuando el alcance está más claro. Actuar demasiado pronto sobre un sistema puede destruir evidencia; actuar demasiado tarde puede permitir que el ataque se extienda. Esa tensión se resuelve con un plan y con criterio, no con improvisación.

## El plan de respuesta a incidentes

El plan de respuesta, conocido por sus siglas IRP, es la base de la respuesta. Evalúa los activos críticos, fija las cadenas de comunicación y las responsabilidades, y decide qué hacer en cada escenario. Cuando surge un incidente, se consultan las tablas de activos, se identifican los afectados y se categoriza. De la categoría salen el impacto y la prioridad.

Un plan útil cabe en la cabeza de quien está de guardia y se encuentra rápido cuando hay prisa. Debe responder, como mínimo:

- Qué activos son críticos y quién responde de cada uno.
- A quién se avisa dentro y fuera de la organización.
- Quién decide aislar un servicio, apagarlo o mantenerlo funcionando.
- Cómo se conserva la evidencia.
- Cuándo se notifica a una autoridad o a las personas afectadas.
- Dónde están las copias y cómo se comprueba que se pueden restaurar.

El plan se escribe antes, se prueba y se actualiza después de cada incidente o de cada cambio relevante. Un plan que nunca se ha revisado suele contener números de teléfono antiguos, roles que ya no existen y procedimientos que la realidad ha desmentido.

## Detección en el terminal: EDR y XDR

EDR significa *Endpoint Detection and Response*: detección y respuesta en el terminal. No es un «Sistema Europeo de Retransmisión de Datos»; esa lectura es un error frecuente. Un EDR registra comportamiento, detecta patrones sospechosos y permite responder sobre el propio equipo, no solo avisar.

XDR es su evolución ampliada, *Extended Detection and Response*. Integra señales de terminal, red, correo y nube para correlacionarlas. No es una simple herramienta de retransmisión ni un antivirus con otro nombre: su valor está en unir piezas que por separado no cuentan la misma historia.

## ATT&CK y las fases

MITRE ATT&CK describe las tácticas y técnicas del adversario: qué hace un atacante en cada fase y cómo se puede reconocer. Es una base de conocimiento, no un plan de respuesta. Situar el ciclo en prevención, detección, protección y respuesta es una agrupación didáctica; ATT&CK ayuda a localizar la técnica concreta, pero no sustituye al IRP ni a la decisión de la organización.

## Ejemplo: ransomware

Un ransomware cifra los documentos de un servidor. La prevención incluye parches, copias probadas y formación para no abrir el adjunto que lo introdujo. La detección puede llegar por el EDR, por un usuario que no puede abrir sus archivos o por una alerta de tráfico anómalo. La contención aísla el equipo afectado; la erradicación elimina la muestra y la persistencia; la recuperación restaura desde una copia que se ha verificado y que no estaba conectada al mismo recurso. La mejora revisa cómo entró, qué copia falló y qué regla de detección se puede ajustar.

La copia es la medida que más se nombra y la que más se descuida. Una copia que nunca se ha restaurado es una esperanza; una copia conectada permanentemente al servidor puede cifrarse junto con los datos. La prueba de restauración forma parte de la medida, no es un extra.

## La copia que no se restaura no existe

Una copia se diseña con tres preguntas: qué se copia, cada cuánto y cuánto tiempo se tarda en restaurar. La tercera es la que se olvida. Un volumen enorme de copias diarias no sirve si la restauración completa tarda más de lo que el negocio puede esperar.

Conviene probar la restauración de forma periódica y registrar el resultado. La prueba no solo valida la copia: valida el procedimiento, los permisos y el orden en que se levantan los servicios. Un plan de recuperación que nunca se ha ejecutado es un guion sin ensayo.

## Cierre

La higiene reduce la probabilidad y el ciclo de vida reduce el daño. Ninguna de las dos es un producto que se instala: son prácticas que se revisan. El siguiente paso es bajar al lugar donde la información se maneja todos los días: el puesto de trabajo.
