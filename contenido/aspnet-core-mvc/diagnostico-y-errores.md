# Diagnóstico y tratamiento de errores

Cuando una aplicación falla, lo primero que hace falta es saber por qué. ASP.NET Core trae las piezas para verlo durante el desarrollo y para responder sin filtraciones cuando el fallo ocurre delante de un usuario, pero el *framework* no añade ninguna por su cuenta: el *pipeline* hay que componerlo. La plantilla de proyecto solo activa la página detallada en desarrollo.

## La página detallada, solo en desarrollo

La página de errores para desarrolladores vive en el paquete `Microsoft.AspNetCore.Diagnostics`, incluido en el marco compartido. Se añade al *pipeline* con `UseDeveloperExceptionPage()`, y solo tiene sentido en el entorno de desarrollo:

```csharp
if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage();
}

app.MapGet("/boom", () =>
{
    throw new InvalidOperationException("Operación no válida");
});
```

Una petición a `/boom` lanza la excepción y el navegador muestra su tipo, su mensaje, la traza de pila y el código de la línea que falló. Esa información es exactamente la que no debe ver un cliente: en producción, la misma excepción devuelve un 500 sin cuerpo y sin detalles. Ese es el comportamiento por defecto, y no conviene cambiarlo.

## Por qué el orden del pipeline importa

El *middleware* de errores captura las excepciones de los componentes que vienen después. La petición baja por la cadena y la respuesta sube en sentido inverso; cuando algo lanza una excepción, el recorrido se interrumpe y el control vuelve hacia arriba hasta el primer componente que sepa tratarla.

Por eso el capturador se coloca al principio. Si se añade al final, la excepción ya ha pasado por delante de él y no la ve. El mismo razonamiento vale para cualquier *middleware* que envuelva a otros: trazas, cabeceras de seguridad o compresión tienen que entrar antes que lo que miden o protegen.

## Un mensaje propio para el usuario

En producción lo habitual es sustituir la página detallada por una respuesta amable. `UseExceptionHandler()` captura la excepción y reejecuta el *pipeline* contra una ruta indicada:

```csharp
if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage();
}
else
{
    app.UseExceptionHandler("/error");
}

app.UseStaticFiles();
app.UseRouting();

app.MapGet("/error", () => Results.StatusCode(500));
app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");
```

La ruta puede apuntar a una página estática de `wwwroot` o, mejor, a un endpoint propio como el anterior, que decide el contenido y el código de estado. La versión estática exige tener `UseStaticFiles()` en el *pipeline*, porque sin él la petición interna no encuentra el archivo.

Un detalle que se pasa por alto: el manejador vuelve a entrar por la misma cadena. Si la página de error necesita servicios o rutas, tienen que estar registrados antes de configurarla, y conviene evitar que la propia página de error lance otra excepción, porque entonces el resultado es un 500 vacío y una traza difícil de leer.

## Un manejador centralizado

Desde .NET 8, `IExceptionHandler` permite tratar la excepción en una clase, sin depender de una ruta de reejecución:

```csharp
public class ManejadorDeErrores : IExceptionHandler
{
    private readonly ILogger<ManejadorDeErrores> _logger;

    public ManejadorDeErrores(ILogger<ManejadorDeErrores> logger)
    {
        _logger = logger;
    }

    public async ValueTask<bool> TryHandleAsync(
        HttpContext context, Exception exception, CancellationToken token)
    {
        _logger.LogError(exception, "Fallo no controlado");
        context.Response.StatusCode = 500;
        await context.Response.WriteAsJsonAsync(new
        {
            error = "Se ha producido un error",
            traceId = context.TraceIdentifier
        }, token);
        return true;
    }
}

builder.Services.AddExceptionHandler<ManejadorDeErrores>();
app.UseExceptionHandler();
```

El `traceId` permite cruzar lo que ve el usuario con la traza del servidor. Devolver el mensaje de la excepción o la pila es una fuga de información: el cliente recibe un texto genérico y el detalle queda en el registro.

## Errores que no son excepciones

Un 404 no lanza nada: alguien responde con ese código y la aplicación sigue. Para esos casos existe `UseStatusCodePages()`, que captura las respuestas 4xx y 5xx sin cuerpo y añade un contenido mínimo con el código y su descripción:

```csharp
app.UseStatusCodePages();
```

Cualquier ruta no atendida sale con un 404 sin cuerpo, y el *middleware* lo convierte en una respuesta con el código y su descripción. La variante con argumentos permite escribir el texto y el tipo de contenido. También admite una función que reciba el contexto y decida qué devolver para cada código:

```csharp
app.UseStatusCodePages("text/plain", "Error HTTP {0}");
```

## Redirigir o reejecutar

Para no escribir esa lógica en cada proyecto hay dos extensores listos. Se parecen en el nombre y se comportan de forma distinta, y la diferencia se nota en la barra del navegador y en el código que recibe el cliente:

- `UseStatusCodePagesWithRedirects()` responde un 302 hacia la ruta indicada. El navegador cambia de URL y la página de destino se sirve con un 200, que es lo que conviene para un archivo estático.
- `UseStatusCodePagesWithReExecute()` repite el *pipeline* con otra ruta. La URL que escribió el cliente y el código original se conservan, que es lo correcto para un buscador y para un cliente de API.

Con la reejecución, el *middleware* que atiende la ruta interna puede consultar la petición original. La información viaja en `IStatusCodeReExecuteFeature`, accesible desde `HttpContext.Features`:

```csharp
app.UseStatusCodePagesWithReExecute("/error404");
```

La respuesta conserva el 404 y la URL que escribió el cliente, pero el cuerpo lo genera la aplicación. Es la forma de dar un mensaje útil sin mentir sobre lo ocurrido.

## Errores en una API

Una API no devuelve una página HTML. Devuelve un código de estado y un cuerpo estructurado, preferiblemente con el formato Problem Details. Un 400 por validación, un 404 por recurso inexistente y un 500 por fallo interno deben distinguirse, y el detalle técnico se queda en el registro. La nota [API HTTP](apis-rest.md) cubre ese contrato.

## Probar los tres casos

Una aplicación con errores bien tratados se comprueba en tres escenarios: una excepción controlada que debe mostrar la página propia, una ruta inexistente que debe devolver el 404 con cuerpo y una petición a una API que debe recibir JSON con el código correcto. Si los tres responden como se espera, el tratamiento está cerrado; si alguno devuelve una página de error del *framework*, falta un middleware o está en el orden equivocado.
