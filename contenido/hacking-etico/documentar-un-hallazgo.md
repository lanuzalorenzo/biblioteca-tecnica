# Documentar un hallazgo

Un fallo que no se documenta bien no se corrige. La ficha de hallazgo es el producto real de una auditoría: si otra persona no puede entenderla, comprobarla y arreglarla, el trabajo técnico se pierde por el camino.

## Anatomía de un hallazgo

La ficha sirve a tres lectores: al directivo le dice por qué importa, al técnico qué está mal y cómo arreglarlo, y al auditor qué hizo y qué vio. Por eso tiene una estructura fija.

| Elemento | Qué debe contener | Error típico |
|---|---|---|
| Identificador y título | Código único y título que resuma problema y activo | «Vulnerabilidad en servidor» |
| Resumen | Una o dos frases en lenguaje comprensible | Empezar con jerga |
| Activo afectado | Sistema, versión, puerto o URL exactos | «Los servidores» |
| Descripción técnica | Causa raíz y condiciones para aprovecharla | Describir el síntoma y callar la causa |
| Severidad | Puntuación estándar más valoración contextual | Copiar la cifra de una herramienta |
| Impacto | Qué logra un atacante y qué propiedades se ven afectadas | «Podría comprometer el sistema» |
| Evidencia | Capturas, salidas y registros con fecha y origen | Capturas sin contexto o con datos personales |
| Pasos para reproducir | Método suficiente para que el cliente lo compruebe | Pasos que no se pueden repetir |
| Recomendación | Corrección concreta y medida compensatoria si urge | «Mejorar la seguridad» |
| Referencias | CVE, CWE y avisos del fabricante | Enlaces sin comprobar |
| Estado | Nuevo, comunicado, corregido, verificado o aceptado | No hacer seguimiento tras entregar |

Dos criterios atraviesan toda la ficha. La **reproducibilidad** exige que otra persona llegue al mismo resultado con lo escrito. La **proporcionalidad** exige no presentar todo como crítico ni minimizar lo grave: un informe alarmista pierde credibilidad y uno complaciente incumple el deber de honestidad.

## Un ejemplo

Una ejecución remota de código en un servidor expuesto se documenta así: título que nombra el componente y el tipo de fallo; resumen que explica en dos frases que cualquiera con acceso a internet puede ejecutar órdenes sin autenticarse; activo con dominio, puerto y versión; descripción con la causa raíz, que en este caso es la falta de un proceso de parches; severidad base 9.8 con su vector; impacto sobre confidencialidad, integridad y disponibilidad, incluido el movimiento posterior hacia la red interna; dos evidencias fechadas y con los datos personales tapados; tres pasos para reproducirlo dentro de la ventana autorizada; recomendación de actualizar en menos de siete días y medida compensatoria mientras tanto; referencias y estado. Todo el caso es ficticio y no incluye código de ataque.

## Nombrar, clasificar y medir

**CVE** nombra un caso concreto y tiene la forma `CVE-AAAA-NNNN`. Lo asignan organizaciones autorizadas —fabricantes, equipos de respuesta, organismos de coordinación— y lo coordina MITRE; el NVD enriquece cada entrada con productos afectados, referencias y puntuaciones. Cuando el fallo es una configuración o un diseño propio, no hay CVE: se describe con precisión y se relaciona con el tipo de debilidad.

**CWE** clasifica la clase de debilidad, no el caso. Sirve para explicar la causa y para buscar patrones, y no sustituye al CVE.

**CVSS** mide la severidad intrínseca de 0 a 10. La versión 3.1 sigue siendo la más extendida y la 4.0 convive con ella desde 2023; sus puntuaciones no son comparables entre versiones, así que hay que comprobar qué versión usa la herramienta o el cliente. Las ocho métricas de la base, el vector y la escala completa están en [Severidad con CVSS](severidad-con-cvss.md); aquí basta recordar que el resultado se resume en un vector que permite recalcularlo y comparar dos fallos.

## De la severidad al riesgo

La puntuación base mide la gravedad técnica, no el riesgo para una organización concreta. Un 9.8 en un servidor aislado y apagado no pesa lo mismo que un 6.5 que permite leer la base de datos de clientes. Para priorizar se añaden cuatro dimensiones: explotación real —si hay exploit público, qué dice EPSS (*Exploit Prediction Scoring System*) y si la vulnerabilidad está en el catálogo KEV de CISA—, exposición del activo, valor del activo y de sus datos, y controles compensatorios. La severidad contextual que aparece en el informe debe explicar el ajuste cuando se aleja de la base.

Regla práctica: no copies la puntuación de una herramienta sin comprobar que el vector describe lo que has observado.

## El informe

El informe tiene dos audiencias: la dirección, con poco tiempo y sin detalles técnicos, y los técnicos, que necesitan precisión para corregir y verificar. De ahí la separación entre parte ejecutiva y parte técnica.

| Bloque | Contenido | Audiencia |
|---|---|---|
| Portada y control | Cliente, versión, fecha, autores, clasificación y distribución | Todos |
| Resumen ejecutivo | Objetivo, resultado global, problemas graves en términos de negocio y prioridades | Dirección |
| Alcance y metodología | Qué se probó, cuándo, con qué enfoque y con qué limitaciones | Ambos |
| Resumen de hallazgos | Tabla ordenada por severidad y recuentos | Todos |
| Hallazgos detallados | Una ficha por hallazgo | Técnicos |
| Plan de remediación | Acciones por plazo, con prioridad y esfuerzo | Ambos |
| Conclusiones | Valoración global y recomendaciones estratégicas | Dirección |
| Anexos | Cronología, herramientas, evidencias ampliadas y glosario | Técnicos |

Tres principios de redacción: rigor objetivo —distinguir lo demostrado, lo inferido y lo no comprobado—, no culpabilizar a personas y reconocer también los controles que funcionaron, porque indican qué conservar y sostienen la credibilidad del documento.

## Documentar mientras se trabaja

El cuaderno de campo se rellena durante la prueba, no al final. Cada acción relevante se anota con fecha y hora, junto con el comando o la prueba y su resultado. Lo que no se apunta se olvida, y lo reconstruido de memoria pierde fiabilidad. Esa cronología alimenta el anexo que permite al cliente cruzar la actividad con sus propios registros y protege al auditor ante una controversia.

## Custodia y ciclo de vida

Un informe de intrusión es un mapa de cómo atacar a una organización. Se clasifica, se numera, se distribuye solo a personas nombradas, se entrega por canal cifrado, se controlan sus versiones y se conserva o destruye según el contrato. Las evidencias con datos personales siguen las reglas de minimización y destrucción del encargo.

El trabajo no termina con la entrega: cada hallazgo tiene un estado que evoluciona y suele incluir una verificación posterior, semanas después, para comprobar que las correcciones funcionan.

## Divulgación responsable

Fuera de un encargo, quien descubre un fallo se enfrenta a tres posturas. La divulgación completa presiona para corregir, pero expone a los usuarios mientras no hay parche. El silencio mantiene el riesgo de forma indefinida. La divulgación coordinada es la práctica profesional: se avisa en privado a quien puede corregir, se da un plazo razonable y se publica cuando hay corrección o cuando vence el plazo. Las normas ISO/IEC 29147 y 30111 describen el proceso; el fichero `security.txt` del RFC 9116 indica a quién avisar. En España, [INCIBE-CERT](https://www.incibe.es/incibe-cert) actúa como autoridad de numeración CVE (CNA) desde 2020, con un [procedimiento de asignación y publicación](https://www.incibe.es/incibe-cert/alerta-temprana/vulnerabilidades/asignacion-publicacion-cve), y mantiene un [canal para notificar incidentes](https://www.incibe.es/incibe-cert/incidentes/respuesta-incidentes); el Centro Criptológico Nacional cubre el sector público.

La divulgación responsable es una práctica profesional, no un salvoconducto jurídico: quien accede a un sistema vulnerando medidas de seguridad puede quedar expuesto aunque actúe de buena fe. De ahí las reglas del investigador: detenerse al confirmar, no acceder a más datos, no copiar ni modificar nada, avisar por el canal previsto, no exigir contraprestación, dar plazo y documentar lo mínimo con los datos de terceros ocultos.

## Errores frecuentes

- Títulos vagos y recomendaciones genéricas.
- Severidades copiadas de la herramienta sin revisar el vector.
- Evidencias sin contexto o con datos personales a la vista.
- Un informe ilegible para la dirección o sin detalle para los técnicos.
- Documentar de memoria al final del encargo.
- Entregar el informe por un canal inseguro.
- Confundir CVE con CVSS: uno nombra, el otro mide.
- Seguir investigando después de confirmar el fallo o pedir dinero por él.

## Glosario

| Término | Definición |
|---|---|
| CNA | Organización autorizada para asignar identificadores CVE. |
| KEV | Catálogo de CISA de vulnerabilidades explotadas de hecho. |
| NVD | Base de datos del NIST que enriquece las entradas CVE. |
| security.txt | Fichero normalizado con el canal para notificar fallos. |

## Fuentes

- FIRST. *CVSS v3.1 Specification Document* y *EPSS*.
- MITRE. *CVE* y *CWE*; NIST. *NVD*.
- CISA. *Known Exploited Vulnerabilities Catalog*.
- ISO/IEC 29147 e ISO/IEC 30111; IETF RFC 9116.
