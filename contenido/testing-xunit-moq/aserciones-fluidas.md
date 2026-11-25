# Aserciones

Una aserción es una comprobación que lanza una excepción cuando no se cumple. El runner captura esa excepción, marca la prueba como fallida y muestra el mensaje. Todo lo demás —la biblioteca, la sintaxis, el mensaje— existe para que ese fallo sea fácil de entender.

## Las aserciones de xUnit

xUnit incluye un conjunto suficiente para la mayoría de los casos:

| Aserción | Comprueba |
|---|---|
| `Equal` / `NotEqual` | Igualdad de valor |
| `Same` / `NotSame` | Identidad de referencia |
| `True` / `False` | Valor booleano |
| `Null` / `NotNull` | Referencia nula |
| `Contains` / `DoesNotContain` | Pertenencia en una colección o cadena |
| `Empty` / `NotEmpty` | Colección vacía |
| `InRange` / `NotInRange` | Rango inclusivo |
| `IsType<T>` / `IsAssignableFrom<T>` | Tipo exacto o compatible |
| `Throws<T>` / `ThrowsAsync<T>` | Excepción esperada |
| `Record.Exception` | Captura sin afirmar, para inspeccionar después |

```csharp
[Fact]
public void CrearPedido_DevuelvePedidoVacio()
{
    var pedido = Pedido.Crear("A-1");

    Assert.Equal("A-1", pedido.Numero);
    Assert.Empty(pedido.Lineas);
    Assert.NotNull(pedido.CreadoEn);
}
```

`Assert.Equal` sobre colecciones compara elemento a elemento. Sobre `double` conviene usar la sobrecarga con tolerancia:

```csharp
Assert.Equal(0.3, 0.1 + 0.2, precision: 10);
```

Sin tolerancia, la representación binaria del `double` produce diferencias que no tienen relación con la regla que se prueba.

## Excepciones

Comprobar que un código lanza la excepción correcta es tan importante como comprobar el resultado:

```csharp
[Fact]
public void Retirar_MasQueElSaldo_LanzaInvalidOperationException()
{
    var cuenta = new Cuenta(saldo: 50m);

    Action retirar = () => cuenta.Retirar(100m);

    var excepcion = Assert.Throws<InvalidOperationException>(retirar);
    Assert.Contains("saldo", excepcion.Message, StringComparison.OrdinalIgnoreCase);
}
```

`Assert.Throws<T>` exige el tipo exacto; `Assert.ThrowsAny<T>` acepta derivados. En código asíncrono se usa `await Assert.ThrowsAsync<T>(...)`. Afirmar solo que «se lanzó una excepción» deja pasar errores de tipo que el consumidor no espera.

## Aserciones fluidas

FluentAssertions es una biblioteca que sustituye `Assert.X(...)` por una cadena que se lee de izquierda a derecha: el sujeto, `Should()`, la expectativa.

```csharp
resultado.Should().Be(121m);
pedido.Lineas.Should().HaveCount(2);
cliente.Should().BeEquivalentTo(esperado);
```

La ganancia no es solo estética. `BeEquivalentTo` compara grafos de objetos por propiedades, sin exigir que sean la misma instancia ni que implementen igualdad estructural; `HaveCount` produce un mensaje que dice cuántos elementos había y cuántos se esperaban; `WithMessage` permite afirmar el texto de una excepción con comodines.

```csharp
Action retirar = () => cuenta.Retirar(100m);

retirar.Should().Throw<InvalidOperationException>()
    .WithMessage("*saldo*");
```

Las colecciones tienen un vocabulario amplio: `Contain`, `ContainInOrder`, `BeInAscendingOrder`, `OnlyHaveUniqueItems`, `SatisfyRespectively`. Los diccionarios añaden `ContainKey`, `ContainValue` y `Contain(key, value)`. Las fechas se construyen con extensiones legibles:

```csharp
var fecha = 1.January(2026).At(10, 30);
fecha.Should().BeAfter(1.January(2026));
```

Los eventos se afirman con `Monitor()`:

```csharp
using var monitor = sensor.Monitor();

sensor.Actualizar(21.5);

monitor.Should().Raise(nameof(Sensor.Cambio))
    .WithSender(sensor)
    .WithArgs<double>(valor => valor > 20);
```

Cada aserción admite un motivo al final, que se añade al mensaje de fallo:

```csharp
total.Should().Be(121m, "el IVA general es del 21 %");
```

Ese texto es útil cuando la prueba falla meses después y quien la lee no conoce la regla.

## Licencia: comprobar antes de adoptar

FluentAssertions fue gratuita durante años, pero desde la versión 8 se distribuye con una licencia comercial de Xceed: es gratuita para proyectos de código abierto y uso no comercial, y requiere licencia de pago en uso comercial. No es un detalle menor en una empresa. Antes de introducirla conviene revisar las condiciones vigentes y, si no encajan, valorar alternativas:

- **Shouldly**: sintaxis fluida, licencia permisiva.
- **AwesomeAssertions**: bifurcación de FluentAssertions mantenida por la comunidad con licencia libre.
- **Assert de xUnit**: suficiente para la mayoría de los casos, sin dependencia extra.

La decisión se toma una vez por proyecto y se documenta. Mezclar estilos de aserción en la misma suite complica la lectura sin aportar nada.

## Qué afirmar y qué no

Una aserción debe comprobar el contrato observable:

- El valor devuelto.
- El estado del objeto después de la operación.
- La excepción y su condición.
- La interacción con un colaborador, solo cuando esa interacción sea el contrato (un correo enviado, un evento publicado).

No debe comprobar detalles internos que pueden cambiar sin alterar el comportamiento: el orden de llamadas a métodos privados, el número exacto de consultas o la estructura de una colección intermedia. Esas afirmaciones convierten cualquier refactorización en una tarea de arreglo de pruebas.

Tampoco conviene acumular aserciones independientes en una sola prueba. Si el total, el IVA y el descuento pueden fallar por separado, son tres pruebas. Cuando falla una sola, el mensaje ya dice qué regla se rompió; cuando fallan tres juntas, hay que abrir el código para saber por dónde empezar.
