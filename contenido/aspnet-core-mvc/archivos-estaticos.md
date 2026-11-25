# Archivos estáticos

ASP.NET Core no sirve archivos estáticos por su cuenta. En una aplicación alojada en IIS era el servidor web quien resolvía las peticiones a CSS, JavaScript o imágenes antes de que llegaran a la aplicación. Aquí todo pasa por el *pipeline*: si ningún componente atiende el recurso, la respuesta es un 404.

Para cubrir esa necesidad está el *middleware* de archivos estáticos, incluido en el paquete `Microsoft.AspNetCore.StaticFiles` y en el metapaquete `Microsoft.AspNetCore.App`. Se añade al *pipeline* con `UseStaticFiles()`:

```csharp
app.UseStaticFiles();

app.MapGet("/", () => "Hola");
```

## Qué peticiones atiende

El componente observa las peticiones entrantes y toma el control cuando la ruta coincide con un archivo del sistema de archivos. Una petición a `/test.html` devuelve el `test.html` de la raíz de `wwwroot`, y lo mismo ocurre con scripts, hojas de estilo o imágenes.

Solo atiende `GET` y `HEAD`. Si el archivo no existe, o el verbo es otro, deja pasar la petición al siguiente componente. Cuando ninguno la recoge, el cliente recibe un 404.

El *middleware* no aplica autorización. Sirve cualquier archivo que esté dentro de la carpeta pública, así que no es el sitio para guardar documentos reservados a algunos usuarios.

## La carpeta pública

Por convención los archivos se buscan en `wwwroot`, en la raíz del proyecto. El nombre puede cambiarse al construir el host con `UseWebRoot()`, y la ruta pública no tiene por qué coincidir con la física.

La opción `RequestPath` fija el prefijo desde el que se publican. Con `RequestPath = "/static"`, una petición a `/static/index.html` devuelve el archivo, mientras que `/index.html` deja de encontrarlo aunque exista. El archivo sigue en `wwwroot` y se sirve bajo el prefijo nuevo: `RequestPath` cambia la URL pública, no decide qué archivos quedan fuera de ella.

## Opciones de configuración

`UseStaticFiles()` acepta un objeto `StaticFileOptions` con estas propiedades:

- `ServeUnknownFileTypes`: sirve extensiones que el componente no reconoce.
- `DefaultContentType`: tipo que se asigna a esos archivos.
- `RequestPath`: prefijo de la URL desde el que se publican.
- `OnPrepareResponse`: permite retocar la respuesta antes de enviarla.
- `ContentTypeProvider`: decide el *content-type* de cada ruta.
- `FileProvider`: cambia el origen de los archivos.

Por defecto `ServeUnknownFileTypes` es `false`: una petición a `/archivo.xyz` devuelve 404 aunque el archivo exista. Al activarlo, el contenido se envía con el tipo declarado en `DefaultContentType`. Conviene limitarlo a extensiones conocidas; abrir el servicio a cualquier archivo amplía la superficie sin necesidad.

`OnPrepareResponse` se ejecuta justo antes de enviar la respuesta. Sirve para añadir cabeceras o ajustar la caché:

```csharp
app.UseStaticFiles(new StaticFileOptions
{
    OnPrepareResponse = ctx =>
    {
        ctx.Context.Response.Headers.CacheControl =
            "public,max-age=604800";
    }
});
```

`ContentTypeProvider` recibe una implementación de `IContentTypeProvider`: un método que, dada una ruta, devuelve el tipo MIME que le corresponde. `FileProvider` sustituye el sistema de archivos por cualquier implementación de `IFileProvider`, ya sea Azure Storage, una base de datos o un sistema en memoria. La interfaz es pequeña:

```csharp
public interface IFileProvider
{
    IFileInfo GetFileInfo(string subpath);
    IDirectoryContents GetDirectoryContents(string subpath);
    IChangeToken Watch(string filter);
}
```

## Navegación por directorios

`UseDirectoryBrowser()` añade un listado HTML cuando la ruta coincide con una carpeta. Antes hay que registrar el servicio:

```csharp
builder.Services.AddDirectoryBrowser();
app.UseDirectoryBrowser();
```

Con el componente activo, una petición a la raíz muestra el contenido de `wwwroot` y otra a `/images` muestra esa subcarpeta. `DirectoryBrowserOptions` admite `RequestPath`, `FileProvider` y `Formatter`, que decide el HTML generado a través de `IDirectoryFormatter`.

Viene desactivado por un motivo: publica la estructura de carpetas y los nombres de los archivos. Se activa de forma expresa, y en producción solo si el contenido no revela nada.

## Documentos por defecto

Los servidores web suelen devolver un archivo cuando se pide una carpeta. `UseDefaultFiles()` reproduce ese comportamiento: si la ruta corresponde a un directorio y dentro hay un documento por defecto, reescribe la URL para añadirlo y deja seguir la petición.

Los nombres que prueba son `default.htm`, `default.html`, `index.htm` e `index.html`. `DefaultFilesOptions` permite cambiarlos y también fijar `RequestPath` o `FileProvider`.

Este componente no devuelve el contenido: solo reescribe la ruta. Por eso va antes del *middleware* de archivos estáticos, que es quien sirve el archivo encontrado. Si va después, la petición ya ha pasado y el documento no se entrega.

## Los tres componentes en una línea

`UseFileServer()` reúne archivos estáticos, documentos por defecto y navegación por directorios. La navegación sigue siendo opcional y hay que pedirla:

```csharp
builder.Services.AddDirectoryBrowser();
app.UseFileServer(enableDirectoryBrowsing: true);
```

El orden interno lo resuelve el propio extensor: documentos por defecto, archivos estáticos y, si se ha pedido, navegación. Para una aplicación que solo publica CSS, JavaScript e imágenes, `UseStaticFiles()` basta; `UseFileServer()` ahorra tres llamadas cuando se necesita el comportamiento completo.

## Activos con huella y caché

Desde .NET 9, `MapStaticAssets()` sirve los archivos del proyecto con una huella en el nombre y una cabecera de caché larga. La huella cambia cuando cambia el contenido, así que el navegador puede guardar el archivo durante un año sin riesgo de quedarse con una versión vieja. Se usa en lugar de `UseStaticFiles()` para los activos que forman parte del build; `UseStaticFiles()` sigue siendo la opción para archivos que se añaden después de publicar o que no pasan por el pipeline de compilación.

## Seguridad

Todo lo que se copia a `wwwroot` es público, incluidos los mapas de origen, los archivos de configuración que se hayan dejado ahí y los documentos de ejemplo. Antes de publicar se revisa esa carpeta. Los archivos que solo deben ver algunos usuarios se sirven desde una acción que compruebe permisos, no desde el middleware estático.
