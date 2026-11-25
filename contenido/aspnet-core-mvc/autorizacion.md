# Autorización

La autenticación dice quién es el usuario; la autorización decide si puede ejecutar una acción concreta. Son dos pasos y conviene no mezclarlos: primero se identifica al visitante y después se comprueba si su identidad cumple las reglas del recurso. Una aplicación puede tener usuarios autenticados que no tengan permiso para todo.

La comprobación manual consiste en mirar `User.Identity.IsAuthenticated` dentro de cada manejador. Funciona para un caso suelto, pero repite código y se olvida con facilidad. ASP.NET Core ofrece un *middleware* que lee las reglas declaradas en el endpoint y corta la petición antes de ejecutarlo.

## Registrar los servicios y el middleware

El metapaquete `Microsoft.AspNetCore.App` ya incluye todo lo necesario. Hay que registrar los servicios de autorización y añadir el *middleware* justo después del de autenticación:

```csharp
builder.Services.AddAuthorization();
builder.Services
    .AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
    .AddCookie();

var app = builder.Build();

app.UseRouting();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();
```

El orden importa. `UseAuthorization()` necesita la identidad que prepara `UseAuthentication()`, y ambos deben ir antes de la ejecución del endpoint para que la decisión se tome antes de ejecutar el manejador. Si la autorización va delante de la autenticación, el *middleware* no encuentra usuario y deniega o redirige cuando no debería.

## Exigir autenticación

Un endpoint puede declarar que solo se ejecute con usuario autenticado. `RequireAuthorization()` marca el endpoint para que el *middleware* exija un usuario:

```csharp
app.MapGet("/private", () => "Contenido reservado")
   .RequireAuthorization();
```

Sin usuario, la petición no llega al manejador. El *middleware* devuelve un 302 hacia `LoginPath` —por defecto, `/Account/Login`— y, si esa ruta no existe, el navegador muestra un 404 después de la redirección. El destino se cambia en las opciones de la cookie.

En un controlador MVC, el equivalente es el atributo `[Authorize]`, que se puede aplicar a una acción o a toda la clase:

```csharp
[Authorize]
public class AccountController : Controller
{
    public IActionResult Profile() => View();
}
```

`[AllowAnonymous]` abre una excepción dentro de un controlador protegido. Se usa en el login y en las páginas que deben verse sin cuenta, y conviene revisar que no quede abierta una acción que debería estar cerrada.

## Roles

Los roles se declaran con una sobrecarga que recibe datos de autorización. `AuthorizeAttribute` implementa esa interfaz, y los roles se separan por comas:

```csharp
app.MapGet("/onlyforadmins", () => "Contenido de administración")
   .RequireAuthorization(new AuthorizeAttribute { Roles = "Admin,Superadmin" });
```

Un usuario autenticado que no tenga ninguno de esos roles recibe un 403 y se le redirige a `AccessDeniedPath` si está configurado. La diferencia entre 401 y 403 es la que hay entre «no sé quién eres» y «sé quién eres, pero no puedes pasar».

## Políticas con nombre

Los roles cubren casos simples. Una política agrupa varias condiciones bajo un nombre y se aplica a los endpoints que la necesiten. Se definen al registrar los servicios:

```csharp
builder.Services.AddAuthorization(options =>
{
    options.AddPolicy("UsuarioEspecial", policy =>
        policy.RequireClaim("UserType", "1", "2"));

    options.AddPolicy("AdultoVerificado", policy =>
        policy.RequireAuthenticatedUser()
              .RequireClaim("EdadVerificada", "true"));
});
```

El objeto `policy` es un builder: encadena requisitos como `RequireClaim`, `RequireRole`, `RequireAuthenticatedUser` o `RequireAssertion` para lógica propia.

```csharp
options.AddPolicy("NombreConX", policy =>
    policy.RequireAuthenticatedUser()
          .RequireAssertion(ctx =>
              (ctx.User.Identity?.Name ?? "")
                  .Contains('x', StringComparison.OrdinalIgnoreCase)));
```

Para aplicar una o varias políticas se pasan sus nombres a `RequireAuthorization`:

```csharp
app.MapGet("/reallyprivate", () => "Contenido reservado")
   .RequireAuthorization("UsuarioEspecial", "NombreConX");
```

Cuando se indican varias, se deben cumplir todas. La política se evalúa en cada petición, así que conviene mantener las condiciones baratas y sin dependencias que puedan fallar por su cuenta.

## Autorización basada en recursos

Una política puede necesitar el recurso concreto, no solo el usuario. Para eso existe `IAuthorizationService` y el patrón de *handler*: se implementa `AuthorizationHandler<TRequirement>` y se registra en el contenedor. Es el camino cuando la regla es «puede editar esta factura» y depende del propietario, del estado o de otra relación que no cabe en un *claim*. En aplicaciones pequeñas, una comprobación explícita en el servicio de dominio suele ser más clara; la política se reserva para reglas que se repiten y se quieren declarar junto al endpoint.

## Qué recordar

La autorización no se reparte por el código de cada manejador: se declara en el endpoint y la aplica el *middleware*. Conviene empezar por exigir usuario autenticado, añadir roles cuando el caso sea simple y pasar a políticas cuando la condición tenga varios requisitos o cambie con el tiempo. La interfaz de usuario no autoriza nada: ocultar un botón no impide llamar a la acción.
