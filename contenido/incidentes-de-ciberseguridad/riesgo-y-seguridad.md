# Riesgo y seguridad

Cerrar una casa no consiste en poner una sola cerradura. La ventana abierta es la vulnerabilidad, el ladrón que ronda es la amenaza y la posibilidad de que entre es el riesgo. Una reja reduce el riesgo, pero no hace desaparecer al ladrón; por eso se combinan capas, se revisan y se acepta que ninguna protección es definitiva.

## De la cibernética a la ciberseguridad

La cibernética estudia cómo un sistema procesa información y se corrige a sí mismo. La ciberseguridad toma las estrategias de la seguridad clásica y las aplica a los sistemas informáticos: no es una ciencia exacta, sino una práctica que cambia al mismo ritmo que la tecnología y que el ingenio de quien busca aprovechar sus fallos.

Esa diferencia importa. Un sistema de seguridad no se diseña para un estado inmóvil, sino para un entorno que se modifica: aparecen servicios nuevos, se conectan dispositivos, cambian los permisos y se descubre una debilidad que antes nadie conocía. La revisión forma parte del trabajo, no es un trámite posterior.

## Amenaza, vulnerabilidad y riesgo

El vocabulario se confunde con facilidad y cada confusión lleva a una medida equivocada. Conviene fijar cuatro términos:

| Término | Qué es | Ejemplo |
|---|---|---|
| Activo | Lo que tiene valor para la organización | Una base de datos con historiales |
| Amenaza | Evento o circunstancia con potencial de causar daño | Un atacante, un malware, un incendio |
| Vulnerabilidad | Debilidad que puede ser explotada | Un servicio sin parchear, un permiso excesivo |
| Riesgo | Posibilidad de que la amenaza aproveche la vulnerabilidad y produzca un impacto | Acceso no autorizado a los historiales |

El impacto es la consecuencia si el riesgo se materializa: una fuga, una multa, una parada del servicio o una pérdida de confianza. Una amenaza sin vulnerabilidad no produce daño; una vulnerabilidad que nadie explota tampoco. El riesgo aparece cuando coinciden, y su importancia depende del valor del activo y de la gravedad del impacto.

Una empresa que guarda historiales de clientes tiene un activo claro. La amenaza puede ser un acceso no autorizado; la vulnerabilidad, una aplicación con permisos de más. El riesgo no se elimina con una sola medida: se reduce con autenticación fuerte, permisos mínimos, cifrado y copias, y se acepta que queda un resto que hay que vigilar.

## Las tres reglas pragmáticas

Estas tres reglas ordenan casi cualquier plan de seguridad:

1. **Prevención: protegerse de lo conocido.** Parches, versiones actualizadas, antimalware, cortafuegos y el resto de medidas frente a riesgos ya identificados.
2. **Concienciación: alertar de lo desconocido.** Protocolos para avisar de lo sospechoso, con procesos mecanizados y personas formadas.
3. **Respuesta: prepararse para el peor caso.** No se pueden prever todas las variantes; hacen falta mecanismos para contener y reducir el daño cuando la prevención falla.

Las tres se sostienen entre sí. Un antivirus sin usuarios formados se desactiva con un clic; una formación sin un canal de respuesta deja a la persona sabiendo qué ocurre pero sin saber a quién avisar. La prevención sin respuesta aguanta hasta el primer fallo; la respuesta sin prevención apaga fuegos que podrían haberse evitado.

## La tríada CIA

La seguridad de la información se mide en tres dimensiones:

- **Confidencialidad:** solo accede quien está autorizado.
- **Integridad:** la información es exacta y no se altera sin control.
- **Disponibilidad:** el servicio está cuando se necesita.

La autenticación y el no repudio las refuerzan: permiten saber quién accede y demostrar que una acción ocurrió. Ninguna dimensión se maximiza a costa de las otras. Cifrar todos los datos y perder la clave protege la confidencialidad y destruye la disponibilidad; hacer copias sin cifrar protege la disponibilidad y abre una vía a la fuga. El objetivo es un equilibrio proporcionado al valor de cada activo y al coste de cada medida.

## Marcos y organismos

Los marcos y organismos de referencia habituales son NIST, ENISA, INCIBE, CCN, CCN-CERT y el Esquema Nacional de Seguridad. Los marcos aportan métodos y catálogos; los organismos publican guías, alertas y certificaciones. Su función es orientar el análisis y la implantación de medidas proporcionadas; no son recetas cerradas. Cada organización adapta el marco a su tamaño, su sector y su presupuesto, y documenta por qué elige unas medidas y no otras.

Un marco no sustituye al criterio. Sirve para no empezar de cero, para comparar el estado propio con una referencia y para justificar decisiones ante terceros. Cuando la organización es pequeña, el marco se recorta; cuando el servicio es crítico, se profundiza. Lo que no cambia es la necesidad de saber qué se protege y qué se acepta como riesgo residual.

## Cómo se evalúa el riesgo

El procedimiento se puede resumir en cinco pasos:

1. Identificar activos, procesos y datos críticos.
2. Reconocer las amenazas y las vulnerabilidades que los afectan.
3. Evaluar el impacto y la probabilidad de cada escenario.
4. Aplicar las tres reglas: prevenir, concienciar y preparar la respuesta.
5. Revisar el riesgo y el plan de respuesta de forma periódica.

El resultado no es una lista de deseos, sino un orden de prioridades. Una vulnerabilidad en un servidor de pruebas no pesa lo mismo que la misma vulnerabilidad en el sistema que cobra las nóminas. La evaluación sirve para decidir dónde se pone el esfuerzo primero y qué riesgo se acepta conscientemente.

## Riesgo residual

Ninguna medida deja el riesgo a cero. Lo que queda después de aplicar los controles se llama riesgo residual, y también hay que decidirlo: se acepta, se transfiere a un tercero —por ejemplo, un seguro— o se vuelve a reducir. Lo que no se puede hacer es ignorarlo y descubrirlo cuando ya ha ocurrido el incidente.

La aceptación debe quedar escrita, con el motivo y con la persona que la asume. «Ya veremos» no es una decisión; es una deuda que se paga en el peor momento. La revisión periódica existe para comprobar que el riesgo aceptado sigue siendo tolerable cuando cambian el negocio, el proveedor o la amenaza.

## Errores frecuentes

- **Confundir amenaza con vulnerabilidad.** La amenaza es lo que puede pasar; la vulnerabilidad es la grieta que lo permite.
- **Creer que una herramienta elimina el riesgo.** Un cortafuegos, un antivirus o un SIEM reducen una parte del problema; no sustituyen al resto del plan.
- **Maximizar una sola dimensión.** Una medida que protege la confidencialidad puede dejar el servicio inutilizable.
- **Comprar medidas sin conocer los activos.** Sin inventario, la inversión se reparte por intuición.
- **Guardar el análisis y no revisarlo.** El entorno cambia; un riesgo aceptado hace un año puede no ser aceptable hoy.

## Cierre

La seguridad es una práctica de equilibrio y de revisión. No promete que no ocurra nada; promete que lo que ocurra se detecte antes, se contenga mejor y deje una lección aprovechable. Ese es el puente hacia los apuntes siguientes: la higiene que reduce la probabilidad y el ciclo de vida que ordena la respuesta.

## Fuentes

- CCN. *Principios generales en materia de ciberseguridad* (decálogo básico).
- NIST, ENISA, INCIBE, CCN-CERT y el Esquema Nacional de Seguridad como marcos de referencia.
