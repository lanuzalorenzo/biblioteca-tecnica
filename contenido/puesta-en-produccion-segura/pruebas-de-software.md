# Pruebas de software

Probar se parece a ensayar una evacuación: no cubre todos los incendios posibles, pero revela si la ruta, las señales y el recuento funcionan cuando hacen falta. El ensayo no demuestra que el edificio sea seguro; demuestra que el plan que ya tenía funciona en el escenario que he elegido. Elegir bien el escenario es casi todo el trabajo.

Me interesa la disciplina por dos motivos. El primero es funcional: una prueba que falla señala dónde mirar. El segundo es de seguridad: una vulnerabilidad corregida sin prueba vuelve con la siguiente refactorización. Aquí recojo cómo elijo casos, qué mide cada técnica y cómo convierto un hallazgo en algo que no se rompa en silencio. La teoría general de pruebas y los dobles tienen su módulo en [Testing de aplicaciones .NET con xUnit y Moq](../testing-xunit-moq/README.md); aquí resumo lo que necesito para leer una revisión y me quedo con el paso del hallazgo a la regresión.

## Error, defecto y fallo

Los tres términos se usan como sinónimos y no lo son:

- El **error** es la equivocación de una persona.
- El **defecto** es su huella en el código.
- El **fallo** es el comportamiento incorrecto que se observa al ejecutar.

Si escribo `> 10` donde debía poner `>= 10`, el defecto es el operador y el fallo aparece solo cuando alguien compra exactamente diez unidades. Mientras nadie lo haga, el programa parece correcto. Esa es la razón de que los casos no se elijan al azar. El desbordamiento de un pedido que describo en [Java y ejecución real](java-y-ejecucion-real.md) es otro defecto que solo aparece con una entrada concreta.

También distingo **verificación** de **validación**: verificar es comprobar que el producto cumple su especificación; validar, que es el producto que se necesita. Una función que calcula con precisión un descuento que nadie pidió pasa la verificación y falla la validación. En seguridad, los requisitos casi nunca los formula el cliente, así que si el equipo no los deriva de un estándar, ninguna prueba de negocio los va a reclamar.

## Qué necesita una prueba para servir

Toda prueba necesita un **oráculo**: una especificación, un resultado calculado a mano o una propiedad que deba cumplirse siempre. Sin oráculo no hay prueba, solo una ejecución que alguien tiene que juzgar.

Además, una prueba automatizada útil es rápida, determinista, independiente de las demás y legible cuando falla. Una prueba que a veces pasa y a veces falla se llama inestable (*flaky*) y entrena al equipo a ignorar los avisos en rojo. Una prueba que depende del orden de ejecución esconde fallos en lugar de encontrarlos.

## Cuatro ejes, no una jerarquía

Una misma prueba puede ser unitaria, de caja blanca, funcional, de regresión y automatizada a la vez. En lugar de buscarle una etiqueta, le hago cuatro preguntas independientes:

| Pregunta | Tipos | Idea esencial |
|---|---|---|
| ¿Qué parte ejercita? | Unitaria, integración, sistema, aceptación | De la función aislada al producto completo |
| ¿Cuánto conoce quien prueba? | Caja negra, blanca, gris | La interfaz, el código interno o ambos |
| ¿Qué comprueba? | Funcional, no funcional, regresión, humo | Qué hace, cómo lo hace, que no se rompió, que arranca |
| ¿Cómo se ejecuta? | Estática o dinámica; manual o automatizada | Sin ejecutar o ejecutando; a mano o con un programa |

Los niveles funcionan como un zoom. La prueba unitaria aísla una pieza y localiza el fallo con precisión; la de integración comprueba las costuras; la de sistema ejecuta el producto completo en un entorno parecido al real; la de aceptación la define quien encarga el producto. La pirámide recomienda muchas unitarias, menos de integración y muy pocas de sistema, porque cuanto más arriba, más lentas, frágiles y caras de diagnosticar.

## La prueba unitaria

Una prueba unitaria suele tener tres tiempos: organizar el escenario, actuar una vez y comprobar el resultado. Si necesita comprobar diez cosas distintas, probablemente sean diez pruebas. El nombre de la que falla debe decir qué se rompió.

En Python, pytest descubre archivos `test_*.py` y funciones que empiezan por `test_`, y usa el `assert` normal del lenguaje. `pytest.mark.parametrize` ejecuta la misma prueba con varios datos y los cuenta por separado; las fixtures y `tmp_path` preparan y limpian el escenario. En Java, JUnit 5 anota los métodos con `@Test` y comprueba con `assertEquals`, `assertThrows` y similares. La diferencia de estilo es pequeña: en Python la prueba es una función y se descubre por su nombre; en Java es un método y se descubre por su anotación.

Cuando la unidad depende de la hora, la red o una base de datos, uso dobles de prueba. Un *stub* devuelve respuestas preparadas, un *fake* es una implementación simplificada pero funcional y un *mock* registra cómo se le ha llamado. La prueba no llama a servicios de terceros ni usa credenciales verdaderas: si necesita un secreto, le doy uno falso.

## Elegir los casos

No puedo probar todas las entradas posibles. La **partición de equivalencia** divide el dominio en grupos donde el programa debe comportarse igual y elige un representante de cada uno. El **análisis de valores límite** añade los bordes y sus vecinos, porque ahí se concentran los errores de `<` frente a `<=`.

Con un descuento por volumen, las particiones serían menos de 1 unidad, de 1 a 9, de 10 a 49, de 50 a 99 y 100 o más, además de los valores que no son enteros. Los límites que hay que probar son 9 y 10, 49 y 50, 99 y 100.

Una versión defectuosa con `>` en las tres condiciones lo ilustra. Las pruebas con un valor representativo de cada tramo pasan todas, porque 5, 25, 75 y 500 quedan lejos de los bordes. Fallan exactamente las de 10, 50 y 100. Un conjunto de pruebas puede estar en verde y no haber probado lo único que importaba. El desfase de una unidad es CWE-193 y, si el límite protege un tamaño de búfer o un número de intentos, se convierte en una brecha.

## Cobertura y mutación

La cobertura de líneas cuenta qué instrucciones se ejecutaron; la de ramas exige que cada decisión se haya evaluado como verdadera y como falsa. Es más exigente y es la que conviene pedir. En Python se mide con `coverage.py` alrededor de pytest; en Java, la herramienta habitual es JaCoCo.

El límite se ve con un ejemplo. Una prueba que llama a una función con tres entradas y no comprueba ningún resultado ejecuta todas las líneas y todas las ramas: cobertura del 100 %. Y no detecta nada; si cambio `>=` por `>` o devuelvo siempre el mismo valor, sigue en verde. La cobertura dice qué código se ejecutó, no qué comportamiento se comprobó.

La **prueba de mutación** genera versiones ligeramente rotas del código y comprueba si alguna prueba falla. Un mutante que hace fallar la batería está muerto; el que sobrevive delata una prueba que no comprueba lo que debiera. La cobertura sirve en un sentido: una zona al 0 % es una zona que nadie ha probado. Un porcentaje alto, en cambio, no garantiza nada.

## Integración, sistema y aceptación

Las pruebas unitarias aseguran que cada pieza funciona sola; las de integración comprueban las costuras, que es donde aparecen muchos fallos de seguridad. Sustituir la base de datos por un objeto falso no detecta una consulta mal construida, porque la consulta nunca llega a ejecutarse. SQLite en memoria es un *fake* útil: ejecuta SQL de verdad, no necesita instalación ni red y desaparece al cerrar la conexión.

Un módulo que busca usuarios concatenando el nombre en la consulta lo muestra. Las pruebas del camino normal pasan; falla la de un apellido con apóstrofo, como `o'brien`, porque la comilla del dato cierra la cadena. El mismo defecto es un fallo funcional para el usuario honrado y una inyección SQL (CWE-89) para quien no lo es. La corrección es una consulta parametrizada, que mantiene separados instrucción y dato.

Las pruebas de sistema tratan la aplicación como una caja negra completa y se reservan para recorridos críticos: acceso, pago, recuperación de contraseña. Las de aceptación responden a si es lo que se pidió y pueden incluir criterios de seguridad, como el bloqueo tras cinco intentos fallidos. Las no funcionales miden rendimiento, carga o resistencia, y conectan con seguridad porque un servicio que no aguanta una carga normal tampoco aguantará una hostil.

## Estáticas, propiedades y fuzzing

Las pruebas estáticas examinan sin ejecutar: revisión por pares, avisos del compilador, verificación de tipos con `mypy` y analizadores de seguridad (SAST) como Semgrep o SonarQube. Encuentran defectos sin montar el entorno, pero producen falsos positivos y no ven lo que solo ocurre en ejecución.

Las dinámicas ejecutan y observan. La prueba basada en propiedades sustituye ejemplos por una regla que debe cumplirse para cualquier entrada y una herramienta genera casos para intentar romperla; en Python, Hypothesis es la biblioteca habitual. El *fuzzing* lleva la idea al extremo: alimenta el programa con entradas malformadas y vigila cierres y consumos anómalos. Es rentable con analizadores de formatos y con código de memoria insegura. La frontera con un ataque es el objetivo: se ejecuta sobre código propio, en un entorno aislado y para corregirlo.

## Del hallazgo a la regresión

Una vulnerabilidad corregida sin prueba vuelve a aparecer: alguien refactoriza, otro dependiente reescribe o una fusión recupera el código antiguo. El procedimiento tiene seis pasos y conviene convertirlo en hábito:

1. **Hallazgo.** Describir qué entrada produce qué comportamiento inaceptable.
2. **Causa raíz.** Localizar el defecto y clasificarlo, por ejemplo con un identificador CWE.
3. **Prueba que falla.** Expresar el comportamiento correcto y comprobar que falla con el código actual.
4. **Corrección.** Cambiar lo mínimo imprescindible.
5. **Verificación.** Ejecutar la prueba y toda la batería para comprobar que no se rompió nada más.
6. **Integración.** Dejar la prueba en el repositorio y ejecutarla en cada cambio.

En la descarga de adjuntos, la versión vulnerable une el directorio base con el nombre que envía el cliente; nada impide `..` ni una ruta absoluta, y `Path(base) / "/etc/passwd"` ignora la base. Es un recorrido de rutas (CWE-22). Las pruebas fijan primero el comportamiento legítimo y después el prohibido, sin abrir ningún fichero ajeno: solo se calcula la ruta y se examina. La corrección no busca la cadena `..`, que tiene demasiadas formas de escribirse; resuelve la ruta real, sigue los enlaces simbólicos y comprueba que sigue dentro de la base.

Tres detalles separan una buena prueba de seguridad de una mala: prueba el comportamiento y no la implementación, prueba también el camino legítimo —una corrección que rechaza todo cumple las pruebas de abuso y rompe la aplicación— y mantente en lo mínimo. La prueba demuestra que la protección existe; no es un catálogo de cargas útiles. El aislamiento, que es la otra mitad de la defensa, se trata en [Seguridad en lenguajes y entornos de ejecución](sandboxes-y-aislamiento.md).

## Errores frecuentes

- Escribir la prueba después de ver que pasa y no comprobar que antes fallaba.
- Probar solo el camino feliz y no el vacío, el máximo, el negativo, el tipo equivocado o los caracteres especiales.
- Confundir cobertura con calidad.
- Compartir estado entre pruebas, de modo que el orden cambie el resultado.
- Ajustar el valor esperado para que la prueba pase en lugar de corregir el código.
- Probar en producción con datos reales o credenciales verdaderas.

## Glosario

| Término | Definición |
|---|---|
| *Assert* | Comprobación que falla si el resultado no coincide con el esperado. |
| *Fixture* | Preparación y limpieza del escenario de una prueba. |
| *Flaky* | Prueba inestable que no da siempre el mismo resultado. |
| Mutante | Versión del código con un defecto introducido a propósito. |
| Oráculo | Criterio que determina el resultado correcto. |
| SAST | Análisis estático de seguridad sobre el código fuente. |

## Fuentes

- ISTQB. *Glosario de términos de pruebas de software*.
- Documentación oficial de pytest, JUnit 5, JaCoCo y PIT.
- MITRE. *CWE-22*, *CWE-89*, *CWE-190* y *CWE-193*.
