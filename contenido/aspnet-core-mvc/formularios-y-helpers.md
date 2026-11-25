# Formularios y helpers

Un formulario MVC tiene tres partes: el modelo que recibe los datos, la vista que genera los controles y la acción que los procesa. Los tag helpers de ASP.NET Core escriben la mayor parte del HTML, enlazan cada control con una propiedad y añaden la protección antiforgery. Entender lo que generan evita los fallos típicos de campos que no llegan o de tokens que faltan.

## Un formulario de edición

```cshtml
@model PostEditModel

<form asp-action="Edit" method="post">
    <input type="hidden" asp-for="Id" />

    <label asp-for="Title"></label>
    <input asp-for="Title" class="form-control" />
    <span asp-validation-for="Title" class="text-danger"></span>

    <label asp-for="Body"></label>
    <textarea asp-for="Body" class="form-control"></textarea>
    <span asp-validation-for="Body" class="text-danger"></span>

    <button type="submit">Guardar</button>
</form>
```

`asp-for` toma la propiedad indicada y genera `name`, `id`, `value` y los atributos de validación. `asp-validation-for` reserva el hueco donde el script de validación escribe el error. `asp-action` construye la URL de la acción; el tag helper añade el token antiforgery porque el método es `POST`.

El formulario debe incluir un campo oculto para la clave cuando se edita. Sin él, la acción no sabe qué registro actualizar. El campo no es una barrera de seguridad: el servidor debe comprobar que el usuario puede editar ese registro.

## Controles de edición

Los tag helpers cubren los tipos habituales:

```cshtml
<input asp-for="Email" type="email" />
<input asp-for="Age" type="number" min="18" max="99" />
<input asp-for="BornAt" type="date" />
<input asp-for="Accepted" type="checkbox" />
<textarea asp-for="Description" rows="5"></textarea>
```

El tipo se puede fijar a mano o dejar que lo deduzca el modelo. Para una fecha, el formato que espera el navegador es `yyyy-MM-dd`; una fecha con formato local puede no rellenar el campo. Para un booleano, el tag helper genera un checkbox y un campo oculto que envía `false` cuando no está marcado.

## Listas de selección

Un `<select>` se llena con `asp-items`, que recibe una colección de `SelectListItem` o de elementos con texto y valor:

```csharp
public IActionResult Create()
{
    var model = new PostEditModel
    {
        Categories = _categories.GetAll()
            .Select(c => new SelectListItem(c.Name, c.Id.ToString()))
            .ToList()
    };
    return View(model);
}
```

```cshtml
<select asp-for="CategoryId" asp-items="Model.Categories">
    <option value="">Elige una categoría</option>
</select>
```

La opción vacía es importante: sin ella, el navegador selecciona la primera y el usuario puede enviar un valor que no eligió. El servidor valida que el identificador exista y que el usuario tenga acceso a esa categoría.

## Validación en cliente

Los scripts de validación se incluyen en el layout o en la sección de scripts de la vista:

```cshtml
@section Scripts {
    <partial name="_ValidationScriptsPartial" />
}
```

La parcial de la plantilla carga `jquery.validate` y `jquery.validate.unobtrusive`. Con esos scripts, las anotaciones del modelo se convierten en reglas de JavaScript y los mensajes aparecen sin recargar. La validación del servidor sigue siendo la que manda: el cliente puede desactivar JavaScript o enviar la petición directamente.

`[Remote]` añade una comprobación contra una acción, por ejemplo para un nombre de usuario repetido:

```csharp
[Remote(action: "IsUsernameAvailable", controller: "Users")]
public string Username { get; set; } = "";
```

La acción devuelve `Json(true)` o un mensaje de error. Es una ayuda de interfaz, no una garantía: la comprobación definitiva se repite al guardar.

## Antiforgery

El token antiforgery protege contra peticiones cruzadas: un sitio ajeno no puede enviar un formulario en nombre del usuario porque no conoce el token. El tag helper de formulario lo añade automáticamente en los `POST`. En una acción que no use el tag helper, se añade a mano:

```cshtml
@Html.AntiForgeryToken()
```

Y se valida en el controlador:

```csharp
[HttpPost]
[ValidateAntiForgeryToken]
public IActionResult Delete(int id) { /* ... */ }
```

Para proteger todas las acciones de escritura sin repetir el atributo, se registra un filtro global:

```csharp
builder.Services.AddControllersWithViews(options =>
{
    options.Filters.Add(new AutoValidateAntiforgeryTokenAttribute());
});
```

`AutoValidateAntiforgeryToken` valida los verbos que modifican estado (`POST`, `PUT`, `PATCH`, `DELETE`) y deja pasar `GET`. Es la opción recomendada en una aplicación con vistas. Una API que consume un cliente externo no usa cookies y, por tanto, no necesita este token; se protege con autenticación de token.

## Helpers de HTML

Los helpers clásicos siguen disponibles y a veces son la forma más corta:

```cshtml
@Html.ActionLink("Volver", "Index", "Posts")
@Url.Action("View", "Posts", new { id = 18 })
@await Html.PartialAsync("_Footer")
@Html.Raw(Model.HtmlPermitido)
```

`ActionLink` genera un enlace, `Url.Action` devuelve la URL, `PartialAsync` incluye una parcial y `Raw` escribe HTML sin codificar. Los tag helpers sustituyen a los tres primeros en código nuevo; `Raw` se usa solo con contenido de confianza.

## Helpers propios

Cuando una combinación de marcado se repite, se puede escribir un helper como método de extensión sobre `IHtmlHelper` o como función en `@functions`. Para un fragmento con lógica, es mejor una parcial o un componente de vista. Un helper propio debe limitarse a generar marcado a partir de datos; si necesita consultar servicios, el sitio es un componente.

## Plantillas de edición

`EditorFor` y `DisplayFor` eligen la plantilla según el tipo de la propiedad. Para personalizar cómo se muestra un tipo, se crea una vista en `Views/Shared/EditorTemplates/` o `DisplayTemplates/` con el nombre del tipo:

```cshtml
@model DateTime
<input asp-for="@Model" type="date" value="@Model.ToString("yyyy-MM-dd")" />
```

Las plantillas se aplican a todas las vistas y evitan repetir el mismo control. Son útiles en formularios grandes o en un panel de administración con muchos tipos comunes.

## Comprobar un formulario

Se prueba con datos válidos, con un campo vacío, con un formato incorrecto y con un intento de enviar un identificador que no pertenece al usuario. En los cuatro casos, la respuesta debe ser la esperada y la base de datos no debe quedar en un estado inconsistente. También se comprueba que el formulario funciona sin JavaScript: si no, la validación del servidor no está bien conectada.
