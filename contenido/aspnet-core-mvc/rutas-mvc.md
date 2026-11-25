# Rutas de MVC

El routing es el puente entre una URL y el código que la atiende. En MVC hay dos formas de declararlo: por convención, con un patrón común para todos los controladores, y por atributos, escribiendo la ruta junto a la acción. Las dos conviven y conviene saber cuándo usar cada una.

## Rutas por convención

La plantilla de MVC declara una ruta por defecto:

```csharp
app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");
```

El patrón tiene tres segmentos. `controller` y `action` identifican el controlador y el método; `id` es opcional por la interrogación. Los valores tras el signo igual son los que se usan cuando el segmento no aparece. Una petición a `/` ejecuta `HomeController.Index`; `/Posts` ejecuta `PostsController.Index`; `/Posts/View/18` ejecuta `PostsController.View(18)`.

El orden de las rutas importa. La primera que coincide es la que se ejecuta, así que una ruta genérica colocada antes tapa a las específicas que vengan detrás. Las rutas más concretas se declaran primero.

### Valores por defecto y restricciones

`MapControllerRoute` acepta `defaults` y `constraints` además del patrón:

```csharp
app.MapControllerRoute(
    name: "blog",
    pattern: "blog/{year:int}/{month:int}",
    defaults: new { controller = "Blog", action = "Archive" },
    constraints: new { year = @"20\d{2}" });
```

Los valores por defecto rellenan lo que la URL no trae. Las restricciones limitan el tipo o el formato; una petición que no las cumple no entra en esa ruta y sigue probando las siguientes. Las restricciones en línea (`{id:int}`) son más legibles y suficientes en la mayoría de los casos.

### Nombres de ruta

El parámetro `name` permite referirse a la ruta desde el código y desde las vistas:

```csharp
app.MapControllerRoute(
    name: "post-by-id",
    pattern: "post/{id:int}",
    defaults: new { controller = "Posts", action = "View" });
```

Generar un enlace por nombre evita escribir la URL a mano y evita que un cambio de patrón deje enlaces rotos:

```csharp
var url = Url.RouteUrl("post-by-id", new { id = 18 });
```

Los nombres deben ser únicos. Un nombre repetido no siempre falla al arrancar, y el enlace generado puede apuntar a la ruta equivocada.

## Rutas por atributos

El routing por atributos declara la ruta junto a la acción. Es la forma natural de una API y también sirve para páginas con URLs estables:

```csharp
[Route("product/{category}/{product}")]
public IActionResult Show(string category, string product)
{
    return Content($"Categoría: {category}, producto: {product}");
}
```

Una vez que una acción lleva `[Route]`, deja de ser accesible por la ruta por convención. Esa es la diferencia que más sorprende al mezclar los dos sistemas.

Una acción puede tener varias rutas:

```csharp
[Route("catalog/{category}")]
[Route("browse/{category}")]
public IActionResult Index(string category) { /* ... */ }
```

Y un controlador puede llevar el prefijo común:

```csharp
[Route("api/[controller]")]
public class ProductsController : ControllerBase
{
    [HttpGet("{id:int}")]
    public IActionResult Get(int id) { /* ... */ }
}
```

Los tokens `[controller]` y `[action]` se sustituyen por el nombre del controlador y de la acción sin el sufijo `Controller`. Así, renombrar la clase actualiza la ruta. El token `[area]` hace lo propio con el área.

### Verbos y selección

`[HttpGet]`, `[HttpPost]`, `[HttpPut]`, `[HttpPatch]` y `[HttpDelete]` limitan la acción a un verbo. `[AcceptVerbs]` acepta una lista. Sin atributo de verbo, la acción responde a cualquiera, lo que casi nunca es lo que se quiere en una API.

```csharp
[HttpGet("posts/{id:int}")]
public IActionResult GetPost(int id) { /* ... */ }
```

En MVC, la combinación de ruta y verbo forma el endpoint. Dos acciones con la misma ruta y verbos distintos conviven; dos con la misma ruta y el mismo verbo producen una ambigüedad que se detecta al arrancar o en la primera petición.

## Generación de URL

Escribir `/Posts/View/18` en una vista es frágil. MVC ofrece helpers que construyen la URL a partir del controlador, la acción y los valores:

```cshtml
<a asp-controller="Posts" asp-action="View" asp-route-id="@post.Id">@post.Title</a>
```

El tag helper `asp-controller`, `asp-action` y `asp-route-*` genera el `href` con la ruta correcta. En código C# se usan `Url.Action("View", "Posts", new { id = 18 })` o `LinkGenerator`. La ventaja es la misma: si cambia el patrón, el enlace se actualiza solo.

La generación también sirve para mantener una URL canónica. Si una ruta admite varios formatos, se genera siempre el que se considera oficial.

## Áreas

Un área agrupa controladores, vistas y modelos de un módulo funcional dentro de la misma aplicación: un blog, un foro, una administración. Físicamente vive en `Areas/{Nombre}/`, con sus carpetas `Controllers` y `Views`.

El controlador se marca con `[Area]`:

```csharp
[Area("Blog")]
public class HomeController : Controller
{
    public IActionResult Index() => View();
}
```

La ruta por convención se declara con `MapAreaControllerRoute`:

```csharp
app.MapAreaControllerRoute(
    name: "blog",
    areaName: "Blog",
    pattern: "blog/{controller=Home}/{action=Index}/{id?}");
```

Con rutas por atributo se usa el token `[area]`:

```csharp
[Area("Blog")]
[Route("[area]/[controller]")]
public class HomeController : Controller { /* ... */ }
```

Las vistas de un área se buscan en `Areas/{Área}/Views/{Controlador}` y en `Areas/{Área}/Views/Shared`; si no aparecen, se recurre a `Views/Shared` de la raíz. Los enlaces a una acción de un área incluyen `asp-area` o el parámetro `area` en `Url.Action`.

Un área no es un proyecto separado ni un ensamblado: es una convención de organización dentro de la misma aplicación. Para módulos que deben compilarse y desplegarse por separado, la respuesta es una biblioteca de clases o un servicio aparte, no un área.

## Cuándo usar cada sistema

La ruta por convención sirve para las páginas de una aplicación MVC con una estructura regular: un controlador por recurso y acciones con nombres previsibles. El routing por atributos sirve cuando la URL debe ser estable e independiente del nombre de la clase, cuando se mezclan verbos y cuando se publica una API. Lo habitual es tener la ruta por defecto para las páginas y atributos para los endpoints que necesitan una URL propia.

## Comprobar las rutas

Las rutas se comprueban arrancando la aplicación y pidiendo las URLs reales, no leyendo el código. Un 404 indica que ninguna ruta coincide; un 405, que coincide pero el verbo no está permitido; una excepción de ambigüedad, que dos endpoints compiten. Las tres se ven en el registro de arranque o en la respuesta, y las tres se arreglan en la declaración, no en el controlador.
