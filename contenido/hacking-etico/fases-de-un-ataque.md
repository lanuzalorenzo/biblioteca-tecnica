# Fases de un ataque

Una mudanza no se improvisa: primero se decide qué se lleva, luego se embala, después se carga y al final se comprueba que todo ha llegado. Una intrusión también sigue una secuencia reconocible. Dividirla en fases ayuda a entender qué ocurre en cada momento, dónde puede detectarlo un defensor y qué técnica encaja en cada paso.

## Por qué se habla de fases

Una intrusión no es un acto único, sino una cadena: informarse, localizar un punto débil, aprovecharlo, asegurar el acceso y avanzar hacia el objetivo. El esquema sirve a tres destinatarios: al atacante le da un método; al defensor, un mapa de oportunidades de detección; al estudiante, una estructura para ordenar técnicas que, de otro modo, parecen herramientas sueltas.

Las fases no son estrictamente lineales. Al obtener acceso se descubre una red interna y se vuelve a reconocer y escanear desde la nueva posición. Tampoco se recorren siempre todas ni con la misma intensidad: un atacante oportunista puede saltarse el reconocimiento y un adversario dirigido puede dedicar semanas a él. El modelo es una simplificación útil, no una ley.

## Las cinco fases

### 1. Reconocimiento

Se construye un mapa de la organización con el menor contacto posible: dominios y subdominios, direcciones IP, tecnologías, empleados y proveedores. Las fuentes suelen ser públicas: registros DNS y de certificados, buscadores con operadores avanzados, redes sociales y profesionales, ofertas de empleo, repositorios de código, metadatos de documentos y credenciales filtradas.

El reconocimiento pasivo no interactúa con los sistemas y es casi invisible; el activo, como visitar la web o consultar DNS directamente, deja huellas modestas. La defensa reduce lo que se expone, limpia metadatos, controla los registros públicos y vigila filtraciones. Investigar personas implica tratar datos personales: que una información sea pública no autoriza a recopilarla y combinarla sin límite.

### 2. Escaneo y enumeración

Empieza la interacción directa. Se busca qué equipos responden, qué puertos y servicios exponen, qué versiones y sistemas operativos usan, y qué recursos, cuentas o directorios se pueden enumerar. El análisis de vulnerabilidades contrasta esos datos con bases de fallos conocidos y produce una lista de puntos de entrada candidatos.

Es la fase que más rastro deja: cortafuegos con intentos de conexión a muchos puertos, alertas de detección y peticiones anómalas. También puede causar problemas de disponibilidad en servicios antiguos o industriales, por lo que el ritmo y las franjas se pactan en las reglas de actuación.

### 3. Obtención de acceso

Convierte un punto de entrada en un acceso real: una sesión, una cuenta o la capacidad de ejecutar órdenes. Las vías no se limitan a un fallo de software: credenciales débiles, por defecto o robadas, servicios mal configurados, fallos web, engaño a una persona, interceptación de credenciales o acceso a una red inalámbrica débil. El resultado es un *foothold*, un punto de apoyo inicial.

Los rastros típicos son alertas de detección, errores y comportamientos anómalos en los registros, procesos inesperados e inicios de sesión fuera de lo habitual.

### 4. Mantenimiento del acceso y consolidación

El atacante asegura y amplía la posición: eleva privilegios, recopila credenciales, avanza lateralmente y deja mecanismos para volver aunque se corrija el fallo original. Los rastros incluyen cuentas o tareas que nadie creó, conexiones salientes periódicas, accesos entre equipos que no solían comunicarse y cambios de configuración.

En un test de intrusión, la persistencia solo se instala si el alcance la autoriza expresamente; cada elemento creado se registra y se retira al terminar.

### 5. Borrado de huellas

Un atacante real altera o elimina registros, manipula marcas de tiempo y usa canales cifrados o herramientas legítimas para confundirse con la actividad normal. Un auditor **no** replica esta fase: conserva una cronología rigurosa de lo que hizo para que el cliente compruebe si sus sistemas lo detectaron.

La cara defensiva es central: los registros deben enviarse a un sistema centralizado fuera del alcance de quien compromete una máquina, protegerse su integridad y tratar la ausencia de registros como una alarma.

## Las dos fases que añade un pentest

Un auditor recorre las fases anteriores con límites y añade dos tramos propios:

- **Preparación y autorización**: alcance, reglas de actuación y documentos firmados.
- **Documentación y reporte**: informe técnico y ejecutivo, evidencias y recomendaciones.

Son las que convierten una intrusión en un servicio profesional.

## Resumen comparativo

| Fase | Qué busca | Rastro para el defensor |
|---|---|---|
| 1. Reconocimiento | Mapa de la organización y su superficie de ataque | Casi ninguno si es pasivo; leve si es activo |
| 2. Escaneo y enumeración | Inventario de equipos, servicios y vulnerabilidades | Abundante: cortafuegos, IDS/IPS, registros |
| 3. Obtención de acceso | Un punto de apoyo en el objetivo | Alertas, errores, accesos anómalos |
| 4. Mantenimiento y consolidación | Ampliar y asegurar la posición | Cuentas y tareas nuevas, conexiones salientes |
| 5. Borrado de huellas | Ocultar la actividad | Huecos o incoherencias en los registros |

## Modelos del atacante

- **Cyber Kill Chain** (Lockheed Martin, hacia 2011): reconocimiento, preparación del arma, entrega, explotación, instalación, mando y control y acciones sobre el objetivo. Su idea fuerte es que romper un eslabón detiene la cadena y que conviene detectar pronto. Encaja peor con robo de credenciales, amenazas internas o servicios en la nube.
- **MITRE ATT&CK**: organiza comportamiento observado en tácticas y técnicas, no como una cadena lineal sino como una matriz. Se usa para describir incidentes con un vocabulario común, medir la detección de los controles y diseñar simulaciones de adversario. Existen matrices para empresa, móvil y sistemas de control industrial.

## Metodologías del auditor

- **PTES**: interacciones previas, inteligencia, modelado de amenazas, análisis de vulnerabilidades, explotación, postexplotación e informe. Útil como lista de comprobación de un proyecto.
- **NIST SP 800-115**: planificación, descubrimiento, ataque e informe. Referencia neutral y habitual en pliegos y cumplimiento; conviene comprobar si hay una revisión más reciente.
- **OSSTMM**: enfoque cuantitativo orientado a medir la superficie de ataque operativa.
- **Guías OWASP**: la Web Security Testing Guide para aplicaciones web y la guía equivalente para móviles.

Las equivalencias entre modelos son orientativas: cada uno reparte el trabajo de forma distinta. Un profesional combina la metodología que mejor estructura el encargo, el modelo que mejor comunica al equipo defensivo y las cinco fases como esquema mental. Todos son abstracciones: una intrusión por identidad en la nube o por cadena de suministro puede no encajar en el esquema clásico.

## Las fases en un caso ficticio

> **Ejemplo hipotético.**

En una empresa de logística, un atacante real descubre en registros de certificados un subdominio de pruebas olvidado, localiza un servicio de ficheros con acceso anónimo, explota una vulnerabilidad conocida, crea una cuenta persistente y salta a la red del almacén. El equipo auditor, en cambio, recopila solo información de los dominios incluidos, escanea a ritmo limitado dentro de la ventana, demuestra la ejecución de una orden inocua y no instala persistencia porque está prohibida. Finalmente entrega una cronología detallada sin alterar registros.

Las defensas más eficaces actúan pronto: reducir la exposición, parchear y bastionar, segmentar la red, exigir segundo factor y centralizar y proteger los registros. La misma cadena de acciones es una intrusión o una prueba según el alcance, que decide hasta qué fase se llega.

## Procedimiento

Para analizar un ataque o planificar una prueba:

1. Identifica la fase y el objetivo que se persigue en ella.
2. Determina qué información hace falta antes de pasar a la siguiente.
3. Reconoce el rastro que deja y la oportunidad de detección asociada.
4. Comprueba si el alcance autoriza la actividad y hasta dónde.
5. Registra la actividad y los elementos creados, y retíralos al terminar.
6. Documenta hallazgos, impacto y recomendaciones.

## Aviso de alcance

> Las fases cuatro y cinco solo se ejecutan completas en un ataque real. En una prueba autorizada, la persistencia, el movimiento lateral y el acceso a datos requieren autorización expresa; el impacto se demuestra con la intervención mínima y el auditor nunca borra sus huellas.

## Glosario

| Término | Definición |
|---|---|
| ATT&CK | Marco de tácticas y técnicas de adversarios mantenido por MITRE. |
| Enumeración | Obtención de información detallada de servicios y recursos. |
| Foothold | Punto de apoyo inicial en un sistema comprometido. |
| OSSTMM | Metodología abierta de pruebas de seguridad orientada a métricas. |
| PTES | Estándar de ejecución de pruebas de penetración. |
| Pivotaje | Acceso a otros sistemas desde uno ya comprometido. |

## Fuentes

- NIST. *SP 800-115, Technical Guide to Information Security Testing and Assessment*.
- PTES: *Penetration Testing Execution Standard*.
- MITRE ATT&CK y Lockheed Martin, *Cyber Kill Chain*.
