# Capas de internet

La «web oscura» es la parte de internet que más se describe con metáforas y menos con criterios. Antes de hablar de Tor o de mercados ilícitos conviene fijar el vocabulario: no hay dos internets, una normal y otra prohibida, sino tres preguntas distintas —qué indexan los buscadores, qué exige identificarse y qué solo es alcanzable por una red especial— que se mezclan todo el tiempo.

## Tres criterios, no una escala de profundidad

| | ClearNet | Deep Web | Dark Web |
|---|---|---|---|
| ¿La indexan los buscadores? | Sí | No | No |
| ¿Exige identificarse? | Normalmente no | Con frecuencia sí | Depende del servicio |
| ¿Qué red usa? | Internet convencional | Internet convencional | Una darknet |
| ¿Cómo se accede? | Navegador habitual | Navegador, con credenciales | Software específico |
| Ejemplos | Medios, tiendas, webs públicas | Correo web, banca, intranet, nube privada | Servicios onion, eepsites |

La consecuencia de seguridad de estar en la ClearNet es la atribución: el operador y quien observe el camino saben al menos quién se conecta a qué servicio, aunque el contenido vaya cifrado. La Deep Web no es una zona peligrosa: es lo privado de todos los días. Y la Dark Web es una parte muy pequeña de la Deep Web, no su sinónimo.

El dibujo del iceberg —una punta visible y una masa sumergida con un rincón siniestro— mezcla criterios independientes como si fueran profundidad, sugiere que bajar es más ilegal y se apoya en cifras sin base medible. Cuando aparezca un porcentaje sobre el tamaño de estas capas, la pregunta correcta es de dónde sale.

## Tor: qué hace y qué no

El encaminamiento en cebolla nace de investigaciones de los años noventa y hoy lo mantiene el Tor Project con miles de nodos voluntarios. El cliente construye un circuito de tres nodos —entrada, intermedio y salida—, cifra los datos en capas y cada nodo retira solo la suya. El de entrada sabe quién eres y no a dónde vas; el de salida sabe a dónde va el tráfico y no quién lo envía; el intermedio solo conoce a sus vecinos. Los circuitos se renuevan periódicamente y la lista de nodos la publican autoridades de directorio.

Tor sirve para dos cosas: navegar por la ClearNet ocultando la dirección de origen al servicio y acceder a servicios onion, que no se resuelven por DNS sino que derivan de una clave criptográfica. En el segundo caso, cliente y servicio se encuentran en un punto de encuentro y el tráfico no sale de la red.

Tor no da anonimato absoluto. No protege si te identificas tú mismo con una cuenta personal, si el navegador tiene una vulnerabilidad, si abres un documento que contacta con la red por fuera del circuito o si un adversario observa los dos extremos y correlaciona. El nodo de salida ve el tráfico no cifrado que va a la ClearNet, el operador sabe que usas Tor aunque no qué haces y la conexión es más lenta. Tampoco es una VPN en sentido estricto.

## Las otras tres redes

| Red | Modelo | Qué protege | ¿Navegación anónima por la ClearNet? |
|---|---|---|---|
| Tor | Circuito de tres nodos con cifrado en capas | Quién se conecta a qué; ubicación del servicio | Sí |
| I2P | Túneles unidireccionales y agrupación de mensajes; base de datos distribuida | Servicios internos anónimos | Limitada |
| Freenet / Hyphanet | Almacén distribuido y cifrado, sin servidores | Publicación resistente a la censura | No |
| ZeroNet | Sitios sin servidor, repartidos entre visitantes | Censura y caída de servidores | No |

**I2P** se centra en servicios internos —eepsites, mensajería, intercambio de ficheros—, usa un túnel de entrada y otro de salida por separado y no tiene autoridades de directorio centrales. **Freenet** responde a otra pregunta: cómo publicar y conservar información frente a la censura, con un almacén cifrado en el que lo solicitado se conserva y lo que nadie pide desaparece; puede funcionar abierto a desconocidos o solo entre conocidos. **ZeroNet** distribuye sitios identificados por clave pública y solo deja publicar a quien tiene la clave privada; no oculta la dirección IP por defecto y puede combinarse con Tor.

El estado de mantenimiento de ZeroNet y el cambio de denominación de Freenet conviene comprobarlos antes de apoyarse en ellos. Ejecutar software sin mantenimiento es un riesgo en sí mismo, así que cualquier prueba va en una máquina virtual aislada y desechable.

## Herramientas de acceso

Para Tor, el Tor Browser, descargado siempre del sitio oficial y verificado; reduce la huella digital del navegador, es decir, los rasgos que permiten distinguir un equipo de otro. También Tails, que fuerza todo el tráfico por la red, y Whonix, que separa el puesto de trabajo del acceso. Para el resto se instala el software de cada proyecto y se usa su interfaz local.

Los servicios onion no están en el DNS ni en los buscadores: se llega por enlaces o directorios, y la suplantación de direcciones parecidas es frecuente. La buena práctica es obtener la dirección desde la página oficial del servicio en la ClearNet, no de un directorio anónimo.

## Por qué importa a quien defiende

1. **Inteligencia de amenazas.** Los grupos de *ransomware* publican datos de víctimas que no pagan; los intermediarios anuncian accesos iniciales; las credenciales robadas circulan. Saber que esa información existe permite forzar cambios de contraseña, revocar accesos y preparar la comunicación de una brecha.
2. **Vigilancia de credenciales y de marca.** Comprobar si los correos corporativos aparecen en filtraciones y si se menciona a la empresa. Suele contratarse como servicio, porque hacerlo directamente exige marco jurídico y método.
3. **Detección del uso de redes de anonimato desde dentro.** Como las listas de nodos son públicas, se puede detectar o bloquear su uso, con la limitación de los puentes. Bloquear o vigilar es una decisión de política: en un banco puede ser razonable bloquear; en una redacción, un uso legítimo.
4. **Ampliación del reconocimiento.** Algunas fuentes de filtraciones consultadas en la fase de [reconocimiento](fases-de-un-ataque.md) viven en estos espacios.

## Límites del auditor

Acceder a una darknet no es ilegal por sí mismo, como no lo es instalar el navegador. Lo que puede serlo son los contenidos, lo que se descarga y las acciones que se realizan. De ahí:

- No se usa Tor para ocultar el origen de pruebas autorizadas: el alcance exige direcciones declaradas y muchos servicios bloquean nodos de salida.
- No se interactúa con delincuentes, no se compra ni se participa en foros ilícitos.
- No se descargan ni almacenan datos filtrados sin base legal y procedimiento aprobado.
- Ante contenido ilegal grave, se abandona de inmediato, no se descarga ni se captura y se comunica por el cauce establecido y a la autoridad competente.
- Nada que exigiera autorización en la ClearNet deja de exigirla aquí.

## Uso seguro en el laboratorio

Máquina virtual dedicada y en red separada de las máquinas vulnerables; ninguna cuenta personal; no se descarga ni se abre ningún fichero; solo se visitan los servicios previstos, con direcciones obtenidas de sus webs oficiales; instantánea antes de empezar y descarte al terminar; y respeto a las restricciones de red de la organización. ZeroNet, Freenet e I2P se tratan de forma conceptual o con demostración controlada en máquinas desechables.

## Un caso hipotético: credenciales en una filtración

Un servicio de vigilancia avisa de que catorce correos del dominio de una empresa aparecen en la filtración de un foro sectorial. La respuesta correcta no es entrar al foro: se verifica el aviso —qué datos, de qué servicio y cuándo—, se valora el riesgo real por reutilización de contraseñas, se fuerzan cambios y se revocan sesiones, se buscan intentos de acceso anómalos en los registros, se evalúan las obligaciones de notificación y se documenta. Ninguna persona de la empresa entra en el foro, descarga la filtración ni busca al autor: eso lo hace el servicio contratado, bajo su marco profesional.

## Errores frecuentes

- Usar Deep Web y Dark Web como sinónimos.
- Creer que la Dark Web es la mayor parte de internet o que todo lo que hay es ilegal.
- Pensar que usar Tor es delito o, al contrario, que da anonimato total.
- Identificarse con una cuenta personal desde la red de anonimato.
- Descargar datos filtrados «para comprobar».
- Usar Tor para ocultar el origen de una prueba autorizada.
- Fiarse de direcciones obtenidas de directorios anónimos.
- Ejecutar software abandonado fuera de una máquina aislada.

## Glosario

| Término | Definición |
|---|---|
| Darknet | Red superpuesta con acceso mediante software específico. |
| Servicio onion | Sitio alojado en Tor, con dirección derivada de una clave. |
| Eepsite | Sitio alojado dentro de I2P. |
| Relay | Nodo que reenvía tráfico de la red Tor. |
| Puente | Nodo de entrada no publicado, para sortear bloqueos. |
| Huella digital del navegador | Rasgos que permiten distinguir un navegador de otro. |

## Fuentes

- Tor Project. *Documentación oficial de Tor y del Tor Browser*.
- Reglamento (UE) 2016/679, protección de datos.
