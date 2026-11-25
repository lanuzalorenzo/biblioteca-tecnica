# Configuración y servicios

Una aplicación web necesita dos cosas antes de atender la primera petición: saber qué servicios va a usar y en qué orden va a procesar las peticiones. En el modelo moderno ambas se declaran en `Program.cs`, sobre el builder primero y sobre la aplicación después.

## Un archivo con dos momentos

`WebApplication.CreateBuilder` devuelve un builder con el contenedor y la configuración ya creados. Antes de `Build`, se registran los servicios; después, se compone el pipeline:

```csharp
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllersWithViews();
builder.Services.AddScoped<ICalculadora, Calculadora>();

var app = builder.Build();

app.UseHttpsRedirection();
app.UseStaticFiles();
app.UseRouting();
app.UseAuthorization();

app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");

app.Run();
```

`Build` cierra el registro. A partir de ahí, el contenedor no acepta servicios nuevos y solo queda decidir qué ocurre con cada petición. Esa frontera evita el error clásico de pedir un servicio que se registró después de construir la aplicación.

## El pipeline se compone sobre `app`

Cada llamada `Use...` añade un middleware. La cadena se ejecuta de arriba abajo en la petición y de abajo arriba en la respuesta:

- `UseHttpsRedirection()` responde con una redirección a quien llega por HTTP.
- `UseStaticFiles()` sirve CSS, JavaScript e imágenes de `wwwroot` sin pasar por MVC.
- `UseRouting()` analiza la ruta y anota qué endpoint la atenderá.
- `UseAuthentication()` lee la cookie o el token y establece el usuario.
- `UseAuthorization()` decide si ese usuario puede ejecutar el endpoint.
- `MapControllerRoute(...)` declara la ruta por convención de MVC y ejecuta el controlador.

El orden no es decorativo. Un middleware de errores colocado al final no captura los fallos de los anteriores, y uno de autenticación que vaya después del enrutado llega tarde para decidir el acceso. Los componentes que envuelven a otros —errores, trazas, cabeceras— van al principio; los que terminan la petición, al final.

## Los servicios se registran en el contenedor

Los servicios son los componentes que otros componentes necesitan. Se registran con un extensor sobre `builder.Services`, que es un `IServiceCollection`:

```csharp
builder.Services.AddAuthentication().AddCookie();
builder.Services.AddControllersWithViews();
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("Default")));
```

Cada *framework* trae su extensor: `AddControllersWithViews` para MVC, `AddRazorPages` para páginas, `AddDbContext<T>` para Entity Framework, `AddHealthChecks` para salud, `AddLocalization` para idiomas. Si un componente se usa en el pipeline y no se ha registrado, la aplicación se detiene al arrancar con un error de servicio no resuelto. Por eso, al añadir un *framework*, se consulta su documentación para saber qué extensor hay que llamar.

## Tres tiempos de vida

Al registrar un servicio propio se elige cuánto vive la instancia:

- **Transient**: se crea una instancia nueva cada vez que se solicita.
- **Scoped**: se crea una por petición y se libera al terminar. Es el tiempo adecuado para recursos caros que se comparten dentro de una petición, como un `DbContext`.
- **Singleton**: se crea la primera vez que se pide y se reutiliza mientras viva la aplicación.

```csharp
builder.Services.AddTransient<ICalculadora, Calculadora>();
builder.Services.AddScoped<IRepositorio, Repositorio>();
builder.Services.AddSingleton<IReloj, Reloj>();
```

Cada extensor admite una factoría, útil cuando la instancia necesita configuración previa:

```csharp
builder.Services.AddTransient<ICalculadora>(_ => new Calculadora("es-ES"));
```

Y un *singleton* puede registrarse ya construido:

```csharp
var reloj = new Reloj();
builder.Services.AddSingleton<IReloj>(reloj);
```

Elegir mal el tiempo de vida tiene consecuencias visibles: un servicio *scoped* inyectado en un *singleton* queda retenido más allá de su petición, y un *singleton* que guarda estado de usuario mezcla los datos de unos con los de otros. La regla es la más corta que funcione: *transient* si no guarda estado, *scoped* si acompaña a una petición y *singleton* solo si es inmutable y compartido por diseño.

## Servicios con clave

Desde .NET 8 se pueden registrar varias implementaciones de la misma interfaz y elegir por una clave:

```csharp
builder.Services.AddKeyedSingleton<INotificador, EmailNotificador>("email");
builder.Services.AddKeyedSingleton<INotificador, SmsNotificador>("sms");
```

Quien los consume usa `[FromKeyedServices("email")]` en el constructor o pide `IServiceProvider.GetRequiredKeyedService<INotificador>("sms")`. Es una alternativa limpia a las factorías que reciben una cadena y devuelven una implementación.

## Comprobar el registro

`builder.Services` se puede inspeccionar en una prueba, pero la comprobación real es arrancar la aplicación. Un servicio mal registrado o una dependencia circular se manifiestan en la primera resolución, no al compilar. Por eso conviene arrancar y ejercitar la ruta principal después de tocar el registro, antes de dar el cambio por cerrado.
