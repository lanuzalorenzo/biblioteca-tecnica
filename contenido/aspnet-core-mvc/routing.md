# Routing

Decidir qué código atiende cada dirección es una necesidad de cualquier aplicación web. ASP.NET Core trae dos sistemas que hacen ese trabajo: el routing básico, más antiguo, y *endpoint routing*, que es el recomendado desde la versión 3.0. MVC, Razor Pages y las API mínimas se apoyan en el segundo.

## Dos sistemas y una diferencia

El routing básico une en un solo paso tres cosas: analizar la ruta, decidir qué *handler* la atiende y ejecutarlo. Es simple y suficiente para aplicaciones pequeñas, pero acopla la decisión a la ejecución, y eso complica combinar componentes transversales —autorización, CORS— con *frameworks* de más alto nivel como MVC.

*Endpoint routing* separa las dos mitades. Un *middleware* analiza la petición y deja anotado qué endpoint la atenderá; otro, situado más adelante, lo ejecuta. Entre los dos queda un hueco por el que cualquier *middleware* puede consultar cuál será el endpoint y actuar en consecuencia, que es justo lo que necesita una comprobación de permisos.

## Rutado básico

El sistema se apoya en el paquete `Microsoft.AspNetCore.Routing`. En una aplicación web, el host ya deja registrados sus servicios, así que el routing básico funciona sin tocar nada. Las rutas se declaran con un `RouteBuilder`:

```csharp
var routes = new RouteBuilder(app);
routes.MapGet("hello", async context =>
{
    await context.Response.WriteAsync("Hello world!");
});
routes.MapPost("post-test", async context =>
{
    await context.Response.WriteAsync("This is a post!");
});
app.UseRouter(routes.Build());
```

`MapGet()`, `MapPost()`, `MapPut()` y compañía cubren los verbos de HTTP. Cuando llega una petición, el *middleware* busca la primera ruta que coincida y ejecuta su *handler*; si ninguna encaja, la deja seguir por el pipeline. No hay comprobación de duplicados ni de ambigüedad: **manda el orden de declaración**, así que una ruta genérica colocada antes tapa a las que vengan detrás.

En código nuevo no se usa. Las API mínimas declaran endpoints sobre `app` y MVC usa sus propios mapeos; el routing básico queda para aplicaciones pequeñas o para entender de dónde viene el sistema.

## Endpoint routing

Aquí hay dos *middlewares*, cada uno con una misión. `EndpointRoutingMiddleware` analiza la ruta y anota el endpoint elegido en el contexto. `EndpointMiddleware` lo recoge y lo ejecuta. El orden en el pipeline es el que se acaba de describir, sin excepciones.

Ese tramo intermedio es la razón de ser del sistema. Un *middleware* de autorización colocado entre ambos sabe qué endpoint se va a ejecutar y puede decidir si lo permite antes de que se ejecute; con el routing básico esa información no existía en ese punto.

## Ponerlo en marcha

`UseRouting()` añade el primero de los *middlewares*. El segundo lo añade el mapeo de endpoints: `MapControllerRoute`, `MapControllers`, `MapRazorPages` o `MapGet`. En MVC, la ruta por convención se declara así:

```csharp
app.UseRouting();

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");
```

`MapControllerRoute` registra el patrón y el endpoint que ejecuta el controlador y la acción correspondientes. `MapControllers()` registra solo las acciones decoradas con rutas por atributo. `MapFallback()` cubre lo que no encaja en ninguno de los anteriores.

Si la aplicación sirve archivos estáticos, `UseStaticFiles()` va **antes** de `UseRouting()`: esos archivos no necesitan pasar por el análisis de rutas y se entregan antes.

## Qué ocurre con cada petición

El primer *middleware* analiza ruta y verbo y se encuentra con tres desenlaces posibles. Si hay un endpoint compatible, lo anota en el contexto. Si hay varios, lanza `AmbiguousMatchException`, que se ve con detalle si la página de desarrollo está al principio. Si no hay ninguno, no hace nada y la petición sigue su camino.

Más adelante, el segundo *middleware* comprueba si el contexto lleva endpoint. Si lo lleva, lo ejecuta y la petición termina ahí; si no, la deja pasar para que la atienda quien pueda. Por eso un 404 sin cuerpo es el resultado normal de una ruta que no encaja y ningún *middleware* posterior responde.

## Consultar el endpoint elegido

Cualquier *middleware* situado después de `UseRouting()` puede preguntar por el endpoint con `GetEndpoint()`. El siguiente ejemplo lo anota en el registro antes de que se ejecute; cuando no hay endpoint, avisa:

```csharp
app.UseRouting();
app.Use(async (contexto, siguiente) =>
{
    var endpoint = contexto.GetEndpoint();
    if (endpoint is null)
    {
        app.Logger.LogWarning("No hay endpoint para esta petición");
    }
    else
    {
        app.Logger.LogInformation("{Endpoint}", endpoint);
    }
    await siguiente();
});
```

La representación textual de un endpoint es su plantilla y su verbo: `/ HTTP: GET`. Además del delegado, un endpoint puede llevar metadatos que otros componentes leen. Los extensores de mapeo permiten añadirlos sin salir de la declaración:

```csharp
app.MapGet("/another/test", () => "Test")
   .RequireAuthorization()
   .WithDisplayName("Prueba");
```

`RequireAuthorization()` no autoriza por sí mismo: deja una marca que el *middleware* de autorización consulta cuando le toca. `WithDisplayName()` da un nombre legible y `WithMetadata()` añade objetos arbitrarios, disponibles luego en la propiedad `Metadata`.

## Parámetros en la ruta

Una plantilla puede mezclar tramos fijos y tramos variables entre llaves. Cada variable se recupera después con `GetRouteValue()`:

```csharp
app.MapGet("/hello/{name}", (string name) => $"Hola, {name}!");
```

En un endpoint mínimo el parámetro llega por enlace directo; con un `HttpContext`, se lee con `GetRouteValue("name")`. Un patrón como `/catalog/{family}/{subfamily}/{id}` convierte cada llave en un par clave-valor. Para `/catalog/computers/netbooks/lenovo-yoga` se obtienen `family=computers`, `subfamily=netbooks` e `id=lenovo-yoga`.

Los parámetros admiten dos modificadores. La interrogación los hace opcionales y el signo igual fija un valor por defecto: `/catalog/browse/{currentPage?}` y `/catalog/browse/{currentPage=1}`. El parámetro *catch-all*, escrito `{*data}`, captura todos los segmentos que quedan hasta el final, sin incluir la cadena de consulta: en `/catalog/it/seems/it/is/raining?when=now`, `data` vale `it/seems/it/is/raining`.

## Restricciones en línea

Una restricción limita qué valores acepta un parámetro y se escribe tras dos puntos. Con `/product/edit/{id:int}`, una petición a `/product/edit/4` entra y una a `/product/edit/lenovo-yoga` no llega a ese endpoint, porque el análisis la descarta.

| Restricción | Ejemplo | Acepta |
|---|---|---|
| `int` | `{id:int}` | Un entero |
| `bool` | `{activo:bool}` | `true` o `false` |
| `datetime` | `{fecha:datetime}` | Una fecha en cultura invariable |
| `decimal` | `{precio:decimal}` | Un decimal válido |
| `double`, `float` | `{peso:double}` | Un número en coma flotante |
| `guid` | `{id:guid}` | Un identificador válido |
| `long` | `{ticks:long}` | Un entero largo |
| `minlength(n)` | `{usuario:minlength(5)}` | Cadena de n caracteres o más |
| `maxlength(n)` | `{archivo:maxlength(8)}` | Cadena de n caracteres o menos |
| `length(n)` | `{pin:length(4)}` | Cadena de longitud exacta |
| `length(a,b)` | `{archivo:length(4,16)}` | Cadena entre a y b caracteres |
| `min(n)` | `{edad:min(18)}` | Valor mayor o igual que n |
| `max(n)` | `{edad:max(120)}` | Valor menor o igual que n |
| `range(a,b)` | `{edad:range(18,120)}` | Valor dentro del intervalo |
| `alpha` | `{nombre:alpha}` | Solo letras |
| `regex(patrón)` | `{ssn:regex(^\d{{3}}-\d{{2}}-\d{{4}}$)}` | Coincide con la expresión |
| `required` | `{nombre:required}` | Obliga a que el parámetro aparezca al generar rutas |

Los tipos numéricos y de fecha se interpretan siempre en cultura invariable, porque una URL no se traduce. Las restricciones se pueden encadenar sobre el mismo parámetro, y los modificadores van al final: `/test/{data:alpha:length(3)?}` acepta `/test/abc` y `/test`, y rechaza `/test/123` y `/test/abcde`. En `regex()` las llaves del cuantificador se escapan doblando: una plantilla es texto con llaves y, sin doblarlas, el analizador cierra el parámetro antes de tiempo.

## Restricciones propias

Cuando ninguna de las anteriores sirve, se implementa `IRouteConstraint`, una interfaz del espacio de nombres `Microsoft.AspNetCore.Routing`. El método `Match()` recibe el contexto, el nombre del parámetro (`routeKey`), el diccionario de valores ya capturados y la dirección del tránsito, y devuelve si la petición pasa:

```csharp
public class EvenNumberConstraint : IRouteConstraint
{
    public bool Match(HttpContext httpContext, IRouter route,
        string routeKey, RouteValueDictionary values,
        RouteDirection routeDirection)
    {
        return int.TryParse(values[routeKey]?.ToString(), out var numero)
               && numero % 2 == 0;
    }
}
```

Después se le da un nombre y se registra en la tabla de restricciones, que es la que consulta el analizador al leer la plantilla:

```csharp
builder.Services.AddRouting(options =>
{
    options.ConstraintMap.Add("even", typeof(EvenNumberConstraint));
});

app.MapGet("/number/{i:even}", (int i) => $"El número par es {i}");
```

## Generar rutas

Una ruta no solo sirve para entrar: también se usa para construir enlaces. `LinkGenerator` genera una URL a partir del nombre de la ruta y los valores, y los helpers de MVC lo usan por debajo. Generar enlaces en lugar de escribirlos a mano evita que un cambio de plantilla deje enlaces rotos repartidos por las vistas.

## Dónde encaja MVC

MVC usa *endpoint routing* como cualquier otro componente. La diferencia está en cómo declara sus endpoints: `MapControllerRoute` para rutas por convención, `MapControllers` para rutas por atributo y `MapAreaControllerRoute` para áreas. El detalle de esas tres formas, con sus tokens y su generación de URL, está en [Rutas de MVC](rutas-mvc.md).
