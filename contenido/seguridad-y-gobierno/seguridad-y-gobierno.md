# Seguridad y gobierno en Azure

Configurar bien cada recurso es necesario y no es suficiente. Queda por resolver tres preguntas: cómo se sabe si algo está mal, cómo se detecta lo que ocurre y quién decide qué se permite. La primera es postura, la segunda es operación de seguridad y la tercera es gobierno.

## Postura

La **postura** es el estado de la configuración frente a una referencia. Microsoft publica esa referencia como un conjunto de controles agrupados por dominio —identidad, red, datos, registro y vigilancia— y la plataforma la evalúa sobre los recursos y devuelve recomendaciones con una puntuación.

La puntuación es una herramienta de priorización, no una nota. Sube igual resolviendo un control crítico que diez cosméticos, y por eso se lee junto al número de recursos afectados y a su exposición. Un recurso con dirección pública y puerto de administración abierto pesa más que tres con el cifrado pendiente.

En el nivel gratuito se obtiene la evaluación básica y las recomendaciones del benchmark. Los planes de pago añaden análisis de rutas de ataque, exploración sin agente, inventario de datos sensibles y evaluación de la configuración de las máquinas.

## Protección de cargas

Los planes por tipo de recurso añaden detección sobre lo que ya está desplegado. Los que más se usan:

| Carga | Qué añade |
|---|---|
| Servidores | Detección de comportamiento anómalo, acceso temporal a máquinas, integridad de ficheros |
| Almacenamiento | Detección de acceso anómalo y de exposición de datos |
| Bases de datos | Detección de inyección y de acceso inusual |
| Contenedores | Evaluación de imágenes y de la configuración del clúster |
| Key Vault | Detección de acceso anómalo a secretos |

El **acceso temporal** merece explicación aparte: en lugar de dejar el puerto de administración abierto, se abre solo para una IP y una ventana de tiempo. Es la diferencia entre una regla permanente y una excepción con fecha.

## Detección y respuesta

La plataforma de operaciones de seguridad es **Microsoft Sentinel**: recibe registros de Azure, de Microsoft 365, de identidad y de terceros; los guarda en un área de trabajo; los cruza con reglas y genera incidentes; y puede ejecutar una respuesta automática.

El flujo tiene cuatro piezas:

1. **Conectores.** Traen los datos. Sin ellos, no hay nada que correlacionar.
2. **Reglas analíticas.** Definen qué combinación de eventos es un incidente. Pueden ser programadas, casi en tiempo real o de fusión de incidentes.
3. **Incidentes.** Agrupan las alertas con su contexto y su gravedad para que una persona decida.
4. **Automatización.** Reglas y cuadernos de procedimiento que enriquecen, asignan o cierran sin intervención.

El coste se factura por volumen ingerido y por retención, así que el diseño empieza por decidir qué se envía y qué no. Ingerir todo lo posible es la forma más rápida de tener un sistema caro y ruidoso; ingerir solo los eventos de seguridad que importan deja capacidad para investigar.

## Gobierno

El **gobierno** decide qué se permite antes de que se despliegue. Tiene cuatro instrumentos, y cada uno actúa en un momento distinto:

- **Jerarquía de grupos de administración.** Agrupa suscripciones y permite aplicar una decisión a muchas a la vez.
- **Políticas e iniciativas.** Definen qué configuración es aceptable. Deniegan, auditan o corrigen.
- **Roles y ámbitos.** Deciden quién puede hacer qué y dónde.
- **Presupuestos y etiquetas.** Ponen precio y dueño a lo que se crea.

Una plataforma ordenada se construye sobre esa jerarquía: un grupo por entorno o por dominio, y las suscripciones como unidad de facturación y de límite. Cuando un equipo necesita algo que la política prohíbe, la respuesta es una excepción con dueño y fecha, no desactivar la política para todos.

La tentación contraria también existe: políticas tan estrictas que nadie puede trabajar, hasta que alguien las apaga un viernes. Una política que se va a incumplir es peor que no tenerla, porque enseña que las reglas se saltan.

## Medir el resultado

Cuatro números dicen si esto funciona: porcentaje de recomendaciones de severidad alta resueltas, antigüedad media de los hallazgos abiertos, tiempo entre la primera señal y la primera acción sobre un incidente, y número de excepciones vivas frente a las documentadas.

Si el primero sube y el segundo también, lo que hay es una lista creciente, no una mejora.

## Qué revisar

- ¿La postura se revisa con una cadencia y con un dueño?
- ¿Hay alguna ruta de ataque que llegue de internet a datos sin escalar?
- ¿Los planes de protección cubren las cargas críticas y no todas por inercia?
- ¿Se ingiere en la plataforma lo que se va a mirar, con retención razonable?
- ¿Existen excepciones de política sin dueño ni fecha de revisión?
- ¿Alguien mide el tiempo de respuesta, o solo el número de alertas?
