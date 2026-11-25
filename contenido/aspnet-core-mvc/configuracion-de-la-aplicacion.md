# Configuración de la aplicación

En ASP.NET clásico los valores de configuración vivían en `Web.config`: cadenas de conexión, constantes y conmutadores en un único archivo XML que obligaba a reiniciar la aplicación al cambiar. ASP.NET Core separa el sistema de configuración del resto y lo alimenta desde varios orígenes a la vez, con recarga en caliente cuando el origen lo permite.

Ese diseño tiene dos consecuencias prácticas. La configuración es un servicio más: se inyecta y se compone como cualquier otro. Y los secretos no van en archivos versionados; para contraseñas y claves están los *user secrets* en desarrollo y las variables de entorno en el resto de entornos.

## Una pieza por origen

Todos los paquetes cuelgan de `Microsoft.Extensions.Configuration`, que es el núcleo. Cada origen añade un sufijo: `.Json` para los archivos JSON, `.Ini` para los INI, `.Xml` para los XML, `.EnvironmentVariables` para las variables de entorno, `.CommandLine` para los argumentos de la línea de comandos, `.KeyPerFile` para un valor por archivo y `.UserSecrets` para los secretos de desarrollo. Key Vault usa `Azure.Extensions.AspNetCore.Configuration.Secrets`; el antiguo `.AzureKeyVault` ya no se usa.

`Microsoft.AspNetCore.App` incluye casi todos, así que una aplicación web normal no tiene que declararlos. El paquete se elige por el origen que se va a usar, no por el hecho de configurar.

## Los orígenes por defecto

`WebApplication.CreateBuilder` prepara la configuración con este orden:

1. `appsettings.json`.
2. `appsettings.{entorno}.json`, con el entorno activo en el nombre.
3. *User secrets*, solo en `Development`.
4. Variables de entorno del sistema operativo.
5. Argumentos de la línea de comandos.

El orden es la regla que resuelve los conflictos: si una clave aparece en varios orígenes, gana el último añadido. Una variable de entorno llamada `title` sobrescribe el `title` de `appsettings.json`, y un argumento pasado a la aplicación sobrescribe a ambos.

```json
{
  "title": "Mi aplicación",
  "options": {
    "stringOption": "Hola",
    "boolOption": true,
    "integerOption": 42
  }
}
```

El archivo `appsettings.json` es opcional. Si se modifica mientras la aplicación corre, el proveedor lo detecta y entrega los valores nuevos, sin reiniciar como ocurría con `Web.config`. El archivo por entorno sigue la misma estructura y solo necesita las claves que cambian:

```json
{
  "title": "Mi aplicación (desarrollo)",
  "options": {
    "decimalOption": 18.42
  }
}
```

Las claves se fusionan: lo que no aparece en el archivo de entorno se mantiene, y lo que aparece se sobrescribe. Es el equivalente a las transformaciones de `Web.config`, sin archivos duplicados ni herramientas aparte. Para lanzar con un valor puntual, el argumento va detrás de `--`, que separa las opciones de `dotnet run` de las de la aplicación:

```bash
dotnet run -- --title="Otro título"
```

## Consultar un valor

La configuración se pide al contenedor de dependencias como cualquier otro servicio. En el arranque ya está disponible en `builder.Configuration`, y en cualquier clase se recibe `IConfiguration` por constructor:

```csharp
app.Use(async (ctx, next) =>
{
    ctx.Response.Headers["X-App"] = app.Configuration["title"];
    await next();
});
```

El indexador devuelve la cadena asociada a la clave. Para estructuras anidadas se usa `:` como separador:

```csharp
var stringOption = app.Configuration["options:stringOption"]; // "Hola"
```

Esta forma basta para un valor suelto. Cuando la aplicación lee muchos ajustes, las claves escritas a mano se convierten en un problema: un cambio de nombre no lo detecta el compilador y solo aparece en ejecución.

## Acceso tipado

La alternativa es una clase cuyas propiedades reproducen la estructura de la configuración:

```csharp
public class MyAppSettings
{
    public string Title { get; set; } = "";
    public AppOptions Options { get; set; } = new();
}

public class AppOptions
{
    public string StringOption { get; set; } = "";
    public bool BoolOption { get; set; }
    public int IntegerOption { get; set; }
}
```

Se enlaza con `Configure<T>()`, que añade el servicio de opciones:

```csharp
builder.Services.Configure<MyAppSettings>(
    builder.Configuration.GetSection("MyAppSettings"));
```

A partir de ahí, `IOptionsSnapshot<MyAppSettings>` entrega una instancia actualizada en cada petición:

```csharp
app.MapGet("/ajustes", (IOptionsSnapshot<MyAppSettings> options) =>
{
    var settings = options.Value;
    return $"Title: {settings.Title}, opción: {settings.Options.StringOption}";
});
```

`IOptionsSnapshot<T>` relee los valores cuando cambia el origen. `IOptions<T>` entrega una sola instancia, útil cuando no se espera recarga. `IOptionsMonitor<T>` avisa de los cambios y es la elección en un *singleton* o en un servicio en segundo plano. En los tres casos conviene recibir la interfaz por constructor en lugar de pedirla con `GetService<T>()`: el código queda igual de corto y las dependencias se ven en la firma.

## Añadir orígenes propios

`builder.Configuration` permite sumar archivos que no están en la lista por defecto. El ejemplo añade un INI obligatorio y su variante por entorno:

```csharp
builder.Configuration
    .AddIniFile("MySettings.ini", optional: false, reloadOnChange: true)
    .AddIniFile(
        $"MySettings.{builder.Environment.EnvironmentName}.ini",
        optional: true,
        reloadOnChange: true);
```

Cada origen declara si es obligatorio —la aplicación no arranca si falta— y si se recarga al cambiar el archivo. El contenido del INI es el mismo que el del JSON, con secciones entre corchetes:

```ini
title=Mi aplicación

[options]
stringOption=Hola
boolOption=true
integerOption=42
```

Existen métodos equivalentes para JSON y XML: `AddJsonFile()` y `AddXmlFile()`. También se puede vaciar la lista y construirla desde cero, por ejemplo con un diccionario en memoria:

```csharp
builder.Configuration.Sources.Clear();
builder.Configuration.AddInMemoryCollection(new Dictionary<string, string?>
{
    ["title"] = "Otro título"
});
```

Vaciar los orígenes elimina también `appsettings.json` y las variables de entorno. Es una decisión para pruebas o para un host que necesita control total, no algo que se haga por comodidad.

## Secretos

En desarrollo, `dotnet user-secrets init` añade un identificador al proyecto y guarda los valores fuera del repositorio. En producción se usan variables de entorno o un almacén de secretos —Key Vault, por ejemplo— y se cargan como un origen más. Un secreto en `appsettings.json` acaba en el historial de Git y deja de ser secreto en el primer `push`.
