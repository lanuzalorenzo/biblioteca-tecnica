# Detección y señales

Un detector de humo no apaga el incendio, pero avisa antes de que la casa arda. La detección de incidentes funciona igual: no sustituye a la respuesta, pero decide cuánto tiempo se gana. Este apunte explica de dónde salen las señales, quién las mira y con qué herramientas.

## Tres capas de control

Antes de hablar de herramientas conviene separar tres tipos de control, porque un incidente puede entrar por cualquiera de ellas:

- **Técnicos.** Software o hardware que protege sistemas y datos: cortafuegos, antivirus, sistemas de detección.
- **Físicos.** Medidas que protegen equipos, documentos e instalaciones: control de acceso, vigilancia del centro de datos.
- **Personales.** Comportamiento y formación de las personas: concienciación, buenas prácticas, procedimientos.

Los tres se necesitan. Un cortafuegos perfecto no sirve si alguien conecta un USB infectado en la sala de servidores.

## Precursores e indicadores

La distinción es la base de toda la detección:

- **Precursor.** Indicio de que un incidente **puede ocurrir** en el futuro. Todavía no ha pasado nada.
- **Indicador.** Indicio de que un incidente **ha ocurrido o está ocurriendo** ahora.

Ejemplos de precursores:

- Un escaneo de vulnerabilidades aparece en los registros del servidor web.
- Se publica un exploit para una vulnerabilidad que la organización tiene sin parchear.
- Un grupo anuncia públicamente que atacará a un sector o a una empresa concreta.

Ejemplos de indicadores:

- El sensor de intrusión alerta de un intento de desbordamiento de búfer contra una base de datos.
- El antivirus detecta y bloquea un archivo malicioso.
- Aparece un nombre de archivo con caracteres extraños en un directorio compartido.
- El registro muestra un cambio de configuración que nadie autorizó.
- Una aplicación acumula intentos fallidos de inicio de sesión desde una IP externa.
- Sube el número de correos rebotados con contenido sospechoso.
- El tráfico interno se desvía de su patrón habitual.

La diferencia práctica: un precursor pide **preparación** (parchear, vigilar, avisar); un indicador pide **investigación**. Confundirlos lleva a dos errores opuestos: ignorar un aviso porque «todavía no ha pasado nada» o tratar un rumor como una brecha confirmada.

## De dónde salen las señales

Una organización no necesita sensores en todas partes, pero sí cubrir los puntos donde un incidente deja rastro:

| Fuente | Qué aporta | Ejemplo |
|---|---|---|
| Registros del sistema y de aplicaciones | Quién hizo qué y cuándo | Intentos de login, cambios de configuración, errores |
| Red | Conexiones, volumen, destinos raros | Picos de tráfico, conexiones a un servidor de mando y control, escaneos |
| Terminales | Procesos, archivos, malware | Antivirus, EDR, ejecución de herramientas |
| Identidad y accesos | Autenticación y privilegios | Fuerza bruta, cuentas nuevas, escalada |
| Personas | Lo que la tecnología no ve | Un usuario llama porque su equipo va lento |
| Fuentes externas | Contexto y avisos | CCN-CERT, INCIBE-CERT, fabricantes, comunidades |

El CCN-CERT coordina esta vigilancia en el sector público español con el Sistema de Alerta Temprana de Red SARA (SAT-SARA) y el de Sistemas de Control Industrial (SAT-ICS).

## Quién mira las señales

Un equipo interno conoce la organización y responde antes en el sitio, pero cuesta mantenerlo y depende de personas clave. Un equipo externo aporta experiencia y escala, pero conoce peor el negocio y no decide dentro. Muchas organizaciones combinan ambos.

Los equipos que conviene distinguir:

- **SOC** (Centro de Operaciones de Seguridad): monitoriza, analiza y coordina la respuesta.
- **CSIRT** (equipo de respuesta a incidentes): investiga y responde.
- **CERT**: similar al CSIRT, con alcance más amplio, a veces sectorial o gubernamental.
- **CISO**: dirige la estrategia de seguridad.

Y tres formas de mirar el mismo sistema:

- **Red team (equipo rojo)**: ataca y busca debilidades, como lo haría un atacante real.
- **Blue team (equipo azul)**: defiende, detecta y responde.
- **Purple team (equipo morado)**: coordina a los dos para que las pruebas ofensivas mejoren las defensas.

Los sombreros se refieren a la intención: **black hat** busca beneficio o daño; **white hat** es el hacker ético que informa; **grey hat** explora sin autorización, pero sin ánimo claramente malicioso. La etiqueta no cambia la legalidad de la acción: sin permiso, una prueba ofensiva sigue siendo un acceso no autorizado.

## Herramientas por función

- **EPP** (protección de terminal): antivirus y filtros instalados en el equipo.
- **EDR** (detección y respuesta en terminal): va más allá; registra comportamiento y permite responder.
- **Monitorización de red**: vigila tráfico y disponibilidad (Nagios, Auvik).
- **Escáneres de vulnerabilidades**: buscan debilidades conocidas (Nessus, OpenVAS, Acunetix, Nexpose, hoy InsightVM). Producen precursores, no incidentes por sí solos.
- **IDS/IPS**: detectan intrusiones; el IPS además bloquea.
- **SIEM**: centraliza registros y correlaciona eventos.
- **DLP**: vigila que la información sensible no salga.
- **Cortafuegos y proxies**: filtran y registran el tráfico.

La lista de productos cambia con el mercado; la función es lo que se elige primero. Comprar un SIEM sin saber qué fuentes se van a conectar produce un archivo caro, no detección.

## SIEM: el archivo y la centralita

Un SIEM recoge datos de muchas fuentes, los guarda en un almacén central y los analiza. Sus funciones típicas:

1. **Recopilación** de registros, eventos y alertas.
2. **Almacenamiento** para consultas e informes.
3. **Monitorización en tiempo real** de usuarios y dispositivos.
4. **Detección** por firmas, por anomalías y por comportamiento.
5. **Correlación** de eventos de fuentes distintas, apoyada en inteligencia de amenazas.
6. **Generación de alertas** clasificadas por peligrosidad.
7. **Respuesta**: playbooks y acciones automatizadas como bloquear una IP o aislar un equipo.
8. **Integración** con IDS, escáneres, EPP y otras herramientas.

Su valor está en la correlación: un login fallido aislado no dice nada; ese login, seguido de una conexión saliente rara y de un cambio de configuración, cuenta una historia. Ejemplos de SIEM: Splunk, QRadar, Elastic Stack, Wazuh.

## IDS e IPS: detectar o impedir

El **IDS** observa y alerta. El **IPS** observa, alerta y además puede bloquear paquetes, direcciones o aislar sistemas.

Funciones que conviene distinguir:

- **Detección por patrones o firmas**: compara el tráfico con actividades maliciosas ya conocidas.
- **Alertas**: IP de origen, sistema afectado y protocolo, para que el analista investigue.
- **Defensa en tiempo real** (solo IPS): bloqueo o aislamiento durante el ataque.
- **Análisis forense y cumplimiento**: conserva registros detallados que sirven para investigar y auditar.
- **Detección de intentos de explotación**: avisa de que una vulnerabilidad está siendo probada.

Herramientas de referencia: Snort, Suricata y Zeek en código abierto; Cisco Firepower o McAfee Network Security Platform (hoy Trellix) en el ámbito comercial.

## La seguridad física también detecta

Un incidente lógico puede empezar con un pie dentro de la sala. Los activos físicos no son solo equipos: también documentos, suministros y personas. Las consecuencias van de la pérdida económica a la interrupción del servicio o la fuga de datos.

Los riesgos físicos habituales son:

1. Acceso no autorizado a áreas restringidas.
2. Robo de equipos o soportes.
3. Caída de suministro eléctrico o de comunicaciones.
4. Condiciones climáticas extremas y desastres.
5. Eliminación o donación de equipos sin borrar datos.
6. Mantenimiento deficiente.

La ISO/IEC 27001 los ordena en dos bloques: **áreas seguras** (perímetros, controles de entrada, protección de oficinas, amenazas ambientales, trabajo en áreas seguras, carga y descarga) y **seguridad de los equipos** (emplazamiento, suministro, cableado, mantenimiento, retirada de material, equipos fuera de la sede, reutilización o eliminación segura, puesto desatendido, pantalla y mesa limpias).

El anexo A.11 corresponde a la edición de 2013. La revisión de 2022 reorganizó los controles y los de seguridad física pasan al anexo A.7. El contenido es equivalente; conviene citar la edición vigente.

## OSINT: lo que la organización ya está contando

La inteligencia de fuentes abiertas (OSINT) es información obtenida de fuentes públicas: medios, portales gubernamentales, foros, redes sociales, blogs, conferencias y publicaciones. Sirve para conocer la reputación de una empresa, auditar su exposición o detectar amenazas. También la usan los atacantes para preparar un APT o un spear phishing.

El proceso tiene seis fases:

1. **Requisitos**: qué información se necesita y para qué.
2. **Identificación de fuentes**: acotar dónde buscarla.
3. **Adquisición**: recopilarla.
4. **Procesamiento**: ordenarla y darle formato.
5. **Análisis**: relacionarla y buscar patrones.
6. **Presentación**: convertirla en algo comprensible y útil.

Los dos problemas son siempre los mismos: **demasiada información** y **fuentes poco fiables**. Sin criterio de selección, el sistema se vuelve lento y produce conclusiones falsas.

Herramientas habituales: buscadores y operadores avanzados, Shodan, archivos web, servicios de dominios, Metagoofil para metadatos, Maltego y SpiderFoot para relaciones, y utilidades de redes sociales. La lista cambia rápido; lo que no cambia es la necesidad de verificar y de tener autorización para investigar. Analizar la exposición propia no autoriza a tocar sistemas ajenos: el límite es la ley y el permiso escrito.

## Cómo montar un catálogo de señales

Para que la detección no dependa de la intuición:

1. **Inventaría activos y servicios críticos.** Sin saber qué proteges, no sabes qué vigilar.
2. **Define qué señal indica qué.** Cada alerta debe apuntar a una categoría de la taxonomía y a un responsable.
3. **Fija umbrales y ruido aceptable.** Una alerta que salta cien veces al día se ignora.
4. **Centraliza y correlaciona.** El SIEM no sustituye al analista; le quita trabajo repetitivo.
5. **Revisa falsos positivos y huecos.** Un detector que nunca falla suele estar mal configurado.
6. **Documenta la fuente y la hora.** Sin eso, la alerta no sirve como evidencia.

## Cierre

Detectar es ganar tiempo. Las señales salen de los registros, la red, los terminales, la identidad, las personas y las fuentes externas; las herramientas las recogen y las correlacionan, pero la decisión sigue siendo humana. Con la señal en la mano, el siguiente paso es clasificarla, valorarla y decidir quién actúa.

## Fuentes

- ISO/IEC 27001, controles de seguridad física (anexo A.11 en la edición de 2013; anexo A.7 en la de 2022).
- CCN-CERT. Sistemas de alerta temprana SAT-SARA y SAT-ICS.
- ENISA. *Reference Security Incident Taxonomy*.
