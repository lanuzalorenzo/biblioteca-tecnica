# API HTTP

Una API es una aplicación web que devuelve datos en lugar de páginas. MVC trae todo lo necesario para construirla: los mismos controladores, el mismo routing y el mismo enlace de modelos, con un contrato pensado para que otro sistema lo consuma sin interpretar HTML.

## REST en una tabla

REST organiza la API alrededor de recursos, cada uno con una URI, y usa los verbos HTTP para indicar la operación. No es una norma que haya que cumplir al pie de la letra, pero da un contrato predecible:

| URI | Verbo | Acción |
|---|---|---|
| `/api/products` | GET | Obtiene la colección |
| `/api/products` | POST | Crea un producto |
| `/api/products/23` | GET | Obtiene el producto 23 |
| `/api/products/23` | PUT | Reemplaza el producto 23 |
| `/api/products/23` | PATCH | Modifica parte del producto 23 |
| `/api/products/23` | DELETE | Elimina el producto 23 |
| `/api/products/23/comments` | GET | Obtiene los comentarios del producto 23 |
| `/api/products/23/comments` | POST | Añade un comentario |

El nombre del recurso va en plural, sin verbos en la URL. La operación la dice el verbo. Un `GET /api/getProducts` funciona, pero pierde la ventaja de REST: el cliente tiene que conocer una acción concreta en lugar de un recurso.

## Configurar una API

```csharp
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddOpenApi();

var app = builder.Build();

app.MapOpenApi();
app.MapControllers();
app.Run();
```

`AddControllers()` registra lo necesario para controladores y resultados, sin vistas ni Razor. `MapControllers()` publica solo los endpoints declarados con atributos; una API no usa la ruta por convención de MVC. `AddOpenApi` y `MapOpenApi` publican el documento OpenAPI en `/openapi/v1.json` desde .NET 9; Swashbuckle ya no es necesario para lo básico.

## El controlador de API

Un controlador de API hereda de `ControllerBase` y se marca con `[ApiController]`:

```csharp
[ApiController]
[Route("api/[controller]")]
public class ProductsController : ControllerBase
{
    private readonly IProductServices _products;

    public ProductsController(IProductServices products)
    {
        _products = products;
    }

    [HttpGet]
    public ActionResult<IEnumerable<ProductDto>> GetAll()
        => Ok(_products.GetAll());

    [HttpGet("{id:int}")]
    public ActionResult<ProductDto> Get(int id)
    {
        var product = _products.Get(id);
        return product is null ? NotFound() : Ok(product);
    }

    [HttpPost]
    public ActionResult<ProductDto> Create(ProductCreateDto input)
    {
        var product = _products.Create(input);
        return CreatedAtAction(nameof(Get), new { id = product.Id }, product);
    }
}
```

`[ApiController]` aplica tres convenciones que ahorran código:

- **Rutas por atributo obligatorias.** El controlador debe declarar `[Route]` o una ruta en cada acción; una ruta por convención no lo alcanza.
- **Inferencia del origen de los parámetros.** Un tipo complejo se toma del cuerpo; `IFormFile`, del formulario; un nombre que coincide con la ruta, de la ruta; el resto, de la cadena de consulta.
- **400 automático por validación.** Si `ModelState` no es válido, la acción no se ejecuta y la respuesta es un 400 con Problem Details.

La inferencia se puede revertir con atributos explícitos (`[FromBody]`, `[FromQuery]`, `[FromRoute]`, `[FromForm]`). Conviene usarlos cuando la intención no es evidente o cuando un parámetro simple debe venir del cuerpo.

## Recibir datos

Un `POST` con JSON se enlaza a un DTO:

```csharp
public record ProductCreateDto(
    [Required, StringLength(100)] string Name,
    [Range(0, 100000)] decimal Price);
```

El cuerpo se lee una sola vez: no puede haber dos parámetros `[FromBody]` en la misma acción. El DTO de entrada no debe ser la entidad de persistencia; si lo es, el cliente puede enviar campos que no debería cambiar. Un DTO explícito documenta el contrato y evita el *over-posting*.

## Negociación de contenido

El formato de salida se decide por la cabecera `Accept`. Por defecto, `System.Text.Json` serializa a JSON con nombres en `camelCase`. Si el cliente pide XML, se añade el formateador:

```csharp
builder.Services.AddControllers()
    .AddXmlSerializerFormatters();
```

`RespectBrowserAcceptHeader` está desactivado por defecto: si el cliente pide un formato que no existe, se devuelve JSON en lugar de un 406. Activarlo hace que el contrato sea más estricto y es útil cuando la API se consume desde varios clientes.

La serialización se configura en un único sitio:

```csharp
builder.Services.AddControllers()
    .AddJsonOptions(options =>
    {
        options.JsonSerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.CamelCase;
        options.JsonSerializerOptions.DefaultIgnoreCondition =
            JsonIgnoreCondition.WhenWritingNull;
    });
```

## Códigos de estado

El código HTTP es parte del contrato. Los más usados:

| Código | Cuándo |
|---|---|
| `200 OK` | La operación devuelve datos |
| `201 Created` | Se creó un recurso; incluye `Location` |
| `204 No Content` | La operación se completó sin cuerpo |
| `400 Bad Request` | Datos inválidos o mal formados |
| `401 Unauthorized` | Falta autenticación o el token no es válido |
| `403 Forbidden` | El usuario está autenticado pero no puede |
| `404 Not Found` | El recurso no existe |
| `409 Conflict` | Conflicto con el estado actual, por ejemplo un duplicado |
| `422 Unprocessable Entity` | Semánticamente inválido, si el contrato lo distingue del 400 |
| `500 Internal Server Error` | Fallo no controlado |

`ControllerBase` ofrece `Ok()`, `Created()`, `CreatedAtAction()`, `NoContent()`, `BadRequest()`, `NotFound()`, `Conflict()` y `StatusCode()`. Devolver un objeto directamente equivale a `Ok(objeto)`; para controlar el código, se usa el método correspondiente.

## ActionResult<T>

`ActionResult<T>` combina el tipo de dato y los resultados de error. Permite escribir `return product;` o `return NotFound();` en el mismo método, y OpenAPI deduce el tipo de respuesta:

```csharp
[HttpGet("{id:int}")]
[ProducesResponseType(StatusCodes.Status200OK)]
[ProducesResponseType(StatusCodes.Status404NotFound)]
public ActionResult<ProductDto> Get(int id)
{
    var product = _products.Get(id);
    return product is null ? NotFound() : product;
}
```

Los atributos `ProducesResponseType` no cambian el comportamiento, pero documentan el contrato y alimentan la especificación OpenAPI. Son la forma de que el cliente sepa qué códigos puede recibir.

## Problem Details

Cuando hay un error, el cuerpo no debe ser un texto suelto. El estándar Problem Details (RFC 9457, que sustituye a RFC 7807) define una estructura común:

```json
{
  "type": "https://miapi.example/problems/stock",
  "title": "No hay stock",
  "status": 409,
  "detail": "El producto 23 no tiene unidades disponibles",
  "instance": "/api/products/23/orders"
}
```

`ControllerBase.Problem()` construye la respuesta y fija `Content-Type: application/problem+json`:

```csharp
return Problem(
    statusCode: StatusCodes.Status409Conflict,
    title: "No hay stock",
    detail: "El producto no tiene unidades disponibles");
```

`ValidationProblem(ModelState)` genera un 400 con los errores por campo y lo usa automáticamente `[ApiController]`. Las extensiones del estándar permiten añadir datos propios, como un identificador de traza. El mensaje de una excepción no se publica: va al registro y el cliente recibe un texto genérico.

## OpenAPI

`AddOpenApi()` genera el documento a partir de los controladores, los tipos y los atributos. `MapOpenApi()` lo publica. En desarrollo se puede añadir una interfaz —Scalar, Swagger UI o Redoc— que lo lea; en producción conviene decidir si el documento debe ser público. Una API interna no necesita exponer su superficie a internet.

El documento sirve para generar clientes, validar el contrato y detectar cambios incompatibles. Un cambio de nombre en una propiedad JSON es un cambio de contrato aunque el código compile; OpenAPI lo hace visible.

## CORS

Una API consumida desde una página de otro origen necesita CORS. Se configura con `AddCors` y se aplica por endpoint o de forma global. La política nombra los orígenes reales y limita verbos y cabeceras; `AllowAnyOrigin` no es una configuración de producción. El detalle está en [CORS](cors.md).

## Consumir una API desde .NET

`HttpClient` es la clase para hacer peticiones HTTP. No se crea uno por petición: se registra con `AddHttpClient` y se inyecta `IHttpClientFactory`, que reutiliza los manejadores y evita el agotamiento de sockets.

```csharp
builder.Services.AddHttpClient<PostsClient>(client =>
{
    client.BaseAddress = new Uri("https://api.example/");
    client.Timeout = TimeSpan.FromSeconds(10);
});
```

```csharp
public class PostsClient
{
    private readonly HttpClient _http;

    public PostsClient(HttpClient http) => _http = http;

    public async Task<List<PostDto>?> GetLatestAsync(CancellationToken token)
        => await _http.GetFromJsonAsync<List<PostDto>>("api/posts", token);
}
```

Para respuestas que pueden fallar, se comprueba `IsSuccessStatusCode` o se usa `EnsureSuccessStatusCode`, y se distinguen los códigos que el contrato define. Un `catch` genérico que devuelve una lista vacía oculta el fallo y hace creer que no hay datos cuando el servicio está caído.

## Autenticación

Una API consumida por otro sistema no usa la cookie del navegador: usa un token en la cabecera `Authorization: Bearer ...`. La generación, validación y protección de endpoints con JWT se explican en [Autenticación con cookies](autenticacion-con-cookies.md#tokens-para-api).

## Probar la API

`curl`, `HTTP REPL` o una colección de Postman permiten enviar cualquier verbo y ver la respuesta completa. La comprobación mínima cubre el camino feliz, un 400 por validación, un 404 por recurso inexistente y un 401 sin token. Si los cuatro responden como dice el contrato, la API está presentable; si el 400 devuelve HTML o el 500 muestra la pila, falta el tratamiento de errores.
