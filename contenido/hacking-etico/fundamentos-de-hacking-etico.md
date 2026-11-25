# Fundamentos del hacking ético

Probar la seguridad de un sistema se parece a cargar un puente recién construido con camiones de peso conocido antes de abrirlo al tráfico: la carga es real, pero el puente no está en servicio y nadie resulta herido si cede. Lo que separa ese ensayo de un accidente no son los camiones, sino el permiso, el perímetro acotado y el uso que se hace del resultado.

## Qué convierte una prueba en una evaluación legítima

El hacking ético es la evaluación autorizada de sistemas mediante técnicas ofensivas, con un alcance, unos objetivos y unos límites acordados. La técnica es la misma que emplearía un atacante; lo que cambia es el consentimiento, el perímetro y la forma de entregar los hallazgos.

Una prueba de penetración, o *pentest*, es una actividad concreta dentro de ese marco: un encargo acotado a unos activos y a un periodo. Un programa de seguridad más amplio puede incluir además revisiones periódicas, divulgación de fallos, revisión de configuraciones y seguimiento de las correcciones.

La clasificación por sombreros describe motivaciones y permisos, no categorías legales:

- **Sombrero blanco**: actúa con permiso y dentro del alcance acordado.
- **Sombrero negro**: actúa sin autorización y con fines ilícitos.
- **Sombrero gris**: descubre o publica fallos sin permiso previo. Una intención benévola no convierte el acceso no autorizado en una prueba ética.
- **Hacktivismo**: intrusión o interrupción motivada por una causa política o social. No es sinónimo de hacking ético.

Otras etiquetas —*script kiddie*, *insider*, *whistleblower*— describen perfiles o conductas y no sustituyen el análisis de autorización, motivación, impacto y contexto. La diferencia entre hacking, hacking ético, pentest y hacktivismo se desarrolla en [Hacking, pentest y hacktivismo](hacking-pentest-y-hacktivismo.md).

## Los principios de la seguridad de la información

La seguridad de la información protege el dato en cualquier soporte y combina controles técnicos, físicos y organizativos. La seguridad informática se centra en los sistemas que almacenan, procesan o transmiten esa información.

La tríada clásica, conocida por sus iniciales en inglés como **CIA**, reúne tres propiedades:

- **Confidencialidad**: solo acceden a la información las personas o los procesos autorizados.
- **Integridad**: los datos y los sistemas mantienen su exactitud y no se alteran sin autorización.
- **Disponibilidad**: los servicios y los datos están accesibles cuando los necesitan los usuarios autorizados.

A ellas se suman la **autenticidad** y la **autenticación**, que permiten confiar en el origen de una comunicación o verificar la identidad declarada, y el **no repudio**, que aporta evidencias de que una acción ocurrió y de quién participó. El no repudio depende de los mecanismos, la gestión de claves y el contexto: no es una garantía absoluta.

Una debilidad puede afectar a uno o varios principios. La exposición de datos rompe la confidencialidad; una modificación no autorizada, la integridad; la caída de un servicio, la disponibilidad.

## Vulnerabilidad, amenaza, riesgo e impacto

Los cuatro términos se encadenan, pero no son intercambiables:

1. Existe una **vulnerabilidad**, como un permiso excesivo o un error de validación.
2. Una **amenaza** puede aprovecharla si tiene capacidad y oportunidad.
3. El **riesgo** expresa la posibilidad y las consecuencias de que eso ocurra en un contexto concreto.
4. El **impacto** describe el daño resultante: interrupción del servicio, pérdida económica, consecuencias legales o pérdida de confianza.

Valorar bien exige mirar el activo afectado, las protecciones existentes, la exposición y las consecuencias para la organización. El nombre técnico del fallo, por sí solo, no dice nada sobre el daño.

## Cómo se clasifican las debilidades

| Criterio | Ejemplos |
|---|---|
| Acceso necesario | Remota o local. «Local» puede incluir un atacante que ya dispone de acceso inicial. |
| Componente afectado | Cliente, servidor, aplicación, red o configuración, entre otros. |
| Causa | Diseño, implementación, configuración, permisos o proceso. |
| Conocimiento y corrección | Desconocida para el proveedor, divulgada o conocida y pendiente de parche. |

Los términos *zero-day* y *one-day* se usan con matices distintos según la fuente; conviene precisar qué significa cada uno en el informe y no dar por hecho que todos lo leen igual.

## Nombrar y medir un fallo

Tres referencias complementarias acompañan a un hallazgo:

- **CVE** (*Common Vulnerabilities and Exposures*): identifica una vulnerabilidad divulgada concreta.
- **CWE** (*Common Weakness Enumeration*): clasifica el tipo de debilidad, no el caso.
- **CVSS** (*Common Vulnerability Scoring System*): expresa la severidad técnica mediante métricas, un vector y una puntuación.

La puntuación base no sustituye el análisis del contexto ni equivale al riesgo de negocio. Para priorizar hay que considerar la exposición, el activo, las mitigaciones, la probabilidad de explotación y el impacto local. Además, cada versión de CVSS tiene sus propias métricas y sus notas no se comparan entre versiones. El detalle está en [Severidad con CVSS](severidad-con-cvss.md).

## Las fases como mapa

La *Cyber Kill Chain* describe una intrusión en siete etapas: reconocimiento, preparación del arma, entrega, explotación, instalación, mando y control y acciones sobre el objetivo. Otros modelos agrupan el trabajo de otra manera.

Estos esquemas ordenan observaciones y ayudan a pensar dónde prevenir, detectar y responder; no son una secuencia obligatoria ni todos los ataques recorren todas las etapas. En una evaluación autorizada, los objetivos y los límites pactados mandan sobre cualquier modelo. No se instala persistencia, no se mueve lateralmente, no se accede a datos ni se ejecutan acciones destructivas sin autorización expresa y controles específicos: el impacto se demuestra con la mínima intervención posible. Las fases se detallan en [Fases de un ataque](fases-de-un-ataque.md).

## Cuánta información recibe el auditor

El modelo de conocimiento depende de lo que se entrega al equipo antes de empezar:

- **Caja negra**: poca información inicial, desde una perspectiva externa.
- **Caja gris**: información parcial, como una cuenta de usuario o documentación limitada.
- **Caja blanca**: arquitectura, código o cuentas de prueba para un análisis profundo.

Antes de empezar hay que acordar por escrito quién autoriza y quién ejecuta, qué activos entran y cuáles no, qué técnicas se permiten y cuáles se prohíben, las fechas y ventanas, los contactos y el procedimiento de parada, el tratamiento de datos y evidencias, y la forma de comunicar incidentes y resultados. El alcance y las reglas de actuación tienen su propia nota: [Autorización y alcance](autorizacion-y-alcance.md).

## La superficie de internet

La web superficial es la que indexan los buscadores; la profunda, la que no se indexa porque exige autenticación o forma parte de servicios privados; la oscura, la alcanzable solo mediante redes específicas como Tor o I2P. Ninguna de las tres es sinónimo de actividad ilícita y ninguna garantiza anonimato absoluto.

Durante el reconocimiento, la información pública aporta contexto sobre activos y exposición, pero consultarla no autoriza a probar, escanear ni acceder a los sistemas identificados. Servicios como Shodan sirven aquí para observar, no como permiso para sondear dispositivos. Las capas se explican en [Capas de internet](capas-de-internet.md).

## Herramientas ofensivas y defensivas

La elección depende del objetivo, la escala, la experiencia del equipo, el presupuesto y los requisitos de operación. Los ejemplos son ilustrativos y no una recomendación de producto:

| Finalidad | Familias y ejemplos |
|---|---|
| Descubrimiento y auditoría de red | Escáneres como Nmap; análisis de vulnerabilidades como Nessus u OpenVAS |
| Pruebas de aplicaciones web | Proxies de análisis como Burp Suite u OWASP ZAP |
| Simulación controlada de explotación | Marcos como Metasploit |
| Monitorización y detección | IDS/IPS, antivirus o NGAV, EDR, SIEM y SOAR; Suricata, Snort, Wazuh, ELK, Splunk o QRadar |
| Análisis de tráfico | Herramientas de captura y análisis como Zeek |

Las herramientas ofensivas evalúan dentro de un alcance autorizado; las defensivas recogen y analizan señales para detectar o responder. La organización las elige por su arquitectura, su capacidad operativa y sus objetivos, no solo por su tamaño. Los criterios están en [Clasificar herramientas](clasificar-herramientas.md).

## Antes de empezar

1. Confirma la autorización documentada y quién la concede.
2. Define los activos incluidos y excluidos, las fechas y las condiciones.
3. Acuerda técnicas permitidas, límites, contactos y criterios de parada.
4. Decide cómo se protegen credenciales, datos, capturas y artefactos.
5. Ejecuta solo lo pactado y registra evidencia mínima y verificable.
6. Comunica los hallazgos con su impacto y una recomendación.
7. Elimina o devuelve la información de prueba y confirma el cierre.

## Un caso concreto

Una organización autoriza revisar una aplicación de pruebas en una ventana concreta, facilita una cuenta de bajo privilegio y prohíbe las pruebas de denegación de servicio y el acceso a datos personales. El equipo escribe esas restricciones en las reglas de actuación, valida únicamente la aplicación indicada y, si encuentra una debilidad que podría exponer datos, demuestra el riesgo con datos sintéticos y lo comunica sin ampliar el acceso.

## Aviso de autorización

> Estas notas describen técnicas ofensivas con fines formativos. No se aplican a ningún sistema sin autorización escrita de su titular. El laboratorio propio debe estar aislado de la red de la organización, de la red doméstica y de internet a través de adaptadores mal configurados.

## Glosario

| Término | Definición |
|---|---|
| CVE | Identificador de una vulnerabilidad divulgada. |
| CVSS | Sistema para expresar la severidad técnica con métricas, vector y puntuación. |
| CWE | Catálogo de tipos de debilidad de software. |
| RoE | Reglas de actuación que delimitan cómo se ejecuta una prueba. |

## Fuentes

- NIST. *SP 800-115, Technical Guide to Information Security Testing and Assessment*.
- PTES: *Penetration Testing Execution Standard*.
- MITRE ATT&CK y Lockheed Martin, *Cyber Kill Chain*.
