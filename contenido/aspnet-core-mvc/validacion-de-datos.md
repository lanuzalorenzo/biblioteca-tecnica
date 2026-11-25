# Validación de datos

El enlace de modelos llena los objetos, pero no garantiza que los datos sean correctos. La validación comprueba que lo recibido cumple las reglas del formulario y del dominio antes de tocar la base de datos. En MVC hay dos niveles: las anotaciones de datos, que se declaran junto al modelo, y las comprobaciones propias, que se ejecutan en el servicio o en el controlador.

## ModelState

Después del enlace, MVC deja el resultado de la validación en `ModelState`. `ModelState.IsValid` es `true` solo si no hay errores. La acción típica vuelve a mostrar el formulario cuando algo falla:

```csharp
[HttpPost]
[ValidateAntiForgeryToken]
public IActionResult Edit(PostEditModel model)
{
    if (!ModelState.IsValid)
        return View(model);

    _posts.Update(model);
    return RedirectToAction(nameof(Index));
}
```

`ModelState` contiene también los errores de conversión: un `int` que no se pudo convertir, una fecha con formato inválido o un campo obligatorio ausente. Por eso no basta con comprobar las anotaciones; hay que mirar `IsValid` después del enlace.

## Anotaciones de datos

Las anotaciones son atributos de `System.ComponentModel.DataAnnotations` que se aplican a propiedades o parámetros:

```csharp
public class Friend
{
    [Required, StringLength(50)]
    public string Name { get; set; } = "";

    [Required, StringLength(100), EmailAddress]
    public string Email { get; set; } = "";

    [Range(18, 99)]
    public int Age { get; set; }

    public string? Description { get; set; }
}
```

Las más frecuentes son:

| Atributo | Qué comprueba |
|---|---|
| `[Required]` | Que el valor no sea nulo; en cadenas, que no esté vacío salvo `AllowEmptyStrings` |
| `[StringLength(max)]` | Longitud máxima y, opcionalmente, mínima |
| `[MaxLength]`, `[MinLength]` | Límites de longitud o de tamaño de colección |
| `[Range(min, max)]` | Valor dentro de un intervalo |
| `[RegularExpression]` | Coincidencia con un patrón |
| `[EmailAddress]` | Formato de correo |
| `[Phone]` | Formato de teléfono |
| `[Url]` | Formato de URL |
| `[Compare]` | Igualdad entre dos propiedades, típico de contraseña y confirmación |
| `[CreditCard]` | Formato de tarjeta |
| `[FileExtensions]` | Extensiones permitidas en un archivo |
| `[Remote]` | Validación en cliente contra una acción del servidor |

Todas aceptan `ErrorMessage` para cambiar el mensaje. El texto puede ser una clave de recurso para traducirlo. En tipos valor como `int`, `[Required]` no distingue un cero de un valor ausente; para eso se declara `int?`.

## Validación de parámetros

Las anotaciones también se aplican a los parámetros de una acción:

```csharp
[HttpPost]
public IActionResult Create(
    [Required, MinLength(3)] string name,
    [Required, EmailAddress] string email,
    [Range(0, 120)] int age)
{
    if (!ModelState.IsValid)
        return Content("Error");

    _friends.Create(name, email, age);
    return Ok();
}
```

Es útil en una API o en una acción simple. En un formulario con varios campos, un modelo de vista con las anotaciones en sus propiedades suele ser más claro y reutilizable.

## Reglas de clase

Cuando la regla implica varias propiedades, se implementa `IValidatableObject`:

```csharp
public class User : IValidatableObject
{
    public string Username { get; set; } = "";
    public string Password { get; set; } = "";
    public string RetypedPassword { get; set; } = "";

    public IEnumerable<ValidationResult> Validate(ValidationContext context)
    {
        if (string.IsNullOrWhiteSpace(Username))
            yield return new ValidationResult(
                "El usuario no puede estar vacío", new[] { nameof(Username) });

        if (Password != RetypedPassword)
            yield return new ValidationResult(
                "Las contraseñas no coinciden",
                new[] { nameof(Password), nameof(RetypedPassword) });
    }
}
```

`Validate` solo se ejecuta si no hay errores previos en las anotaciones. Cada `ValidationResult` puede indicar las propiedades afectadas, y la vista muestra el mensaje junto a ellas.

Para una regla reutilizable se hereda de `ValidationAttribute`:

```csharp
public class IsEvenAttribute : ValidationAttribute
{
    public override bool IsValid(object? value)
        => value is int number && number % 2 == 0;
}

public class Modelo
{
    [IsEven(ErrorMessage = "Debe ser par")]
    public int Numero { get; set; }
}
```

Un atributo de clase recibe la instancia completa y sirve para comprobaciones que afectan a varias propiedades. Es la alternativa a `IValidatableObject` cuando la regla debe poder aplicarse a varios tipos.

## Clases buddy

Si las entidades se generan con una herramienta y se regeneran, las anotaciones escritas en ellas se pierden. Las *buddy classes* separan los metadatos:

```csharp
[MetadataType(typeof(FriendMetadata))]
public partial class Friend { /* generada */ }

public class FriendMetadata
{
    [Required, StringLength(50)]
    public string Name { get; set; } = "";

    [EmailAddress, Required]
    public string Email { get; set; } = "";
}
```

La clase de metadatos declara las mismas propiedades con las anotaciones y se enlaza con `[MetadataType]`. Es una solución para código generado; en código propio, las anotaciones van directamente en el modelo de vista.

## Validación en cliente

Las anotaciones también generan reglas de JavaScript cuando la vista incluye los scripts de validación. El tag helper `asp-validation-for` y el `jquery-validation-unobtrusive` muestran los errores sin recargar la página. La validación en cliente mejora la experiencia, pero no sustituye a la del servidor: cualquiera puede desactivar JavaScript o enviar la petición con `curl`.

```cshtml
<input asp-for="Email" class="form-control" />
<span asp-validation-for="Email" class="text-danger"></span>
```

La validación remota (`[Remote]`) consulta una acción para comprobar un valor, por ejemplo si un nombre de usuario ya existe. Añade una petición por campo y debe protegerse como cualquier endpoint público: no es una barrera de seguridad, solo una ayuda.

## Dónde va cada regla

La anotación valida el formulario: formato, longitud, obligatoriedad. La regla de negocio —el cliente no puede tener dos facturas abiertas, el stock no puede ser negativo— vive en el dominio y se ejecuta siempre, venga la petición de la web, de una API o de un proceso en segundo plano. Mezclar las dos hace que la regla se pueda saltar por otra vía y que el modelo dependa de la interfaz.

Cuando la regla de dominio falla, se añade el error a `ModelState` para que la vista lo muestre:

```csharp
if (!_orders.CanCreate(model.CustomerId))
    ModelState.AddModelError(nameof(model.CustomerId),
        "El cliente tiene una factura abierta");
```

## Comprobar la validación

Se prueba con datos válidos, con un campo obligatorio vacío, con un formato incorrecto y con un valor fuera de rango. En los cuatro casos, la acción debe devolver la vista con los errores y no tocar la base de datos. Si el formulario se envía sin JavaScript, la validación del servidor debe seguir funcionando.
