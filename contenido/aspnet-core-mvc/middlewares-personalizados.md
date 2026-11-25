# Middlewares propios

El *framework* trae resuelto lo común: archivos estáticos, errores, autenticación, compresión. Cuando aparece una necesidad que no está en esa lista, lo natural es escribir un middleware y colocarlo en la cadena en el punto adecuado. No hace falta heredar de nada ni implementar una interfaz: basta con respetar dos convenciones, recibir el delegado al siguiente componente y exponer un método que procese la petición. Ese margen explica por qué un nombre mal escrito no se detecta al compilar, sino al arrancar.

## Qué hace un middleware

La cadena está explicada en [Una arquitectura modular](arquitectura-modular.md): cada componente recibe la petición, decide si la cede y recupera el control cuando la respuesta vuelve. Lo que importa aquí es el reparto de trabajo. Antes de `await next()` la respuesta todavía no existe, así que el middleware puede leer la petición y decidir si corta; después, cuando el resto ha terminado, puede anotar el código de estado o cambiar el cuerpo. Un registro actúa en los dos lados; un gestor de errores solo en el segundo; una autorización solo en el primero.

Un componente puede implementar los tres pasos o quedarse con uno. El último de la cadena responde sin ceder nada, y el orden de inserción es el orden de ejecución: un middleware colocado detrás de otro no ve las peticiones que ese otro haya resuelto.

## Un middleware en línea

La forma más rápida es un delegado dentro de `Program.cs`. Se llama a `app.Use()` con una función asíncrona que recibe el contexto y el delegado al siguiente componente. El ejemplo mide lo que tarda cada petición y lo anota al terminar:

```csharp
var perfilador = app.Services.GetRequiredService<ILoggerFactory>()
    .CreateLogger("Perfilador");

app.Use(async (context, next) =>
{
    var reloj = Stopwatch.StartNew();
    await next();
    perfilador.LogDebug("Ruta={Ruta}, estado={Estado}, tiempo={Tiempo}",
        context.Request.Path, context.Response.StatusCode, reloj.Elapsed);
});

app.UseStaticFiles();
```

El orden de las llamadas es el orden de ejecución. Aquí el perfilador va antes que los archivos estáticos, así que mide también el tiempo que tarda el componente de abajo en servir el archivo. Si se colocara detrás, no vería esas peticiones: el componente anterior las habría resuelto sin ceder el control.

La fórmula funciona para pruebas y para piezas de un solo uso, pero en cuanto el código crece o se repite en dos proyectos conviene sacarlo a una clase. Un delegado en línea no se puede configurar, no se puede probar por separado y arrastra el arranque entero.

## Una clase aparte

La convención para una clase middleware es corta. El constructor recibe un `RequestDelegate`, que es el siguiente componente, y un método público `Invoke()` recibe el contexto y devuelve una tarea. El *framework* construye la instancia y la coloca en la cadena con `UseMiddleware<T>()`:

```csharp
public class PerfiladorMiddleware
{
    private readonly RequestDelegate _next;

    public PerfiladorMiddleware(RequestDelegate next)
    {
        _next = next;
    }

    public async Task Invoke(HttpContext context)
    {
        var reloj = Stopwatch.StartNew();
        await _next(context);
        Console.WriteLine("Ruta={0}, tiempo={1}",
            context.Request.Path, reloj.Elapsed);
    }
}

app.UseMiddleware<PerfiladorMiddleware>();
app.UseStaticFiles();
```

El nombre del método importa. Si en lugar de `Invoke()` se escribe `Invke()`, el proyecto compila y el fallo aparece al arrancar, cuando el *framework* construye el pipeline y busca el método por reflexión. La convención no la comprueba el compilador.

### Parámetros de configuración

El constructor admite más argumentos, que se pasan en el momento de insertar el middleware. Sirven para lo que no cambia con la petición: un prefijo, un umbral, un nombre de cabecera. El *framework* los toma de la llamada y los inyecta en orden:

```csharp
public class SelloMiddleware
{
    private readonly RequestDelegate _next;
    private readonly string _texto;

    public SelloMiddleware(RequestDelegate next, string texto)
    {
        _next = next;
        _texto = texto;
    }

    public async Task Invoke(HttpContext context)
    {
        context.Response.Headers["X-Sello"] = _texto;
        await _next(context);
    }
}

app.UseMiddleware<SelloMiddleware>("beta");
```

### Dependencias y ciclo de vida

El contenedor también resuelve las dependencias que se piden en el constructor, de modo que un middleware puede recibir su *logger* o un servicio de configuración como cualquier otra clase. La diferencia está en cuándo: la instancia se crea una sola vez, al arrancar, y todas las peticiones pasan por ese mismo objeto.

Esa instancia única obliga a dos cuidados. El primero, no guardar estado de la petición en campos: lo que se escribe en una petición lo lee la siguiente. El segundo, no pedir en el constructor servicios con vida por petición. Los servicios *scoped* se reciben como argumento adicional de `Invoke()`, y el *framework* los resuelve en cada llamada:

```csharp
public async Task Invoke(HttpContext context, IVisitasRepositorio visitas)
{
    await visitas.AnotarAsync(context.Request.Path);
    await _next(context);
}
```

## Middlewares guiados por factoría

La interfaz `IMiddleware` cambia el modelo. La clase implementa un único método `InvokeAsync()` que recibe el contexto y el siguiente delegado, y el *framework* crea una instancia por petición pidiéndola al contenedor. A cambio, el registro en el contenedor pasa a ser obligatorio: si falta, la aplicación falla en la primera petición.

```csharp
public class PerfiladorMiddleware : IMiddleware
{
    private readonly ILogger<PerfiladorMiddleware> _logger;

    public PerfiladorMiddleware(ILogger<PerfiladorMiddleware> logger)
    {
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context, RequestDelegate next)
    {
        var reloj = Stopwatch.StartNew();
        await next(context);
        _logger.LogDebug("Ruta={Ruta}, tiempo={Tiempo}",
            context.Request.Path, reloj.Elapsed);
    }
}

builder.Services.AddTransient<PerfiladorMiddleware>();
app.UseMiddleware<PerfiladorMiddleware>();
```

El registro habitual es `AddTransient`, aunque se puede elegir otro ciclo de vida. La contrapartida es que este modelo no admite parámetros de inicialización: lo que se pasaría por el constructor de la convención se resuelve con opciones registradas en el contenedor. Las dos formas conviven en la misma aplicación.

| | Convención | `IMiddleware` |
|---|---|---|
| Método | `Invoke()` | `InvokeAsync()` |
| Instancia | Una, creada al arrancar | Una por petición, desde el contenedor |
| Registro | No hace falta | Obligatorio |
| Parámetros de inicio | Sí, en `UseMiddleware` | No |

## Un método Use propio

Los middlewares del *framework* se insertan con métodos como `UseStaticFiles()`, y nada impide ofrecer la misma comodidad. Basta con escribir un extensor sobre `IApplicationBuilder` que envuelva la llamada a `UseMiddleware<T>()` y devuelva el mismo constructor para poder encadenar. La clase debe estar en el espacio de nombres `Microsoft.AspNetCore.Builder` para que el método aparezca sin `using` adicional:

```csharp
namespace Microsoft.AspNetCore.Builder;

public static class PerfiladorExtensions
{
    public static IApplicationBuilder UsePerfilador(this IApplicationBuilder app)
        => app.UseMiddleware<PerfiladorMiddleware>();
}
```

El extensor es también el sitio donde se validan los argumentos y se construyen las opciones, de modo que la llamada desde el arranque quede en una línea. Si el middleware crece hasta necesitar configuración, el método `UseXXX()` la recibe y la convierte en argumentos del constructor.

## Ramas con Map y MapWhen

Un pipeline no tiene por qué ser una línea. `Map()` abre una rama para las peticiones cuya ruta empieza por un prefijo, y dentro de esa rama se configura un pipeline completo. Es la forma de dar a una parte de la aplicación sus propios middlewares sin afectar al resto:

```csharp
app.UseExceptionHandler("/error.html");
app.Map("/signalr", rama =>
{
    rama.UseCors("signalr");
});
app.Map("/api", rama =>
{
    rama.UseCors("api");
});
app.UseStaticFiles();
```

La rama no vuelve al pipeline principal. Cuando una petición entra en ella, termina allí: el `MapMiddleware` que la desvía no cede el control a los componentes de después. Eso la hace útil para separar zonas con reglas propias y peligrosa si se espera que la petición continúe: un middleware colocado detrás de `Map()` no se ejecuta para las rutas desviadas.

`MapWhen()` hace lo mismo con una condición libre en lugar de un prefijo. El predicado recibe el contexto, así que puede mirar cualquier dato de la petición: el método, una cabecera, una cookie o el agente de usuario:

```csharp
app.MapWhen(
    ctx => ctx.Request.Cookies.ContainsKey("auth"),
    rama =>
    {
        rama.UseAuthentication();
    });
```

La condición se evalúa en cada petición. Si es costosa —una consulta, un cálculo— se paga en todas, incluidas las que no van a entrar en la rama. Para el caso frecuente de separar por ruta, `Map()` es más barato y más claro.

El cuarto extensor de la familia es `Run()`, que añade un componente final: procesa la petición y no cede el control, porque no hay nada detrás. Se usa para el último eslabón de una rama, no para piezas que deban convivir con las siguientes.
