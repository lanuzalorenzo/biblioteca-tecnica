# Clasificar herramientas

Un taller mecánico no se organiza memorizando marcas de llaves, sino por lo que hay que hacer con cada una. Con las herramientas de seguridad pasa lo mismo: saber ordenarlas por función y elegir las que encajan con una organización vale más que recitar nombres de programas, porque los programas cambian y la función permanece.

## Cuatro criterios que se combinan

**Por fase.** Es el orden en que se trabaja: reconocimiento, escaneo y enumeración, obtención de acceso, mantenimiento del acceso y borrado de huellas, más la documentación que añade un test de intrusión. Sirve para ordenar un laboratorio, porque las herramientas se usan en ese orden.

**Por función técnica.** Es el criterio más preciso y el que se usa como esqueleto aquí: qué hace la herramienta, no cómo se llama.

**Por licencia y procedencia.** Abierta, gratuita de código cerrado, comercial con o sin edición limitada, o servicio en la nube. El código abierto permite auditar y no ata al proveedor, pero exige más conocimiento para mantenerlo; lo comercial aporta soporte y respaldo documental a cambio de coste. Las condiciones de las ediciones gratuitas —uso personal, número de direcciones, prohibición de uso comercial— se leen antes de usar la herramienta en un encargo.

**Por modo de uso.** Automática o interactiva; pasiva, que solo observa, o activa, que interactúa y puede alterar el sistema. El modo activo condiciona la autorización que hace falta.

Ninguna clasificación es una frontera: una misma herramienta cruza categorías. Una utilidad de descubrimiento puede incluir módulos de detección, y un proxy de interceptación sirve para analizar y para atacar.

## Clasificación por función

| Función | Para qué sirve |
|---|---|
| Reconocimiento y búsqueda de información pública | Reunir datos del objetivo sin tocarlo |
| Descubrimiento y escaneo de red | Saber qué equipos y servicios existen |
| Análisis de vulnerabilidades | Localizar debilidades conocidas |
| Captura y análisis de tráfico | Ver qué viaja por la red |
| Interceptación y suplantación | Situarse en medio de una comunicación |
| Marcos de explotación | Ejecutar y encadenar ataques |
| Ataques a contraseñas | Recuperar u obtener credenciales |
| Redes inalámbricas | Analizar y atacar wifi |
| Aplicaciones web | Buscar fallos en portales y API |
| Acceso remoto y postexplotación | Mantener y ampliar el control |
| Ingeniería social simulada | Medir la respuesta de las personas |
| Documentación | Registrar evidencias y redactar el informe |

Las distribuciones especializadas —Kali Linux, mantenida por OffSec, y Parrot OS como alternativa— agrupan estas utilidades ya instaladas. No son un conjunto misterioso: ahorran instalación y mantenimiento, y exigen saber qué hace cada programa antes de lanzarlo.

## Monitorización: dos preguntas distintas

Al elegir herramientas de monitorización se mezclan dos preguntas que conviene separar:

- **Preventiva**: ¿qué debilidades tenemos ahora? La responden los escáneres de vulnerabilidades, la auditoría de configuración y la vigilancia de la superficie expuesta.
- **Detectiva**: ¿alguien las está aprovechando? La responden la detección de intrusiones, la monitorización de red, la detección en el equipo y la correlación de registros.

| Categoría | Qué observa o responde | Ejemplos representativos |
|---|---|---|
| Gestión de vulnerabilidades | Inventario priorizado de fallos conocidos | Greenbone/OpenVAS, Nessus, Qualys, InsightVM |
| Auditoría de configuración | Desviaciones frente a guías de bastionado | Lynis, OpenSCAP, benchmarks CIS |
| Superficie de ataque externa | Activos visibles desde internet, incluidos los olvidados | Shodan, Censys, servicios comerciales |
| Detección de intrusiones en red | Patrones de ataque en el tráfico; puede bloquear | Snort, Suricata |
| Monitorización de red | Registro detallado con capacidad forense | Zeek, Security Onion |
| Detección en el equipo | Procesos, ficheros y cambios no autorizados | Wazuh, OSSEC, AIDE, EDR comerciales |
| Correlación de eventos (SIEM) | Normaliza y cruza registros de muchas fuentes | Elastic Security, Splunk, Graylog, Sentinel, QRadar |
| Inteligencia de amenazas | Indicadores y credenciales expuestas | MISP, OpenCTI, vigilancia de filtraciones |
| Señuelos | Sistemas falsos cuyo uso es siempre alerta | Cowrie, T-Pot |
| Disponibilidad y rendimiento | Estado y carga, con valor de seguridad indirecto | Zabbix, Nagios, Prometheus con Grafana |

Un escáner de vulnerabilidades es la misma clase de herramienta que usa un auditor, pero ejecutada por la organización de forma recurrente. Ahí está la clave: una prueba de intrusión es una fotografía de unos días y los fallos aparecen cada semana; entre auditoría y auditoría hace falta un proceso continuo.

## La cadena que no se compra entera

Sensores que observan, recogida y normalización en un punto central, correlación que convierte miles de eventos en unas pocas alertas y respuesta con alguien que las atienda. Las dos primeras piezas son técnicas; la última es organizativa. Instalar sensores y un SIEM sin persona, horario y procedimiento produce ruido caro y la fatiga de alertas que deja pasar una intrusión durante semanas.

## Elegir según la organización

Los criterios estables son: tamaño y valor de los activos; sector y obligaciones —Esquema Nacional de Seguridad en el sector público, normativa sectorial, contratos—; capacidad real del equipo; infraestructura propia, nube o sistemas industriales; coste total de propiedad; e integración mediante formatos estándar. A ellos se suman la escalabilidad, la madurez del producto, el soporte, la ubicación de los datos y la capacidad de producir evidencias para auditoría.

| Perfil | Enfoque razonable | Riesgo principal |
|---|---|---|
| Microempresa o autónomo | Servicios gestionados, actualizaciones automáticas, copias, vigilancia de credenciales y análisis externo ocasional | Montar herramientas que nadie atenderá |
| Pyme sin equipo de seguridad | Escáner periódico, detección en equipos críticos, centralización mínima y alertas por correo | Acumular alertas sin capacidad de respuesta |
| Mediana empresa con obligaciones | SIEM con casos de uso, detección en puntos clave, gestión de vulnerabilidades con plazos y auditoría de configuración | Herramientas aisladas sin procesos |
| Gran organización con centro de operaciones | Correlación con automatización, red avanzada, EDR o XDR, caza de amenazas y superficie externa | Coste de personal y soluciones solapadas |
| Administración pública | Productos conformes con el ENS y, cuando proceda, catálogo del CCN | Adoptar soluciones sin acreditación |
| Entorno industrial | Monitorización pasiva, segmentación estricta y escaneos activos solo con acuerdo de operaciones | Un escaneo normal detiene la producción |
| Nube y servicios SaaS | Registros y postura nativos del proveedor, auditoría de identidades | Dar por hecho que el proveedor cubre todo |

## La matriz de decisión ponderada

Cuando hay varias opciones razonables, se enumeran los criterios, se reparte un peso que sume 100, se puntúa cada opción de 1 a 5 y se calcula la suma ponderada. El valor del método no es acertar, sino hacer explícitas las prioridades y ver cuánto cambia el resultado al cambiarlas.

Un ejemplo típico es una empresa de logística con un administrador, un proveedor externo y ningún centro de operaciones, que compara una solución autoalojada con herramientas abiertas, una suite comercial con detección gestionada y un servicio de operación externalizado. Con pesos equilibrados gana el servicio gestionado, porque la empresa no tiene personas para operar herramientas propias; cuando el presupuesto domina, gana la autoalojada; la opción intermedia queda estable en el centro. La recomendación profesional añade la sensibilidad, los supuestos que cambian el resultado y, a menudo, una combinación con prueba piloto.

## Uso responsable

- Entender antes de ejecutar: qué tráfico genera y qué efectos puede tener.
- Comprobar la procedencia y verificar la integridad; las copias de sitios dudosos son un vector habitual de infección.
- Mantener actualizadas las herramientas y sus bases de datos, y anotar las versiones usadas.
- Empezar por perfiles poco intrusivos y probar antes en el laboratorio.
- Interpretar: una alerta es una hipótesis y la ausencia de alertas no demuestra nada.
- Respetar las licencias y registrar comandos, parámetros, salidas y horas.
- Proteger el equipo del auditor: cifrado, actualizado y segregado por cliente.

Tener la herramienta no es delito; usarla sin autorización contra sistemas ajenos sí lo es, con independencia de lo inofensiva que parezca.

## Errores frecuentes

- Aprender nombres de programas en lugar de categorías.
- Dar el resultado de un escáner por una auditoría.
- Instalar detección o correlación sin nadie que atienda las alertas.
- Recomendar lo más completo en vez de lo más adecuado al perfil.
- Descargar herramientas de fuentes no fiables o ignorar sus condiciones de licencia.
- Vigilar solo el perímetro y olvidar la nube, los equipos y las personas.

## Glosario

| Término | Definición |
|---|---|
| EDR | Detección y respuesta en el punto final: vigila el comportamiento del equipo. |
| HIDS | Detección de intrusiones en un equipo concreto. |
| NIDS / NIPS | Detección o prevención de intrusiones en la red. |
| ENS | Esquema Nacional de Seguridad, obligatorio en el sector público español. |
| SIEM | Plataforma que recoge, normaliza y correlaciona registros. |

## Fuentes

- Real Decreto 311/2022, Esquema Nacional de Seguridad.
- Center for Internet Security. *CIS Benchmarks*.
- NIST. *SP 800-115* y *SP 800-137*.
