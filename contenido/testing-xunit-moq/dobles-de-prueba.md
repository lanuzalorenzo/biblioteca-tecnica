# Dobles de prueba

Un doble de prueba es un objeto que ocupa el lugar de una dependencia real durante una prueba. No es un concepto de una biblioteca concreta: es una técnica de diseño que aprovecha las costuras del código para sustituir lo que no conviene ejecutar. Moq, NSubstitute o un simple `class FakeRepositorio : IRepositorio` son formas distintas de crear el mismo tipo de objeto.

## Por qué sustituir una dependencia

Una prueba unitaria debe fallar por la lógica que prueba, no porque la base de datos esté caída, la red vaya lenta o el servicio externo haya cambiado su respuesta. Sustituir esas dependencias consigue tres cosas:

- **Determinismo.** La respuesta es siempre la misma; no depende del entorno.
- **Velocidad.** No hay entrada/salida ni esperas de red.
- **Aislamiento.** Cuando la prueba falla, el fallo está en la pieza que se ejecutó.

La posibilidad de sustituir existe si la clase recibe la dependencia como abstracción. Si construye el colaborador dentro, no hay costura y no hay doble posible sin técnicas más agresivas.

```csharp
public interface IReloj
{
    DateTime Ahora { get; }
}

public class CalculadoraDePlazos
{
    private readonly IReloj _reloj;

    public CalculadoraDePlazos(IReloj reloj) => _reloj = reloj;

    public bool EstaVencido(DateTime vencimiento) => _reloj.Ahora > vencimiento;
}
```

Con esa interfaz, la prueba fija la hora sin tocar la del sistema.

## La familia de dobles

La terminología de Gerard Meszaros y Martin Fowler distingue cinco papeles según lo que el objeto hace y lo que la prueba comprueba:

| Tipo | Qué hace | Qué se afirma |
|---|---|---|
| *Dummy* | Rellena un parámetro; nunca se usa | Nada sobre él |
| *Stub* | Devuelve respuestas prefijadas | El resultado del código probado |
| *Spy* | Stub que registra las llamadas recibidas | Qué se llamó, después de actuar |
| *Mock* | Spy con expectativas y fallos programados | Interacciones esperadas |
| *Fake* | Implementación simplificada pero funcional | El resultado, usando una alternativa real |

La frontera entre ellos es difusa y no siempre importa. Lo que sí importa es elegir entre **verificar estado** y **verificar interacción**. Un stub o un fake se usan para que el código llegue a un resultado; un mock o un spy se usan cuando la interacción es el resultado.

## Un fake escrito a mano

Un fake es una implementación real, pero simplificada: un repositorio en memoria, un reloj fijo, un bus que guarda mensajes en una lista.

```csharp
public interface IRepositorioPedidos
{
    void Guardar(Pedido pedido);
    Pedido? Buscar(string numero);
}

public class RepositorioPedidosEnMemoria : IRepositorioPedidos
{
    private readonly Dictionary<string, Pedido> _pedidos = new();

    public void Guardar(Pedido pedido) => _pedidos[pedido.Numero] = pedido;

    public Pedido? Buscar(string numero) =>
        _pedidos.TryGetValue(numero, out var pedido) ? pedido : null;
}
```

```csharp
[Fact]
public void Confirmar_GuardaElPedido()
{
    var repositorio = new RepositorioPedidosEnMemoria();
    var servicio = new ServicioPedidos(repositorio);

    servicio.Confirmar(new Pedido("A-1"));

    Assert.NotNull(repositorio.Buscar("A-1"));
}
```

El fake es código de producción de pruebas: tiene sus propios fallos posibles. Si el fake no respeta el contrato de la interfaz —por ejemplo, lanza una excepción que la implementación real no lanza—, las pruebas pasan con una mentira. La defensa es un **test de contrato**: la misma batería de pruebas se ejecuta contra el fake y contra la implementación real.

## Stub y spy

Un stub devuelve lo que la prueba necesita:

```csharp
public sealed class RelojFijo : IReloj
{
    public RelojFijo(DateTime ahora) => Ahora = ahora;

    public DateTime Ahora { get; }
}
```

Un spy registra lo que ocurrió:

```csharp
public sealed class NotificadorEspia : INotificador
{
    public List<string> Destinatarios { get; } = new();

    public void Enviar(string destinatario) => Destinatarios.Add(destinatario);
}
```

```csharp
[Fact]
public void AvisarVencimiento_NotificaAlCliente()
{
    var notificador = new NotificadorEspia();
    var servicio = new Avisos(notificador);

    servicio.Avisar(new Pedido("A-1", "cliente@ejemplo.com"));

    Assert.Contains("cliente@ejemplo.com", notificador.Destinatarios);
}
```

El spy se usa cuando el efecto es la llamada. Si el efecto fuera el estado del pedido, bastaría con afirmar sobre el pedido y el notificador sería un dummy.

## Cuándo usar la biblioteca y cuándo no

Un fake escrito a mano es claro, tipado y fácil de depurar. A cambio, hay que mantenerlo y crece con la interfaz. Una biblioteca de mocks evita ese mantenimiento, pero introduce una sintaxis y una configuración que pueden ocultar el escenario.

Como criterio práctico:

- Si el doble se reutiliza en muchas pruebas, escríbelo como fake y pruébalo con un contrato.
- Si solo necesitas una respuesta concreta en una prueba, un stub o un mock de biblioteca es más corto.
- Si la dependencia la defines tú y tiene pocos métodos, el fake suele ganar en legibilidad.
- Si la interfaz es grande o ajena, la biblioteca evita implementar métodos que no se usan.

## Exceso de dobles

Sustituir todo lo que se mueve produce pruebas que comprueban la coreografía de llamadas, no el comportamiento. Se reconocen por varias señales:

- La prueba necesita cinco mocks para arrancar una clase.
- Al refactorizar sin cambiar el resultado, hay que reescribir las pruebas.
- Se afirma el orden exacto de llamadas que nadie pactó.
- El doble devuelve datos que la implementación real nunca produciría.

En ese punto, el problema no es la prueba: es el diseño. Una clase con cinco dependencias suele tener más de una responsabilidad. La solución es dividirla, no añadir un sexto mock.

También hay piezas que no se sustituyen. Los objetos de valor, las funciones puras y las estructuras del lenguaje se usan reales: un `decimal`, una lista o una fecha no necesitan doble. Sustituirlos añade ceremonia sin aislar nada.
