# Testing de aplicaciones .NET con xUnit y Moq

Una prueba de código es un programa que comprueba el comportamiento de otro programa. Se escribe una vez y se ejecuta tantas veces como haga falta, de forma que un cambio que rompe algo se detecta en segundos y no en producción. Su valor no está en demostrar que el código funciona hoy, sino en evitar que deje de hacerlo mañana: son la red que atrapa las regresiones.

## Qué se prueba

- **Pruebas unitarias**: comprueban una pieza aislada —una clase, un método— sin base de datos, sin red y sin sistema de archivos. Son rápidas y señalan el fallo con precisión.
- **Pruebas de integración**: comprueban varias piezas juntas, o el código con una dependencia real. Tardan más, pero detectan fallos que la prueba unitaria no ve.
- **Pruebas de extremo a extremo**: recorren la aplicación como lo haría una persona. Son las más lentas y frágiles, y se reservan para los caminos críticos.

Las dependencias externas se sustituyen por dobles de prueba para que la prueba sea rápida y determinista y para poder forzar casos que con el sistema real son difíciles de provocar: un error de red, una respuesta vacía, una excepción.

## El ciclo de una prueba

Toda prueba sigue tres pasos, conocidos como AAA:

- ***Arrange***: se prepara el escenario, con los datos y las dependencias que necesita.
- ***Act***: se ejecuta el código que se quiere probar.
- ***Assert***: se comprueba que el resultado es el esperado.

## Las herramientas

- **xUnit** ejecuta las pruebas y ofrece las aserciones básicas. Los atributos `[Fact]` y `[Theory]` distinguen una prueba suelta de una que se repite con varios juegos de datos.
- **Moq** genera implementaciones falsas de interfaces y clases para inyectarlas en el código bajo prueba.
- **Fluent Assertions** sustituye las aserciones clásicas por una sintaxis encadenada que se lee casi como una frase.
- La **cobertura** mide qué parte del código ejecutan las pruebas, y la **integración continua** las lanza en cada cambio para que el aviso llegue antes de que el fallo se publique.

## Contenido

| Nota | Qué trata |
|---|---|
| [Por qué probar el código](por-que-probar.md) | Regresiones, coste, tipos de prueba y diseño que se deja probar |
| [Triple A](triple-a.md) | Preparar, actuar y afirmar; nombres, casos límite y errores frecuentes |
| [xUnit.net](xunit.md) | Proyecto, descubrimiento, ciclo de vida, salida, paralelismo y filtros |
| [Hechos y teorías](hechos-y-teorias.md) | `Fact`, `Theory`, `InlineData`, `ClassData`, `MemberData` y datos propios |
| [Fixtures y traits](fixtures-y-traits.md) | `IClassFixture`, `ICollectionFixture`, colecciones y categorías |
| [Aserciones](aserciones-fluidas.md) | `Assert`, excepciones, FluentAssertions y su licencia |
| [Dobles de prueba](dobles-de-prueba.md) | Dummy, stub, spy, mock y fake; estado frente a interacción |
| [Mocks con Moq](mocks-con-moq.md) | Configuración, propiedades, eventos, secuencias y verificación |
| [Entity Framework](entity-framework.md) | SQLite en memoria, proveedor InMemory, semillas y EF 6 |
| [HTTP y servicios web](http-y-servicios-web.md) | `HttpMessageHandler`, `WebApplicationFactory` y pruebas de endpoints |
| [Casos difíciles](casos-dificiles.md) | Envoltorios, herencia, reflexión y código heredado |
| [TDD y código heredado](tdd-y-legacy.md) | Rojo, verde, azul; caracterización y refactorización por partes |
| [Cobertura](cobertura.md) | Líneas y ramas, Coverlet, umbrales y límites de la métrica |
| [Integración continua](integracion-continua.md) | Pipeline, entorno reproducible, etapas y pruebas inestables |

## Convenciones

Los ejemplos declaran el tipo de forma explícita cuando aclara la intención y usan `var` cuando el tipo se deduce sin ambigüedad. Los nombres de prueba siguen `Metodo_ResultadoEsperado_Condicion`. Las aserciones se escriben con `Assert` de xUnit en los casos simples y con sintaxis fluida cuando el mensaje de fallo o la comparación lo justifican.
