# Fundamentos de programación para administradores de sistemas

Revisar el código de otra persona se parece a inspeccionar la fontanería de una casa que no he construido: no necesito haber soldado cada tubo, pero sí saber de dónde viene el agua, dónde está la llave de paso y qué grifo depende de qué ramal. Con esa orientación puedo detectar una fuga antes de abrir la válvula general.

Como administrador de sistemas no voy a escribir la aplicación, pero sí a decidir si puedo ejecutarla, con qué permisos, qué dependencias arrastra y qué hace con los datos que toca. Para eso necesito entender cómo llega el texto que veo en un editor hasta las instrucciones que ejecuta el procesador, y cómo se recorre un programa desconocido sin perderse en la primera función.

## De la receta a la instrucción

El procesador solo ejecuta instrucciones en código máquina, atadas a una arquitectura concreta. Las personas escribimos en lenguajes de más alto nivel y alguien tiene que salvar la distancia. Esa traducción se hace de tres maneras, y cada una reparte el trabajo en un momento distinto.

| Modelo | Cuándo se traduce | Lo que gano | Lo que pago |
|---|---|---|---|
| Compilación nativa | Antes de ejecutar, a instrucciones de la arquitectura | Rendimiento y errores detectados pronto | Binario dependiente de arquitectura, sistema y bibliotecas |
| Interpretación | Durante la ejecución, instrucción a instrucción | Iteración rápida y código portable | Necesito el intérprete y el código fuente queda a la vista |
| Código intermedio | Antes, a un formato que ejecuta una máquina virtual | Portabilidad del formato y optimización en caliente | Arranque y consumo del entorno virtual |

La tabla ordena conceptos, no productos. En la práctica los modelos se mezclan: una implementación puede compilar a bytecode y después interpretarlo o compilar las partes más usadas con un compilador **JIT** (*Just-In-Time*). Por eso «compilado» e «interpretado» no son etiquetas exclusivas, y conviene preguntar qué se distribuye, no en qué casilla cae el lenguaje.

El código máquina y el ensamblador son el extremo bajo: el ensamblador traduce mnemónicos a instrucciones, pero no ejecuta el programa. El intérprete sí lo hace, o ejecuta una representación intermedia. Un archivo `.class` de Java o un `.pyc` de Python son formatos intermedios: legibles por su entorno, no por el procesador directamente.

## Qué se distribuye y qué implica

Esta distinción tiene consecuencias prácticas para quien despliega:

- Un binario nativo depende de la arquitectura y de las bibliotecas del sistema. Actualizar el servidor puede romperlo aunque el código no haya cambiado.
- Un programa interpretado entrega el código fuente. Si el servicio se ejecuta en un equipo ajeno, ese código se puede leer, copiar y modificar.
- Un artefacto de bytecode se puede inspeccionar con herramientas del propio ecosistema aunque no sea texto. Compilar no oculta secretos.

Elegir un modelo no es una decisión de seguridad por sí sola, pero sí cambia la superficie: qué hay que actualizar, qué se puede auditar y qué queda expuesto en el servidor.

## Anatomía de un programa desconocido

Antes de leer línea a línea, localizo las piezas grandes. Es la diferencia entre abrir un plano y empezar a medir habitaciones al azar.

1. **Importaciones y dependencias.** Me dicen qué capacidades tiene el programa: red, ficheros, procesos, criptografía. Que importe `socket` no lo convierte en malicioso; que lo haga sin que su función lo justifique merece una pregunta.
2. **Punto de entrada.** Es donde arranca la ejecución. En Python suele ser el bloque `if __name__ == "__main__":`; en Java, `main`. Sin localizarlo, las funciones que leo pueden no llegar a ejecutarse nunca.
3. **Variables.** Guardan los valores que se transforman. Me interesa de dónde salen y en qué operación terminan, no cuántas hay.
4. **Funciones.** Agrupan el comportamiento reutilizable. Leo primero las que aparecen en el punto de entrada y salto a las que llaman, en lugar de recorrer el archivo de arriba abajo.

Un programa pequeño se puede leer entero; uno grande no. La lectura por llamadas evita gastar tiempo en código auxiliar que nunca se ejecuta en el caso que estoy revisando.

## Seguir el dato

La técnica que más me sirve es seguir un valor desde que entra hasta que se usa. Para cada dato relevante respondo cuatro preguntas:

- **Origen:** ¿lo escribe una persona, llega por la red, sale de un fichero, de una variable de entorno o de otra función?
- **Transformaciones:** ¿se valida, se normaliza, se codifica, se recorta? ¿Se comprueba el tipo y el rango?
- **Destino:** ¿se muestra en una página, se guarda en una base de datos, se concatena en una consulta, se usa como ruta o se pasa a un comando?
- **Control:** ¿el tratamiento encaja con ese destino y se mantienen los permisos mínimos?

El recorrido señala dónde mirar. No demuestra la vulnerabilidad: un dato sin validar que solo se compara con una constante no es una inyección. La diferencia entre sospecha y hallazgo está en el contexto y en una prueba que lo confirme.

## Un ejemplo mínimo

Un script de comprobación de puertos en la propia máquina sirve para practicar la lectura:

```python
import socket

def puerto_abierto(direccion, puerto):
    with socket.socket() as s:
        s.settimeout(0.5)
        return s.connect_ex((direccion, puerto)) == 0

destino = "127.0.0.1"
for puerto in (22, 80, 443):
    print(puerto, puerto_abierto(destino, puerto))
```

En pocas líneas ya puedo hacer el recorrido completo: la dependencia `socket` aporta capacidad de red; `puerto_abierto` recibe dos datos y devuelve un booleano; `destino` y la tupla de puertos son valores fijos; el bucle llama a la función. La dirección está limitada a la propia máquina, que es lo que hace el ejemplo aceptable. Cambiarla por un dominio ajeno convertiría el mismo código en un escaneo no autorizado. El mismo recorrido sobre un lenguaje compilado, con su artefacto y su proceso, está en [Java y ejecución real](java-y-ejecucion-real.md).

## Compilar no garantiza nada

Un compilador detecta errores de sintaxis y, en lenguajes de tipado estático, incoherencias de tipo. No comprueba la lógica, no valida los rangos de negocio y no impide que un programa correcto haga algo peligroso. Un binario sin errores de compilación puede contener una contraseña incrustada o aceptar una ruta arbitraria.

Por eso la revisión no termina cuando el programa arranca. Empieza ahí: si se ejecuta, ya puedo observar qué procesos lanza, qué ficheros abre, a qué red se conecta y con qué usuario lo hace. Esa observación se apoya en el sistema operativo, que solo ve un proceso, no las abstracciones del lenguaje.

## Antes de ejecutar código ajeno

1. Identifico el lenguaje, el punto de entrada y las dependencias.
2. Anoto las capacidades que aportan las importaciones y las comparo con la función declarada.
3. Sigo los datos de interés desde su origen hasta su destino.
4. Busco lecturas de configuración, rutas, consultas y llamadas al sistema.
5. Ejecuto en un entorno aislado, con un usuario sin privilegios y sin datos reales.
6. Registro lo que observo y separo lo comprobado de lo que supongo.

## Glosario

| Término | Definición |
|---|---|
| AOT | Compilación anticipada, antes de la ejecución. |
| Bytecode | Código intermedio pensado para una máquina virtual. |
| JIT | Compilación a código máquina durante la ejecución. |
| Mnemónico | Nombre simbólico de una instrucción de ensamblador. |
| Punto de entrada | Lugar donde comienza la ejecución del programa. |

## Fuentes

- Python Software Foundation. *Documentación oficial de Python 3*.
- Oracle. *Java Language Specification* y *Java Virtual Machine Specification*.
- ISO/IEC 9899, estándar del lenguaje C.
