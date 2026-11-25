# Controladores y acciones

Los controladores son las clases a las que el routing delega el proceso de las peticiones. Las acciones son sus métodos públicos: donde se recibe lo que llega, se valida, se llama al modelo y se elige el resultado. El controlador no es el sitio de la lógica de negocio; es el adaptador entre HTTP y el dominio.

## Convenciones

MVC descubre los controladores por convención. Para que una clase lo sea:

- Debe ser pública y no abstracta.
- No puede tener parámetros genéricos.
- Su nombre debe terminar en `Controller` o llevar el atributo `[Controller]`.

Lo habitual es heredar de `Controller`, que aporta `View`, `Json`, `NotFound`, `RedirectToAction`, `ModelState`, `User`, `Request` y el resto de utilidades. Para una API se hereda de `ControllerBase`, que ofrece esos resultados pero no las vistas.

```csharp
public class PostsController : Controller
{
    private readonly IPostServices _posts;

    public PostsController(IPostServices posts)
    {
        _posts = posts;
    }

    public IActionResult Index()
    {
        var posts = _posts.GetLatest();
        return View(posts);
    }
}
```

Las dependencias se reciben por constructor y el contenedor las resuelve. El controlador se crea por petición, así que no debe guardar estado entre llamadas ni usar campos mutables para datos del usuario.

## Acciones

Una acción es un método público de instancia, sin parámetros genéricos y invocable directamente. Su forma general sigue unos pasos:

1. Obtener y convertir los datos de entrada.
2. Comprobar que son válidos.
3. Llamar al modelo.
4. Elegir la vista o el resultado.
5. Entregar a la vista la información que necesita.
6. Devolver el resultado.

No todas las acciones siguen los seis pasos. Una acción que solo devuelve una página estática no necesita modelo; una que crea un recurso no devuelve vista. Lo que sí conviene es que cada acción tenga un propósito claro y una extensión razonable. Si un método necesita más de una pantalla de código, probablemente está haciendo el trabajo de un servicio.

## Resultados

Una acción devuelve un `IActionResult` o un `ActionResult<T>`. Los resultados más usados son:

| Resultado | Efecto |
|---|---|
| `View(modelo)` | Ejecuta una vista y devuelve HTML con 200 |
| `PartialView(...)` | Devuelve un fragmento de HTML |
| `Json(datos)` | Serializa el objeto como JSON |
| `Content(texto)` | Devuelve texto plano o HTML sin vista |
| `NotFound()` | Responde 404 |
| `BadRequest(...)` | Responde 400 |
| `Unauthorized()` | Responde 401 |
| `Forbid()` | Responde 403 |
| `RedirectToAction(...)` | Responde 302 hacia otra acción |
| `StatusCode(n)` | Responde con el código indicado |

`View()` sin argumentos usa el nombre de la acción como nombre de vista. `View("OtroNombre", modelo)` elige otra plantilla. `RedirectToAction` es la forma correcta de redirigir dentro de la aplicación; una URL escrita a mano se rompe cuando cambia el routing.

## Selección por verbo y por nombre

Los atributos de selección limitan qué peticiones ejecutan una acción:

```csharp
[HttpGet]
public IActionResult Edit(int id) { /* ... */ }

[HttpPost]
[ValidateAntiForgeryToken]
public IActionResult Edit(PostEditModel model) { /* ... */ }
```

`[HttpPost]`, `[HttpPut]`, `[HttpDelete]` y `[HttpPatch]` son los habituales. `[AcceptVerbs("GET", "HEAD")]` permite una lista. `[ActionName("nombre")]` cambia el nombre con el que la acción es accesible sin renombrar el método. `[NonAction]` excluye un método público de la consideración de acción, útil para helpers internos del controlador.

Dos acciones con el mismo nombre y verbos distintos conviven; con el mismo verbo, producen ambigüedad. La ambigüedad se detecta al arrancar o en la primera petición, y se resuelve cambiando la ruta o el verbo, no añadiendo lógica dentro del método.

## Acciones asíncronas

Una acción que espera a una base de datos o a un servicio externo debe ser asíncrona. El servidor tiene un número limitado de hilos; si una acción bloquea el suyo durante una consulta lenta, ese hilo no atiende otras peticiones. Con `async` y `await`, el hilo se libera mientras espera y vuelve cuando el resultado está listo.

```csharp
public async Task<IActionResult> Index(CancellationToken token)
{
    var posts = await _posts.GetLatestAsync(token);
    return View(posts);
}
```

La regla es sencilla: si el método que se llama tiene una versión `Async`, se usa y se espera con `await`. No se usa `.Result` ni `.Wait()`, porque bloquean el hilo y pueden producir interbloqueos. El token de cancelación se pasa a las operaciones que lo admiten; cuando el cliente corta la petición, la consulta se cancela en lugar de seguir gastando recursos.

Una acción asíncrona no hace que la respuesta llegue antes al usuario; hace que el servidor pueda atender a más usuarios mientras espera. En una aplicación con poca carga la diferencia no se nota; en una con muchas peticiones concurrentes, es la diferencia entre escalar y quedarse sin hilos.

## Buenas prácticas

- Un controlador delgado: validar, llamar al servicio, elegir el resultado.
- Una acción, una responsabilidad. Si necesita varias, se parte o se mueve al servicio.
- No acceder a `Request.Form` o `RouteData` a mano si el enlace de modelos lo puede hacer; el código es más corto y más fácil de probar.
- No devolver entidades de persistencia directamente a una vista o a una API; usar un modelo de vista o un DTO.
- No capturar excepciones para devolver 200 con un mensaje de error. El código de estado es parte del contrato.
- Cerrar el círculo con una prueba: la acción devuelve el resultado esperado, el modelo recibe los datos correctos y el caso de error responde lo que debe.

## Controladores frente a API mínimas

Un controlador agrupa acciones relacionadas y aporta filtros, enlace de modelos y resultados uniformes. Una API mínima declara cada endpoint como una función y es más directa para un servicio pequeño. Los dos pueden convivir. La decisión depende del tamaño y de la necesidad de convenciones: para un recurso con varias operaciones y validación, un controlador suele ordenar mejor; para dos endpoints sueltos, una función basta.
