# AJAX y páginas parciales

AJAX es el intercambio asíncrono entre la página y el servidor: el usuario sigue interactuando mientras llega la respuesta y solo se actualiza una zona. En MVC, la petición es HTTP como cualquier otra; lo que cambia es el tipo de respuesta —HTML de una parcial o datos JSON— y el código del cliente que la consume.

## Qué cambia en el servidor

Poco. El routing elige el endpoint, el enlace de modelos llena los parámetros y la acción se ejecuta igual. La diferencia está en el resultado:

```csharp
public IActionResult GetCustomerPartial(int id)
{
    var customer = _customers.Get(id);
    return customer is null
        ? PartialView("_CustomerNotFound")
        : PartialView("_Customer", customer);
}

[HttpPost]
public IActionResult GetCustomer(int id)
{
    var customer = _customers.Get(id);
    return customer is null ? NotFound() : Json(customer);
}
```

`PartialView` devuelve HTML sin layout, listo para insertar en la página. `Json` devuelve datos serializados. La elección depende de quién construye el marcado: si el servidor ya tiene la plantilla, una parcial evita duplicar HTML en JavaScript; si el cliente necesita los datos para otra cosa, JSON es más flexible.

## Actualizar una zona

El escenario clásico: un campo, un botón y un contenedor que se rellena con la respuesta. Con `fetch`, el código del cliente es breve:

```html
<div>
    <input type="text" id="name" />
    <button id="send">Enviar</button>
    <div id="contentbox"></div>
</div>

<script>
    document.getElementById("send").addEventListener("click", async () => {
        const name = document.getElementById("name").value;
        const response = await fetch(`/Ajax/GetPartialView?name=${encodeURIComponent(name)}`);

        if (!response.ok) {
            document.getElementById("contentbox").textContent = "No se pudo cargar";
            return;
        }

        document.getElementById("contentbox").innerHTML = await response.text();
    });
</script>
```

La acción devuelve la parcial:

```csharp
public IActionResult GetPartialView(string name)
{
    if (string.IsNullOrWhiteSpace(name))
        return BadRequest();

    return PartialView("_Greetings", name);
}
```

`fetch` sustituye a `XMLHttpRequest` y a jQuery para este caso. No necesita una biblioteca y devuelve una promesa. jQuery sigue siendo válido en un proyecto que ya lo usa, pero un proyecto nuevo no lo necesita para hacer una petición.

## Intercambiar JSON

Cuando el cliente necesita los datos, no el marcado, la acción devuelve un objeto y el cliente lo pinta:

```csharp
[HttpGet]
public IActionResult Buscar(string texto)
{
    var resultados = _posts.Search(texto)
        .Select(p => new { p.Id, p.Title, p.Date })
        .ToList();

    return Json(resultados);
}
```

```javascript
const response = await fetch(`/Posts/Buscar?texto=${encodeURIComponent(texto)}`);
const posts = await response.json();

const lista = document.getElementById("resultados");
lista.innerHTML = "";
for (const post of posts) {
    const item = document.createElement("li");
    item.textContent = post.title;
    lista.appendChild(item);
}
```

Dos cuidados. El primero, no construir HTML concatenando datos del servidor: un título con `<img onerror=...>` se ejecuta. Se usa `textContent` o una plantilla que codifique. El segundo, comprobar `response.ok` antes de leer el cuerpo; un 400 o un 500 también tienen cuerpo y `json()` puede fallar.

## Enviar datos

Para un `POST` con JSON, se envía la cabecera `Content-Type` y el cuerpo serializado:

```javascript
const response = await fetch("/Posts/Create", {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
        "RequestVerificationToken": document.querySelector("input[name='__RequestVerificationToken']").value
    },
    body: JSON.stringify({ title, body })
});
```

En MVC con vistas, el token antiforgery debe viajar en la cabecera o en el cuerpo. El tag helper de formulario lo incluye en un campo oculto; para una petición `fetch` se lee ese campo y se copia a la cabecera `RequestVerificationToken`. Sin él, la acción con `[ValidateAntiForgeryToken]` responde 400 aunque el resto sea correcto.

Si el endpoint es una API sin cookies, no hay antiforgery y la protección es el token de autenticación.

## Actualización parcial con parciales

La combinación de parcial y `fetch` es la forma más directa de actualizar una zona sin duplicar el marcado. El servidor mantiene una sola plantilla, la vista principal incluye la parcial en la carga inicial y el cliente la vuelve a pedir cuando cambia un dato.

```csharp
[HttpPost]
public IActionResult Toggle(int id)
{
    var tarea = _tareas.Toggle(id);
    return tarea is null ? NotFound() : PartialView("_Tarea", tarea);
}
```

El cliente reemplaza el elemento de esa tarea con el HTML recibido. El estado lo decide el servidor; el cliente no intenta adivinar si la tarea quedó hecha o pendiente.

## Errores y estados de carga

Una petición asíncrona puede tardar o fallar. La interfaz debe decirlo: deshabilitar el botón mientras se envía, mostrar un texto de carga y, si falla, un mensaje que el usuario pueda entender. Un `fetch` sin `try/catch` deja la página igual y al usuario sin saber qué pasó.

```javascript
button.disabled = true;
try {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    box.innerHTML = await response.text();
} catch (error) {
    box.textContent = "No se pudo actualizar. Inténtalo de nuevo.";
} finally {
    button.disabled = false;
}
```

## Cuándo no usar AJAX

No toda interacción necesita AJAX. Un formulario que cambia de página, una búsqueda que se puede repetir con una URL y una navegación normal funcionan mejor con una petición completa: son más simples, accesibles y fáciles de cachear. AJAX se justifica cuando la actualización es pequeña, frecuente y no debe perder el contexto de la página. Convertir toda la aplicación en peticiones asíncronas añade estados, errores y código que hay que mantener.

## Razor Pages y AJAX

Una página Razor puede responder a una petición AJAX con un manejador con nombre (`OnGetBuscar`, `OnPostToggle`) y devolver una parcial o JSON. El patrón es el mismo; cambia dónde vive el código, en el `PageModel` en lugar de un controlador. La nota [Razor Pages](razor-pages.md) cubre esa estructura.
