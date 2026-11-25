# Casos difíciles

Hay código que no se deja probar con las técnicas habituales: librerías sin interfaz, clases con constructores internos, dependencias estáticas, código heredado que nadie diseñó pensando en pruebas. La respuesta no es rendirse ni reescribir el mundo. Es aplicar la costura menos invasiva que permita comprobar el comportamiento.

## Dependencias estáticas

`DateTime.Now`, `Guid.NewGuid()`, `File.ReadAllText` y `Environment.GetEnvironmentVariable` son llamadas estáticas: no se pueden sustituir por un doble y hacen que la prueba dependa del entorno. La solución es envolverlas detrás de una interfaz propia.

Antes de .NET 8 se inyectaba una interfaz propia, como `IReloj`, con una implementación fija para las pruebas. Hoy `TimeProvider` cubre el mismo papel para el tiempo y las zonas horarias, y `FakeTimeProvider` de `Microsoft.Extensions.TimeProvider.Testing` evita escribir el doble.

```csharp
public class CalculadoraDePlazos
{
    private readonly TimeProvider _reloj;

    public CalculadoraDePlazos(TimeProvider reloj) => _reloj = reloj;

    public bool EstaVencido(DateTimeOffset vencimiento) =>
        _reloj.GetUtcNow() > vencimiento;
}

public class VencimientoTests
{
    [Fact]
    public void EstaVencido_CuandoLaFechaYaPaso()
    {
        var reloj = new FakeTimeProvider(DateTimeOffset.Parse("2026-01-10T00:00:00Z"));
        var calculadora = new CalculadoraDePlazos(reloj);

        var vencido = calculadora.EstaVencido(DateTimeOffset.Parse("2026-01-09T00:00:00Z"));

        Assert.True(vencido);
    }
}
```

El mismo patrón sirve para el sistema de archivos (`IFileSystem`), el generador de identificadores (`IGuidProvider`) y la configuración. Envolver una llamada estática es barato; dejar que se cuele en la lógica convierte cualquier prueba en dependiente de la máquina.

## Clases sin interfaz: el envoltorio

Una librería de terceros expone una clase útil que no implementa ninguna interfaz. No se puede inyectar un doble porque el tipo concreto es la dependencia. Se envuelve en una interfaz propia:

```csharp
public interface IPuertoSerie
{
    void Abrir();
    void Escribir(string mensaje);
    void Cerrar();
}

public sealed class PuertoSerieEnvoltorio : IPuertoSerie
{
    private readonly SerialPort _puerto;

    public PuertoSerieEnvoltorio(SerialPort puerto) => _puerto = puerto;

    public void Abrir() => _puerto.Open();
    public void Escribir(string mensaje) => _puerto.WriteLine(mensaje);
    public void Cerrar() => _puerto.Close();
}
```

La clase que usa el puerto pasa a depender de `IPuertoSerie`, y la prueba inyecta un doble que registra las llamadas. El envoltorio no añade lógica: solo adapta una API que no se puede sustituir.

El coste es una capa más y un lugar donde puede perderse un detalle de la API original. Se justifica cuando la dependencia es externa, inestable o difícil de montar. No se justifica para envolver una clase propia que podría implementar la interfaz directamente.

## Constructores internos o protegidos: herencia

Una clase de librería puede tener un constructor `internal` o `protected`. Si no está sellada, se puede heredar y exponer un constructor propio:

```csharp
public class RecursoDeLibreria
{
    protected internal RecursoDeLibreria(string nombre) => Nombre = nombre;

    public string Nombre { get; }
}

public sealed class RecursoConstruible : RecursoDeLibreria
{
    public RecursoConstruible(string nombre) : base(nombre) { }
}
```

```csharp
var recurso = new RecursoConstruible("ejemplo");

Assert.Equal("ejemplo", recurso.Nombre);
```

La herencia también sirve para reemplazar métodos `virtual` o `protected` y observar su comportamiento. Dos cautelas: solo funciona si la clase no está sellada y si el miembro es sustituible; y heredar de una clase de terceros acopla la prueba a su jerarquía, que puede cambiar entre versiones.

Para código propio, la alternativa limpia es `InternalsVisibleTo`:

```xml
<ItemGroup>
  <InternalsVisibleTo Include="Tienda.Tests" />
</ItemGroup>
```

Así las pruebas acceden a tipos internos sin abrirlos al resto del mundo. Es preferible a convertir miembros en públicos solo para probarlos.

## Reflexión: el último recurso

Cuando la clase está sellada, el constructor es privado y no hay interfaz, queda la reflexión. En código intermedio los modificadores de acceso son una convención del compilador, no una barrera física: con el `Type` y el constructor adecuados se puede crear la instancia.

```csharp
var tipo = typeof(RecursoSellado);
var constructor = tipo.GetConstructor(
    BindingFlags.NonPublic | BindingFlags.Instance,
    binder: null,
    types: new[] { typeof(string) },
    modifiers: null);

var recurso = (RecursoSellado)constructor!.Invoke(new object[] { "ejemplo" });
```

Los parámetros de `GetConstructor` localizan el constructor por ámbito, tipo y orden de argumentos. `Invoke` devuelve `object`; la conversión explícita es responsabilidad de quien escribe la prueba. Si el constructor cambia, la prueba falla en ejecución, no al compilar.

La reflexión tiene tres problemas: es más lenta, es más difícil de leer y depende de detalles internos que nadie prometió mantener. Se usa cuando no hay otra opción y se aísla en un helper con un nombre que explique por qué está ahí. Nunca como herramienta por defecto.

## Código heredado sin costuras

El código antiguo suele tener clases enormes, dependencias construidas dentro y ningún punto de sustitución. Cambiarlo entero antes de probarlo es inviable. El orden razonable es:

1. **Caracterizar el comportamiento actual.** Escribir pruebas que capturen lo que hace hoy, aunque parezca incorrecto. Son la red que permite cambiar sin romper.
2. **Introducir una costura mínima.** Extraer la dependencia que impide probar, sin reescribir la clase.
3. **Probar y refactorizar solo lo que se toca.** El resto se queda como está hasta que haya motivo para cambiarlo.
4. **Repetir en la siguiente modificación.** La deuda se paga por partes, no de golpe.

Este enfoque se parece al patrón *strangler*: la funcionalidad nueva se escribe al lado, con buen diseño y pruebas, y sustituye a la antigua por partes. La clase de 3.000 líneas no se arregla en una tarde; se reduce cada vez que se modifica.

## Elegir la técnica

| Situación | Técnica | Coste |
|---|---|---|
| Llamada estática | Envolver en interfaz propia | Bajo |
| Clase de terceros sin interfaz | Envoltorio | Medio |
| Constructor interno o protegido | Herencia o `InternalsVisibleTo` | Medio |
| Clase sellada, constructor privado | Reflexión | Alto |
| Código heredado acoplado | Caracterizar, costura mínima, refactorizar por partes | Alto |

La regla es elegir la intervención más pequeña que permita afirmar el comportamiento. Cuanto más agresiva es la técnica, más frágil es la prueba y más probable es que el problema real esté en el diseño de la clase.
