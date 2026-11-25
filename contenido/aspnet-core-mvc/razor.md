# Razor

Razor es el motor de vistas de ASP.NET Core MVC. Convierte un archivo `.cshtml` en una clase que escribe HTML, mezclando marcado con código C#. Su sintaxis está pensada para que el código sea la excepción y el marcado se lea como marcado: una arroba abre la puerta al servidor y el resto es HTML.

## Una vista mínima

```cshtml
@model MyApp.ViewModels.PostViewModel
@{
    ViewData["Title"] = Model.Title;
}

<h1>@Model.Title</h1>
<p>@Model.Body</p>
```

`@model` declara el tipo que recibe la vista. `@{}` abre un bloque de código que no escribe nada; en el ejemplo, asigna el título. `@Model.Title` es una expresión implícita: Razor detecta dónde termina y escribe el valor codificado.

## Expresiones y bloques

- `@expresión` escribe el resultado. Si la expresión contiene espacios o operadores que confunden al parser, se usa `@( ... )`.
- `@{ ... }` ejecuta código sin escribir.
- `@if`, `@foreach`, `@for`, `@while` y `@switch` controlan el marcado.
- `@* comentario *@` es un comentario de servidor; no llega al cliente.
- `@@` escribe una arroba literal, útil en un correo o en una mención.

```cshtml
@if (Model.Posts.Any())
{
    <ul>
        @foreach (var post in Model.Posts)
        {
            <li>@post.Title — @post.Date.ToString("d")</li>
        }
    </ul>
}
else
{
    <p>No hay artículos.</p>
}
```

Dentro de un bloque, el HTML se escribe sin arroba. Razor entiende el cambio de contexto y no hay que cerrar y abrir etiquetas de servidor como en otras tecnologías.

## Directivas

Las directivas se escriben al principio del archivo o en `_ViewImports.cshtml`:

- `@model Tipo` declara el modelo.
- `@using Espacio` importa un espacio de nombres.
- `@inject Servicio Nombre` inyecta un servicio en la vista.
- `@inherits Clase` cambia la clase base de la vista.
- `@functions { ... }` declara métodos o propiedades locales.
- `@addTagHelper`, `@removeTagHelper` y `@tagHelperPrefix` controlan los tag helpers.

```cshtml
@inject IStringLocalizer<HomeView> Localizer
@functions {
    string FormatDate(DateTime date) => date.ToString("yyyy-MM-dd");
}
```

`@functions` sirve para una función de presentación pequeña. Si la lógica crece, va a un helper, a un view component o al modelo de vista; una vista no es el sitio para reglas de negocio.

## Codificación

Razor codifica el HTML de las expresiones por defecto. Un título con `<script>` se muestra como texto, no se ejecuta. Esa protección evita la mayoría de los XSS y no hay que activarla: viene puesta.

Para escribir HTML que ya se sabe seguro se usa `Html.Raw` o `@Html.Raw(...)`. La decisión debe ser consciente: si el contenido viene del usuario, `Html.Raw` abre un XSS. Si viene de una plantilla propia y está saneado, puede tener sentido. En caso de duda, se deja la codificación.

```cshtml
<p>@Model.Title</p>              @* codificado *@
<div>@Html.Raw(Model.HtmlBody)</div> @* solo si el HTML es de confianza *@
```

La codificación se aplica al HTML, no a JavaScript ni a CSS. Un valor dentro de un `<script>` necesita `JavaScriptEncoder` o, mejor, pasarse como JSON serializado. Una URL construida con datos del usuario necesita `UrlEncoder`. Razor no adivina el contexto.

## Layouts y secciones

Un layout es una plantilla común con un hueco para el cuerpo:

```cshtml
<!DOCTYPE html>
<html>
<head>
    <title>@ViewData["Title"]</title>
</head>
<body>
    <header>...</header>
    <main>
        @RenderBody()
    </main>
    <footer>...</footer>
    @await RenderSectionAsync("Scripts", required: false)
</body>
</html>
```

La vista declara el layout en `_ViewStart.cshtml` o en su propio bloque. `RenderBody()` inserta el contenido de la vista; `RenderSection` inserta una sección opcional u obligatoria. La vista define la sección:

```cshtml
@section Scripts {
    <script src="~/js/posts.js"></script>
}
```

Las secciones son la forma de que una página añada scripts o estilos al layout sin duplicar la estructura. Si una sección es obligatoria, todas las vistas que usen ese layout deben definirla; si no, la aplicación falla al renderizar.

## Vistas parciales

Una vista parcial es un fragmento reutilizable. No tiene layout y se incluye desde otra vista o desde un controlador:

```cshtml
<partial name="_PostSummary" model="post" />
```

o, en código:

```csharp
return PartialView("_PostSummary", post);
```

La inclusión con `<partial>` es del lado del servidor: el HTML se genera antes de enviar la respuesta. No tiene nada que ver con AJAX, que cambia una zona después de cargar la página. `Html.PartialAsync` y `Html.RenderPartialAsync` hacen lo mismo desde código Razor; el tag helper es más legible.

## Tag helpers

Los tag helpers dan comportamiento a etiquetas HTML normales. El más útil es el de formularios:

```cshtml
<form asp-action="Edit" asp-controller="Posts" method="post">
    <input asp-for="Title" class="form-control" />
    <span asp-validation-for="Title" class="text-danger"></span>
    <button type="submit">Guardar</button>
</form>
```

`asp-for` genera el `name`, el `id` y el valor del campo, y añade los atributos de validación. `asp-action` y `asp-controller` construyen la URL. `asp-route-id` añade un valor de ruta. `asp-items` llena un `<select>` con una colección. `asp-validation-for` muestra el error de esa propiedad.

El tag helper de formulario añade el token antiforgery de forma automática cuando el método es `POST`. Es una de las razones para usarlo en lugar de escribir `<form action="...">` a mano.

## Helpers de HTML

Los helpers clásicos siguen disponibles:

```cshtml
@Html.ActionLink("Volver", "Index", "Posts")
@Url.Action("View", "Posts", new { id = 18 })
@await Html.PartialAsync("_Footer")
```

`Html.ActionLink` genera un enlace, `Url.Action` devuelve solo la URL y `Html.PartialAsync` incluye una parcial. En código nuevo, los tag helpers sustituyen a la mayoría: el marcado queda más limpio y el editor lo entiende mejor. Los helpers se reservan para casos que el tag helper no cubre.

## Componentes de vista

Un view component es una pieza reutilizable con lógica propia, más pesada que una parcial. Se implementa en una clase que hereda de `ViewComponent` y expone `InvokeAsync`:

```csharp
public class RecentPostsViewComponent : ViewComponent
{
    private readonly IPostServices _posts;

    public RecentPostsViewComponent(IPostServices posts)
    {
        _posts = posts;
    }

    public async Task<IViewComponentResult> InvokeAsync(int count)
    {
        var posts = await _posts.GetLatestAsync(count);
        return View(posts);
    }
}
```

La vista se busca en `Views/Shared/Components/RecentPosts/Default.cshtml`. Se invoca desde una vista con `<vc:recent-posts count="5" />` o con `@await Component.InvokeAsync("RecentPosts", new { count = 5 })`. Es la opción cuando el fragmento necesita una consulta, dependencias o parámetros, y una parcial no basta.

## Errores frecuentes

- Una vista no encuentra el modelo porque `@model` no coincide con el tipo que envía la acción.
- Un `null` en `Model` produce una excepción al acceder a una propiedad; se comprueba antes o se usa un modelo vacío.
- Un `@` en un correo se interpreta como código; se escribe `@@`.
- Una sección no aparece porque la vista no la define o el layout no la renderiza.
- Un tag helper no funciona porque falta `_ViewImports.cshtml` o el paquete no está registrado.

La comprobación es siempre la misma: ejecutar la página y leer el error. Razor señala la línea y el tipo que esperaba, y la traza de la vista suele ser más útil que la del controlador.
