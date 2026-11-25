# Autenticación con cookies

Autenticar es averiguar quién es el usuario; autorizar es decidir qué puede hacer. Esta nota cubre lo primero con el *middleware* de autenticación por cookies de ASP.NET Core. El *middleware* no pinta formularios ni valida contraseñas: eso lo pone la aplicación. Él se encarga de emitir la cookie, cifrarla, leerla en las peticiones siguientes y reconstruir con ella la identidad del usuario.

Para escenarios completos —registro, contraseñas, recuperación de cuenta, proveedores externos— existe ASP.NET Core Identity, un *framework* aparte. Aquí se monta el mecanismo mínimo, que sirve para entender qué hay debajo y para aplicaciones pequeñas.

## Registrar el esquema

El *middleware* vive en `Microsoft.AspNetCore.Authentication.Cookies`, incluido en el metapaquete `Microsoft.AspNetCore.App`. El registro se hace en dos pasos: `AddAuthentication()` crea el constructor de esquemas y `AddCookie()` añade el esquema de cookies.

```csharp
builder.Services
    .AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
    .AddCookie();
```

El argumento de `AddAuthentication` fija el esquema por defecto. Sin él, el *middleware* no sabe con qué esquema autenticar cada petición y `User.Identity` llega vacío. `CookieAuthenticationDefaults.AuthenticationScheme` vale `"Cookies"`, y ese nombre se reutiliza al iniciar y cerrar sesión.

El mismo constructor admite más esquemas. Los proveedores externos, como Google o Microsoft, se añaden con `AddGoogle` o `AddMicrosoftAccount` y suelen exigir un paquete NuGet propio. Las credenciales se leen de configuración, nunca se escriben en el código.

```csharp
builder.Services.AddAuthentication()
    .AddCookie()
    .AddGoogle(options =>
    {
        options.ClientId = builder.Configuration["Authentication:Google:ClientId"]!;
        options.ClientSecret = builder.Configuration["Authentication:Google:ClientSecret"]!;
    });
```

El pipeline debe llamar a `UseAuthentication()` antes de la autorización y de los endpoints. Si se coloca después, la identidad no está lista cuando el endpoint la necesita:

```csharp
app.UseRouting();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();
```

## Configurar la cookie

`AddCookie()` acepta un delegado para ajustar el comportamiento. Estas opciones cubren las más frecuentes: nombre, seguridad, caducidad y rutas de redirección.

```csharp
builder.Services
    .AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
    .AddCookie(options =>
    {
        options.Cookie.Name = "Auth";
        options.Cookie.HttpOnly = true;
        options.Cookie.SecurePolicy = CookieSecurePolicy.Always;
        options.Cookie.SameSite = SameSiteMode.Lax;
        options.ExpireTimeSpan = TimeSpan.FromDays(30);
        options.LoginPath = "/users/login";
        options.AccessDeniedPath = "/users/denied";
    });
```

`LoginPath` es la ruta a la que se redirige una petición sin autenticar, y `AccessDeniedPath`, la que recibe un usuario autenticado sin permiso. Los dos valores por defecto apuntan a `/Account/Login` y `/Account/AccessDenied`; si no existen en la aplicación, el navegador acabará en un 404 después de la redirección. `ExpireTimeSpan` fija la validez del ticket, que se renueva mientras haya actividad. La cookie del navegador solo lleva fecha propia cuando el inicio de sesión se marca como persistente.

La cookie contiene un ticket cifrado y firmado con las claves de protección de datos. En una granja de servidores esas claves deben compartirse; si cada nodo usa las suyas, la cookie emitida por uno no se puede leer en otro.

## Iniciar sesión

El alta de la cookie se hace con `SignInAsync`, un extensor de `HttpContext`. Hay que pasarle el esquema y un `ClaimsPrincipal` con una o varias identidades. Cada `Claim` es un atributo del usuario: nombre, correo, rol o cualquier dato propio.

```csharp
app.MapPost("/login", async (HttpContext context, LoginRequest request) =>
{
    // Validar las credenciales contra el almacén de usuarios.
    if (!CredencialesValidas(request))
        return Results.Unauthorized();

    var identity = new ClaimsIdentity(
        CookieAuthenticationDefaults.AuthenticationScheme);
    identity.AddClaim(new Claim(ClaimTypes.Name, request.Usuario));
    identity.AddClaim(new Claim(ClaimTypes.Email, request.Email));
    identity.AddClaim(new Claim(ClaimTypes.Role, "Admin"));

    await context.SignInAsync(
        CookieAuthenticationDefaults.AuthenticationScheme,
        new ClaimsPrincipal(identity));

    return Results.Ok();
});
```

Un usuario puede tener varios roles: basta con añadir un `Claim` de tipo `ClaimTypes.Role` por cada uno. La cookie resultante dura lo que dure la sesión del navegador. Para que sobreviva al cierre se pasa un `AuthenticationProperties` con `IsPersistent`:

```csharp
await context.SignInAsync(
    CookieAuthenticationDefaults.AuthenticationScheme,
    principal,
    new AuthenticationProperties { IsPersistent = true });
```

En una aplicación real, el endpoint no recibe la contraseña por la URL ni la guarda en claro: la comprueba contra un almacén que usa un *hash* lento —bcrypt, Argon2 o el que trae Identity— y solo entonces construye la identidad. El navegador únicamente recibe el ticket cifrado.

## Leer al usuario

Con el esquema por defecto configurado, el *middleware* autentica cada petición y rellena `HttpContext.User`. Para saber si hay usuario, se consulta `User.Identity.IsAuthenticated`; para leer sus datos, la colección `User.Claims`:

```csharp
app.MapGet("/perfil", (HttpContext context) =>
{
    if (context.User.Identity?.IsAuthenticated != true)
        return Results.Unauthorized();

    var name = context.User.Identity.Name;
    var email = context.User.FindFirstValue(ClaimTypes.Email);
    var roles = context.User.FindAll(ClaimTypes.Role).Select(c => c.Value);

    return Results.Ok(new { name, email, roles });
});
```

`User.Identity.Name` devuelve el valor del *claim* de nombre, y los *claims* de rol se filtran por su tipo. Si se usa un esquema con otro nombre, debe coincidir en el registro, en la identidad y en las llamadas a `SignInAsync` y `SignOutAsync`; un nombre distinto en uno de esos puntos deja partes del mecanismo sin funcionar.

## Cerrar sesión

`SignOutAsync` invalida el ticket y pide al navegador que borre la cookie. Se le pasa el mismo esquema con el que se inició la sesión:

```csharp
app.MapPost("/logout", async (HttpContext context) =>
{
    await context.SignOutAsync(
        CookieAuthenticationDefaults.AuthenticationScheme);
    return Results.Ok();
});
```

La llamada sin esquema funciona si hay un esquema de cierre por defecto. Escribirlo de forma explícita evita depender de esa configuración y deja claro qué cookie se está retirando.

## Límites del mecanismo

La cookie de autenticación sirve para una aplicación web que el usuario visita en el navegador. No es la mejor opción para una API consumida por otro servicio o por una aplicación móvil: en esos casos se usa un token Bearer, que se explica en [Tokens para API](#tokens-para-api). Tampoco sustituye a la autorización: una cookie válida dice quién es el usuario, no qué puede hacer.

## Tokens para API

Una API consumida por otro servicio o por una aplicación móvil no puede depender de una cookie de navegador. El cliente guarda un token y lo envía en cada petición:

```http
GET /api/posts HTTP/1.1
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

Un JWT tiene tres partes separadas por puntos: la cabecera, con el algoritmo; el *payload*, con los *claims*; y la firma, que permite comprobar que el servidor lo emitió y que nadie lo modificó. El *payload* no está cifrado: cualquiera puede decodificarlo, así que solo lleva datos no sensibles. La firma protege la integridad, no la confidencialidad.

### Generar un token

El token se emite tras comprobar las credenciales. La clave de firma se lee de configuración y no se escribe en el código:

```csharp
using Microsoft.IdentityModel.JsonWebTokens;
using Microsoft.IdentityModel.Tokens;

var handler = new JsonWebTokenHandler();
var clave = new SymmetricSecurityKey(
    Encoding.UTF8.GetBytes(builder.Configuration["Jwt:Key"]!));

var descriptor = new SecurityTokenDescriptor
{
    Issuer = builder.Configuration["Jwt:Issuer"],
    Audience = builder.Configuration["Jwt:Audience"],
    Expires = DateTime.UtcNow.AddMinutes(15),
    SigningCredentials = new SigningCredentials(clave, SecurityAlgorithms.HmacSha256),
    Claims = new Dictionary<string, object>
    {
        ["sub"] = usuario.Id,
        ["name"] = usuario.Nombre,
        ["role"] = "Admin"
    }
};

var token = handler.CreateToken(descriptor);
return Results.Ok(new { token });
```

Un token de acceso debe durar poco: minutos, no días. Para una sesión larga se usa un *refresh token*, que se guarda en el servidor y se puede revocar. El token de acceso, una vez emitido, no se revoca sin una lista de revocación o un cambio de clave; por eso su vida corta es la protección principal.

### Validar el token

El *middleware* de autenticación JWT se registra con el esquema Bearer y los parámetros de validación:

```csharp
builder.Services
    .AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = builder.Configuration["Jwt:Issuer"],
            ValidAudience = builder.Configuration["Jwt:Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(
                Encoding.UTF8.GetBytes(builder.Configuration["Jwt:Key"]!))
        };
    });

builder.Services.AddAuthorization();

var app = builder.Build();
app.UseAuthentication();
app.UseAuthorization();
```

Con el esquema registrado, `[Authorize]` protege un controlador o una acción y `User` se rellena con los *claims* del token. `[AllowAnonymous]` abre una excepción, por ejemplo en el endpoint que emite el token. Una API que solo acepta tokens no necesita antiforgery: no hay cookie que un sitio ajeno pueda reutilizar.

### Errores que se cometen

- **Clave en el código o en el repositorio.** La clave de firma es un secreto; si se filtra, cualquiera puede emitir tokens válidos.
- **No validar emisor, audiencia o caducidad.** Un token de otro sistema o uno vencido se aceptaría.
- **Guardar datos sensibles en el *payload*.** Es legible por cualquiera que tenga el token.
- **Tokens de larga duración sin revocación.** Un robo de token se convierte en acceso permanente.
- **Usar JWT para una aplicación web con cookies.** Para el navegador, la cookie con `HttpOnly` es más sencilla y más segura; el token se reserva para clientes que no pueden usar cookies.

Para escenarios completos —registro, contraseñas, recuperación, proveedores externos— ASP.NET Core Identity añade las tablas, los flujos y las plantillas. El mecanismo de esta nota sirve para entender la pieza y para APIs pequeñas; Identity es la opción cuando la gestión de usuarios es parte del producto.
