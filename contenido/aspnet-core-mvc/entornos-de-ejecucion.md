# Entornos de ejecución

La misma aplicación no se comporta igual mientras se desarrolla y cuando atiende a usuarios reales. ASP.NET Core lo resuelve con una variable de entorno que el *runtime* consulta al arrancar, y con un mecanismo que permite cambiar la configuración y el pipeline según su valor.

## Tres entornos por convención

El *framework* define tres nombres:

- **Development**, el entorno de trabajo diario.
- **Staging**, una preproducción para probar antes de desplegar.
- **Production**, el entorno de los usuarios reales.

Son una convención, no una lista cerrada: se puede usar cualquier otro nombre. La utilidad es la de siempre: en desarrollo interesan las trazas y la página de errores detallada; en producción, el rendimiento y el mensaje de error escueto.

## Cómo se fija el entorno

El *runtime* lee la variable `ASPNETCORE_ENVIRONMENT`. En Windows el nombre no distingue mayúsculas; en Linux y macOS sí. Si no está definida, el valor por defecto es `Production`.

```bash
export ASPNETCORE_ENVIRONMENT=Development
dotnet run
```

La consola muestra el entorno activo en el arranque:

```text
info: Microsoft.Hosting.Lifetime[0]
      Hosting environment: Development
info: Microsoft.Hosting.Lifetime[0]
      Content root path: /home/ana/MiAplicacion
```

Nada impide poner un valor propio, como `HomeComputer`. Lo único que se pierde son los atajos que esperan los tres nombres convencionales.

Al lanzar desde el proyecto, el archivo `launchSettings.json` manda sobre la variable del sistema. Cada perfil puede fijar sus propias variables en `environmentVariables`:

```json
{
  "profiles": {
    "MiAplicacion": {
      "commandName": "Project",
      "launchBrowser": true,
      "environmentVariables": {
        "ASPNETCORE_ENVIRONMENT": "Development"
      },
      "applicationUrl": "https://localhost:7123;http://localhost:5123"
    }
  }
}
```

Desde la línea de comandos se elige el perfil con `--launch-profile`. Por defecto se usa el que coincide con el nombre del proyecto:

```bash
dotnet run --launch-profile MiPerfil
```

Solo se pueden lanzar así los perfiles que no dependan de IIS Express, que es exclusivo de Windows. En Visual Studio, el perfil se elige en el desplegable de la barra de herramientas y sus variables se editan en las propiedades del proyecto, pestaña *Debug*.

## Configuración distinta por entorno

La plantilla ya decide con `app.Environment`. `IWebHostEnvironment` expone el nombre en `EnvironmentName` y los atajos `IsDevelopment()`, `IsStaging()` e `IsProduction()`:

```csharp
var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage();
}
else
{
    app.UseExceptionHandler("/Home/Error");
    app.UseHsts();
}
```

Para nombres propios se usa `IsEnvironment()`:

```csharp
if (app.Environment.IsEnvironment("HomeComputer"))
{
    // Configuración del entorno propio
}
```

El segundo camino para separar entornos no duplica la clase: se pide al contenedor el entorno y se decide dentro del arranque. Los servicios también pueden registrarse de forma condicional:

```csharp
if (builder.Environment.IsDevelopment())
{
    builder.Services.AddSingleton<IEmailSender, ConsoleEmailSender>();
}
else
{
    builder.Services.AddSingleton<IEmailSender, SmtpEmailSender>();
}
```

La configuración por entorno sigue el mismo criterio sin escribir código: `appsettings.Development.json` y `appsettings.Production.json` se fusionan con el archivo base. Para valores que no deben estar en el repositorio, variables de entorno o un almacén de secretos.

## Un pipeline que no cambia de forma accidental

Las diferencias entre entornos deben ser explícitas y pocas. La página detallada de errores solo en desarrollo, HSTS solo fuera de desarrollo y las trazas con más detalle en desarrollo son las tres habituales. Cualquier otra diferencia conviene justificarla, porque un comportamiento que solo se prueba en desarrollo acaba fallando en producción.

## Comprobar el entorno

Una respuesta que devuelva el entorno activo sirve para confirmar que la variable llegó al proceso:

```csharp
app.MapGet("/entorno", (IWebHostEnvironment env) => env.EnvironmentName);
```

Si el valor no es el esperado, el problema suele estar en el perfil de arranque, en la variable del servicio del sistema o en un proxy que no la reenvía. Se comprueba en la consola de arranque antes de tocar el código.
