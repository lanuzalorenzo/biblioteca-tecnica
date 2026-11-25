# Internacionalización

Internacionalizar una aplicación es prepararla para convivir con varias culturas e idiomas; localizarla es darle los textos concretos de una de ellas. El sector lo llama I18N: la «I», los dieciocho caracteres que hay entre la primera y la última letra de *internationalization* y la «N» final.

ASP.NET Core resuelve el problema en tres piezas. La cultura de la petición decide cómo se formatean fechas, números y monedas. Los recursos `.resx` y `IStringLocalizer` dan acceso a los textos de cada idioma. Y el *middleware* de localización elige la cultura de cada visitante a partir de la petición, sin que el código de la aplicación tenga que mirar cabeceras ni cookies.

## La cultura de la petición

Cada hilo de ejecución lleva dos objetos `CultureInfo`. `CurrentCulture` manda en el formato de fechas, números y monedas; `CurrentUICulture`, en el idioma de los textos. Los dos arrancan con la cultura del sistema donde corre la aplicación, que no se controla: un equipo de desarrollo en «es-ES» y un servidor en «en-US» formatean distinto la misma fecha.

Para fijar una cultura por defecto se asignan en el arranque las propiedades `DefaultThreadCurrentCulture` y `DefaultThreadCurrentUICulture`. La asignación afecta a los hilos nuevos, así que se hace antes de recibir peticiones:

```csharp
var cultura = new CultureInfo("es-ES");
CultureInfo.DefaultThreadCurrentCulture = cultura;
CultureInfo.DefaultThreadCurrentUICulture = cultura;
```

Un *middleware* propio puede cambiar la cultura de cada petición con cualquier criterio, por ejemplo el prefijo de la ruta:

```csharp
public class SetCultureMiddleware
{
    private readonly RequestDelegate _next;

    public SetCultureMiddleware(RequestDelegate next)
    {
        _next = next;
    }

    public async Task Invoke(HttpContext context)
    {
        if (context.Request.Path.StartsWithSegments("/es"))
        {
            var culture = new CultureInfo("es-ES");
            CultureInfo.CurrentCulture = culture;
            CultureInfo.CurrentUICulture = culture;
        }

        await _next(context);
    }
}
```

El cambio dura lo que dura la petición. Un *middleware* posterior que escriba la cultura activa devolverá «es-ES» para `/es` y la cultura por defecto para el resto de rutas.

## Localización de textos

El paquete `Microsoft.Extensions.Localization`, incluido en `Microsoft.AspNetCore.App`, aporta `IStringLocalizer<T>`. El localizador se pide al contenedor de dependencias y devuelve el texto de la cultura activa a partir de una clave. Los textos viven en archivos `.resx` dentro de la carpeta que fija `ResourcesPath`:

```csharp
builder.Services.AddLocalization(options => options.ResourcesPath = "Resources");
```

El nombre del archivo sigue el de la clase, con un punto y la cultura delante de la extensión. Para la clase `HelloWorldMiddleware` del espacio de nombres `LocalizationDemo.Middlewares`, los recursos son `Resources/Middlewares.HelloWorldMiddleware.es-ES.resx` y su pareja en `en-US`. La regla completa:

- El archivo se llama como la clase completamente calificada, sin el espacio de nombres por defecto del proyecto.
- Los puntos del espacio de nombres pueden sustituirse por carpetas: `Resources/Middlewares/HelloWorldMiddleware.es-ES.resx`.
- La cultura puede ser completa (`es-ES`) o solo el idioma (`es`).
- La búsqueda va en cascada: primero `es-ES`, después `es`, y por último el archivo sin cultura.

Con los recursos creados, el localizador se usa como un diccionario. La clave devuelve el texto de la cultura activa:

```csharp
public class HelloWorldMiddleware
{
    private readonly RequestDelegate _next;
    private readonly IStringLocalizer<HelloWorldMiddleware> _loc;

    public HelloWorldMiddleware(RequestDelegate next,
        IStringLocalizer<HelloWorldMiddleware> loc)
    {
        _next = next;
        _loc = loc;
    }

    public async Task Invoke(HttpContext context)
    {
        var culture = CultureInfo.CurrentCulture.Name;
        var text = _loc["Message"];
        await context.Response.WriteAsync($"{text} ({culture})");
    }
}
```

Si la clave no existe, el localizador devuelve la propia clave. Los argumentos que siguen a la clave se pasan por `string.Format`, así que un texto con `{0}` se rellena con el valor indicado. Eso permite escribir el texto por defecto como clave y traducirlo solo en los idiomas que lo necesiten, sin crear un `.resx` para el idioma base:

```csharp
var text = _loc["Hola. Cultura actual: {0}", culture];
```

El atajo tiene un coste: las claves dejan de ser identificadores estables y pasan a ser el texto en la cultura por defecto. Cambiar una coma del texto obliga a cambiar la clave en todos los recursos traducidos.

## El middleware de localización

Elegir la cultura con un criterio propio funciona, pero la necesidad es tan común que el *framework* trae su propio *middleware*: `RequestLocalizationMiddleware`, en `Microsoft.AspNetCore.Localization`. Se configura con las culturas soportadas y la cultura por defecto, y se añade al pipeline:

```csharp
var supportedCultures = new[] { "es-ES", "en-US" };

var locOptions = new RequestLocalizationOptions
{
    DefaultRequestCulture = new RequestCulture("es-ES"),
    SupportedCultures = supportedCultures.Select(c => new CultureInfo(c)).ToList(),
    SupportedUICultures = supportedCultures.Select(c => new CultureInfo(c)).ToList()
};

app.UseRequestLocalization(locOptions);
```

Los objetos `Culture` y `UICulture` se configuran por separado: el primero formatea fechas y números, el segundo elige los textos. El *middleware* consulta una lista de proveedores en orden hasta que uno devuelve una cultura válida. Si ninguno lo consigue, o la cultura pedida no está entre las soportadas, aplica `DefaultRequestCulture`. De fábrica vienen tres:

1. `QueryStringRequestCultureProvider`, que lee los parámetros `culture` y `ui-culture` de la URL. Una petición a `https://localhost:5001/?culture=es-ES&ui-culture=es-ES` fija las dos culturas; con un solo parámetro se fijan ambas.
2. `CookieRequestCultureProvider`, que lee la cookie `.AspNetCore.Culture`. Como la cookie persiste, es el método habitual para recordar la elección entre peticiones.
3. `AcceptLanguageHeaderRequestCultureProvider`, que usa el encabezado `Accept-Language` que envía el navegador.

Los nombres de los parámetros y de la cookie se pueden cambiar. También se puede escribir una cookie con la cultura elegida desde un endpoint:

```csharp
app.MapGet("culture/{culture}", (HttpContext ctx, string culture) =>
{
    ctx.Response.Cookies.Append(
        key: CookieRequestCultureProvider.DefaultCookieName,
        value: CookieRequestCultureProvider.MakeCookieValue(new RequestCulture(culture)),
        options: new CookieOptions { Expires = DateTimeOffset.MaxValue });

    return $"Cultura: {culture}";
});
```

El valor de la cookie no es el nombre de la cultura a secas: se construye con `MakeCookieValue`, que aplica el formato que espera el proveedor.

Si sobra un proveedor o cambia el orden, se toca la colección `RequestCultureProviders`:

```csharp
var aceptaIdiomas = locOptions.RequestCultureProviders
    .OfType<AcceptLanguageHeaderRequestCultureProvider>()
    .FirstOrDefault();

if (aceptaIdiomas is not null)
{
    locOptions.RequestCultureProviders.Remove(aceptaIdiomas);
}
```

Para criterios propios existe `CustomRequestCultureProvider`, que recibe la petición y devuelve una cultura o `null`. El ejemplo elige «es-ES» cuando el host empieza por `es.`:

```csharp
locOptions.RequestCultureProviders.Insert(0,
    new CustomRequestCultureProvider(ctx =>
    {
        var host = ctx.Request.Host.Host.ToLowerInvariant();
        return host.StartsWith("es.")
            ? Task.FromResult<ProviderCultureResult?>(new ProviderCultureResult("es-ES"))
            : Task.FromResult<ProviderCultureResult?>(null);
    }));
```

## Localizar validaciones y vistas

Las anotaciones de datos aceptan un `ErrorMessage` que puede ser una clave de recurso en lugar de un texto. Con `AddDataAnnotationsLocalization` y un `IStringLocalizer` compartido, los mensajes de validación se traducen como el resto. En las vistas, `IViewLocalizer` resuelve los textos de la página actual y `IStringLocalizer<T>` sirve para los servicios.

## Qué no se traduce

Los nombres de rutas, los identificadores internos, los códigos de estado y los datos que consume otra máquina no se traducen. La cultura afecta a la presentación, no al contrato. Una API que devuelve fechas en formato local en lugar de ISO 8601 crea un problema al cliente que no se arregla con más recursos.
