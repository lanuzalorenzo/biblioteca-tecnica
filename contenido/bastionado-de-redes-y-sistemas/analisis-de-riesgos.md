# Análisis de riesgos

Una panadería con dos ordenadores decidió que era demasiado pequeña para analizar riesgos. Tenía el antivirus caducado y una copia que nadie había probado a restaurar. Cuando el sistema de pedidos se bloqueó, estuvo cuatro días facturando a mano. El análisis de riesgos no es un rito de grandes corporaciones: es la lista de lo que puede salir mal y lo que costaría. Sin ella, se protege lo que da miedo y se descuida lo que sostiene el negocio.

El vocabulario básico —activo, amenaza, vulnerabilidad, riesgo— se explica en [Conceptos de seguridad](../seguridad-y-alta-disponibilidad/conceptos-de-seguridad.md). Este apunte se ocupa del método: cómo se ordena el trabajo y cómo se elige dónde invertir el esfuerzo.

## Qué aporta y qué no

Un análisis de riesgos pone nombre a los activos, a las amenazas que los acechan, a la probabilidad de que ocurran y al daño que causarían. No adivina el futuro: sirve para priorizar. Cambia la pregunta «¿qué herramienta compramos?» por «¿qué nos puede pasar y cuánto nos costaría?».

Hay dos rasgos que se suelen olvidar:

- **No es un documento único.** Los sistemas, las personas y las amenazas cambian; un análisis de hace un año puede haber caducado.
- **No es solo técnico.** Requiere entrevistas, cuestionarios y el respaldo de la dirección. Sin presupuesto ni prioridad, el plan se queda en un cajón.

## Dónde se parte

Antes de decidir qué mejorar hay que describir la situación actual. Se mira en cinco planos:

- El grado de madurez en ciberseguridad.
- Los elementos técnicos: equipos, redes, aplicaciones, copias.
- La organización: roles, procedimientos, formación.
- Las obligaciones normativas que aplican.
- La criticidad de la información: qué se perdería si desapareciera o se filtrara.

Los obstáculos de esta fase rara vez son tecnológicos. Lo habitual es que un área no entregue información, que el responsable de un servicio crítico no tenga tiempo o que la dirección vea el proyecto como un gasto sin retorno.

## Acotar y elegir activos

El análisis tiene que caber en un presupuesto y en un calendario. Acotar el alcance permite saber cuánto trabajo hay y qué áreas entran. Una consulta médica, una planta industrial y un departamento de investigación no se protegen con las mismas medidas ni con el mismo esfuerzo.

Dentro del alcance se identifican los activos. Se empieza por los críticos, porque no se puede proteger todo a la vez. Un inventario con dueño y nivel de criticidad evita que el análisis se convierta en una lista de deseos sin responsable.

## Medir la madurez

Un mismo control puede estar implantado de formas muy diferentes. Un modelo de madurez inspirado en CMMI, con un nivel «inexistente» añadido, ayuda a describirlo sin engañarse. Aplicado a las copias de seguridad:

| Nivel | Qué hay |
|---|---|
| Inexistente | No hay política de copias |
| Inicial | Hay un sistema, pero nadie lo controla ni lo planifica |
| Repetible | Se hacen, pero sin normalización; a demanda |
| Definido | Existe un procedimiento claro, sin aprobación de la dirección |
| Administrado | El procedimiento está aprobado formalmente |
| Optimizado | Está aprobado y se verifica su eficacia con indicadores |

Entre «definido» y «administrado» media la firma de la dirección. Entre «administrado» y «optimizado» media la medición. Un control documentado que nadie mide se queda a medio camino.

## Cinco pasos

1. **Inventariar los activos.** Sin saber qué hay, no hay nada que proteger.
2. **Describir el riesgo intrínseco.** Es la exposición antes de aplicar controles: qué amenazas afectan al activo y qué debilidades tiene.
3. **Estimar la probabilidad.** ¿Qué posibilidad hay de que la amenaza se materialice?
4. **Calcular el riesgo.** Una fórmula sencilla para ordenar es `Riesgo = Impacto × Probabilidad`.
5. **Separar lo no aceptable de lo residual.** El riesgo no aceptable puede dejar el servicio sin prestar; el residual es el que queda tras los controles y la organización decide asumir.

La fórmula no da una cifra contable exacta. Si un incendio impide acceder a los servidores y cuesta 1.000 € al día durante 30 días, el impacto son 30.000 €. Con una probabilidad baja de 2 sobre 10, la puntuación es 60.000; si se normaliza a 0,2, el resultado son 6.000 €. La utilidad está en comparar riesgos, no en presupuestar al céntimo.

## Tres formas de tratarlo

- **Poner controles.** Es lo habitual cuando el proceso es necesario y se puede proteger.
- **Eliminar la actividad.** Se deja de hacer lo que genera el riesgo. Solo vale si el proceso no es necesario.
- **Transferirlo.** Un ciberseguro comparte la consecuencia económica, pero no la responsabilidad de proteger.

Equivocarse sale caro en los dos sentidos: un control desproporcionado frena la actividad y uno insuficiente deja el riesgo intacto.

## Comprobar que sirve

Después de implantar un control hay que verificar que cumple lo que promete. Sin medición no hay verificación. En las copias, por ejemplo, no basta con que el trabajo se ejecute: hay que revisar la frecuencia, el resultado y, sobre todo, que la restauración funcione. El diseño y la prueba de copias se detallan en [Almacenamiento y copias de seguridad](../seguridad-y-alta-disponibilidad/almacenamiento-y-copias.md).

El análisis se cierra con indicadores y se reabre cuando cambian los sistemas, los servicios o las amenazas. Es un ciclo, no un informe que se archiva.

## Errores que se repiten

- Tomar el análisis por una auditoría. La auditoría mide cumplimiento; el análisis decide prioridades.
- Elegir la herramienta antes de conocer los activos.
- Dejar fuera a la dirección y quedarse sin recursos.
- No definir indicadores: un control sin medida es una promesa.
- Hacer el trabajo una sola vez.
- Vender una puntuación como pérdida esperada exacta.

## Fuentes

- ISO/IEC 27001 (2013 y 2022) e ISO/IEC 27005 (2018 y 2022), gestión del riesgo de seguridad de la información.
- ISACA. *CMMI*, modelo de madurez de procesos.
- INCIBE. Guías de análisis y gestión de riesgos para pymes.
