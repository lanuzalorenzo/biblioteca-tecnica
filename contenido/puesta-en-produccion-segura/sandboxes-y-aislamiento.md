# Seguridad en lenguajes y entornos de ejecución (sandboxes)

Un sandbox se parece al banco de pruebas de una fábrica: la pieza puede romperse, pero los trozos no alcanzan la línea de producción. La pieza sigue siendo la misma y el fallo sigue ocurriendo; lo que cambia es hasta dónde llega el daño. Confundir ese banco con una garantía de que la pieza no se rompe es el error que más veces veo.

Al revisar una aplicación separo tres cosas que suelen ir juntas en la conversación: lo que protege el lenguaje, lo que protege el entorno de ejecución y lo que solo puede proteger el sistema operativo. Ninguna capa sustituye a las otras, y saber cuál actúa en cada caso cambia la decisión de despliegue.

## Tres capas distintas

- **Seguridad de memoria:** el programa no puede leer ni escribir fuera de las zonas que le corresponden.
- **Seguridad de tipos:** cada valor se usa solo como su tipo permite.
- **Aislamiento:** aunque el programa tenga un defecto o sea hostil, una frontera externa limita el daño.

La tercera no la da el lenguaje, sino el entorno y el sistema operativo. La pregunta útil no es «¿es seguro este lenguaje?», sino «¿protege frente a un atacante que controla esta entrada?». Eso es el **modelo de amenaza**: no es lo mismo procesar datos propios que aceptar ficheros subidos por desconocidos.

## Memoria: C frente a los lenguajes gestionados

En C, el programador reserva un tamaño concreto y responde de no salirse. El lenguaje no lo comprueba. Si el programa escribe más allá del final de una reserva, la escritura ocurre igual y pisa lo que haya al lado: otra variable, el estado interno o la dirección de retorno. Eso es un **desbordamiento de búfer**. Leer fuera de límites filtra información y usar memoria ya liberada permite que el programa trabaje sobre una zona reasignada.

```c
void saludar(const char *nombre) {
    char buffer[8];
    strcpy(buffer, nombre);   /* con 40 letras, escribe 41 bytes donde caben 8 */
}
```

Sin herramientas, el programa puede seguir funcionando o romperse de forma impredecible. Compilado con AddressSanitizer (`gcc -g -fsanitize=address`), el fallo se detiene en la línea exacta. La corrección comprueba la longitud y copia de forma acotada con `snprintf`; la verificación repite la entrada larga y comprueba que ahora se rechaza.

Java, Python, C# y Go comprueban los límites, no permiten aritmética de punteros y liberan con un recolector. Un acceso fuera de límites lanza una excepción y el programa falla de forma limpia. Rust logra una garantía parecida sin recolector mediante el sistema de propiedad que verifica el compilador.

Memoria segura no significa programa seguro. Quedan inyección, control de acceso roto y secretos en el código. Además, los lenguajes gestionados se apoyan en intérpretes y bibliotecas escritos en C o C++, así que un defecto ahí sigue afectando. Cuando no hay más remedio que usar C o C++, se activan mitigaciones que dificultan el aprovechamiento pero no eliminan el defecto: canarios de pila, pila no ejecutable, aleatorización del espacio de direcciones y ejecutables independientes de la posición.

## Tipos, nulos, enteros y deserialización

Cuanto antes se detecta una confusión de tipos, menos oportunidades hay de aprovecharla. En un lenguaje de tipado estático el compilador comprueba antes de ejecutar; en uno dinámico, la comprobación llega al ejecutar la línea concreta y un camino poco usado puede pasar meses sin ejecutarse. Eso no hace inseguro a Python, pero traslada al equipo la responsabilidad de cubrir ese camino con pruebas.

El tipado fuerte o débil mide cuánto convierte el lenguaje sin que se lo pidan. JavaScript convierte en silencio (`"5" + 1` da `"51"` y `"5" - 1` da `4`), y esas conversiones han estado detrás de comparaciones de contraseñas y permisos. Python y Java son fuertes: sumar una cadena y un número en Python produce un `TypeError` en lugar de adivinar.

Tres fallos se repiten:

- **Referencia nula (CWE-476).** Usar un valor que debería ser objeto y no lo es provoca `NullPointerException` en Java y un acceso a la dirección cero en C. Es sobre todo un fallo de disponibilidad: un servicio que se cae con una entrada concreta está a un mensaje de una denegación de servicio. Kotlin distingue `String` de `String?` y obliga a decidir.
- **Desbordamiento de enteros (CWE-190).** Un `int` de 32 bits no supera 2 147 483 647; al sumar uno da la vuelta y devuelve el mínimo negativo. `Math.addExact` lanza una excepción en lugar de devolver un valor falso. Python no tiene ese límite, pero sigue habiendo que validar rangos de negocio. En C, el desbordamiento con signo es comportamiento indefinido.
- **Confusión de tipos al deserializar (CWE-502).** Reconstruir objetos desde datos externos permite que el dato elija qué clase se instancia. `pickle` advierte de que no debe usarse con datos no fiables porque cargarlos puede ejecutar código. Para intercambiar datos con terceros se usa un formato que solo describe datos, como JSON con validación de esquema.

## La JVM como frontera

La JVM añade una capa de integridad. Antes de ejecutar una clase, el verificador de bytecode comprueba que los tipos de la pila son coherentes y que no se accede a variables sin inicializar; un `.class` hecho a mano que intente saltarse las reglas es rechazado. Los cargadores de clases separan espacios de nombres y, desde Java 9, el sistema de módulos permite ocultar paquetes internos. Son medidas de encapsulación e integridad, no un aislamiento fuerte.

Java intentó además un recinto dentro del propio proceso con el **SecurityManager**, que consultaba una política de permisos antes de cada operación delicada. En la práctica era difícil de configurar y de mantener correcto, y aparecieron fallos que permitían saltárselo. Java 17 lo marcó para eliminación (JEP 411) y las versiones recientes lo han desactivado de forma permanente (JEP 486). La lección es que un recinto construido dentro del mismo proceso, con la misma memoria y el mismo intérprete que el código que quiere contener, es muy difícil de hacer a prueba de fallos. Hoy el aislamiento se delega fuera: sistema operativo, contenedores o máquinas virtuales.

## Python no ofrece un sandbox

El intérprete de Python está pensado para ejecutar código en el que se confía. Su modelo de objetos expone la maquinaria interna a quien pueda escribir expresiones: se puede llegar a casi cualquier cosa recorriendo atributos de objetos que ya existen. Por eso son peligrosas `eval()`, `exec()` y `pickle` sobre datos externos. Existen intentos de «Python restringido», pero sus propios proyectos advierten de sus límites. Lo que se hace en su lugar es no ejecutar datos como código y aislar desde fuera lo que haya que ejecutar.

## Qué define un sandbox

Un sandbox es un entorno en el que un programa puede hacer lo necesario para su función y nada más. Aplica el principio de **mínimo privilegio** a la ejecución: no se confía en que el código se porte bien, se limita lo que puede hacer aunque se porte mal. Se apoya en la **mediación completa** —toda operación sensible pasa por un guardián que el programa no puede esquivar— y en la **defensa en profundidad**.

Un buen sandbox responde a cuatro preguntas: qué ve el programa, qué puede hacer, cuánto puede consumir y quién hace cumplir los límites. La última es la decisiva: si el límite lo impone el propio lenguaje, es tan fuerte como el código que se quiere contener; si lo impone el núcleo o un hipervisor, el programa no puede modificarlo.

| Mecanismo | Qué limita | Dónde se ve |
|---|---|---|
| Usuarios y permisos | Quién puede leer, escribir o ejecutar | Cada app de Android es un usuario |
| Namespaces | Lo que el proceso ve: procesos, red, montajes | Contenedores |
| cgroups | Lo que consume: CPU, memoria, procesos | Límites de Docker |
| Capabilities | Trocea los poderes de root en privilegios sueltos | `--cap-drop ALL` |
| seccomp | Qué llamadas al núcleo puede hacer | Perfil por defecto de Docker |
| SELinux / AppArmor | Política obligatoria que ni el dueño puede saltarse | Android, Ubuntu |
| Virtualización | Un núcleo completo separado | Máquinas virtuales |

Todos los mecanismos salvo la virtualización limitan un proceso dentro de un núcleo compartido; la virtualización separa núcleos. De ahí la regla práctica más importante: **un contenedor no es una máquina virtual**. Un defecto en el núcleo de Linux puede afectar a todos los contenedores del equipo porque comparten núcleo.

## Caso: `eval()` en una calculadora

Una aplicación permite escribir fórmulas como `2*(150+30)`. La versión vulnerable usa `eval(expresion)`, que no entiende de aritmética: ejecuta cualquier expresión Python. Una llamada como `__import__('os').getpid()` demuestra que el texto se trata como orden. Es una inyección de código (CWE-94 y CWE-95), el mismo error de fondo que la inyección SQL con otro intérprete.

La prueba se escribe antes de corregir, como explico en [Pruebas de software](pruebas-de-software.md), e incluye expresiones no aritméticas y también fórmulas legítimas, para que una función que rechace todo no pase. Vaciar los `builtins` de `eval` —`eval(expresion, {"__builtins__": {}}, {})`— bloquea las llamadas directas, pero `().__class__` y el recorrido de subclases siguen funcionando, porque el código se ejecuta en el mismo intérprete. Es la diferencia entre restringir y aislar.

La corrección de raíz no ejecuta: analiza el texto con `ast.parse` y recorre el árbol aceptando solo números, operaciones aritméticas, signo y paréntesis. Es una **lista blanca**: se enumera lo permitido y todo lo demás se rechaza. Excluyo la potencia (`**`) a propósito porque `9**9**9` es aritmética válida y bloquearía la CPU (CWE-400), y pongo un límite de longitud por la misma razón. Una regla estática que marque `eval` o `exec` nuevos dificulta que el defecto reaparezca.

## Caso: contenedor sin endurecer

La versión habitual lanza el contenedor con las opciones por defecto: el proceso es root dentro, puede escribir en todo su sistema de ficheros, conserva capacidades amplias, tiene red y no tiene límites. Si la aplicación tiene un defecto, todo ese poder queda a disposición de quien lo aproveche.

La versión endurecida cierra cada puerta con una opción:

```bash
docker run --user 10001:10001 --read-only --tmpfs /tmp \
  --cap-drop ALL --security-opt no-new-privileges \
  --pids-limit 100 --memory 256m mi-aplicacion
```

`--user` evita root incluso dentro; `--read-only` deja la raíz en solo lectura y `--tmpfs /tmp` ofrece el único lugar escribible; `--cap-drop ALL` quita las capacidades; `--security-opt no-new-privileges` impide ganar privilegios; `--pids-limit` y `--memory` ponen techo a procesos y memoria. `--network none` elimina la red cuando el servicio no la necesita. No todas las aplicaciones aguantan todo, y el método es partir de lo más cerrado y abrir solo lo que la aplicación demuestre necesitar.

La verificación no consiste en confiar en lo escrito: conviene leer la configuración real con `docker inspect` y comprobar usuario, sistema de ficheros, capacidades, privilegios, red, procesos, memoria y puntos de montaje. Una comprobación que devuelve 0 si cumple y 1 si no puede usarse como puerta en un pipeline.

Hay configuraciones que anulan el aislamiento y aparecen en tutoriales sin advertencia: `--privileged`, montar el socket de Docker dentro del contenedor o montar directorios del anfitrión con permiso de escritura. Se buscan en la revisión de configuraciones y en los escaneos de infraestructura como código.

## Comparativa

| Lenguaje | Memoria | Tipado | Frontera de ejecución | Riesgos que quedan |
|---|---|---|---|---|
| C | Sin comprobación | Estático, con conversiones implícitas | Ninguna propia | Corrupción de memoria, enteros |
| Java | Gestionada | Estático, fuerte | JVM; SecurityManager retirado | Inyección, deserialización, enteros, nulos |
| Kotlin | Gestionada (JVM) | Estático, fuerte, nulos en el tipo | JVM / ART | Los del entorno |
| Python | Gestionada | Dinámico, fuerte | Ninguna propia | `eval`/`exec`, `pickle`, inyección |
| JavaScript | Gestionada | Dinámico, débil | El navegador; Node.js sin ninguna propia | XSS, inyección, dependencias |
| Go | Gestionada | Estático, fuerte | Ninguna propia | Condiciones de carrera, inyección |
| Rust | Segura sin recolector | Estático, fuerte | Ninguna propia | Lógica, bloques `unsafe` |

«Ninguna propia» no significa que el lenguaje sea un defecto: significa que el aislamiento se pide al sistema, igual que en Java hoy. La columna de riesgos es la que hay que leer con más atención: son los defectos que ningún lenguaje evita. Incluso Rust, con la mejor garantía de memoria, permite una inyección SQL.

Una elección se razona con el caso. Para un servicio que analiza ficheros subidos por clientes conviene un lenguaje de memoria segura, ejecutar el análisis en un proceso con el mínimo privilegio dentro de un contenedor endurecido, con límites de memoria y tiempo, y probarlo con entradas malformadas. La elección final depende también de lo que sabe el equipo.

## Errores frecuentes

- «Python o Java son seguros porque gestionan la memoria»: gestionan la memoria, no la lógica.
- «Restringir es lo mismo que aislar»: el caso de `eval` con `builtins` vacíos lo desmiente.
- «Java tiene sandbox con el SecurityManager»: ya no se puede contar con él.
- «Un contenedor es una máquina virtual ligera»: comparte el núcleo y depende de la configuración.
- «Si el contenedor corre como root dentro, no pasa nada»: es el razonamiento que deja la configuración por defecto.
- «Con una lista de palabras prohibidas bloqueo el ataque»: una lista negra siempre es incompleta.

## Glosario

| Término | Definición |
|---|---|
| AddressSanitizer | Compilador instrumentado que detecta accesos inválidos a memoria. |
| ASLR | Aleatorización de las direcciones de memoria de un proceso. |
| cgroup | Grupo de control que limita los recursos de un proceso. |
| Namespace | Espacio de nombres que separa lo que un proceso ve. |
| seccomp | Filtro de llamadas al sistema. |
| Lista blanca | Enumerar lo permitido y rechazar todo lo demás. |

## Fuentes

- ISO/IEC 9899, estándar del lenguaje C, y documentación de AddressSanitizer.
- Oracle. *Java Language Specification*; JEP 411 y JEP 486.
- Documentación de Python sobre `eval()` y `exec()`.
- NIST SP 800-190 y documentación de Docker sobre aislamiento.
- MITRE. *CWE-94*, *CWE-95*, *CWE-400* y *CWE-502*.
