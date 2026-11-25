# xUnit.net: el motor de pruebas

xUnit.net es un framework de pruebas para .NET, gratuito y de código abierto, distribuido como paquete NuGet. Su modelo es el de la familia xUnit: cada prueba es un método independiente, el runner descubre los métodos marcados con un atributo y crea una instancia nueva de la clase para cada uno. Esa independencia es la que permite ejecutar pruebas en paralelo sin que compartan estado por accidente.

## El proyecto de pruebas

Una solución .NET suele separar el código de producción del de pruebas:

```text
src/
  Tienda/
    Tienda.csproj
tests/
  Tienda.Tests/
    Tienda.Tests.csproj
```

La plantilla `dotnet new xunit` crea el proyecto con el paquete de xUnit, un runner y las referencias de prueba ya configuradas. El proyecto de pruebas referencia al de producción; el de producción no sabe que existen las pruebas.

```bash
dotnet new xunit -n Tienda.Tests -o tests/Tienda.Tests
dotnet add tests/Tienda.Tests reference src/Tienda/Tienda.csproj
dotnet test
```

Las versiones actuales conviven en dos líneas: xUnit 2, madura y todavía mayoritaria, y xUnit 3, con el proyecto convertido en ejecutable y algunos tipos actualizados. Los atributos y el modelo mental son los mismos; conviene fijar la versión en el proyecto y no mezclar guías de una y otra.

## Qué descubre el runner

Para que un método se ejecute como prueba:

1. La clase que lo contiene debe ser pública.
2. El método debe llevar `[Fact]` o `[Theory]`.
3. El método debe ser público y no tener parámetros, salvo que sea una teoría.
4. El valor de retorno debe ser `void` o `Task` (en xUnit 3, `Task` o `ValueTask`).

No hace falta un constructor sin parámetros: xUnit instancia la clase por reflexión y admite parámetros cuando los aporta un fixture o el propio framework, como `ITestOutputHelper`.

```csharp
public class PrecioTests
{
    [Fact]
    public void ConDescuentoDel10_RestaDiezPorCiento()
    {
        var precio = new Precio(100m);

        var rebajado = precio.ConDescuento(0.10m);

        Assert.Equal(90m, rebajado.Importe);
    }
}
```

El runner crea una instancia de `PrecioTests` para esta prueba, ejecuta el método y la descarta. Dos pruebas de la misma clase nunca comparten la instancia, aunque se ejecuten en el mismo proceso.

## Ejecutar y filtrar

`dotnet test` compila y ejecuta. Durante el desarrollo conviene acotar:

```bash
dotnet test
dotnet test --filter "FullyQualifiedName~PrecioTests"
dotnet test --filter "Category=Unitaria"
dotnet test --logger "console;verbosity=detailed"
```

El filtro por nombre completo es útil cuando se itera sobre una clase. El filtro por categoría depende de que las pruebas estén marcadas con traits; sin ellos, no hay nada que filtrar.

`dotnet watch test` repite la ejecución al detectar un cambio en el código. Es cómodo en una pantalla secundaria: el ciclo de escribir, guardar y ver el resultado se acorta, a cambio de consumir recursos de forma continua.

## Ciclo de vida

Sin fixtures, el orden es:

1. Se ejecuta el constructor de la clase de prueba.
2. Se ejecuta el método de prueba.
3. Se llama a `Dispose` si la clase implementa `IDisposable`.

```csharp
public class DirectorioTemporalTests : IDisposable
{
    private readonly string _ruta;

    public DirectorioTemporalTests()
    {
        _ruta = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
        Directory.CreateDirectory(_ruta);
    }

    [Fact]
    public void EstaVacio_AlCrearse()
    {
        Assert.Empty(Directory.EnumerateFiles(_ruta));
    }

    public void Dispose() => Directory.Delete(_ruta, recursive: true);
}
```

El constructor prepara y `Dispose` limpia. Es la forma más directa de aislar una prueba que toca el sistema de archivos, una base de datos temporal o una variable de entorno.

Cuando la preparación es asíncrona, se implementa `IAsyncLifetime`:

```csharp
public class RepositorioTests : IAsyncLifetime
{
    private BaseDeDatos _db = null!;

    public async Task InitializeAsync()
    {
        _db = await BaseDeDatos.CrearAsync();
    }

    public async Task DisposeAsync()
    {
        await _db.DisposeAsync();
    }

    [Fact]
    public async Task GuardaYRecupera()
    {
        await _db.GuardarAsync(new Articulo("A"));

        var recuperado = await _db.ObtenerAsync("A");

        Assert.NotNull(recuperado);
    }
}
```

En xUnit 2 los métodos de `IAsyncLifetime` devuelven `Task`; en xUnit 3 devuelven `ValueTask`. El orden completo, cuando hay interceptores, es: constructor, `InitializeAsync`, atributos `Before`, prueba, atributos `After` en orden inverso, `DisposeAsync` y `Dispose`.

## La salida de una prueba

En local se depura, pero en integración continua no hay depurador. `ITestOutputHelper` permite escribir mensajes que quedan asociados al resultado de la prueba, pase o falle:

```csharp
public class CalculadoraTests
{
    private readonly ITestOutputHelper _salida;

    public CalculadoraTests(ITestOutputHelper salida) => _salida = salida;

    [Fact]
    public void Suma()
    {
        var resultado = Calculadora.Sumar(2, 3);
        _salida.WriteLine($"Resultado obtenido: {resultado}");

        Assert.Equal(5, resultado);
    }
}
```

No se debe usar `Console.WriteLine` para esto: con pruebas en paralelo, el runner no siempre puede atribuir la línea a la prueba correcta. `ITestOutputHelper` sí mantiene la asociación.

## Omitir y paralelizar

`Skip` marca una prueba para que no se ejecute:

```csharp
[Fact(Skip = "Pendiente de decidir el redondeo con negocio")]
public void CalculaComision_ConImporteNegativo() { }
```

Omitir debe ser excepcional y con motivo escrito. Un `Skip` sin fecha ni responsable se convierte en una prueba muerta que nadie recuerda reactivar. Si el problema es que la prueba tarda o depende de un entorno, el filtro por categoría suele ser mejor herramienta.

Por defecto, xUnit ejecuta en paralelo las colecciones de pruebas y en serie las pruebas de una misma colección. Las clases sin colección explícita forman cada una su propia colección. Cuando el paralelismo rompe algo —dos pruebas que escriben el mismo archivo, por ejemplo— se agrupan en una colección o se ajusta el ensamblado:

```csharp
[assembly: CollectionBehavior(
    CollectionBehavior.CollectionPerAssembly,
    DisableTestParallelization = true,
    MaxParallelThreads = 2)]
```

Desactivar el paralelismo global es la última opción: multiplica el tiempo de la suite. Casi siempre el arreglo correcto es aislar el recurso compartido.

## Pruebas contra varios frameworks

Un proyecto de pruebas puede compilar para varios destinos:

```xml
<PropertyGroup>
  <TargetFrameworks>net10.0;net8.0</TargetFrameworks>
</PropertyGroup>
```

El segundo destino (`net8.0`) solo se mantiene mientras haya que probar una versión anterior; la referencia actual es `net10.0`.

El runner ejecuta la batería una vez por destino. Sirve para una biblioteca que se publica en varias versiones de .NET; para una aplicación que solo corre en una, añade tiempo sin aportar información. Los destinos de .NET Framework solo se compilan en Windows.
