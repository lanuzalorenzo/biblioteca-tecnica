# Introducción al bastionado

Preparar una casa para dejarla sola no consiste solo en cerrar la puerta con llave. Se revisan las ventanas, se deja una luz encendida, se guarda lo importante en un sitio que no se vea desde la calle y se avisa al vecino de que se va a estar fuera. Con un sistema ocurre lo mismo: la protección no está en un único control, sino en recorrer todos los puntos de entrada y decidir cuáles deben seguir abiertos.

Bastionar es ese recorrido. No es instalar un producto ni aplicar una lista de comprobación sin mirar el contexto, sino reducir las debilidades y la exposición de una red o un sistema mediante configuración, políticas y controles proporcionados al riesgo.

## Qué se reduce

El trabajo actúa sobre tres cosas distintas, y conviene no mezclarlas:

- **La superficie de ataque:** todo lo que está expuesto sin necesidad. Puertos abiertos, servicios que nadie usa, cuentas que sobreviven a su dueño, interfaces de administración accesibles desde cualquier sitio.
- **La vulnerabilidad:** la debilidad concreta que permite que una amenaza tenga éxito. Un software sin actualizar, una configuración por defecto, un permiso de más.
- **El impacto:** lo que ocurre cuando el fallo ya se ha producido. Copias que permiten volver, segmentación que limita hasta dónde llega un equipo comprometido, registro que permite reconstruir lo que pasó.

Las tres se apoyan en lo mismo: conocer qué hay. Un inventario de activos, con dueño y criticidad, es el punto de partida. Sin él se protege lo que se ve, no lo que importa.

El vocabulario completo —activo, amenaza, vulnerabilidad, riesgo, confidencialidad, integridad, disponibilidad y no repudio— está en [Conceptos de seguridad](../seguridad-y-alta-disponibilidad/conceptos-de-seguridad.md). Aquí interesa la consecuencia práctica: una vulnerabilidad conocida y parcheada se resuelve aplicando el parche; una desconocida solo se contiene con menos superficie, menos privilegio y capacidad de detección.

## Medidas iniciales

Hay un grupo de medidas que casi siempre está en el primer paso, porque son baratas y reducen mucho:

- Eliminar cuentas innecesarias y cambiar las credenciales que trae el fabricante.
- Deshabilitar servicios y puertos que no se necesitan.
- Mantener sistema y aplicaciones actualizados.
- Proteger los servicios que sí deben quedar habilitados.
- Filtrar el tráfico con cortafuegos y reglas justificadas.
- Tener copias y un procedimiento de recuperación probado.
- Configurar la red inalámbrica de forma segura y mantenerla solo donde haga falta.

Ninguna se aplica a ciegas. Un servicio puede parecer prescindible y ser la dependencia de otro que sí se usa; una actualización puede romper una aplicación antigua. Cada cambio necesita una comprobación previa, un registro y una forma de volver atrás. La medida que nadie ha probado no es una medida: es una intención.

## Defensa en profundidad

La defensa en profundidad coloca controles complementarios en capas distintas. Si uno falla, los demás limitan el daño. No se trata de repetir la misma protección tres veces, sino de cubrir fases distintas: evitar que el ataque llegue, detectarlo si llega, contenerlo mientras dura y recuperar lo que se haya perdido.

El bastionado forma parte de esa estrategia, pero no la sustituye. Un servidor perfectamente configurado sigue necesitando copias, supervisión y un plan para cuando algo falle. La capa que falta no la compensa la capa que está bien hecha.

## Zero Trust: no confiar por el sitio donde estás

Durante mucho tiempo se dibujó una frontera: dentro de la red, confianza; fuera, desconfianza. La movilidad, el teletrabajo, los servicios en la nube y los dispositivos conectados rompieron esa frontera. Estar en la misma red que un servidor ya no dice nada sobre quién es el usuario ni sobre el estado de su equipo.

Zero Trust propone no conceder confianza implícita por la ubicación. Cada acceso se evalúa con una política explícita que mira identidad, dispositivo, contexto y recurso. En la práctica se traduce en cinco decisiones:

- Verificar la identidad y exigir un segundo factor cuando la operación lo justifique.
- Conceder el mínimo privilegio y durante el tiempo necesario.
- Dar acceso a la aplicación concreta, no a toda la red por comodidad.
- Segmentar y observar los flujos entre activos.
- Revisar las políticas cuando cambian las personas, los equipos o los riesgos.

Zero Trust no es un producto que se compra ni una etiqueta que se pone a un cortafuegos. Es una forma de diseñar que exige identidades fiables, inventario de dispositivos y políticas mantenidas. Sin esas piezas, el nombre queda grande.

## Del riesgo al plan

Antes de elegir herramientas conviene saber qué se protege y de qué. El análisis de riesgos identifica activos y procesos críticos, amenazas, debilidades, probabilidad e impacto, y permite ordenar el tratamiento. La seguridad debe apoyar la actividad de la organización; un control que impide trabajar se acaba sorteando.

El plan director convierte esas prioridades en acciones con objetivos, alcance y responsables. Puede apoyarse en marcos como ISO/IEC 27001, el marco de ciberseguridad de NIST, el Esquema Nacional de Seguridad o PCI DSS, pero ninguno se adopta por moda: cada uno tiene su ámbito y sus obligaciones. El plan tampoco termina al implantar las medidas. Se revisa, se mide y se actualiza cuando cambian los sistemas o las amenazas.

## Procedimiento

Una secuencia razonable para empezar:

1. Inventariar activos, información y procesos que deben protegerse.
2. Analizar amenazas, debilidades, probabilidad e impacto.
3. Acordar el nivel de riesgo aceptable con quien responde del servicio.
4. Elegir controles proporcionados: configuración, medidas organizativas y recuperación.
5. Probar cada cambio, documentarlo y dejar una vía de reversión.
6. Supervisar el resultado y revisar el plan cuando cambie el entorno.

## Ejemplo

Una consulta pequeña guarda parte de la historia clínica en papel y depende de un programa de citas. Antes de comprar nada, identifica qué servicios son críticos, quién necesita entrar en cada uno y qué ocurriría si dejaran de funcionar. De ahí salen las prioridades: cuentas individuales, autenticación adecuada, actualizaciones, una separación razonable entre la red de espera y la de gestión y copias que se hayan restaurado alguna vez. El orden importa más que la lista: primero lo que sostiene la atención, después lo que la protege.

## Errores que se repiten

- Empezar por la herramienta y no por el inventario.
- Deshabilitar un servicio sin comprobar quién lo usa.
- Llamar defensa en profundidad a tener tres antivirus.
- Dar por hecho que estar dentro de la red concede confianza.
- Escribir un plan que nadie mide y archivar el análisis de riesgos.
- Presentar como implantado un control que no se ha probado.

## Fuentes

- NIST. *SP 800-123, Guide to General Server Security*, *SP 800-207, Zero Trust Architecture* y *SP 800-30, Guide for Conducting Risk Assessments*.
- ISO/IEC 27001, NIST Cybersecurity Framework, ENS (Real Decreto 311/2022) y PCI DSS.
- INCIBE. Guías de seguridad para pymes y herramienta de autodiagnóstico.
