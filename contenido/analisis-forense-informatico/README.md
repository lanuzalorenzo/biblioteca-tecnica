<img src="../assets/iconos/analisis-forense-informatico.svg" width="64" alt="Análisis forense informático">

# Análisis forense informático

Cuando un sistema se compromete, la pregunta no es solo qué ha fallado, sino qué ha pasado, en qué orden y cómo demostrarlo. El análisis forense informático (AFI) responde a eso: reconstruye los hechos a partir de los rastros que deja un equipo, sin alterar la evidencia y con un registro que permita sostener las conclusiones ante un tercero.

La disciplina se apoya en una idea sencilla y exigente a la vez: lo que no se ha preservado no se puede analizar, y lo que no se ha documentado no se puede probar. Por eso el método pesa tanto como la herramienta.

## Qué reconstruye

El análisis busca responder a cinco preguntas: qué pasó, dónde, quién estuvo implicado, cuándo y con qué medios. La respuesta se arma con evidencias digitales —datos almacenados o transmitidos— que se ordenan en una línea de tiempo.

Hay dos escenarios que cambian el rigor del trabajo:

- **Requerimiento judicial.** La evidencia debe ser admisible en un proceso; la cadena de custodia y la integridad son requisitos, no buenas prácticas.
- **Respuesta ante un incidente.** El foco es recuperar la operatividad y entender el ataque. El método se adapta, pero la preservación y la documentación no se negocian en ninguno de los dos casos.

El análisis forense forma pareja con la respuesta a incidentes: DFIR (Digital Forensics and Incident Response) es el nombre que recibe el conjunto.

## El método en cuatro fases

1. **Identificación.** Determinar qué dispositivos, sistemas y fuentes contienen evidencia relevante.
2. **Adquisición y preservación.** Obtener una copia fiel sin alterar el original.
3. **Análisis.** Examinar la copia para extraer información y relacionarla.
4. **Documentación y reporte.** Registrar el proceso y presentar conclusiones sostenidas por la evidencia.

Saltarse una fase invalida el resultado. Una copia perfecta sin cadena de custodia no sirve como prueba; un informe brillante sobre una copia mal hecha tampoco.

## Orden de volatilidad

La evidencia se recoge de lo que desaparece antes a lo que permanece. La RAM se pierde al apagar o reiniciar, así que se captura antes de tocar el disco.

| Orden | Tipo de evidencia |
|---|---|
| 1.º | Cachés de memoria y registros de CPU |
| 2.º | Memoria RAM, tabla ARP, procesos, swap y temporales |
| 3.º | Discos duros |
| 4.º | Logs remotos y datos de monitorización |
| 5.º | Configuraciones físicas y topologías de red |

El detalle de la captura y del análisis de memoria está en [Volcado y análisis de memoria RAM](volcado-y-analisis-de-memoria-ram.md).

## Contenido

| Nota | Qué trata |
|---|---|
| [Metodología, adquisición y cadena de custodia](metodologia-adquisicion-y-custodia.md) | Fases, volatilidad, copia forense, hashes, custodia y herramientas |
| [Volcado y análisis de memoria RAM](volcado-y-analisis-de-memoria-ram.md) | Captura, integridad y plugins de Volatility 3 por objetivo |
| [Análisis de logs e informe](analisis-logs-e-informe.md) | Qué aporta la memoria, logs de Windows y Linux, informe y línea de tiempo |

## Lo que no es análisis forense

- **Detección no es forense.** Un IDS alerta, pero no reconstruye por sí solo qué pasó ni en qué orden.
- **La recuperación de borrados tiene límite físico.** En un SSD con TRIM, los bloques no reclamados ya no están y el resultado no es fiable.
- **Los metadatos contextualizan, no prueban.** Una fecha EXIF no demuestra integridad; lo hace el hash.
- **Una herramienta no sustituye al método.** Automatizar la extracción sin registrar qué se hizo y sobre qué copia deja un resultado que no se puede defender.

## Fuentes

- ISO/IEC 27037:2012: identificación, recogida, adquisición y preservación de evidencia digital.
- ISO/IEC 27043:2015: investigación de incidentes y principios de análisis forense.
- NIST. *SP 800-86, Guide to Integrating Forensic Techniques into Incident Response*.
- RFC 3227: directrices de recogida y almacenamiento de evidencias.
