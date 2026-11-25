# Seguridad de la información y ENS

Los marcos de seguridad se parecen al código de circulación: no conducen por ti, pero fijan límites, prioridades y qué hacer cuando hay un choque. Sin ellos, cada área inventa su propia norma y nadie sabe cuál prevalece cuando dos instrucciones se contradicen.

## El sistema de gestión y la ISO/IEC 27001

Un sistema de gestión de la seguridad de la información (SGSI) reúne políticas, procesos y controles para proteger la confidencialidad, la integridad y la disponibilidad. La ISO/IEC 27001:2022 es su norma de referencia: define el sistema, sigue el ciclo de planificar, hacer, verificar y actuar, y agrupa los controles del anexo en cuatro bloques —organizativos, de personas, físicos y tecnológicos—.

La norma es certificable y sirve tanto a empresas privadas como a proveedores del sector público. Un SGSI no es una lista de antivirus: es la forma de demostrar que los controles responden a riesgos concretos y que se revisan con el tiempo.

El sistema se apoya en un análisis de riesgos propio. Dos organizaciones pueden certificarse con controles distintos porque sus riesgos y su apetito no son los mismos; lo que comparten es el método para elegirlos y la evidencia de que funcionan.

Los cuatro bloques del anexo no son compartimentos estancos. Un control organizativo, como la definición de roles, condiciona los controles de personas; uno físico, como el acceso a una sala, se apoya en uno tecnológico, como el registro de entradas. La auditoría mira la relación, no la lista.

## El ENS

El Esquema Nacional de Seguridad (ENS) se regula por el Real Decreto 311/2022 y se aplica a las Administraciones Públicas y a los proveedores que les prestan servicios. Exige categorizar el sistema de información —básica, media o alta—, aplicar medidas proporcionadas al nivel, gestionar riesgos, controlar accesos, garantizar la continuidad y notificar incidentes al CCN-CERT.

No es una recomendación: es una obligación con consecuencias contractuales. Un proveedor que no acredita el nivel exigido puede quedarse fuera de un contrato público, aunque su seguridad técnica sea razonable.

La categorización no es un ejercicio de estilo: decide qué medidas son exigibles y qué evidencias hay que conservar. Cambiar el nivel de un sistema cambia sus obligaciones, de modo que la decisión se documenta y se revisa cuando cambia el servicio.

El ENS también pide evidencias de que las medidas están implantadas. Una declaración de conformidad sin registros de acceso, pruebas de continuidad o trazas de incidentes se queda en una afirmación que nadie puede contrastar.

El ENS y la ISO/IEC 27001 se parecen en el fondo, pero no son intercambiables. El ENS es obligatorio y tiene lenguaje propio; la ISO es voluntaria y certificable. Un proveedor puede alinear ambos para no duplicar controles, siempre que no pierda las obligaciones específicas que el ENS añade.

El alineamiento se documenta con un mapa de correspondencias: qué control del ENS cubre cada medida del SGSI y cuál queda sin equivalente. Sin ese mapa, la duplicación se descubre en la auditoría, cuando ya no hay margen para simplificar.

## NIS y NIS2

La Directiva (UE) 2016/1148, conocida como NIS, se transpuso en España por el Real Decreto-ley 12/2018. Obliga a los operadores de servicios esenciales y a los proveedores de servicios digitales a adoptar medidas de seguridad y a notificar incidentes relevantes a los equipos de respuesta ante emergencias de seguridad correspondientes: el CCN-CERT para el sector público, incluidas las administraciones locales, y el INCIBE-CERT para el sector privado.

La Directiva (UE) 2022/2555, NIS2, sustituye a la anterior y amplía el ámbito: más sectores, más entidades y obligaciones reforzadas de gestión de riesgos y notificación. La transposición española debe comprobarse en el BOE antes de citarla como hecho, porque la información sobre su estado puede estar desactualizada.

Esa cautela no es un formalismo. Una nota que cite una norma nacional de transposición sin comprobarla puede envejecer en semanas; la referencia europea es estable, pero la obligación concreta depende del derecho interno.

| Marco | Ámbito principal | ¿Obligatorio? | Notificación |
|---|---|---|---|
| **ENS** | Administraciones Públicas y proveedores | Sí (Real Decreto 311/2022) | CCN-CERT |
| **NIS** | Operadores de servicios esenciales y proveedores digitales | Sí (Real Decreto-ley 12/2018) | CCN-CERT o INCIBE-CERT |
| **NIS2** | Ámbito ampliado: más sectores y entidades | Sí (Directiva 2022/2555; comprobar transposición) | CCN-CERT o INCIBE-CERT |
| **ISO/IEC 27001** | Cualquier organización | Voluntario, certificable | No aplica |

La notificación no es el único deber. NIS exige medidas técnicas y organizativas, y el incidente se declara para que otros puedan protegerse y para que la autoridad evalúe el impacto, no solo para cumplir un formulario. Un mismo suceso puede activar obligaciones distintas —ENS, NIS o protección de datos— y el procedimiento debe decir a quién se informa y en qué orden.

## Infraestructuras críticas

La Ley 8/2011, conocida como Ley PIC, regula la protección de las infraestructuras críticas: activos o servicios cuya interrupción afecta gravemente a la sociedad. El Centro Nacional de Protección de Infraestructuras Críticas coordina el sistema.

La ley no sustituye a los marcos anteriores; añade un régimen de protección para los servicios que no pueden fallar. Un operador puede estar sujeto a la vez al ENS, a NIS y a la Ley PIC, con obligaciones que se solapan y evidencias que conviene unificar.

La coordinación entre marcos es una decisión de arquitectura, no un trámite. Un registro único de incidentes y un mapa de obligaciones compartido evitan que el mismo suceso se notifique tres veces con tres relatos distintos.

## Continuidad

La ISO 22301:2019 aporta el método para identificar procesos críticos, analizar impactos y definir planes de recuperación. Dos medidas ordenan la conversación:

- **RTO** (*recovery time objective*): tiempo máximo que puede estar caído un servicio.
- **RPO** (*recovery point objective*): cantidad máxima de datos que se puede perder.

Un plan de continuidad que nunca se prueba es solo una carpeta con buena intención. La prueba revela si las copias se restauran, si el personal sabe qué hacer y si el RTO declarado resiste la realidad.

El RTO y el RPO no son independientes del negocio. Un sistema de nóminas y un blog corporativo admiten ventanas distintas; fijar los mismos valores para todo suele significar que nadie ha analizado el impacto real de una caída.

El plan también necesita un orden de recuperación. No todos los servicios vuelven a la vez: si la identidad no funciona, el resto espera. Ese orden se decide con el negocio y se prueba, porque en pleno incidente no hay tiempo para negociarlo.

## Un proveedor municipal

Una empresa de servicios cloud presta servicio a varios ayuntamientos. Debe cumplir el ENS, categorizar sus sistemas de información y notificar incidentes al CCN-CERT. Si falla una copia de seguridad, su RTO y su RPO determinan cuánto tarda en recuperar el servicio y cuántos datos puede perder.

La obligación no desaparece porque el proveedor sea privado. El ENS alcanza a quien presta el servicio, y el contrato debe repartir responsabilidades sin convertir la Administración en espectadora de su propio incidente.

## Fuentes

- Real Decreto 311/2022, de 3 de mayo, por el que se regula el Esquema Nacional de Seguridad.
- Directiva (UE) 2016/1148 (NIS) y Real Decreto-ley 12/2018, de 7 de septiembre, de seguridad de las redes y sistemas de información.
- Directiva (UE) 2022/2555 (NIS2).
- Ley 8/2011, de 28 de abril, por la que se establecen medidas para la protección de las infraestructuras críticas.
- ISO/IEC 27001:2022, *Information security, cybersecurity and privacy protection — Information security management systems — Requirements*.
- ISO 22301:2019, *Security and resilience — Business continuity management systems — Requirements*.
