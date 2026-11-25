# HTTPS y cookies

Servir por HTTP dejó de ser aceptable hace años: los navegadores marcan la página como no segura y los datos viajan en claro. ASP.NET Core trae HTTPS activado por defecto en desarrollo y ofrece dos *middlewares* para forzarlo en producción. La otra mitad de la seguridad del navegador son las cookies, que necesitan una política explícita cuando hay que cumplir con el consentimiento del usuario.

## HTTPS en desarrollo

Al crear un proyecto con Visual Studio o con la CLI, el servidor escucha en HTTP y HTTPS a la vez:

```text
info: Microsoft.Hosting.Lifetime[0]
      Now listening on: https://localhost:7123
info: Microsoft.Hosting.Lifetime[0]
      Now listening on: http://localhost:5123
```

El primer uso del SDK crea un certificado de desarrollo y lo instala. El navegador lo acepta con una advertencia hasta que se confía en él. Para quitarla, se marca el certificado como de confianza desde la línea de comandos:

```bash
dotnet dev-certs https --trust
```

El comando pide confirmación una vez y deja el certificado instalado para el usuario actual. No se copia a otros equipos ni se usa en producción.

## Redirigir a HTTPS

`UseHttpsRedirection` captura las peticiones HTTP y responde con una redirección a la misma URL por HTTPS. Por defecto devuelve un `307`, que conserva el método y el cuerpo, y toma el puerto de la configuración del proyecto:

```csharp
app.UseHttpsRedirection();
```

El puerto también se puede fijar con la variable `ASPNETCORE_HTTPS_PORT` o desde código:

```csharp
builder.Services.AddHttpsRedirection(options =>
{
    options.RedirectStatusCode = StatusCodes.Status301MovedPermanently;
    options.HttpsPort = 5001;
});
```

El `301` es permanente y el navegador lo cachea; en desarrollo conviene el `307` por defecto. El *middleware* va antes de cualquier cosa que escriba en la respuesta, para que la redirección no llegue tarde.

## HSTS: HTTP Strict Transport Security

HSTS (*HTTP Strict Transport Security*) añade una cabecera que ordena al navegador no volver a pedir ese dominio por HTTP durante un tiempo. Se define en la RFC 6797 y se activa con `UseHsts`:

```csharp
if (!app.Environment.IsDevelopment())
{
    app.UseHsts();
}
```

Solo se activa fuera de desarrollo: una cabecera HSTS mal puesta en local deja el navegador apuntando a HTTPS en `localhost` durante meses. La configuración fina se hace en `AddHsts`, con `MaxAge`, `IncludeSubDomains`, `Preload` y la lista de hosts excluidos.

`UseHsts` no sustituye a `UseHttpsRedirection`: el primero instruye al navegador para el futuro, el segundo corrige la petición actual. Tampoco sirve si el sitio se sirve solo por HTTP en un dominio interno; en ese caso, HSTS rompe el acceso.

## Cookies y consentimiento

La normativa europea de protección de datos obliga a pedir permiso para las cookies que no son imprescindibles. ASP.NET Core permite marcar una cookie como esencial al crearla:

```csharp
app.MapGet("/cookies", async ctx =>
{
    ctx.Response.Cookies.Append("esencial", "1",
        new CookieOptions { IsEssential = true });
    ctx.Response.Cookies.Append("analitica", "1",
        new CookieOptions { IsEssential = false });
    await ctx.Response.WriteAsync("Cookies creadas");
});
```

Con `UseCookiePolicy`, las cookies no esenciales se eliminan de la respuesta mientras el usuario no haya dado su consentimiento:

```csharp
builder.Services.Configure<CookiePolicyOptions>(options =>
{
    options.CheckConsentNeeded = _ => true;
});

app.UseCookiePolicy();
```

El *middleware* se añade al pipeline antes de los componentes que escriben cookies.

El consentimiento se registra con `ITrackingConsentFeature.GrantConsent()`, que añade la cookie de permiso. La aplicación decide después si muestra un aviso y cómo lo cierra. `CheckConsentNeeded` puede depender de la petición, por ejemplo para no pedir permiso en una intranet.

## Atributos de una cookie

Una cookie de autenticación o de sesión se emite con tres atributos como mínimo:

- `HttpOnly`, para que JavaScript no pueda leerla.
- `Secure`, para que solo viaje por HTTPS.
- `SameSite`, con `Lax` o `Strict` según el flujo; `None` exige `Secure` y abre la puerta a peticiones cruzadas.

El nombre, la caducidad y la ruta se ajustan en las opciones del esquema o del middleware. Una cookie sin `HttpOnly` y sin `Secure` convierte cualquier fallo de XSS en un robo de sesión.
