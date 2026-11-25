# Sesiones y estado del visitante

Una aplicación web recibe peticiones independientes y, por defecto, no recuerda nada entre una y otra. Las variables de sesión cubren el caso contrario: guardan datos de un visitante concreto mientras dura su visita. El servidor identifica al visitante con una cookie que lleva un token, y con ese token recupera su diccionario de valores.

En ASP.NET Core el sistema es opcional. No se carga si no se pide, y los datos no viven en el proceso por defecto: se apoyan en una caché distribuida, que puede ser la memoria local o un almacén externo. Esa decisión cambia la escalabilidad y la velocidad, igual que en cualquier otra caché.

## Activar el sistema

El paquete `Microsoft.AspNetCore.Session` aporta los servicios y el *middleware*. Primero se registra el almacén y después el estado de sesión:

```csharp
builder.Services.AddDistributedMemoryCache();
builder.Services.AddSession();

var app = builder.Build();
app.UseSession();
app.UseRouting();
app.MapControllers();
```

`AddDistributedMemoryCache()` guarda los datos en la memoria del servidor y solo vale para un nodo. En una granja se sustituye por `AddStackExchangeRedisCache` o `AddDistributedSqlServerCache`, con la configuración del servidor correspondiente. El resto del código no cambia: la sesión siempre se lee y se escribe igual.

El *middleware* se inserta antes de los componentes que van a usar la sesión, en particular antes de MVC y de los endpoints.

`UseSession()` también acepta opciones. Este ejemplo cambia el nombre de la cookie, la marca como inaccesible desde JavaScript y fija quince minutos de inactividad:

```csharp
app.UseSession(new SessionOptions
{
    Cookie =
    {
        Name = ".MySession",
        HttpOnly = true,
        SecurePolicy = CookieSecurePolicy.Always
    },
    IdleTimeout = TimeSpan.FromMinutes(15)
});
```

`IdleTimeout` es el tiempo que se conserva la sesión sin actividad; por defecto son veinte minutos. La cookie se renueva con cada petición que use la sesión, así que el contador vuelve a empezar mientras el visitante sigue trabajando.

## Leer, escribir y borrar valores

El acceso se hace por `HttpContext.Session`, de tipo `ISession`. Los métodos básicos trabajan con `byte[]`, una consecuencia de que el almacén sea externo:

```csharp
void Set(string key, byte[] value);
bool TryGetValue(string key, out byte[] value);
void Remove(string key);
```

Para no serializar a mano en cada acceso, el *framework* ofrece `GetString`, `SetString`, `GetInt32` y `SetInt32`. Este endpoint cuenta las visitas de cada usuario:

```csharp
app.MapGet("/visits", async (HttpContext context) =>
{
    await context.Session.LoadAsync();
    var count = context.Session.GetInt32("count") ?? 0;
    count++;
    context.Session.SetInt32("count", count);
    return $"Visitas: {count}";
});
```

La llamada a `LoadAsync()` fuerza la lectura del almacén de forma asíncrona. Sin ella, el primer acceso carga los valores de forma síncrona, lo que con un almacén remoto y mucha carga se nota. Si el valor es un objeto, se serializa a texto o a bytes en un punto único; no conviene repartir conversiones por los controladores.

Para borrar hay dos niveles. `Remove("count")` elimina una clave y `Clear()` vacía toda la sesión del visitante, aunque conserva la cookie que lo identifica. No existen equivalentes a `Session.Abandon()` ni a los eventos de inicio y fin de la sesión clásicos: si hace falta limpiar recursos, se hace en el código que corresponda.

## Qué guardar y qué no

La sesión no es una base de datos. Conviene guardar lo justo, con caducidad, y no usarla para datos que deban sobrevivir a la visita o compartirse entre usuarios. Un carrito pequeño, un mensaje temporal o el idioma elegido encajan; un formulario largo, un informe o cualquier cosa que deba auditarse, no.

Tampoco es un mecanismo de seguridad por sí misma. La cookie de sesión identifica una bolsa de datos, no a una persona: la autenticación y la autorización se resuelven aparte. Si el identificador se filtra, quien lo tenga puede usar la sesión; de ahí que la cookie vaya con `HttpOnly`, `Secure` y una caducidad corta.

## TempData

`TempData` guarda un valor para la siguiente petición y lo borra al leerlo. Es el mecanismo clásico para pasar un mensaje de éxito o error después de una redirección, cuando no se quiere arrastrar el dato en la URL.

```csharp
TempData["Mensaje"] = "Cambios guardados";
return RedirectToAction("Index");
```

En la vista se lee con `@TempData["Mensaje"]`. Por defecto se apoya en cookies o en sesión, según la configuración; si el dato es grande, conviene usar sesión o un identificador. No sustituye al modelo de la vista: es un mensaje puntual, no un canal de datos.

## Alternativas

No todo el estado necesita sesión. El estado de la aplicación —contadores, catálogos, configuración— va en un *singleton* o en una caché. El estado del usuario autenticado va en *claims*, que viajan en la cookie o el token y no requieren almacén. El estado de un formulario va en el propio formulario o en la URL. La sesión queda para lo que no encaja en ninguno de esos sitios y debe desaparecer con la visita.
