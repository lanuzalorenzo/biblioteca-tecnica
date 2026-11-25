# Enlace de modelos

Cuando una petición llega a una acción, sus datos están repartidos entre la ruta, la cadena de consulta, el cuerpo y las cabeceras. El enlace de modelos (*model binding*) convierte esos valores en los argumentos del método: lee el nombre de cada parámetro, busca un valor, lo convierte al tipo y lo asigna. Es la pieza que evita escribir `Convert.ToInt32(Request.Form["id"])` en cada acción.

## Orígenes y orden

Para un parámetro simple, el binder busca el valor en este orden:

1. Campos de formulario.
2. Parámetros de ruta.
3. Parámetros de la cadena de consulta.

Si el mismo nombre aparece en varios sitios, gana el primero. En una petición `POST /Products/Edit/5` con un campo `name`, el parámetro `id` se toma de la ruta y `name` del formulario. Si no hay valor, el parámetro recibe el valor por defecto de su tipo: `0` para un entero, `false` para un booleano, `null` para una referencia.

```csharp
public IActionResult View(string id, int currentPage, bool fullDetails)
{
    return Content($"id={id}, página={currentPage}, detalle={fullDetails}");
}
```

Una petición a `/Products/View/999?currentPage=2&fullDetails=true` enlaza los tres valores. Si falta alguno, se usa el valor por defecto. Para distinguir «no vino» de «vino con el valor por defecto», se declara el parámetro como anulable (`int?`) o se le asigna un valor predeterminado (`bool fullDetails = true`).

## Orígenes explícitos

El orden por defecto se puede sustituir con atributos, y conviene hacerlo cuando la intención no es obvia o cuando el dato debe venir de un sitio concreto:

```csharp
public IActionResult Search(
    [FromQuery] string? texto,
    [FromQuery] int page = 1,
    [FromRoute] int? id = null,
    [FromHeader(Name = "X-Cliente")] string? cliente = null)
```

- `[FromQuery]` lee la cadena de consulta.
- `[FromRoute]` lee los valores de la ruta.
- `[FromForm]` lee el formulario.
- `[FromHeader]` lee una cabecera.
- `[FromBody]` lee el cuerpo, normalmente JSON.
- `[FromServices]` pide un servicio al contenedor.

`[FromBody]` solo puede aparecer una vez por acción, porque el cuerpo se lee una sola vez. En una API con `[ApiController]`, los tipos complejos se enlazan del cuerpo por convención; en MVC con vistas, un tipo complejo se compone con los valores del formulario, la ruta y la consulta.

## Objetos complejos

El binder también construye objetos. Para un parámetro de tipo `PostEditModel`, crea una instancia y rellena cada propiedad pública con el valor del mismo nombre:

```csharp
public class PostEditModel
{
    public int Id { get; set; }
    public string Title { get; set; } = "";
    public string Body { get; set; } = "";
}

[HttpPost]
public IActionResult Edit(PostEditModel model)
{
    if (!ModelState.IsValid)
        return View(model);

    _posts.Update(model);
    return RedirectToAction(nameof(Index));
}
```

Si el objeto tiene propiedades complejas, el nombre del campo lleva el prefijo de la propiedad: `Author.Name`, `Author.Email`. El binder recorre la jerarquía. Para listas, los campos se llaman `Lines[0].ProductId`, `Lines[1].ProductId`, etc.

```csharp
public class OrderEditModel
{
    public string Customer { get; set; } = "";
    public List<OrderLineModel> Lines { get; set; } = new();
}
```

Un formulario que añade líneas dinámicamente debe mantener los índices correlativos. Un hueco en la numeración rompe el enlace de los elementos posteriores en algunas versiones; se renumeran al añadir o quitar.

## Prefijos y exclusión

Cuando un formulario envía un objeto dentro de otro, se usa `[Bind("...")]` para limitar qué propiedades se enlazan. Es también una medida de seguridad: si la entidad tiene una propiedad `IsAdmin` o `Price`, el cliente no debe poder cambiarla enviando un campo con ese nombre.

```csharp
[HttpPost]
public IActionResult Edit([Bind("Id,Title,Body")] Post post)
```

La alternativa es usar un modelo de vista con solo los campos editables, que es la opción recomendada. Un DTO de entrada explícito evita el *over-posting* y documenta el contrato. `[BindNever]` excluye una propiedad concreta; `[BindRequired]` obliga a que el valor venga en la petición.

## Archivos

Un archivo se recibe con `IFormFile`. El formulario debe tener `enctype="multipart/form-data"`; sin eso, el navegador envía solo el nombre y el archivo llega vacío.

```cshtml
<form asp-action="Upload" enctype="multipart/form-data" method="post">
    <input type="file" name="file" />
    <button type="submit">Subir</button>
</form>
```

```csharp
[HttpPost]
public async Task<IActionResult> Upload(IFormFile file)
{
    if (file is null || file.Length == 0)
        return BadRequest("Falta el archivo");

    var destino = Path.Combine(_env.WebRootPath, "uploads",
        Path.GetFileName(file.FileName));

    await using var stream = System.IO.File.Create(destino);
    await file.CopyToAsync(stream);
    return Ok();
}
```

`IFormFile` expone `FileName`, `Length`, `ContentType` y un flujo de lectura. El nombre que envía el cliente no es de fiar: se sanea, se comprueba la extensión y el tipo real, y se guarda con un nombre generado. Un archivo subido a `wwwroot` es público; si no debe serlo, se guarda fuera de esa carpeta y se sirve con una acción que compruebe permisos.

## Valores que no se enlazan

El binder no convierte cualquier cosa. Un `int` que recibe `"abc"` produce un error de modelo, no una excepción. Ese error queda en `ModelState` y hace que `IsValid` sea `false`. Un tipo complejo sin constructor público, una interfaz o una colección sin elementos no se enlazan. Para esos casos se escribe un *model binder* propio, que es raro y solo se justifica cuando el formato de entrada es muy particular.

## Comprobarlo

La forma rápida de comprobar un enlace es una acción que devuelva los valores recibidos y una petición con `curl` o la herramienta de desarrollo del navegador. Si un parámetro llega a `null` o `0`, se revisa el nombre, el origen y el atributo. La mayoría de los fallos de enlace son un nombre distinto entre el campo y la propiedad, o un formulario que no envía el método o el `enctype` correcto.
