# Layouts y vistas parciales

Una aplicación MVC tiene páginas que comparten cabecera, navegación y pie. Repetir esa estructura en cada vista multiplica el trabajo y garantiza que un cambio se olvide en alguna. Los layouts, las parciales y los componentes de vista resuelven la reutilización en tres niveles distintos.

## Layouts

Un layout es una plantilla con la estructura común y un hueco para el contenido. Por convención se llama `_Layout.cshtml` y vive en `Views/Shared`, aunque puede haber varios y una vista puede elegir el suyo:

```cshtml
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>@ViewData["Title"] - Mi sitio</title>
    <link rel="stylesheet" href="~/css/site.css" asp-append-version="true" />
</head>
<body>
    <header>
        <nav>
            <a asp-controller="Home" asp-action="Index">Inicio</a>
            <a asp-controller="Posts" asp-action="Index">Artículos</a>
        </nav>
    </header>
    <main>
        @RenderBody()
    </main>
    <footer>© @DateTime.Now.Year</footer>
    @await RenderSectionAsync("Scripts", required: false)
</body>
</html>
```

`RenderBody()` es el hueco obligatorio donde se inserta la vista. `RenderSection` inserta una sección nombrada; si `required` es `false`, la vista puede no definirla. `asp-append-version="true"` añade una huella al archivo estático para evitar que el navegador use una versión vieja.

La vista elige el layout en `_ViewStart.cshtml` o en su propio bloque:

```cshtml
@{
    Layout = "_Layout";
    ViewData["Title"] = "Artículos";
}
```

`ViewData` es un diccionario débilmente tipado que viaja del controlador a la vista. Para datos estructurados conviene `ViewBag` solo en casos simples o, mejor, un modelo de vista. `ViewData["Title"]` es la convención que usan las plantillas para el título.

## _ViewStart y _ViewImports

`_ViewStart.cshtml` se ejecuta antes de cada vista de contenido y sirve para inicializar valores comunes, sobre todo el layout. Afecta a la carpeta donde está y a sus subcarpetas, así que se puede tener uno en `Views/` y otro en `Views/Admin/` con un layout distinto.

`_ViewImports.cshtml` no ejecuta código: declara directivas que se aplican a las vistas de su carpeta y de sus subcarpetas. Es el sitio para los `@using` comunes, el `@addTagHelper` de los tag helpers de MVC y el `@inject` de servicios transversales.

```cshtml
@using MiApp.ViewModels
@addTagHelper *, Microsoft.AspNetCore.Mvc.TagHelpers
```

Sin `@addTagHelper`, los tag helpers como `asp-for` no se activan. La plantilla lo incluye; si una vista nueva no los reconoce, se revisa ese archivo.

## Vistas parciales

Una parcial es un fragmento de HTML sin layout. Se usa para repetir una tarjeta, una tabla, un formulario o un mensaje:

```cshtml
@model PostSummaryViewModel

<article class="card">
    <h2>@Model.Title</h2>
    <p>@Model.Excerpt</p>
    <a asp-action="View" asp-route-id="@Model.Id">Leer más</a>
</article>
```

Se incluye desde otra vista:

```cshtml
@foreach (var post in Model.Posts)
{
    <partial name="_PostSummary" model="post" />
}
```

El tag helper `<partial>` pasa el modelo y busca la plantilla por nombre. `Html.PartialAsync` hace lo mismo desde código. La inclusión es del lado del servidor: la respuesta sale con el HTML ya compuesto. Si se quiere actualizar solo una zona después de cargar la página, eso es AJAX y se explica en [AJAX](ajax.md).

Las parciales también se devuelven desde un controlador con `PartialView("_Nombre", modelo)`. Es lo habitual en una petición AJAX que espera HTML.

## Secciones

Una sección permite que una vista inyecte contenido en un punto concreto del layout, normalmente scripts al final del body:

```cshtml
@section Scripts {
    <script src="~/js/posts.js" asp-append-version="true"></script>
}
```

El layout debe renderizar la sección; si no, el contenido se ignora. Una sección declarada como `required: true` obliga a todas las vistas a definirla. Es útil para un layout de administración que necesita un script común, pero rompe las vistas que no lo tienen.

## Componentes de vista

Un componente de vista es una pieza con lógica y dependencias propias. Se diferencia de una parcial en que no recibe solo un modelo: ejecuta código, puede consultar servicios y tiene su propio ciclo de vida.

```csharp
public class RecentPostsViewComponent : ViewComponent
{
    private readonly IPostServices _posts;

    public RecentPostsViewComponent(IPostServices posts)
    {
        _posts = posts;
    }

    public async Task<IViewComponentResult> InvokeAsync(int count = 5)
    {
        var posts = await _posts.GetLatestAsync(count);
        return View(posts);
    }
}
```

La vista vive en `Views/Shared/Components/RecentPosts/Default.cshtml`. Se invoca con `<vc:recent-posts count="3" />` si se registra el tag helper, o con `@await Component.InvokeAsync("RecentPosts", new { count = 3 })`.

El componente es la opción cuando el fragmento necesita una consulta, una dependencia o parámetros. Una parcial es suficiente cuando solo recibe datos ya cargados. Abusar de componentes convierte una página en una colección de consultas difíciles de seguir; conviene que el controlador cargue lo principal y que el componente se reserve para lo independiente.

## Dónde va cada cosa

- **Layout**: estructura común, navegación, scripts globales.
- **Sección**: contenido que una página añade al layout.
- **Parcial**: fragmento sin lógica propia, reutilizado con un modelo.
- **Componente**: fragmento con lógica y dependencias.
- **Vista de contenido**: la página concreta, con su modelo y su título.

La regla es no subir de nivel sin necesidad. Una tarjeta que solo pinta datos es una parcial; una que consulta los últimos artículos es un componente; la estructura que comparten todas las páginas es el layout.

## Organización y búsqueda

Razor busca una vista en `Views/{Controlador}/{Nombre}.cshtml` y, si no la encuentra, en `Views/Shared/{Nombre}.cshtml`. Las áreas añaden `Areas/{Área}/Views/...`. Si una vista no aparece, el error de Razor muestra las rutas que probó; casi siempre el nombre o la carpeta no coinciden.

Las parciales suelen empezar por guion bajo (`_PostSummary.cshtml`) para distinguirlas, pero no es obligatorio. El guion bajo no cambia el comportamiento; es una convención de lectura.

## Rendimiento

Cada parcial y cada componente añade trabajo al renderizado. En una página con cien tarjetas, cien parciales son razonables si solo pintan datos; cien componentes con una consulta cada uno, no. La solución es cargar en el controlador y repartir el modelo, no hacer que cada fragmento consulte la base de datos por su cuenta.

Razor compila las vistas en el build por defecto. La compilación en tiempo de ejecución (`AddRazorRuntimeCompilation`) permite editar un `.cshtml` sin recompilar, a cambio de arrancar más lento y de un paquete adicional. Se usa en desarrollo, no en producción salvo una necesidad muy concreta.
