# Razor Pages

Razor Pages es una forma de organizar una aplicación web alrededor de páginas en lugar de controladores. Cada página es un archivo `.cshtml` con su propio modelo y sus manejadores, y la ruta sale de la ubicación del archivo. Para pantallas centradas en un formulario o una vista concreta, elimina la ceremonia de crear un controlador y una acción para cada una.

## Una página

Una página vive en `Pages/` y empieza con la directiva `@page`:

```cshtml
@page
@model MiApp.Pages.HelloModel

<h1>Hola desde Razor Pages</h1>
<p>Hora actual: @DateTime.Now.ToShortTimeString()</p>
```

`@page` convierte el archivo en una página enrutable. Debe estar en la primera línea; si falta, el archivo se trata como una vista y no se puede pedir por su ruta.

La ruta se deduce de la carpeta y del nombre: `Pages/Hello.cshtml` responde en `/Hello`; `Pages/Greetings/Hello.cshtml`, en `/Greetings/Hello`. `Index.cshtml` es el documento por defecto de una carpeta, así que `Pages/Test/Index.cshtml` responde en `/Test`. Si existen `Test.cshtml` y `Test/Index.cshtml`, la ambigüedad produce un error.

## El PageModel

La lógica va en una clase que hereda de `PageModel`, normalmente en un archivo `.cshtml.cs`:

```csharp
public class HelloModel : PageModel
{
    public string Mensaje { get; set; } = "";

    public void OnGet()
    {
        Mensaje = "Página cargada";
    }
}
```

La página accede a las propiedades públicas del modelo con `@Model.Mensaje`. La convención es `OnGet`, `OnPost`, `OnPut`, `OnDelete`, con el nombre del verbo. Un manejador con nombre añade un sufijo: `OnPostSave`, `OnGetBuscar`.

```csharp
public IActionResult OnPostSave()
{
    if (!ModelState.IsValid)
        return Page();

    _service.Save(Input);
    return RedirectToPage("/Index");
}
```

`Page()` vuelve a renderizar la página actual con el modelo y los errores. `RedirectToPage` navega a otra página por su ruta, no por una URL escrita a mano.

## Enlace de propiedades

`[BindProperty]` marca una propiedad para que se rellene con los datos de la petición:

```csharp
public class EditModel : PageModel
{
    [BindProperty]
    public PostEditModel Input { get; set; } = new();

    public void OnGet(int id)
    {
        Input = _posts.Get(id);
    }

    public IActionResult OnPost()
    {
        if (!ModelState.IsValid)
            return Page();

        _posts.Update(Input);
        return RedirectToPage("/Posts/Index");
    }
}
```

Por defecto, `[BindProperty]` solo enlaza en `POST`. Para que también lo haga en `GET`, se usa `SupportsGet = true`. Un parámetro del manejador (`OnGet(int id)`) se enlaza de la ruta o de la consulta sin necesidad del atributo.

Las propiedades enlazadas son una superficie de ataque si incluyen campos que el usuario no debe cambiar. Se usa un modelo de entrada con solo los campos editables, no la entidad completa.

## Handlers

Los manejadores permiten varias acciones en una misma página sin crear endpoints separados:

```cshtml
<form method="post">
    <button asp-page-handler="Save">Guardar</button>
    <button asp-page-handler="Delete">Eliminar</button>
</form>
```

```csharp
public IActionResult OnPostSave() { /* ... */ }
public IActionResult OnPostDelete() { /* ... */ }
```

El nombre del manejador viaja en la cadena de consulta (`?handler=Save`) y el tag helper lo genera. Para una petición AJAX, se llama a la URL con ese parámetro y se devuelve una parcial o JSON.

## Filtros

Una página puede llevar filtros en el modelo o en la clase:

```csharp
[Authorize]
public class AdminModel : PageModel { /* ... */ }
```

Los filtros globales se registran en `AddRazorPages().AddMvcOptions(...)` o con `options.Filters`. Un filtro de página puede implementar `IAsyncPageFilter` para ejecutar código antes o después del manejador. Para una regla que afecta a muchas páginas, un filtro global o una convención es más mantenible que repetir el atributo.

## Configuración

```csharp
builder.Services.AddRazorPages();

var app = builder.Build();
app.MapRazorPages();
```

`AddRazorPages()` registra los servicios; `MapRazorPages()` publica los endpoints. Un proyecto que mezcla MVC y Razor Pages usa `AddControllersWithViews()` y `AddRazorPages()`, y mapea ambos. `AddMvc()` sigue existiendo y registra todo, pero impide recortar.

Una aplicación creada con `dotnet new webapp` no incluye la ruta por convención de MVC. Si se añaden controladores después, hay que mapear `MapControllerRoute` a mano; de lo contrario, sus acciones no se alcanzan.

## Dónde encaja

Razor Pages brilla en aplicaciones con muchas pantallas independientes: un panel de administración, un formulario de alta, una página de detalle. La página y su modelo viven juntos, y el flujo se lee de arriba abajo.

MVC sigue siendo mejor cuando varias acciones comparten un recurso y una lógica de control, o cuando la aplicación ya tiene controladores y no conviene mezclar dos estilos sin motivo. Las dos opciones comparten pipeline, configuración, validación, tag helpers y autenticación; la diferencia es dónde se coloca el código de la página.

## Qué no cambia

Razor Pages no es un framework aparte: es una característica de ASP.NET Core MVC. Usa el mismo motor Razor, los mismos tag helpers, el mismo enlace de modelos y la misma validación. Tampoco sustituye al modelo de dominio: la página coordina, el dominio decide. Una página con consultas y reglas de negocio en el `PageModel` tiene el mismo problema que un controlador con esa lógica.
