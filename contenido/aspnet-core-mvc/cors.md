# CORS: peticiones entre dominios

Un navegador no deja que un script de una página llame a otro dominio por su cuenta. La política *same-origin* exige el mismo protocolo, el mismo host y el mismo puerto; si algo cambia, la petición es de otro origen. CORS (*Cross-Origin Resource Sharing*) es el mecanismo estándar que permite al servidor autorizar esos cruces de forma controlada.

## Qué hace el navegador

Cuando el script pide un recurso a otro origen, el navegador decide si la petición es simple o si necesita permiso previo. Una petición es simple si usa `GET`, `HEAD` o `POST` y se limita a cabeceras y tipos de contenido básicos. En ese caso la envía directamente y comprueba después si la respuesta trae el permiso.

Si la petición usa otro verbo, como `PUT` o `DELETE`, o incluye cabeceras personalizadas, el navegador envía antes una petición `OPTIONS`, llamada *preflight*, para preguntar qué está permitido. El servidor responde con las cabeceras `Access-Control-Allow-*` y el navegador decide si ejecuta la petición real.

```http
OPTIONS /api/resources/18
Access-Control-Request-Method: DELETE
Access-Control-Request-Headers: origin, x-requested-with, accept
Origin: https://miapp.example

HTTP/1.1 204 No Content
Access-Control-Allow-Origin: https://miapp.example
Access-Control-Allow-Methods: POST, GET, OPTIONS, DELETE
Access-Control-Max-Age: 86400
```

`Access-Control-Max-Age` indica cuántos segundos puede el navegador recordar el permiso. Mientras dure, no repite el *preflight*.

## Registrar las políticas

En ASP.NET Core, CORS se configura con `AddCors`. El método admite declarar políticas con nombre, y cada política fija qué orígenes, verbos y cabeceras se aceptan:

```csharp
builder.Services.AddCors(options =>
{
    options.AddPolicy("LecturaDesdeLaWeb", policy =>
    {
        policy
            .WithMethods("GET", "POST")
            .WithOrigins("https://www.mysite.example",
                         "https://www.myothersite.example");
    });
});
```

`WithOrigins` recibe orígenes completos, con protocolo y sin barra final. `WithHeaders` limita las cabeceras y `WithMethods`, los verbos. Los nombres de las políticas se usan en varios puntos, así que conviene guardarlos en constantes.

## Aplicar una política

Hay dos formas de aplicar una política. La primera es el *middleware* `UseCors`, que se coloca entre `UseRouting` y la ejecución de endpoints:

```csharp
app.UseRouting();
app.UseCors("LecturaDesdeLaWeb");

app.MapControllers();
```

La segunda es aplicar la política a un endpoint concreto con `RequireCors`. Es la opción más precisa: solo el endpoint que la declara acepta peticiones de otro origen.

```csharp
app.UseRouting();
app.UseCors();

app.MapGet("/test", () => "ok")
   .RequireCors("LecturaDesdeLaWeb");
```

Si se llama a `UseCors()` sin nombre, se aplica la política marcada como predeterminada. Para marcarla se asigna `options.DefaultPolicyName` al configurar el servicio, o se usa `AddDefaultPolicy`.

## Lo que no se hace en producción

`AllowAnyOrigin`, `AllowAnyMethod` y `AllowAnyHeader` abren la puerta a cualquier página de internet. Sirven para una prueba local, no para un servicio publicado. Tampoco se combinan `AllowAnyOrigin` con credenciales: la especificación lo prohíbe y el *middleware* lanza una excepción al arrancar.

Una política correcta nombra los orígenes reales, limita los verbos a los que el endpoint necesita y deja las cabeceras en la lista mínima. Si la aplicación está detrás de un proxy, el origen que llega puede ser el del proxy; en ese caso se configura `ForwardedHeaders` antes de `UseCors`.

## CORS no es autenticación

CORS protege al usuario de que una página ajena lea respuestas con su sesión. No impide que un cliente que no es un navegador llame a la API: `curl`, un script o un servicio no aplican la política. Para eso están la autenticación y la autorización. Confundir las dos capas deja una API abierta con la excusa de que «CORS ya lo controla».

## Cuándo no hace falta

Si la web y la API se sirven desde el mismo origen —mismo esquema, host y puerto—, no hay petición cruzada y CORS no interviene. También desaparece si la API se consume desde el servidor, como en un renderizado del lado del servidor, porque la llamada no la hace el navegador. Añadir CORS sin un consumidor cruzado solo amplía la superficie.
