# Clasificación y gestión

En urgencias, dos pacientes pueden llegar a la vez y solo hay un quirófano. La decisión de a quién se atiende primero no se toma por orden de llegada, sino por gravedad y por tiempo: eso es el triaje. En un incidente pasa lo mismo: detectar es solo el principio; después hay que clasificarlo, valorar su gravedad y decidir quién actúa.

## La gestión empieza antes de la alerta

La gestión de incidentes se apoya en un plan de acción escrito antes de que ocurra nada. Ese plan no solo sirve para reparar: también debe medir si la protección funciona y detectar tendencias antes de que se conviertan en problemas mayores.

El marco de referencia es el ciclo de vida de respuesta a incidentes. Sus fases habituales son:

1. **Preparación:** políticas, inventario, contactos, herramientas y formación.
2. **Detección y análisis:** confirmar que hay un incidente, clasificarlo y valorarlo.
3. **Contención, erradicación y recuperación:** cortar la propagación, eliminar la causa y volver a operar.
4. **Actividad posterior:** documentar, extraer conclusiones y corregir.

La estrategia que más peso tiene es la **detección temprana**. Cuanto antes se ve el incidente, menos daño hace y menos cuesta contenerlo. Para eso se combinan un IDS eficiente, un análisis rápido en varias etapas y políticas de respuesta con capacidad de prevención (IPS).

## Tres niveles de análisis

Se distinguen tres profundidades, que se usan según lo que se sabe y lo que se necesita demostrar:

- **Preliminar:** ¿qué ha pasado, qué sistemas están afectados y hay que actuar ya?
- **Profundo:** alcance real, causa, persistencia y datos comprometidos.
- **Forense:** evidencia técnica que resista una revisión posterior, con cadena de custodia.

Cuando el incidente ya ha ocurrido, las herramientas de análisis forense —Volatility es el ejemplo habitual— permiten reconstruir qué pasó y rescatar la información válida. Un SIEM ayuda antes y después: almacena los eventos de forma estructurada para poder consultarlos.

La cadena de custodia no es un formalismo. Si la evidencia se copia sin registrar quién la tocó, cuándo y cómo, pierde valor ante una revisión interna o ante una autoridad. La prisa por contener no justifica destruir la prueba de lo que ocurrió.

## El registro del incidente

El registro es lo que permite que otra persona entienda el caso sin hablar contigo. Los datos que no pueden faltar son:

| Dato | Qué debe recoger |
|---|---|
| Tipo | Familia y subtipo de la taxonomía; un incidente puede tener varios |
| Fecha y hora | Cuándo ocurrió y cuándo se detectó; no son lo mismo |
| Descripción | Sistemas afectados, personas implicadas, vulnerabilidad o técnica usada |
| Gravedad | Baja, media, alta o crítica, con el criterio aplicado |
| Estado | Abierto, en proceso, pendiente, solucionado o cerrado |
| Medidas | Acciones tomadas, plan previsto y flujo de trabajo |

La diferencia entre la hora de ocurrencia y la de detección es una de las métricas más útiles: mide el tiempo que el incidente estuvo actuando sin que nadie lo viera. También conviene registrar la hora de contención, porque separa el daño potencial del daño efectivo.

Los estados cuentan una historia:

- **Abierto:** registrado, sin asignar.
- **En proceso:** alguien trabaja en él.
- **Pendiente:** se espera información o un factor externo.
- **Solucionado:** resuelto, aunque queden notificaciones o seguimiento.
- **Cerrado:** sin intervención pendiente; se archiva.

Un incidente «solucionado» no es lo mismo que «cerrado». El primero ha dejado de hacer daño; el segundo ha terminado también el papeleo y las comprobaciones.

## Cómo se valora la gravedad

No basta con decir «es grave». Hay cuatro factores que permiten argumentarlo:

1. **Sistemas y servicios implicados.** No pesa igual un servidor de pruebas que el control industrial de una planta.
2. **Datos afectados.** La naturaleza (datos personales, financieros, de salud) y el volumen cambian la gravedad y las obligaciones legales.
3. **Periodo de tiempo.** Un incidente activo durante semanas ha tenido más oportunidades de dañar que uno contenido en horas.
4. **Alcance.** Cuántas personas, empresas o sectores se han visto afectados.

Con esos factores se asignan los cinco niveles de peligrosidad de la Guía CCN-STIC-817:

| Nivel | Qué implica | Ejemplos |
|---|---|---|
| Bajo | Impacto limitado, sin daños significativos | Spam, escaneo de redes, análisis de paquetes |
| Medio | Compromete la seguridad, pero no es crítico | Delitos de odio, ingeniería social, explotación de vulnerabilidades conocidas, intento de acceso con credenciales |
| Alto | Afecta gravemente a las operaciones; puede tener consecuencias legales y financieras | Pornografía infantil, servidor de mando y control, compromiso de cuenta con privilegios, phishing, pérdida de datos |
| Muy alto | Impacto devastador; exige respuesta rápida y coordinada | Distribución o configuración de malware, robo de información confidencial, sabotaje o interrupción de servicios |
| Crítico | Puede poner en riesgo la continuidad de la organización o de un sector estratégico | APT y amenazas persistentes avanzadas |

La valoración no es definitiva: un incidente puede empezar como medio y subir cuando se descubre que los datos se han filtrado. También puede bajar si la investigación demuestra que el acceso no llegó a producirse. El nivel se revisa con los hechos, no se congela en la primera impresión.

## Herramientas de gestión

Para que el registro no viva en una hoja suelta:

- **ITSM:** gestión de tickets y flujos al estilo ITIL (SysAid, Jira Service Management).
- **Código abierto:** Project-open, GLPI.
- **Específicas de ciberseguridad:** Splunk, AlienVault (hoy LevelBlue).
- **Plataformas de gestión de incidentes:** automatizan tareas, asignan flujos y notifican a los responsables.
- **SOAR:** orquestan y automatizan la respuesta; ejemplos son Splunk SOAR, IBM QRadar SOAR, TheHive y FIR.

Las plataformas avanzadas se conectan con bases de amenazas como MITRE ATT&CK para saber qué técnica se está viendo y qué respuesta encaja.

La automatización tiene un límite claro: puede bloquear una IP o abrir un ticket, pero la decisión de notificar a una autoridad o de apagar un servicio crítico sigue siendo humana. Automatizar esa decisión traslada el riesgo a una regla que nadie está mirando.

## Seguimiento y mejora

Cerrar el ticket no cierra el incidente. Quedan tres tareas:

- **Notificar** a los responsables internos y, si procede, a las autoridades y a las personas afectadas.
- **Medir:** tiempo hasta la detección, tiempo hasta la contención, incidentes repetidos y falsos positivos.
- **Corregir:** parchear la causa, ajustar reglas de detección y actualizar el plan.

El análisis de rendimiento se contrasta con las amenazas más frecuentes del exterior. Si un tipo de incidente se repite o tarda en detectarse, el problema no es solo técnico: puede faltar un control, una regla o formación.

## Ejemplo

Un incidente afecta a diez registros de clientes, pero son datos de salud. El volumen es pequeño; la naturaleza del dato no lo es. La valoración no puede quedarse en «diez registros»: hay que considerar la obligación de notificación, el daño para las personas y la posibilidad de que el acceso haya sido mayor que el detectado.

El caso se analiza primero de forma preliminar, se contiene la cuenta o el servicio afectado y se pasa a un análisis profundo si hay indicios de persistencia. Si se prevé una reclamación o una investigación externa, entra el análisis forense con cadena de custodia. Al cerrar, quedan la notificación, la medición de tiempos y la corrección de la causa.

## Cierre

Detectar abre el caso; clasificar y valorar deciden por dónde se empieza. El registro deja memoria, los estados ordenan el trabajo y la gravedad se argumenta con sistemas, datos, tiempo y alcance. Cerrar el ticket no cierra el incidente: quedan notificar, medir y corregir. Esa es la diferencia entre apagar un fuego y evitar el siguiente.

## Fuentes

- CCN-CERT. *Guía CCN-STIC-817* y *Guía Nacional de Notificación y Gestión de Ciberincidentes*.
- NIST. *Computer Security Incident Handling Guide* (SP 800-61).
- MITRE. *ATT&CK*.
