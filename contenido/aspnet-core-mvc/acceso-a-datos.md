# Acceso a datos con Entity Framework Core

La persistencia traduce las entidades del dominio a un almacén y viceversa. Entity Framework Core es el ORM de .NET: mapea clases a tablas, traduce consultas LINQ a SQL y gestiona el seguimiento de cambios. No es la única opción —Dapper o el acceso directo con `SqlClient` siguen teniendo sentido—, pero cubre la mayoría de los casos sin escribir SQL a mano.

## El contexto

El `DbContext` representa una sesión con la base de datos. Expone colecciones `DbSet<T>` para las entidades y guarda los cambios de forma agrupada:

```csharp
public class BlogContext : DbContext
{
    public BlogContext(DbContextOptions<BlogContext> options)
        : base(options) { }

    public DbSet<Post> Posts => Set<Post>();
    public DbSet<Comment> Comments => Set<Comment>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Post>(entity =>
        {
            entity.Property(p => p.Title).HasMaxLength(200).IsRequired();
            entity.HasIndex(p => p.Date);
            entity.HasMany(p => p.Comments)
                  .WithOne(c => c.Post)
                  .HasForeignKey(c => c.PostId);
        });
    }
}
```

El contexto se registra en el contenedor con `AddDbContext`. El tiempo de vida por defecto es *scoped*: una instancia por petición, que se libera al terminar.

```csharp
builder.Services.AddDbContext<BlogContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("Blog")));
```

En desarrollo, SQLite es cómodo porque no exige un servidor. En producción, SQL Server, PostgreSQL o MySQL suelen ser la elección. El proveedor se cambia en una línea; el código LINQ no.

## Consultar

Las consultas se escriben en LINQ y se ejecutan al materializar el resultado:

```csharp
var recientes = await _context.Posts
    .Where(p => p.Published)
    .OrderByDescending(p => p.Date)
    .Select(p => new PostSummary(p.Id, p.Title, p.Date))
    .Take(10)
    .ToListAsync(token);
```

`ToListAsync`, `FirstOrDefaultAsync`, `CountAsync` y `AnyAsync` son las versiones asíncronas. Se usan siempre que la consulta vaya a la base de datos: bloquean menos y liberan el hilo del servidor. `AsNoTracking()` evita el seguimiento de cambios cuando el resultado solo se va a leer; reduce memoria y acelera la consulta.

`Include` carga una relación:

```csharp
var post = await _context.Posts
    .Include(p => p.Comments)
    .FirstOrDefaultAsync(p => p.Id == id, token);
```

Sin `Include`, la colección llega vacía o se carga en una consulta adicional al acceder a ella (*lazy loading*), que en un bucle produce el problema N+1: una consulta por elemento. `AsSplitQuery()` separa las colecciones grandes en varias consultas para evitar un producto cartesiano; `AsSingleQuery` es el comportamiento por defecto.

## Proyectar y paginar

Devolver la entidad completa a una vista o a una API acopla el contrato a la base de datos. Una proyección a un DTO o a un modelo de vista evita ese acoplamiento y trae solo las columnas necesarias:

```csharp
var page = await _context.Posts
    .OrderByDescending(p => p.Date)
    .Skip((pagina - 1) * tamano)
    .Take(tamano)
    .Select(p => new PostDto(p.Id, p.Title, p.Author))
    .ToListAsync(token);
```

La paginación con `Skip` y `Take` necesita un orden estable. Sin `OrderBy`, la base de datos puede devolver las filas en cualquier orden y una página puede repetir o perder elementos.

## Modificar

El contexto sigue los cambios de las entidades que carga. Para crear, se añade; para modificar, se cambia una propiedad; para borrar, se elimina:

```csharp
var post = await _context.Posts.FindAsync(id);
if (post is null) return NotFound();

post.Title = input.Title;
await _context.SaveChangesAsync(token);
```

`SaveChangesAsync` agrupa los cambios en una transacción. Si una operación afecta a varias entidades y debe ser atómica, se guarda una vez al final, no en cada paso. Para operaciones que no encajan en el seguimiento de cambios, se usa `ExecuteUpdateAsync` o `ExecuteDeleteAsync`, que ejecutan una sola sentencia sin cargar las entidades.

## Migraciones

El esquema se versiona con migraciones. Cada cambio del modelo se convierte en un archivo con las instrucciones para aplicarlo y revertirlo:

```bash
dotnet ef migrations add InitialCreate
dotnet ef database update
```

`dotnet ef` es una herramienta global (`dotnet tool install --global dotnet-ef`) y necesita el paquete `Microsoft.EntityFrameworkCore.Design` en el proyecto. Las migraciones se guardan en el repositorio y se aplican en el despliegue, no al arrancar cada instancia. Una migración destructiva se planifica con cuidado: la versión anterior puede seguir ejecutándose mientras la nueva se despliega.

En desarrollo, `EnsureCreated()` crea la base de datos a partir del modelo sin migraciones. Es cómodo para una prueba y una mala idea para producción: no permite evolucionar el esquema sin perder datos.

## Datos iniciales

La siembra (*seeding*) llena la base con datos imprescindibles: roles, categorías, un usuario administrador. `HasData` en `OnModelCreating` genera los insertos en la migración; un inicializador en el arranque sirve para datos que dependen de lógica o de otros servicios. La siembra debe ser idempotente: ejecutarla dos veces no puede duplicar filas.

## Repositorios y servicios

Un repositorio encapsula las consultas y permite cambiar el almacén o probar el servicio sin base de datos. No es obligatorio: en una aplicación pequeña, el `DbContext` inyectado en el servicio es suficiente y evita una capa de indirección. Cuando se usa, el repositorio devuelve entidades o DTO, no `IQueryable`; devolver la consulta deja al consumidor componer SQL y rompe el aislamiento.

El servicio de aplicación coordina varios repositorios y decide la transacción. El controlador no debe saber si hay EF debajo.

## Errores frecuentes

- **Contexto compartido entre peticiones.** Un `DbContext` no es seguro para usos concurrentes; se registra *scoped* y no se guarda en un *singleton*.
- **N+1.** Cargar una colección dentro de un bucle dispara una consulta por elemento. Se resuelve con `Include` o una proyección.
- **Traer toda la tabla.** Un `ToList()` sin filtro ni paginación funciona en desarrollo y tumba el servidor con datos reales.
- **Consultas que no se traducen.** Una función de C# que EF no entiende puede evaluarse en memoria o lanzar una excepción. Se revisa el SQL generado con `ToQueryString()`.
- **Cambios perdidos.** Dos usuarios cargan la misma fila y el último `SaveChanges` pisa al primero. Un `RowVersion` y `[Timestamp]` permiten detectar el conflicto.
- **Inyección de SQL.** LINQ parametriza los valores; el SQL crudo interpolado, no. Se usan parámetros o `FromSqlInterpolated`.

## Cuándo no usar EF Core

Para consultas muy complejas, informes con SQL específico o un rendimiento que el ORM no alcanza, Dapper o SQL directo son más adecuados. También en una aplicación mínima donde una tabla y dos consultas no justifican el mapeo. La decisión no es ideológica: se elige lo que el equipo puede mantener y lo que el requisito de rendimiento permite.
