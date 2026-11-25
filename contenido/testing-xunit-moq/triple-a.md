# Triple A: preparar, actuar y afirmar

Toda prueba tiene la misma estructura mínima: se coloca el mundo en un estado conocido, se ejecuta la pieza que se quiere comprobar y se verifica que el resultado es el esperado. El patrón se conoce como *triple A* por las iniciales en inglés de *Arrange*, *Act* y *Assert*. Es tan simple que parece trivial, y precisamente por eso se rompe con facilidad.

## Las tres fases

**Arrange** construye el escenario: los datos de entrada, los colaboradores, el estado previo. **Act** ejecuta exactamente una acción sobre el código que se prueba. **Assert** compara el resultado con el esperado y falla con un mensaje útil si no coincide.

```csharp
public static class UtilidadesMatematicas
{
    public static int Sumar(int a, int b) => a + b;
}

public class UtilidadesMatematicasTests
{
    [Fact]
    public void Sumar_Devuelve5_CuandoSuma2y3()
    {
        // Arrange
        const int a = 2;
        const int b = 3;

        // Act
        var resultado = UtilidadesMatematicas.Sumar(a, b);

        // Assert
        Assert.Equal(5, resultado);
    }
}
```

Las tres fases pueden ocupar una línea cada una. Si el *Arrange* necesita treinta líneas, suele ser una señal de que la clase tiene demasiadas dependencias o de que el caso se puede simplificar.

## Una acción por prueba

El *Act* debe ser una sola llamada. Dos llamadas seguidas convierten la prueba en dos pruebas cosidas: si falla, no se sabe cuál de las dos produjo el resultado, y si la primera tiene efectos, la segunda ya no parte del escenario que se describió.

```csharp
// Mal: dos acciones y una afirmación que depende de ambas.
var carrito = new Carrito();
carrito.Agregar(new Articulo("A", 10));
carrito.Agregar(new Articulo("B", 20));
Assert.Equal(30, carrito.Total);
```

```csharp
// Bien: el escenario se prepara entero y se comprueba una sola operación.
var carrito = new Carrito();
carrito.Agregar(new Articulo("A", 10));
carrito.Agregar(new Articulo("B", 20));

var total = carrito.CalcularTotal();

Assert.Equal(30, total);
```

En el segundo caso, las dos llamadas a `Agregar` forman parte de la preparación; lo que se está probando es el cálculo. La distinción no es gramatical: separa lo que se da por supuesto de lo que se quiere verificar.

## Nombre y propósito

El nombre de la prueba debe decir qué se comprueba y en qué condición. Una convención extendida es `Metodo_ResultadoEsperado_Condicion`:

```csharp
[Fact]
public void Dividir_LanzaDivideByZeroException_CuandoDivisorEsCero() { }

[Fact]
public void EsPar_DevuelveFalse_CuandoNumeroEsImpar() { }
```

El nombre aparece en el informe cuando la prueba falla. Un `Test1` obliga a abrir el código para saber qué se rompió; un nombre descriptivo ahorra ese viaje. También sirve para detectar huecos: si no se puede nombrar la condición, probablemente no se sabe qué se está probando.

## Afirmar lo que importa

La fase *Assert* debe comprobar el resultado observable, no la implementación. Si el método devuelve un total, se afirma sobre el total; no sobre cuántas veces se llamó a un colaborador interno, salvo que esa interacción sea el contrato.

```csharp
[Fact]
public void CalcularTotal_AplicaIvaDel21PorCiento()
{
    var linea = new LineaFactura(precio: 100m, cantidad: 1);
    var factura = new Factura(new[] { linea }, iva: 0.21m);

    var total = factura.CalcularTotal();

    Assert.Equal(121m, total);
}
```

Los decimales de dinero se comparan con `decimal`, no con `double`, y con una tolerancia cuando el cálculo lo justifica. `Assert.Equal` sobre `double` sin tolerancia produce fallos por representación binaria que no tienen nada que ver con la regla de negocio.

## Casos límite y errores

Un camino feliz no basta. Cada bifurcación del código —un `if`, un `switch`, un operador ternario, un `??`— duplica los estados posibles. Algunos casos que suelen olvidarse:

- El valor cero y el valor negativo.
- La colección vacía y la colección con un solo elemento.
- La cadena vacía, la cadena con espacios y la cadena nula.
- El límite del rango: el último día del mes, el máximo de un tipo, el índice final.
- La excepción esperada, comprobando el tipo y no solo que «algo falló».

```csharp
[Fact]
public void Dividir_LanzaExcepcion_CuandoDivisorEsCero()
{
    Action act = () => UtilidadesMatematicas.Dividir(10, 0);

    Assert.Throws<DivideByZeroException>(act);
}
```

## Errores frecuentes

**Preparar dentro del assert.** Un `Assert.Equal(3, Sumar(1, 2))` mezcla las tres fases: no se ve qué se está probando ni se puede reutilizar el escenario. No es un fallo grave en un caso trivial, pero se vuelve ilegible cuando el escenario crece.

**Lógica en la prueba.** Bucles, condicionales y cálculos paralelos al código de producción convierten la prueba en un segundo programa que también puede estar mal. Los datos deben ser literales siempre que se pueda.

**Depender del orden.** Una prueba que necesita que otra se ejecute antes no es una prueba, es una secuencia con suerte. Cada prueba debe crear su propio estado.

**Esperar con `Thread.Sleep`.** Introduce tiempo muerto y sigue siendo frágil. Para operaciones asíncronas se espera la `Task`; para condiciones que tardan, se usa un sondeo con límite o se rediseña el código para exponer un punto de sincronización.

**Afirmar varias cosas sin relación.** Si la prueba comprueba el total, el IVA y el número de líneas, cuando falla no se sabe cuál de las tres reglas se rompió. Varias afirmaciones sobre el mismo resultado son aceptables; varias sobre resultados independientes, no.

## La prueba como documentación

Una prueba bien escrita se lee como un ejemplo de uso. Muestra qué necesita la clase para funcionar, qué devuelve y qué considera un error. En un proyecto sin documentación actualizada, esa es a menudo la única descripción fiable del comportamiento.

Por eso conviene escribir primero el caso que duele —el que representa la regla que se acaba de discutir— y dejar los casos triviales para después. La suite crece alrededor de las decisiones, no alrededor de las líneas.
