# Caché de datos y respuestas

Una caché guarda una copia de datos costosos de obtener en un almacén rápido, para responder antes en la siguiente consulta. Es una optimización, no una fuente de verdad: la aplicación debe funcionar cuando la copia no está, y debe asumir que puede desaparecer en cualquier momento. Un mal uso llena la memoria de datos obsoletos; un buen uso quita trabajo repetido al servidor y a la base de datos.

ASP.NET Core permite elegir dónde vive esa copia. En memoria del propio servidor se gana velocidad, pero cada nodo tiene su copia y una granja de servidores puede desincronizarse. En un almacén distribuido —Redis o SQL Server, entre otros— los nodos comparten el contenido y este sobrevive a un reinicio, a cambio de una transferencia de datos por red. Las dos fórmulas pueden convivir en el mismo proyecto.

## Caché en memoria

El paquete `Microsoft.Extensions.Caching.Memory` aporta `IMemoryCache`, que se registra en el contenedor con `AddMemoryCache()`:

```csharp
builder.Services.AddMemoryCache();
```

A partir de ahí, cualquier componente pide `IMemoryCache` por constructor y lee o escribe con `Get`, `TryGetValue`, `Set` y `Remove`. El patrón habitual es intentar leer y, si no hay entrada, calcular el valor y guardarlo:

```csharp
if (!cache.TryGetValue("ultimasNoticias", out List<Noticia>? noticias))
{
    noticias = await _servicio.GetUltimasAsync();
    cache.Set("ultimasNoticias", noticias, new MemoryCacheEntryOptions
    {
        SlidingExpiration = TimeSpan.FromMinutes(5),
        AbsoluteExpirationRelativeToNow = TimeSpan.FromHours(1)
    });
}
```

En ese ejemplo, la entrada se conserva mientras alguien la pida al menos una vez cada cinco minutos, y en todo caso se elimina una hora después de guardarla. La prioridad se cambia con `Priority`: `Low` permite descartarla antes si falta memoria, y `NeverRemove` la deja fuera de la limpieza automática. Para invalidarla de forma explícita está `Remove("ultimasNoticias")`.

## Caché distribuida

El almacén distribuido vive fuera del proceso. Los datos se comparten entre nodos, la caché no se pierde al reiniciar un servidor y todos leen la misma copia, aunque cada acceso cuesta una llamada de red. ASP.NET Core trae adaptadores para Redis y SQL Server en paquetes separados: `Microsoft.Extensions.Caching.StackExchangeRedis` y `Microsoft.Extensions.Caching.SqlServer`.

El registro se hace con el extensor correspondiente. Este ejemplo configura SQL Server con una cadena de conexión y una tabla:

```csharp
builder.Services.AddDistributedSqlServerCache(options =>
{
    options.ConnectionString =
        builder.Configuration.GetConnectionString("Cache");
    options.SchemaName = "dbo";
    options.TableName = "TestCache";
});
```

Antes de usar SQL Server hay que crear la tabla con la herramienta del paquete. Redis se registra con `AddStackExchangeRedisCache`, que recibe la configuración del servidor. En ambos casos el acceso se hace por la interfaz `IDistributedCache`, que trabaja siempre con `byte[]` porque el valor viaja fuera del proceso:

```csharp
public interface IDistributedCache
{
    byte[]? Get(string key);
    Task<byte[]?> GetAsync(string key, CancellationToken token = default);
    void Set(string key, byte[] value, DistributedCacheEntryOptions options);
    Task SetAsync(string key, byte[] value,
        DistributedCacheEntryOptions options, CancellationToken token = default);
    void Refresh(string key);
    Task RefreshAsync(string key, CancellationToken token = default);
    void Remove(string key);
    Task RemoveAsync(string key, CancellationToken token = default);
}
```

Serializar y deserializar a mano en cada acceso es incómodo. Los extensores `SetString` y `GetString` cubren el caso de texto, y para objetos conviene elegir un formato —JSON, por ejemplo— y aplicarlo en un único punto. También existe `MemoryDistributedCache`, una implementación local de la misma interfaz. Sirve para no atar el código a un almacén concreto: en desarrollo se registra en memoria y en producción, Redis o SQL Server.

```csharp
if (builder.Environment.IsDevelopment())
{
    builder.Services.AddDistributedMemoryCache();
}
else
{
    builder.Services.AddStackExchangeRedisCache(options =>
    {
        options.Configuration = builder.Configuration.GetConnectionString("Redis");
        options.InstanceName = "MiApp:";
    });
}
```

## Caché de respuestas

`ResponseCachingMiddleware`, del paquete `Microsoft.AspNetCore.ResponseCaching`, guarda respuestas HTTP completas y las reutiliza cuando la petición vuelve a pedir lo mismo. Se registra con `AddResponseCaching()` —que ya incluye la caché en memoria— y se inserta en el pipeline con `UseResponseCaching()`:

```csharp
builder.Services.AddResponseCaching();
app.UseResponseCaching();

app.MapGet("/hora", (HttpContext ctx) =>
{
    ctx.Response.Headers.CacheControl = "public, max-age=20";
    return DateTime.Now.ToString("T");
});
```

La cabecera `Cache-Control` decide cuánto dura la copia; en el ejemplo, veinte segundos. El *middleware* no cachea cualquier respuesta: exige un código 200, métodos `GET` o `HEAD`, ausencia de `Authorization` y otras condiciones. Tampoco sustituye a una caché de datos: aquí se guarda el resultado ya montado, no el objeto que lo alimenta.

## Caché de salida

Desde .NET 7, `AddOutputCache()` y `UseOutputCache()` ofrecen una caché de salida más flexible que la de respuestas: se aplica por endpoint, admite políticas con nombre, etiquetas para invalidar y almacenamiento distribuido.

```csharp
builder.Services.AddOutputCache(options =>
{
    options.AddBasePolicy(policy => policy.Expire(TimeSpan.FromSeconds(30)));
});

app.UseOutputCache();
app.MapGet("/catalogo", () => ObtenerCatalogo()).CacheOutput();
```

Es la opción recomendada en código nuevo. La diferencia con `ResponseCaching` es que la decisión se declara en el endpoint y se puede invalidar por etiqueta, sin depender solo de las cabeceras HTTP.

## Qué recordar

La caché ahorra trabajo, pero no garantiza que el dato esté. El almacén se elige por lo que pide el despliegue —un nodo o varios, datos que deben sobrevivir a un reinicio— y conviene poner caducidad a todo. Una entrada sin fecha de salida es una fuga de memoria o un dato viejo que nadie revisa. Y toda caché necesita una forma de invalidación: si el dato cambia y la copia no se entera, el usuario ve una mentira.
