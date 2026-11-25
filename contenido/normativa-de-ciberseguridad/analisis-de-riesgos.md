# Análisis de riesgos

Un mapa de riesgos se parece al parte meteorológico de una travesía: no cambia el tiempo, pero dice si conviene salir, qué margen queda y qué llevar por si empeora. Ignorarlo no elimina la tormenta; solo elimina la preparación.

## Qué es un riesgo

La ISO 31000:2018 define el riesgo como el efecto de la incertidumbre sobre los objetivos. Es una guía, no una norma certificable: no impone controles concretos, enseña a gestionarlos. En la práctica, el efecto se simplifica como probabilidad por impacto, una fórmula tosca pero suficiente para ordenar decisiones.

Un riesgo no es «un ciberataque» a secas. Es la combinación de una amenaza —por ejemplo, un ransomware—, una vulnerabilidad —un servidor sin parchear—, un impacto —la pérdida de datos de ciudadanos— y una probabilidad, la de que el ataque ocurra. Sin alguno de esos cuatro elementos, la frase describe una preocupación, no un riesgo gestionable.

Esa distinción separa dos conversaciones que suelen mezclarse. «Hay ransomware» es una amenaza; «tenemos un servidor sin parchear» es una vulnerabilidad; «perderíamos los datos de los ayuntamientos» es un impacto. El riesgo aparece cuando se combinan y se les asigna una probabilidad dentro de un contexto.

## Apetito de riesgo

El apetito de riesgo es la cantidad de riesgo que la dirección está dispuesta a asumir. No es una cifra decorativa: es el criterio que separa lo tolerable de lo que exige acción. Si no está escrito, cada área lo interpreta a su favor y el mapa se convierte en una discusión de opiniones.

El apetito se fija por tipo de riesgo y por proceso. Un servicio interno de bajo impacto puede convivir con más riesgo que una base de datos con información de salud. La comparación solo tiene sentido dentro del mismo marco: dos riesgos de áreas distintas no se ordenan por su color en la matriz, sino por lo que cada uno compromete.

## El proceso

El método de la ISO 31000 se puede resumir en cinco pasos, cada uno con un producto:

| Paso | Qué se hace | Qué deja |
|---|---|---|
| Identificar activos y procesos | Se delimita qué sostiene la actividad | Inventario |
| Identificar amenazas y vulnerabilidades | Se cruzan con los activos | Lista de escenarios |
| Analizar probabilidad e impacto | Se estima cada escenario | Nivel de riesgo |
| Evaluar frente al apetito | Se decide si es tolerable | Prioridad |
| Tratar y registrar | Se elige la respuesta y su dueño | Plan y evidencia |

El orden no es una formalidad. Saltar de la amenaza al control —«ponemos un firewall»— produce medidas que no responden a ningún riesgo concreto y dejan sin cubrir el que sí importaba.

## La matriz de impacto y probabilidad

El mapa sitúa cada riesgo en una matriz de impacto y probabilidad. La zona alta exige decisión inmediata; la zona baja puede monitorizarse. La matriz no decide por sí sola: ordena la conversación y hace visible lo que antes era una lista sin jerarquía.

|  | Probabilidad baja | Probabilidad media | Probabilidad alta |
|---|---|---|---|
| **Impacto alto** | Vigilar y preparar respuesta | Reducir pronto | Actuar de inmediato |
| **Impacto medio** | Aceptar con seguimiento | Reducir | Reducir y vigilar |
| **Impacto bajo** | Aceptar | Aceptar | Revisar el proceso |

La colocación de un riesgo es una estimación, no una medida. Por eso conviene anotar quién la hizo y con qué datos: cuando el riesgo se materializa, esa nota explica si el análisis falló o si el azar jugó en contra.

Una matriz con demasiadas casillas se vuelve ilegible; una con dos niveles oculta diferencias que importan. Lo que no puede faltar es el criterio: qué significa «impacto alto» en esa organización, con ejemplos y umbrales.

## Cuatro formas de tratar un riesgo

Para cada riesgo, la organización elige una opción:

| Opción | Qué hace | Ejemplo |
|---|---|---|
| **Evitar** | Elimina la actividad que genera el riesgo. | No almacenar datos que no se necesitan. |
| **Reducir** | Aplica controles para bajar la probabilidad o el impacto. | Cifrado, copias, formación, autenticación multifactor. |
| **Transferir** | Comparte el riesgo con un tercero. | Seguro ciber, contrato con acuerdos de nivel de servicio. |
| **Asumir** | Acepta el riesgo residual con justificación. | Servicio interno de bajo impacto. |

Evitar no siempre es posible ni deseable: prescindir de un servicio puede cerrar una línea de negocio. Transferir no elimina el riesgo, lo reparte, y el contrato no cubre la reputación. Asumir es una decisión legítima solo si está documentada y si el riesgo entra en el apetito.

Las opciones se combinan. Un mismo riesgo puede reducirse con un control técnico, transferirse con un seguro y asumirse en la parte que queda. Lo que no se puede hacer es elegir dos opciones contradictorias y dejar el mapa con las dos.

## Riesgo residual

El riesgo residual es el que queda después de aplicar un control. Se acepta, se reduce más o se transfiere. La diferencia entre el mapa inherente —antes de controles— y el residual es la prueba de que el plan sirvió; si ambos son iguales, o no se aplicó nada o el control no tenía relación con el riesgo.

Un riesgo residual por encima del apetito exige una decisión explícita: más control, cambio de alcance o aceptación firmada por quien tiene autoridad. Dejarlo en la matriz sin dueño es la forma más común de que un riesgo olvidado reaparezca como incidente.

El riesgo residual no es una cifra para tranquilizar a la dirección. Si el control reduce la probabilidad pero no el impacto, el riesgo sigue siendo grave para ciertos escenarios. La matriz lo muestra si se anota el efecto del control, no solo su existencia.

## Indicadores

Un sistema de riesgos se mide con indicadores clave de riesgo:

- **Incidentes de cumplimiento:** cuántos se detectan y cuánto tardan en cerrarse.
- **Hallazgos de auditoría:** abiertos, en plazo y reincidentes.
- **Formación:** porcentaje de plantilla formada y evaluación superada.
- **Canal ético:** tiempo de respuesta y porcentaje de casos investigados.

Cada indicador necesita dueño, umbral y acción asociada. Un panel sin umbral es un adorno: nadie sabe cuándo un número deja de ser normal, y la revisión se convierte en leer cifras en voz alta.

Los indicadores tampoco sustituyen al juicio. Un descenso de incidentes puede significar menos riesgo o menos detección; un aumento de denuncias puede ser un problema o una señal de que el canal empieza a funcionar. La lectura necesita contexto y una pregunta detrás.

## Documentar la decisión

El mapa de riesgos es documentación del sistema, no una hoja de cálculo privada. Cada riesgo lleva descripción, responsable, probabilidad, impacto, tratamiento elegido y estado. La revisión periódica actualiza la posición y deja rastro de por qué cambió.

Esa trazabilidad es lo que permite responder ante un auditor o un regulador: no solo qué se hizo, sino qué se sabía cuando se decidió. Un mapa sin fecha ni autor no demuestra nada; con ellos, cuenta la historia del sistema.

## Un riesgo mal colocado

Una empresa de servicios cloud detecta que el fallo de las copias de seguridad de sus clientes municipales tiene impacto alto y probabilidad media. En lugar de asumirlo, decide reducirlo con cifrado y pruebas trimestrales, transferir parte con un seguro y asumir el riesgo residual documentando la decisión.

La combinación es razonable porque cada pieza cubre una parte distinta: el cifrado protege el contenido, las pruebas detectan el fallo, el seguro cubre el coste y la aceptación deja claro qué queda fuera. Si en la revisión anual el riesgo sigue en la misma casilla, el problema no es la matriz: es que el plan no se ejecutó o que el control elegido no atacaba la causa.

## Fuentes

- ISO 31000:2018, *Risk management — Guidelines*.
- ISO 37301:2021, *Compliance management systems — Requirements with guidance for use*.
