# Java y ejecución real

Java me obliga a mirar dos veces el mismo programa. La primera veo el texto que escribe una persona; la segunda, un archivo intermedio que ejecuta una máquina virtual. Entre ambas hay un compilador que comprueba tipos y una JVM que verifica lo que recibe. Esa separación, que en Python casi no se nota, deja rastro en disco y permite observar el programa desde fuera.

Me interesa por dos razones. Como administrador, porque un servicio Java es un proceso más y se puede medir con las herramientas del sistema. Como revisor, porque el artefacto compilado se puede abrir, y lo que se abre deja de ser secreto.

## Del `.java` al proceso

El recorrido es corto y conviene fijarlo:

1. `javac` comprueba sintaxis y tipos y genera un `.class` por clase con **bytecode**.
2. `java` localiza la clase, la carga y **verifica** que el bytecode sea coherente: tipos de la pila, variables inicializadas y destinos de salto válidos.
3. La JVM empieza interpretando y compila con **JIT** los métodos que se repiten.

El archivo `.class` empieza por los bytes `ca fe ba be` e incluye una versión de formato. Un bytecode compilado con un JDK reciente puede ser rechazado por una JVM antigua. A cambio, es portable entre sistemas que tengan JVM, y es lo que viaja dentro de un `.jar`, que no es más que un ZIP con clases y metadatos.

El JDK incluye compilador y herramientas (`javac`, `java`, `jar`, `javap`, `jcmd`). En producción suele bastar el entorno de ejecución, lo que reduce lo que hay que actualizar.

## La forma de un programa

Todo programa Java se organiza en clases y arranca en `public static void main(String[] args)`. La firma importa: `public` permite la llamada, `static` evita crear un objeto, `void` dice que no devuelve nada y `String[] args` recibe los argumentos, como `sys.argv` en Python.

Los tipos se declaran y el compilador los exige. Las llaves agrupan bloques, el punto y coma cierra instrucciones y la sangría solo ayuda a leer. Las colecciones pueden llevar genéricos (`List<Servidor>`, `Map<Integer, String>`) para que el compilador conozca su contenido. Un `record` agrupa campos inmutables con constructor y métodos de lectura generados.

Dos trampas al leer código ajeno: para comparar textos se usa `equals`, no `==` (con objetos, `==` compara referencias), y una variable que guarda un objeto no lo contiene: guarda una referencia, de modo que dos variables pueden apuntar al mismo objeto.

## Lo que el compilador no ve

El tipado estático detecta antes de ejecutar una llamada con el tipo equivocado. Python descubre ese fallo solo si la ejecución pasa por la línea. Pero ningún compilador valida el significado del dato.

Un `int` de Java ocupa 32 bits y su máximo es 2 147 483 647. Si una multiplicación lo supera, el resultado da la vuelta sin lanzar excepción. Supongamos un pedido de 3 000 000 unidades a 1 000 céntimos: la operación en `int` devuelve `-1294967296`, un importe negativo que podría convertirse en un abono. El defecto combina dos causas: el desbordamiento (CWE-190) y la ausencia de un límite de negocio.

La corrección valida el rango de unidades y de precio y calcula con `long` mediante `Math.multiplyExact`, que lanza una excepción si el resultado no cabe. Prefiero un error visible a un importe falso. El identificador CWE conviene contrastarlo con la lista vigente antes de citarlo en un informe.

## Pila, montón y recolector

Cada llamada a un método reserva en la **pila** un marco con parámetros y variables locales, que se libera al terminar. Si una recursión no tiene condición de parada, la pila se llena y Java lanza `StackOverflowError`. La defensa no es ampliar la pila, sino limitar la profundidad cuando la estructura la controla quien envía los datos.

Los objetos viven en el **montón** y la variable guarda una referencia. Devolver una colección interna permite modificarla sin pasar por ninguna validación; por eso se devuelve una copia o una vista inmutable. El recolector libera objetos inalcanzables y elimina el `free`, la doble liberación y el uso después de liberar. También comprueba los límites de los arrays y lanza una excepción en lugar de leer memoria ajena.

Eso no cierra todos los riesgos. Quedan el agotamiento de memoria, las fugas lógicas por referencias que se mantienen vivas y los datos sensibles que permanecen en el montón. Una contraseña guardada en un `String` sigue ahí hasta que el recolector decide recogerla, y no puedo forzarlo.

## El proceso visto desde fuera

El sistema operativo no ve clases ni bytecode: ve un proceso llamado `java`. Lo compruebo con `ps`, con `/proc/PID/status`, con `/proc/PID/maps` y con `jcmd`. Un programa aparentemente inactivo muestra varios hilos —compiladores JIT, recolector, mantenimiento de la máquina virtual— y una diferencia enorme entre memoria virtual (`VmSize`) y residente (`VmRSS`).

Para dimensionar un servidor o un contenedor importa la residente y el límite `-Xmx`, no la virtual. El proceso carga bibliotecas compartidas como `libjvm.so`, `libc`, `libm` y `libz`. Una vulnerabilidad en cualquiera de ellas afecta también a Java, aunque el código sea correcto: actualizar el servidor incluye las bibliotecas del sistema, no solo las dependencias del lenguaje.

La JVM no es una frontera frente al sistema operativo. El programa se ejecuta con los permisos del usuario que lo lanza, y por eso los servicios van con usuarios sin privilegios y en entornos aislados.

## El artefacto habla

Quien recibe un `.class` o un `.jar` puede inspeccionarlo. `javap -c -p` muestra el bytecode, `javap -v` la tabla de constantes y `strings` localiza cadenas legibles. Un secreto escrito en el código aparece como texto, como argumento de una instrucción `ldc` y en la tabla de constantes. Es CWE-798, credenciales incrustadas.

La corrección es sacar el secreto del código y leerlo del entorno, negándose a arrancar si falta. Además, la clave publicada debe considerarse comprometida y cambiarse: borrarla de la versión nueva no la retira de las copias que ya circulan. El entorno tampoco es una caja fuerte; `/proc/PID/environ` lo puede leer el mismo usuario y `root`, y pasar la clave como argumento la deja visible en la lista de procesos.

## Leer decisiones, no solo líneas

Un generador de cupones con `java.util.Random` ilustra el límite de las pruebas. `Random` sirve para fines generales, pero no para valores que deben ser impredecibles: su secuencia depende del estado interno y dos instancias con la misma semilla producen el mismo resultado. Es CWE-338.

Una batería que ejecute el generador muchas veces no detecta el problema, porque cada cupón parece aleatorio. Se detecta leyendo el código o con análisis estático. La corrección es `java.security.SecureRandom`, que obtiene entropía del sistema operativo. La prueba de regresión solo confirma que ya no se depende de una semilla reproducible; no demuestra impredecibilidad.

El ciclo completo, desde el hallazgo hasta la prueba que evita la recaída, está en [Pruebas de software](pruebas-de-software.md).

Un cupón de 8 caracteres sobre un alfabeto de 32 tiene unos 40 bits de entropía. Puede bastar para un uso único con control de intentos y caducidad, e insuficiente para proteger algo valioso sin esas medidas. La longitud es una decisión de riesgo, no un dogma.

## Kotlin, de pasada

Kotlin se compila a bytecode de la JVM y es común en Android. Su diferencia más visible para la seguridad es el tratamiento de los nulos: `String?` declara que un valor puede ser nulo y `String` que no, y el compilador obliga a decidir antes de usarlo. Reduce una familia de fallos (CWE-476), pero no evita desbordamientos, secretos incrustados ni generadores predecibles. Al llamar a código Java, las garantías se relajan.

## Comparativa

| Aspecto | Python | Java | C |
|---|---|---|---|
| Qué se distribuye | Código fuente | Bytecode (`.class`, `.jar`) | Binario nativo |
| Ejecución | Intérprete | JVM con verificación y JIT | Procesador |
| Tipado | Dinámico | Estático | Estático |
| Memoria | Gestionada | Gestionada | Manual |
| Enteros | Precisión arbitraria | Tamaño fijo, desbordamiento silencioso | Tamaño fijo, comportamiento indefinido con signo |

Ningún lenguaje es seguro en abstracto. Cada uno retira ciertas familias de errores y deja otras al programador. La diferencia entre Python y Java no es la seguridad, sino dónde y cuándo se detecta el fallo.

## Antes de ejecutar un artefacto ajeno

1. Compruebo versiones con `java -version` y `javac -version`.
2. Reviso importaciones, punto de entrada y origen de los datos.
3. Inspecciono el `.class` o el `.jar` con `javap` y `strings`.
4. Lo ejecuto con un usuario sin privilegios, sin datos reales y en un entorno aislado.
5. Miro el proceso con `ps`, `/proc` y `jcmd`: hilos, memoria y bibliotecas.

## Glosario

| Término | Definición |
|---|---|
| Bytecode | Representación intermedia que ejecuta una máquina virtual. |
| JIT | Compilación a código máquina durante la ejecución. |
| JVM | Máquina virtual que carga, verifica y ejecuta bytecode de Java. |
| Pila | Zona de memoria para marcos de llamada y variables locales. |
| Montón | Zona donde residen los objetos y sus referencias. |
| JAR | Archivo ZIP con clases y metadatos de una aplicación Java. |

## Fuentes

- Oracle. *Java Language Specification* y *Java Virtual Machine Specification*.
- Documentación oficial de `java.util.Random`, `java.security.SecureRandom`, `javap`, `jcmd` y `jps`.
- MITRE. *CWE-190* y *CWE-338*.
