# Protección de datos personales

Custodiar datos personales se parece a llevar las llaves de un edificio: no basta con tener buena cerradura; hay que saber cuántas copias existen, quién las tiene, dónde se guardan y qué se hace si se pierde una. La cerradura protege la puerta, no la organización del olvido.

## Qué es un dato personal

Un dato personal es cualquier información que permita identificar o hacer identificable a una persona física, de forma directa o indirecta. Un nombre, un correo, una dirección IP o una matrícula pueden serlo. La clave está en la identificabilidad: si con los medios razonablemente disponibles se puede llegar a la persona, el dato entra en el ámbito.

Los datos anonimizados de verdad quedan fuera; los pseudonimizados siguen siendo personales. Cambiar el nombre por un código no convierte el dato en anónimo si existe una tabla que permite deshacer el cambio, aunque esa tabla esté en otro sistema.

La frontera se mueve con la tecnología. Un conjunto de datos que hace años no permitía identificar a nadie puede ser identificable hoy al cruzarse con otra fuente. Por eso la anonimización se revisa, no se firma una vez y se archiva.

## El marco

El Reglamento (UE) 2016/679, conocido como RGPD, se aplica en toda la Unión Europea. La Ley Orgánica 3/2018, de Protección de Datos Personales y garantía de los derechos digitales, lo adapta y completa en España. Las dos normas se leen juntas: el reglamento fija el marco general y la ley orgánica concreta extremos de aplicación nacional.

## Los siete principios

El artículo 5 del RGPD fija siete principios:

1. Licitud, lealtad y transparencia.
2. Limitación de la finalidad.
3. Minimización de datos.
4. Exactitud.
5. Limitación del plazo de conservación.
6. Integridad y confidencialidad.
7. Responsabilidad proactiva.

En la práctica significan recoger solo lo necesario, decir para qué se usa, guardarlo el tiempo justo, mantenerlo correcto, protegerlo y poder demostrar que se cumple. El último principio es el que sostiene a los demás: no basta con hacerlo bien, hay que poder enseñarlo.

Los principios se aplican a la vez, no por turnos: una finalidad clara no compensa una conservación eterna, y una seguridad impecable no justifica recoger datos que no hacen falta.

## Base jurídica

Todo tratamiento necesita un motivo legal: consentimiento, contrato, obligación legal, interés vital, interés público o interés legítimo. La elección no es libre; depende de la finalidad y del contexto. El interés legítimo, por ejemplo, no prevalece sobre los derechos y libertades del interesado.

La base jurídica se decide antes de tratar, no después. Cambiar de base a mitad del proyecto —«como no hay consentimiento, diremos que es interés legítimo»— es una señal de que el diseño no estaba claro desde el principio.

## Los derechos de las personas

Las personas pueden acceder a sus datos, rectificarlos, suprimirlos, limitar su tratamiento, oponerse y solicitar su portabilidad. También tienen derecho a ser informadas y a no ser objeto de decisiones individuales automatizadas con efectos significativos.

La organización debe responder en el plazo previsto —normalmente un mes, ampliable en casos complejos— y documentar la respuesta. Una solicitud sin registro es una solicitud que, ante la autoridad, no existió.

## DPO, evaluación de impacto y privacidad por diseño

El delegado de protección de datos (DPO) es obligatorio, entre otros casos, cuando se tratan datos sensibles a gran escala, cuando se vigila sistemáticamente a personas o cuando el responsable es una autoridad pública. Su función es supervisar el cumplimiento y servir de contacto con la autoridad de control.

La evaluación de impacto (EIPD) es obligatoria cuando el tratamiento entraña un riesgo alto para los derechos y libertades. La privacidad por diseño exige incorporar medidas desde el inicio; la privacidad por defecto, que la configuración más protectora sea la que venga activada. Las dos se deciden antes de construir, no después de la primera queja.

El DPO no es un cargo decorativo. Si no tiene acceso a los proyectos desde el principio, solo puede opinar cuando cambiar el diseño ya cuesta dinero. Su valor está en la conversación previa, no en el informe final.

## Brechas de seguridad

Si hay una brecha, la organización debe notificarla a la Agencia Española de Protección de Datos en un plazo máximo de 72 horas cuando suponga un riesgo para los derechos y libertades, y comunicarla a las personas afectadas cuando el riesgo sea alto.

La notificación no sustituye la investigación. El plazo empieza cuando se tiene constancia, y llegar a él sin saber qué pasó convierte una obligación de transparencia en un trámite vacío. La investigación deja constancia de qué ocurrió, qué datos se vieron afectados y qué medidas se tomaron.

## Transferencias internacionales

Una transferencia fuera del Espacio Económico Europeo exige una decisión de adecuación, cláusulas contractuales tipo, normas corporativas vinculantes o una excepción concreta. Que el proveedor sea grande no basta: hay que documentar el mecanismo y comprobar que sigue vigente.

El mecanismo puede caducar. Una transferencia que se apoyaba en una decisión de adecuación debe revisarse cuando esa decisión cambia; el contrato firmado no congela la situación jurídica.

## Registro y responsabilidad proactiva

El responsable mantiene un registro de actividades de tratamiento con finalidades, categorías de datos, destinatarios, plazos y medidas. Es la prueba documental del sistema y la base para decidir si hace falta una evaluación de impacto.

Un registro desactualizado es peor que no tenerlo, porque da una falsa sensación de control. La revisión debe formar parte del ciclo de cambios: un servicio nuevo o una finalidad distinta modifica el registro antes de salir a producción.

## Sanciones

Las infracciones se gradúan en leves, graves y muy graves. Las más altas alcanzan 20 millones de euros o el 4 % del volumen de negocio global anual, la cifra que sea mayor. La cuantía depende de la gravedad, el volumen de afectados y la reincidencia, entre otros factores.

La sanción económica no es el único coste. Una brecha mal gestionada daña la confianza, interrumpe servicios y consume tiempo de dirección; el expediente sancionador es la parte visible de un problema más amplio.

## Categorías especiales

Los datos de salud, origen étnico, opiniones políticas, religión, orientación sexual y datos biométricos exigen una base jurídica reforzada y medidas adicionales. No se tratan con el mismo criterio que un correo comercial, aunque el sistema que los guarde sea el mismo.

## Un tratamiento que cruza municipios

Una empresa de servicios cloud firma contratos de encargo de tratamiento con los ayuntamientos clientes y realiza una evaluación de impacto antes de lanzar un servicio que combina datos de varios municipios para crear perfiles de uso. El contrato reparte obligaciones; la evaluación decide si el tratamiento puede hacerse y con qué garantías.

Si la evaluación concluye que el riesgo es alto y no se puede reducir, la respuesta no es añadir una casilla al formulario: es cambiar el diseño o renunciar al tratamiento. La protección de datos se decide en el diseño, y la documentación solo lo demuestra.

## Fuentes

- Reglamento (UE) 2016/679, Reglamento General de Protección de Datos.
- Ley Orgánica 3/2018, de 5 de diciembre, de Protección de Datos Personales y garantía de los derechos digitales.
- Agencia Española de Protección de Datos, guías y resoluciones.
