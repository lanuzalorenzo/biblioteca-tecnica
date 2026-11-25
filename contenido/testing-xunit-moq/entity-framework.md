# Entity Framework

Entity Framework es el ORM de Microsoft para .NET. Traduce objetos y LINQ a SQL, gestiona el seguimiento de cambios y materializa resultados. Esa comodidad tiene un precio cuando se prueba: una consulta no se ejecuta hasta que se enumera, y su resultado depende del proveedor de base de datos. Sustituir el `DbContext` por un mock parece la salida fácil, pero suele producir pruebas que no se parecen a la realidad.

## Qué se quiere comprobar

Al probar acceso a datos hay dos preguntas distintas:

1. **¿La consulta devuelve lo que la lógica espera?** Filtros, ordenaciones, relaciones, proyecciones.
2. **¿El mapeo y el esquema son correctos?** Claves, relaciones, restricciones, conversiones.

Un mock de `DbSet` puede responder a la primera con datos en memoria, pero no prueba nada del esquema ni del SQL generado. Una base de datos real responde a las dos, a cambio de más tiempo y preparación.

## La opción recomendada: un proveedor real en memoria

Para EF Core, la forma más fiel de probar sin depender de un servidor es SQLite en memoria. Es una base de datos relacional completa, con claves y restricciones, que vive mientras la conexión está abierta.

```csharp
public sealed class BibliotecaFixture : IAsyncLifetime
{
    private SqliteConnection _conexion = null!;
    public BibliotecaDbContext Db { get; private set; } = null!;

    public async Task InitializeAsync()
    {
        _conexion = new SqliteConnection("Data Source=:memory:");
        await _conexion.OpenAsync();

        var options = new DbContextOptionsBuilder<BibliotecaDbContext>()
            .UseSqlite(_conexion)
            .Options;

        Db = new BibliotecaDbContext(options);
        await Db.Database.EnsureCreatedAsync();
        await Db.SembrarAsync();
    }

    public async Task DisposeAsync()
    {
        await Db.DisposeAsync();
        await _conexion.DisposeAsync();
    }
}
```

```csharp
public class ConsultasTests : IClassFixture<BibliotecaFixture>
{
    private readonly BibliotecaDbContext _db;

    public ConsultasTests(BibliotecaFixture fixture) => _db = fixture.Db;

    [Fact]
    public async Task LibrosDeUnAutor_DevuelveSoloLosSuyos()
    {
        var libros = await _db.Libros
            .Where(l => l.AutorId == 1)
            .ToListAsync();

        Assert.All(libros, l => Assert.Equal(1, l.AutorId));
    }
}
```

El contexto debe aceptar las opciones por constructor y no configurarse a sí mismo si ya vienen dadas:

```csharp
public class BibliotecaDbContext : DbContext
{
    public BibliotecaDbContext(DbContextOptions<BibliotecaDbContext> options)
        : base(options) { }

    public DbSet<Libro> Libros => Set<Libro>();
    public DbSet<Autor> Autores => Set<Autor>();

    protected override void OnConfiguring(DbContextOptionsBuilder options)
    {
        if (!options.IsConfigured)
        {
            options.UseSqlite("Data Source=biblioteca.db");
        }
    }
}
```

La comprobación `IsConfigured` evita configurar dos proveedores a la vez, que es un error frecuente al mezclar el contexto de producción con el de pruebas.

### Límites de SQLite

SQLite no es el motor de producción. No reproduce tipos propios de SQL Server o PostgreSQL, funciones específicas, índices avanzados ni el comportamiento exacto de concurrencia. Una consulta que funciona en SQLite puede fallar en el motor real si usa una función que aquel no tiene. Para la lógica de consulta suele ser suficiente; para el esquema y las migraciones, no.

Cuando la fidelidad es un requisito, se levanta el motor real en un contenedor con Testcontainers y se ejecuta la suite contra él. Es más lento, pero elimina la clase de fallo «funciona en SQLite y no en producción». Esa prueba pertenece a la capa de integración, no a la unitaria.

## El proveedor InMemory

EF Core incluye `Microsoft.EntityFrameworkCore.InMemory`, un almacén en memoria que no es relacional. Es rápido y no requiere conexión, pero no aplica claves foráneas, restricciones `unique` ni buena parte de las reglas del esquema. El propio equipo de EF desaconseja usarlo como sustituto de una base de datos en pruebas: una operación que viola una restricción pasa sin error y la prueba da una falsa sensación de seguridad.

Su uso razonable es acotado: prototipos, pruebas de una consulta puramente LINQ o escenarios donde el esquema no interviene. Para todo lo demás, SQLite en memoria ofrece mejor relación entre fidelidad y coste.

```csharp
var options = new DbContextOptionsBuilder<BibliotecaDbContext>()
    .UseInMemoryDatabase($"biblioteca-{Guid.NewGuid()}")
    .Options;
```

El nombre distingue instancias. Si se reutiliza el mismo, los datos de una prueba contaminan la siguiente.

## Sembrar datos

Una base en memoria nace vacía. La semilla debe ser explícita y pequeña, y debe ejecutarse una vez por prueba o por fixture según el aislamiento que se busque.

```csharp
public static class Semilla
{
    public static async Task SembrarAsync(this BibliotecaDbContext db)
    {
        var autor = new Autor { Id = 1, Nombre = "Autora de ejemplo" };
        db.Autores.Add(autor);
        db.Libros.Add(new Libro { Id = 1, Titulo = "Primero", AutorId = 1 });
        db.Libros.Add(new Libro { Id = 2, Titulo = "Segundo", AutorId = 1 });
        await db.SaveChangesAsync();
    }
}
```

Con un fixture compartido, las pruebas de escritura deben limpiarse o ejecutarse en una transacción que se revierte. Si no, el orden de ejecución altera los resultados. La alternativa es crear el contexto por prueba y pagar el coste de `EnsureCreated` cada vez; en SQLite es pequeño, en un motor real no.

## EF 6 y el mock de `DbSet`

En aplicaciones antiguas sobre Entity Framework 6, la técnica habitual fue mockear `DbSet<T>` y sus proveedores LINQ. Consiste en crear listas `AsQueryable()` y configurar `Provider`, `Expression`, `ElementType` y `GetEnumerator`:

```csharp
var libros = new List<Libro> { new() { Id = 1, Titulo = "Primero", AutorId = 1 } }
    .AsQueryable();

var dbSet = new Mock<DbSet<Libro>>();
dbSet.As<IQueryable<Libro>>().Setup(s => s.Provider).Returns(libros.Provider);
dbSet.As<IQueryable<Libro>>().Setup(s => s.Expression).Returns(libros.Expression);
dbSet.As<IQueryable<Libro>>().Setup(s => s.ElementType).Returns(libros.ElementType);
dbSet.As<IQueryable<Libro>>().Setup(s => s.GetEnumerator()).Returns(libros.GetEnumerator);

var contexto = new Mock<BibliotecaDbContext>();
contexto.Setup(c => c.Libros).Returns(dbSet.Object);
```

Funciona para consultas síncronas, pero es frágil: hay que replicar el proveedor para cada tabla, las consultas asíncronas necesitan configuración adicional y las propiedades de navegación se comportan como colecciones estáticas. En código nuevo no se justifica. Si se hereda, conviene aislarlo en un helper y no extenderlo.

## Qué afirmar

Las pruebas de datos deben comprobar el resultado de la operación, no el SQL concreto:

```csharp
[Fact]
public async Task GuardarLibro_AsignaIdentificador()
{
    var libro = new Libro { Titulo = "Nuevo", AutorId = 1 };

    _db.Libros.Add(libro);
    await _db.SaveChangesAsync();

    Assert.True(libro.Id > 0);
    Assert.Equal("Nuevo", (await _db.Libros.FindAsync(libro.Id))!.Titulo);
}
```

Afirmar sobre el texto de la consulta o sobre el número de viajes al servidor acopla la prueba al proveedor y a la versión de EF. Si el rendimiento es un requisito, se mide con una prueba de carga o con el registro de SQL, no con un `Assert` sobre una cadena generada.

## Dónde encaja

| Necesidad | Herramienta |
|---|---|
| Lógica de una consulta LINQ | SQLite en memoria |
| Esquema, restricciones, migraciones | Motor real o Testcontainers |
| Repositorio simulado en una prueba unitaria | Interfaz propia y fake en memoria |
| Compatibilidad con producción | Prueba de integración contra el mismo motor |

La regla es simple: cuanto más se acerca la prueba al motor real, más confianza da y más cuesta. La pirámide se aplica también aquí. La mayoría de las pruebas de datos pueden vivir contra SQLite; unas pocas, contra el motor de producción.
