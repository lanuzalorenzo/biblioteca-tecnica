# Mocks con Moq

Moq crea objetos proxy que implementan una interfaz o heredan de una clase y permiten programar respuestas, registrar llamadas y verificar interacciones. No es la única biblioteca del mercado —NSubstitute y FakeItEasy cubren lo mismo—, pero es la más extendida en .NET y su vocabulario aparece en la mayoría de los proyectos.

```bash
dotnet add package Moq
```

## Crear el mock

```csharp
var repositorio = new Mock<IRepositorioPedidos>();
```

`Mock<T>` es un envoltorio; el objeto que se inyecta en la clase probada está en `Object`:

```csharp
var servicio = new ServicioPedidos(repositorio.Object);
```

El constructor admite un `MockBehavior`:

| Valor | Comportamiento ante un miembro no configurado |
|---|---|
| `Loose` | Devuelve el valor por defecto del tipo; nunca falla |
| `Strict` | Lanza una excepción |
| `Default` | Igual que `Loose` |

`Loose` es cómodo y también peligroso: una prueba que olvida configurar un método recibe `null` o `0` y puede pasar por el camino equivocado. En clases con contrato fuerte, `Strict` convierte ese olvido en un fallo inmediato.

Existe una sintaxis alternativa que devuelve directamente el objeto:

```csharp
IRepositorioPedidos repositorio = Mock.Of<IRepositorioPedidos>();
Mock.Get(repositorio).Setup(r => r.Buscar("A-1")).Returns(new Pedido("A-1"));
```

Es más concisa, pero difumina qué es un mock y qué no. Gana cuando la configuración es trivial y el objeto se pasa a un constructor.

## Configurar llamadas

`Setup` declara una llamada y `Returns` su respuesta:

```csharp
var repositorio = new Mock<IRepositorioPedidos>();
repositorio.Setup(r => r.Buscar("A-1")).Returns(new Pedido("A-1"));
```

Un `Setup` sin `Returns` sirve para métodos `void`; si el método devuelve un valor y no se configura, el mock devuelve el valor por defecto.

Los argumentos se afinan con los comparadores `It`:

```csharp
repositorio.Setup(r => r.Buscar(It.IsAny<string>()))
    .Returns(new Pedido("A-1"));

repositorio.Setup(r => r.Buscar(It.Is<string>(n => n.StartsWith("A-"))))
    .Returns(new Pedido("A-1"));

repositorio.Setup(r => r.Guardar(It.IsAny<Pedido>()));
```

El orden importa: la última configuración que coincide gana. Si se declara primero un `It.IsAny<string>()` y después un valor concreto, el valor concreto debe ir después para tener prioridad. También se puede construir la respuesta a partir del argumento:

```csharp
repositorio.Setup(r => r.Buscar(It.IsAny<string>()))
    .Returns((string numero) => new Pedido(numero));
```

## Callback, excepciones y código real

`Callback` ejecuta una acción cuando la llamada ocurre; `Throws` lanza una excepción; `CallBase` delega en la implementación real de una clase:

```csharp
var contador = 0;
repositorio.Setup(r => r.Guardar(It.IsAny<Pedido>()))
    .Callback(() => contador++);

repositorio.Setup(r => r.Buscar("A-1"))
    .Throws<InvalidOperationException>();

repositorio.Setup(r => r.Buscar("A-1"))
    .Throws(new InvalidOperationException("pedido bloqueado"));
```

`Throws<T>()` crea la excepción; `Throws(exception)` permite controlar el mensaje y los datos. `CallBase` solo funciona con clases, no con interfaces, y obliga a que el miembro sea virtual.

`SetupSequence` devuelve valores distintos en llamadas sucesivas:

```csharp
var generador = new Mock<IGeneradorCodigo>();
generador.SetupSequence(g => g.Siguiente())
    .Returns(1)
    .Returns(2)
    .Throws<TimeoutException>()
    .Returns(4);
```

Es la forma de simular un servicio que falla una vez y se recupera, sin montar una cola manual. Al agotar la secuencia, el mock vuelve al comportamiento por defecto del tipo.

## Propiedades

Las propiedades se configuran con `SetupGet` y `SetupSet`:

```csharp
var sensor = new Mock<ISensor>();
sensor.SetupGet(s => s.Ubicacion).Returns("Madrid");
sensor.SetupSet(s => s.Ubicacion = "Barcelona");
```

Eso programa el acceso, pero no guarda estado: leer después de escribir no devuelve lo escrito, salvo que se configure así. Para que la propiedad se comporte como una propiedad normal se usa `SetupProperty`:

```csharp
sensor.SetupProperty(s => s.Altitud, 100);

sensor.Object.Altitud = 250;

Assert.Equal(250, sensor.Object.Altitud);
```

`SetupAllProperties` aplica el comportamiento a todas las propiedades. Es útil en objetos de configuración con muchas propiedades triviales; en un objeto de dominio puede ocultar que la clase probada depende de un estado que debería venir por constructor.

## Eventos

`Raise` dispara un evento desde el mock:

```csharp
public interface IComunicador
{
    event EventHandler<string> MensajeRecibido;
    void Enviar(string mensaje);
}

var comunicador = new Mock<IComunicador>();
comunicador.Raise(c => c.MensajeRecibido += null, comunicador.Object, "hola");
```

El `+= null` es la forma de referirse al evento; los argumentos siguientes son el remitente y los datos. Deben coincidir en tipo, orden y número con el delegado, o la prueba falla al ejecutar.

`SetupAdd` y `SetupRemove` permiten observar cuándo se suscribe o se da de baja un manejador:

```csharp
comunicador.SetupAdd(c => c.MensajeRecibido += It.IsAny<EventHandler<string>>())
    .Callback(() => suscrito = true);
```

## Secuencias

`MockSequence` comprueba que varias llamadas ocurren en un orden concreto:

```csharp
var secuencia = new MockSequence();
var transmision = new Mock<ITransmision>(MockBehavior.Strict);

transmision.InSequence(secuencia).Setup(t => t.SoltarAcelerador());
transmision.InSequence(secuencia).Setup(t => t.PisarEmbrague());
transmision.InSequence(secuencia).Setup(t => t.CambiarMarcha(It.IsInRange(1, 6, Range.Inclusive)));
transmision.InSequence(secuencia).Setup(t => t.SoltarEmbrague());
transmision.InSequence(secuencia).Setup(t => t.PisarAcelerador());
```

El mock debe crearse en modo `Strict`. Con `Loose`, una llamada fuera de orden no falla y la secuencia deja de comprobar nada. La secuencia es útil para protocolos y máquinas de estados; para el flujo normal de un servicio, suele ser una afirmación demasiado rígida.

## Verificar

`Verify` comprueba interacciones después de actuar:

```csharp
repositorio.Verify(r => r.Guardar(It.Is<Pedido>(p => p.Numero == "A-1")), Times.Once);
repositorio.Verify(r => r.Buscar(It.IsAny<string>()), Times.Never);
repositorio.VerifyNoOtherCalls();
```

| `Times` | Significado |
|---|---|
| `Never` | Ninguna llamada |
| `Once` | Exactamente una |
| `Exactly(n)` | Exactamente `n` |
| `AtLeastOnce` | Una o más |
| `AtLeast(n)` | `n` o más |
| `AtMostOnce` | Cero o una |
| `AtMost(n)` | Como mucho `n` |
| `Between(a, b, Range.Inclusive)` | Entre `a` y `b` |

`VerifyAll` exige que se hayan usado todas las configuraciones, aunque no estén marcadas. `Verifiable` marca una configuración concreta para que `Mock.Verify(mock)` la revise:

```csharp
repositorio.Setup(r => r.Guardar(It.IsAny<Pedido>())).Verifiable();

// ...

repositorio.Verify();
```

`VerifyNoOtherCalls` es el cierre habitual: después de comprobar lo esperado, confirma que no hubo llamadas adicionales. Solo tiene sentido cuando el contrato es estricto; en un mock `Loose` con muchas configuraciones puede producir más ruido que información.

## Casos menos frecuentes

**Miembros protegidos.** Se accede con `Moq.Protected`, por nombre y con `ItExpr` en lugar de `It`:

```csharp
using Moq.Protected;

var mock = new Mock<ClaseConProtegido>();
mock.Protected()
    .Setup<int>("Calcular", ItExpr.IsAny<string>())
    .Returns(1);
```

No hay comprobación de tipos: el nombre, el orden y los tipos de los argumentos son responsabilidad de quien escribe la prueba.

**Métodos genéricos.** Para un método `bool Foo<T>(T arg)` se usan comparadores de tipo:

```csharp
var foo = new Mock<IFoo>();
foo.Setup(f => f.Foo(It.IsAny<It.IsAnyType>())).Returns(true);
foo.Setup(f => f.Foo(It.IsAny<It.IsValueType>())).Returns(false);
```

**Repositorio de mocks.** `MockRepository` unifica el comportamiento y las verificaciones de varios mocks:

```csharp
var repositorio = new MockRepository(MockBehavior.Strict);
var pedidos = repositorio.Create<IRepositorioPedidos>();
var clientes = repositorio.Create<IRepositorioClientes>();

// ...

repositorio.VerifyAll();
```

No reutiliza instancias: cada `Create<T>` devuelve un mock nuevo. Su valor es tener un punto único de verificación cuando una clase recibe varias dependencias.

## Buen uso

- **Mockea lo que no controlas o lo que no quieres ejecutar.** La base de datos, el HTTP, el reloj, el bus. No mockees la clase que estás probando ni sus objetos de valor.
- **Prefiere verificar estado.** Afirma el resultado del servicio; verifica la llamada al repositorio solo si el contrato es «guardar».
- **No afirmes detalles internos.** El número exacto de consultas o el orden de llamadas privadas convierte cualquier refactorización en un arreglo de pruebas.
- **Configura lo mínimo.** Un mock con veinte `Setup` describe un escenario que la prueba no necesita y que hay que mantener.
- **Cuidado con `Loose`.** Si el código probado olvida comprobar un `null`, el mock puede devolverlo y la prueba pasar por una rama que en producción no existe.
