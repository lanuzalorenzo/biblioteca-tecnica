# Taxonomía de incidentes

Una biblioteca no ordena los libros por el color del lomo: los clasifica por materia, y así cualquiera encuentra el mismo título en el mismo sitio. La taxonomía de incidentes hace eso con los avisos de seguridad: les da un sitio estable para que la respuesta no dependa de quién esté de guardia.

## Qué es un incidente

Un incidente de ciberseguridad es un evento, o una cadena de eventos, inesperado o no deseado, con probabilidad significativa de comprometer las operaciones del negocio o la seguridad de la información. La definición de referencia es la de INCIBE.

De ahí se siguen dos ideas que conviene fijar antes de clasificar:

- **Un incidente no es lo mismo que una amenaza.** La amenaza es lo que puede pasar; el incidente es lo que ya está afectando o ha afectado.
- **Tampoco todo aviso es un incidente.** Un intento bloqueado, una exploración sin éxito o una alerta mal configurada pueden ser actividad inocua. Parte del trabajo consiste precisamente en separar el ruido del hecho.

La segunda idea es la que más cuesta. Un SIEM que genera cien alertas al día no está protegiendo más: está entrenando al equipo a ignorarlas. Clasificar también sirve para decidir qué no merece una investigación completa.

## Para qué sirve clasificar

La taxonomía que emplea INCIBE-CERT se apoya en la Taxonomía de Referencia para la Clasificación de Incidentes de Seguridad y en la Guía Nacional de Notificación y Gestión de Ciberincidentes. Su utilidad no es burocrática:

- **Alinear el lenguaje.** «Intrusión», «compromiso de cuenta» y «acceso no autorizado» no significan lo mismo; si cada equipo usa su propia palabra, la coordinación falla.
- **Proporcionar la respuesta.** No se trata igual una denegación de servicio que una fuga de datos personales.
- **Comparar y medir.** Sin categorías estables no se pueden contar incidentes por tipo ni detectar tendencias.
- **Notificar.** España exige notificar determinados incidentes; la categoría forma parte del parte.

La etiqueta no es un adorno del registro. De ella dependen la prioridad, el equipo que interviene y las obligaciones que se activan.

## Las diez familias

La taxonomía de referencia agrupa los incidentes en diez familias. Cada una responde a una pregunta distinta: qué se ha visto afectado y en qué momento del ataque estamos.

| Familia | Qué describe | Ejemplos |
|---|---|---|
| Contenido abusivo | Contenido ilegal o no solicitado que viaja por los sistemas | Spam, delito de odio, pornografía infantil, contenido sexual o violento |
| Contenido dañino | El sistema ya está infectado o sirve de infraestructura al atacante | Sistema infectado, servidor de mando y control, distribución o configuración de malware, dominio DGA |
| Obtención de información | Alguien recopila datos para preparar un ataque | Escaneo de redes, análisis de paquetes, ingeniería social |
| Intento de intrusión | Hay un ataque, pero todavía no hay acceso | Explotación de una vulnerabilidad con CVE, fuerza bruta contra credenciales, ataque con exploit desconocido |
| Intrusión | El atacante ya ha conseguido acceso | Compromiso de cuenta con o sin privilegios, compromiso de aplicación, robo físico |
| Disponibilidad | El servicio deja de prestarse o se degrada | DoS, DDoS, sabotaje físico, interrupción por desastre natural |
| Compromiso de la información | La información se lee, se cambia o se pierde sin autorización | Acceso no autorizado, modificación, pérdida de datos, fuga de información confidencial |
| Fraude | Los recursos se usan para engañar o lucrarse | Uso no autorizado de recursos, software sin licencia, suplantación, phishing |
| Vulnerabilidad | Existe una debilidad explotable, aunque nadie la haya usado todavía | Criptografía débil, amplificador DDoS, Telnet, RDP o VNC expuestos, SNMP o Redis mal configurados |
| Otros | Lo que no encaja en las anteriores | APT, ciberterrorismo, daños informáticos a infraestructuras críticas |

Dentro de cada familia se distinguen subcategorías. Las más útiles son las que se confunden entre sí, y por eso se desarrollan abajo.

## Cómo decidir la familia

Antes de elegir una etiqueta, conviene responder cuatro preguntas en este orden:

1. **¿Hubo acceso real o solo un intento?** Si el atacante no llegó a entrar, la familia es «intento de intrusión». Si entró, es «intrusión».
2. **¿Qué propiedad se ha visto afectada?** Disponibilidad si el servicio cae; confidencialidad, integridad o pérdida si se toca la información.
3. **¿Dónde está el daño?** En el contenido que circula (abusivo), en el equipo infectado (dañino), en el uso que se hace de los recursos (fraude) o en una debilidad latente (vulnerabilidad).
4. **¿El incidente ya ocurrió o es una condición?** Una máquina con Telnet abierto es una vulnerabilidad; el ataque que lo explota es un intento o una intrusión, según el resultado.

El orden importa. Si se empieza por la herramienta que avisó, la etiqueta se contamina con la categoría del producto; si se empieza por el hecho, la etiqueta describe lo que pasó.

## Fronteras que se confunden

- **Intento de intrusión frente a intrusión.** El compromiso de una cuenta, con o sin privilegios, ya es intrusión. La fuerza bruta que no consigue entrar se queda en intento.
- **Vulnerabilidad frente a intento de intrusión.** Tener un servicio expuesto no es un incidente de ataque: es una debilidad. Se convierte en intento cuando alguien la prueba y en intrusión cuando la explota con éxito.
- **Contenido abusivo frente a fraude.** El spam es contenido abusivo; el phishing es fraude, porque hay suplantación para obtener credenciales.
- **Contenido dañino frente a compromiso de la información.** Un sistema infectado por un troyano es contenido dañino; si además se copian datos, hay también compromiso de la información. Un incidente puede ocupar más de una familia.
- **Ransomware.** No es solo contenido dañino: el cifrado de datos añade modificación no autorizada y, si hay robo previo, fuga. La etiqueta principal no elimina las secundarias.

Una misma alerta puede necesitar una etiqueta principal y varias secundarias. El registro no se rompe por ello; al contrario, refleja mejor la realidad.

## La etiqueta no es definitiva

La clasificación tampoco es un acto único: un intento puede convertirse en intrusión, y una intrusión puede acabar en fuga de información. El parte inicial se corrige cuando cambian los hechos.

Ese cambio no es un fracaso de la clasificación; es su uso normal. Lo que sí es un problema es mantener la etiqueta inicial por comodidad cuando la investigación ya ha demostrado otra cosa.

## Por qué importa más allá del registro

Clasificar bien cambia la respuesta y el parte que se envía. Un incidente mal etiquetado como «intento» cuando ya hubo acceso retrasa la contención y puede ocultar una obligación de notificación. Al revés, tratar cada alerta como una intrusión consume recursos y acaba ignorando las señales reales.

## Ejemplo

Llega un correo que suplanta a un banco y pide credenciales. Si solo se ha entregado, es fraude por phishing. Si alguien introduce las credenciales y el atacante accede a la cuenta, hay además intrusión y compromiso de cuenta. Si después se copian datos, se añade compromiso de la información. La etiqueta principal puede seguir siendo fraude, pero las secundarias cuentan la gravedad real del caso.

## Cierre

La taxonomía da un sitio estable a lo que ocurre. Alinea el lenguaje, orienta la respuesta, permite medir y sostiene la notificación. Su valor se pierde si se usa como una etiqueta decorativa o si se queda congelada cuando los hechos cambian. Con el vocabulario fijado, el paso siguiente es ver de dónde salen las señales que permiten reconocer cada familia.

## Fuentes

- ENISA. *Reference Security Incident Taxonomy*.
- CCN-CERT. *Guía Nacional de Notificación y Gestión de Ciberincidentes*.
- INCIBE-CERT. Categorías de incidentes y servicios de gestión.
