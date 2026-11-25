# Arranque de la aplicación

Una aplicación ASP.NET Core es, por debajo, una aplicación de consola. El *runtime* busca el punto de entrada, lo ejecuta y ese código crea el host y deja un servidor a la escucha. Entender ese punto de entrada aclara dónde se configura el servidor, qué hace cada llamada y por qué la misma aplicación puede arrancar de formas distintas.

## Un único Program.cs

Desde .NET 6, la plantilla escribe el arranque completo en `Program.cs` con instrucciones de nivel superior:

```csharp
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllersWithViews();

var app = builder.Build();

if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    app.UseHsts();
}

app.UseHttpsRedirection();
app.UseStaticFiles();
app.UseRouting();
app.UseAuthorization();

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");

app.Run();
```

Cada línea cumple un papel. `CreateBuilder` devuelve un `WebApplicationBuilder` con la configuración, el registro de trazas, el contenedor de dependencias y el servidor ya preparados. `Services` es el contenedor donde se registran los servicios propios y los del *framework*. `Build` construye la aplicación. Sobre `app` se compone el pipeline y se declaran los endpoints. `Run` arranca el servidor y bloquea el hilo hasta que el proceso se detiene.

## El host y el patrón builder

El host envuelve la aplicación y le da los servicios básicos: inyección de dependencias, registro de trazas, configuración y un entorno donde ejecutarse. En una aplicación web es también quien configura y lanza Kestrel, o el servidor que se haya elegido. Se construye con el patrón builder: cada llamada añade configuración y devuelve el mismo objeto para encadenar.

`WebApplication.CreateBuilder(args)` prepara lo común:

- Establece la carpeta del proyecto como raíz de contenido.
- Carga la configuración desde `appsettings.json`, su variante por entorno, los secretos de usuario en desarrollo, las variables de entorno y los argumentos.
- Configura el registro para escribir en consola y en la ventana de depuración.
- Inicializa el contenedor de dependencias.
- Pone Kestrel como servidor y habilita la integración con IIS.

La versión anterior separaba el host (`Program.cs`) de la aplicación (`Startup.cs`). El modelo sigue soportado: `builder.Host.UseStartup<Startup>()` permite reutilizar una clase de arranque antigua. En código nuevo no aporta nada; `builder.Services` y el propio `app` cubren los dos métodos que tenía `Startup`.

## Servicios y pipeline

La división se mantiene, aunque cambie el sitio:

- Lo que la aplicación **necesita** se registra en `builder.Services`, antes de `Build`. Cada componente del pipeline lo pide al contenedor al construirse; si falta un registro, la aplicación falla al arrancar.
- Lo que la aplicación **hace** con cada petición se añade sobre `app`, después de `Build`. El orden de las llamadas es el orden de ejecución.

Esa separación permite preparar la aplicación en una prueba sin dejarla escuchando: se construye el host, se inspecciona y se arranca cuando conviene. `WebApplicationFactory` se apoya en ello para las pruebas de integración.

## Código de arranque personalizado

Cuando la configuración por defecto no encaja, se ajusta el builder antes de construir. Los casos más frecuentes son cambiar el servidor, fijar las direcciones de escucha y añadir orígenes de configuración:

```csharp
var builder = WebApplication.CreateBuilder(args);

builder.WebHost.UseUrls("https://localhost:5001", "http://localhost:5000");
builder.Configuration.AddIniFile("MySettings.ini", optional: true, reloadOnChange: true);
builder.Services.AddControllersWithViews();

var app = builder.Build();
app.MapGet("/", () => "Hola");
app.Run();
```

`UseUrls` sustituye a la configuración de `launchSettings.json` y sirve para un host que no pasa por el IDE. En producción es más habitual dejar las direcciones en variables de entorno (`ASPNETCORE_URLS`) y no en el código.

## El orden de las llamadas importa

`Build` cierra el registro de servicios: después ya no se pueden añadir dependencias al contenedor, solo componer el pipeline. Del mismo modo, un middleware colocado antes de otro ve la petición antes y la respuesta después. Las piezas que necesitan la identidad del usuario van después de `UseAuthentication`; las que deciden el acceso, después de `UseAuthorization`; y la ruta solo se puede consultar después de `UseRouting`.

## Arrancar sin `Main`

Las instrucciones de nivel superior generan un `Main` implícito. Para pruebas y herramientas que buscan un punto de entrada concreto, se puede escribir la clase `Program` de forma explícita y añadir `public partial class Program { }` al final. Es el detalle que necesitan algunas versiones de `WebApplicationFactory` para localizar la aplicación desde el proyecto de pruebas.
