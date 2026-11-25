# Fixtures y traits

Dos mecanismos de xUnit resuelven problemas distintos que aparecen al crecer la suite. Los **fixtures** comparten preparación costosa entre varias pruebas. Los **traits** etiquetan las pruebas para ejecutar subconjuntos por categoría. Ninguno de los dos cambia lo que se prueba; cambian el coste y la organización.

## El problema del constructor

El constructor de la clase de prueba se ejecuta una vez por cada método. Es lo correcto para aislar, pero caro si la preparación tarda: levantar un contenedor, abrir una conexión, crear una base de datos temporal o arrancar un servidor.

```csharp
public class BaseDeDatosTests : IDisposable
{
    private readonly BaseDeDatos _db;

    public BaseDeDatosTests()
    {
        _db = BaseDeDatos.Levantar(); // se repite en cada prueba
    }

    public void Dispose() => _db.Apagar();
}
```

Con veinte pruebas, el servidor se levanta y se apaga veinte veces. El accesorio de clase mueve esa preparación a un objeto que vive lo que vive la clase de pruebas.

## `IClassFixture<T>`

Se crea una clase con la preparación y la limpieza, y la clase de prueba la declara en la herencia y la recibe por constructor:

```csharp
public sealed class BaseDeDatosFixture : IDisposable
{
    public BaseDeDatos Db { get; } = BaseDeDatos.Levantar();

    public void Dispose() => Db.Apagar();
}

public class PedidosTests : IClassFixture<BaseDeDatosFixture>
{
    private readonly BaseDeDatos _db;

    public PedidosTests(BaseDeDatosFixture fixture) => _db = fixture.Db;

    [Fact]
    public void GuardaUnPedido()
    {
        _db.Pedidos.Add(new Pedido("A-1"));

        Assert.Single(_db.Pedidos);
    }
}
```

El fixture se construye antes de la primera prueba de la clase y se libera al terminar la última. Si dos clases usan el mismo `IClassFixture<T>`, cada una recibe su propia instancia: no se comparte entre clases. Para compartir de verdad hay que usar una colección.

Un fixture puede implementar `IAsyncLifetime` si la preparación es asíncrona. En xUnit 2 sus métodos devuelven `Task`; en xUnit 3, `ValueTask`.

## `ICollectionFixture<T>`

Una colección agrupa clases de prueba. Tiene dos efectos: las pruebas de la colección no se ejecutan en paralelo entre sí, y comparten los fixtures declarados en la definición de la colección.

```csharp
[CollectionDefinition("Base de datos")]
public class BaseDeDatosCollection : ICollectionFixture<BaseDeDatosFixture>
{
    // La clase no tiene código; solo declara el nombre y el fixture.
}

[Collection("Base de datos")]
public class PedidosTests
{
    private readonly BaseDeDatos _db;

    public PedidosTests(BaseDeDatosFixture fixture) => _db = fixture.Db;
}

[Collection("Base de datos")]
public class ClientesTests
{
    private readonly BaseDeDatos _db;

    public ClientesTests(BaseDeDatosFixture fixture) => _db = fixture.Db;
}
```

Ahora el fixture se crea una vez para las dos clases y se libera al terminar la colección. El nombre de la clase que define la colección es irrelevante; lo que importa es la cadena de `[CollectionDefinition]` y su coincidencia con `[Collection]`.

Una clase de prueba solo puede pertenecer a una colección. Si necesita dos recursos compartidos, se declaran ambos en la misma definición:

```csharp
[CollectionDefinition("Integración")]
public class IntegracionCollection :
    ICollectionFixture<BaseDeDatosFixture>,
    ICollectionFixture<ServidorFixture>
{
}
```

Como la colección es también la unidad de paralelismo, abusar de ella serializa la suite. Una colección por recurso compartido es razonable; una colección única para todo el proyecto convierte el paralelismo en decorado.

## Rasgos: `[Trait]`

Un rasgo es un par clave-valor aplicado a una prueba o a una clase:

```csharp
[Fact]
[Trait("Category", "Unitaria")]
public void CalculaTotal_ConCarritoVacio() { }

[Fact]
[Trait("Category", "Integracion")]
[Trait("Componente", "Pedidos")]
public void GuardaPedido_EnBaseDeDatos() { }
```

Una prueba puede tener varios traits y pertenecer a varios grupos. En la línea de comandos se filtra por clave y valor:

```bash
dotnet test --filter "Category=Unitaria"
dotnet test --filter "Category=Integracion&Componente=Pedidos"
dotnet test --filter "Category!=Integracion"
```

El filtro es útil para iterar y para separar etapas en integración continua: primero las unitarias, después las de integración. También es un arma de doble filo: si un desarrollador deja un filtro activo en su entorno, ejecuta una parte de la suite y cree que todo está verde. En el pipeline conviene ejecutar sin filtros o con filtros explícitos y revisados.

## Rasgos propios

`[Trait]` solo admite una clave y un valor por atributo. Un proyecto que etiqueta por tipo, componente, ticket y velocidad acumula atributos y repite combinaciones. xUnit permite crear un atributo que expanda varios traits.

El atributo implementa `ITraitAttribute` y declara un descubridor:

```csharp
[TraitDiscoverer(
    "Tienda.Tests.BugDiscoverer",
    "Tienda.Tests")]
[AttributeUsage(AttributeTargets.Method | AttributeTargets.Class, AllowMultiple = true)]
public sealed class BugAttribute : Attribute, ITraitAttribute
{
    public BugAttribute(string id) => Id = id;

    public string Id { get; }
}
```

El descubridor recibe el atributo y devuelve los pares:

```csharp
public sealed class BugDiscoverer : ITraitDiscoverer
{
    public IEnumerable<KeyValuePair<string, string>> GetTraits(IAttributeInfo traitAttribute)
    {
        var id = traitAttribute.GetNamedArgument<string>("Id");

        yield return new KeyValuePair<string, string>("Category", "Bug");
        if (!string.IsNullOrWhiteSpace(id))
        {
            yield return new KeyValuePair<string, string>("Bug", id);
        }
    }
}
```

Se usa como un atributo normal:

```csharp
[Fact]
[Bug("1234")]
public void CalculaDescuento_NoAplicaIvaDosVeces() { }
```

El patrón sirve para cualquier etiqueta compuesta: componente, caso de negocio, criticidad. La contrapartida es que el descubrimiento por reflexión añade complejidad y un punto más donde puede fallar la compilación. Para dos o tres categorías, `[Trait]` directo es más simple.

## Organizar sin sobreetiquetar

Los traits responden a preguntas concretas: ¿qué ejecuto mientras desarrollo? ¿qué se puede saltar si no hay base de datos? ¿qué cubre esta funcionalidad? Una taxonomía con diez claves cruzadas acaba sin uso.

Una convención mínima que funciona:

| Clave | Valores | Para qué |
|---|---|---|
| `Category` | `Unitaria`, `Integracion`, `Funcional` | Separar etapas del pipeline |
| `Componente` | `Pedidos`, `Facturacion`, `Clientes` | Ejecutar lo que se está tocando |
| `Bug` | Identificador | Agrupar regresiones |

El nombre de la carpeta y el espacio de nombres ya agrupan por área. Los traits añaden la dimensión que el árbol de archivos no puede expresar: el coste o la dependencia externa de una prueba.
