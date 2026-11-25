# Instalación y primer proyecto

Una aplicación ASP.NET Core se construye con el SDK de .NET y se ejecuta con el *runtime*. El SDK incluye ambos, así que en el equipo de desarrollo basta con una instalación; en el servidor solo hace falta el *runtime* o, si se publica la aplicación con todo incluido, ni eso.

## Qué instalar

Para programar hace falta el **SDK de .NET 10**. Se descarga del sitio oficial y se instala por el canal del sistema operativo. En Windows, Visual Studio 2022 en adelante trae el SDK y las herramientas web; si ya está instalado, se revisa en *Visual Studio Installer* que estén marcados los *workloads* de ASP.NET Core y desarrollo .NET.

En Linux y macOS también se puede instalar el SDK desde el gestor de paquetes de la distribución o desde el instalador oficial. Para trabajar sin Visual Studio sirve Visual Studio Code con la extensión de C# o cualquier editor con soporte de OmniSharp. Todo el ciclo —crear, compilar, ejecutar y probar— se hace entonces con la CLI.

En producción solo se necesita el *runtime* de ASP.NET Core. En Windows con IIS, el paquete **Hosting Bundle** añade el *runtime*, el módulo de ASP.NET Core y la integración con IIS. En Linux se instala el *runtime* y se configura un proxy inverso o un servicio del sistema.

## Comprobar la instalación

```bash
dotnet --version
dotnet --list-sdks
dotnet --list-runtimes
```

La primera orden responde con la versión del SDK que se usará en la carpeta actual. Las otras dos muestran lo que hay instalado. Si conviven varias versiones, un archivo `global.json` en la raíz del proyecto fija la que se debe usar:

```json
{
  "sdk": {
    "version": "10.0.100",
    "rollForward": "latestFeature"
  }
}
```

`rollForward` permite aceptar una revisión más nueva dentro de la misma banda. Sin ese archivo, manda la versión más alta instalada.

## Crear el proyecto

La vía rápida es la CLI. `dotnet new` lista las plantillas; las de proyecto web más habituales son `web` (vacío), `mvc` (controladores y vistas), `webapp` (Razor Pages) y `webapi` (API).

```bash
mkdir MiAplicacion
cd MiAplicacion
dotnet new mvc
dotnet run
```

`dotnet new` crea los archivos y restaura los paquetes. `dotnet run` compila, arranca el servidor y deja la consola ocupada hasta que se detiene con `Ctrl+C`. La dirección de escucha aparece en la salida; los puertos se fijan en `Properties/launchSettings.json` y suelen ser distintos en cada equipo.

Para un primer contacto sin MVC, `dotnet new web` genera un proyecto mínimo:

```csharp
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

app.MapGet("/", () => "Hello World!");

app.Run();
```

Ese es el arranque completo de una aplicación moderna. `WebApplication.CreateBuilder` prepara configuración, registro de trazas, contenedor de dependencias y servidor; `Build` construye la aplicación; `MapGet` declara un endpoint y `Run` la deja escuchando.

## Crear el proyecto desde el IDE

Visual Studio ofrece la misma plantilla con un asistente: *File > New > Project*, «ASP.NET Core Web App (Model-View-Controller)», nombre y carpeta, y versión del *framework*. Las opciones de Docker, autenticación y HTTPS se pueden dejar por defecto al empezar. El resultado es equivalente al de `dotnet new mvc`.

## Estructura de un proyecto MVC

Un proyecto recién creado tiene estas piezas:

- `Program.cs`, el punto de entrada y la composición de servicios y pipeline.
- `Controllers/`, con los controladores.
- `Views/`, con las vistas Razor, el layout y los archivos `_ViewStart.cshtml` y `_ViewImports.cshtml`.
- `Models/`, si la plantilla o el equipo la usan; MVC no impone una carpeta concreta para el modelo.
- `wwwroot/`, la raíz pública de CSS, JavaScript, imágenes y otros archivos estáticos.
- `appsettings.json` y `appsettings.Development.json`, la configuración por entorno.
- `Properties/launchSettings.json`, los perfiles de arranque locales.
- `MiAplicacion.csproj`, la definición del proyecto.

La carpeta `obj/` y `bin/` se generan al compilar y no se versionan. El archivo `.csproj` declara el SDK, el *framework* de destino y los paquetes; todo lo demás lo aporta el SDK.

## Primer cambio

En la plantilla MVC, la página inicial la sirve `HomeController.Index`. Cambiar el texto de `Views/Home/Index.cshtml` y refrescar el navegador basta para ver el efecto. En el proyecto vacío, el cambio se hace en la función de `MapGet`.

Un endpoint puede leer datos de la petición sin montar un controlador:

```csharp
app.MapGet("/saludo", (string? nombre) =>
    $"Hola, {nombre ?? "invitado"}");
```

Una petición a `/saludo?nombre=Ana` devuelve «Hola, Ana». `MapGet`, `MapPost` y sus hermanos son la base de las API mínimas; MVC declara sus endpoints con `MapControllerRoute` o `MapControllers`.

## Dónde seguir

Con el proyecto en marcha, el orden natural es entender cómo se compone el arranque, cómo se registran los servicios y cómo entra cada petición en el pipeline. Eso ocupa las notas siguientes; la estructura del proyecto y el archivo `.csproj` se detallan en [Compilación y estructura](compilacion-y-estructura.md).
