# Compilación automática y estructura del proyecto

Una de las ventajas que trajo ASP.NET Core fue recuperar algo que los *frameworks* de *scripting* en servidor daban por hecho: modificar el código, refrescar el navegador y ver el cambio sin compilar a mano. Esa comodidad tiene dos caminos, el del IDE y el de la línea de comandos, y ambos se apoyan en lo mismo: alguien vigila los archivos y recompila cuando cambian.

Después de crear un proyecto, la otra pregunta inmediata es qué son todos esos archivos. La respuesta ocupa la segunda mitad de esta nota: qué hay en un proyecto recién creado y qué papel juega el `.csproj`.

## Compilación automática desde el IDE

Visual Studio ejecuta el proyecto con `Ctrl+F5` sin depurar y muestra la salida del servidor en la ventana *Output*. Con la aplicación en marcha, se modifica un archivo y se refresca el navegador: el IDE detecta el cambio, recompila y sirve la versión nueva.

La compilación automática funciona con el perfil de IIS Express y con el perfil de Kestrel, pero no mientras se ejecuta con el depurador detenido en un punto de interrupción. Para el día a día conviene arrancar sin depuración y usar el depurador solo cuando haga falta.

## Compilación automática desde la línea de comandos

`dotnet watch run` vigila los archivos, recompila al detectar cambios y reinicia el servidor:

```text
$ dotnet watch run
watch : Started
info: Microsoft.Hosting.Lifetime[0]
      Now listening on: https://localhost:7123
info: Microsoft.Hosting.Lifetime[0]
      Application started. Press Ctrl+C to shut down.
watch : File changed: Program.cs
watch : Started
...
```

`dotnet watch test` hace lo mismo con las pruebas: cada cambio en el código ejecuta la batería y deja el resultado en la consola. Es la forma de mantener el ciclo corto sin depender de un IDE.

## Qué hay en un proyecto vacío

Un proyecto vacío de .NET 10 contiene pocos elementos. Algunos son comunes a cualquier proyecto .NET y otros son propios de la plantilla web.

La carpeta **Dependencies** del IDE no existe en disco: es una vista de las referencias del proyecto. Agrupa tres cosas: los analizadores de código que reparten diagnósticos y correcciones, los *frameworks* compartidos (`Microsoft.NETCore.App` y `Microsoft.AspNetCore.App`) y los paquetes NuGet añadidos a mano. El *framework* compartido no se declara en el `.csproj`: lo aporta el SDK.

La carpeta **Properties** guarda `launchSettings.json`, con los perfiles de arranque locales: la URL, las variables de entorno y si se abre el navegador. No se publica; cada desarrollador puede tener los suyos.

`appsettings.json` y `appsettings.Development.json` son la configuración base y la del entorno de desarrollo. `Program.cs` contiene el arranque y, en las plantillas MVC, la composición de servicios y rutas. `wwwroot/` es la raíz de los archivos que se sirven tal cual.

## El archivo .csproj

La definición del proyecto vive en un archivo `.csproj`. En ASP.NET Core es conciso porque el SDK aporta el resto:

```xml
<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>
</Project>
```

Las piezas que pueden aparecer son:

- El SDK con el que se construye, aquí `Microsoft.NET.Sdk.Web`.
- El *framework* de destino, `net10.0`.
- Las referencias a paquetes NuGet y a otros proyectos.
- Las opciones de compilación y de publicación.
- Los metadatos: nombre, versión, autor.
- Los scripts que se ejecutan antes o después de la compilación.

El archivo es texto y no depende de Visual Studio. Se edita a mano o con la opción «Editar archivo de proyecto» del IDE. Quien venga de ASP.NET 4.x notará una ausencia: no hay `Web.config`. Ese archivo configuraba la aplicación y su funcionamiento en IIS; su desaparición es consecuencia del nuevo modelo de alojamiento y de la vocación multiplataforma del *framework*.

## Qué se versiona

Se versionan el código, el `.csproj`, los archivos de configuración sin secretos, `wwwroot/` y, si existen, las migraciones de base de datos. No se versionan `bin/`, `obj/`, los archivos de usuario del IDE ni los secretos locales. La regla de `.gitignore` de la plantilla cubre lo habitual; los secretos van en *user secrets* o en variables de entorno, nunca en `appsettings.json`.

## Compilar y publicar no son lo mismo

`dotnet build` compila y deja los ensamblados en `bin/`, pensados para ejecutarse en la máquina de desarrollo. `dotnet publish` prepara una carpeta con lo necesario para el servidor: ensamblados, dependencias, contenido estático, configuración y, si se pide, el propio *runtime*. La diferencia importa al desplegar y se detalla en [Despliegue y calidad](despliegue-y-calidad.md).
