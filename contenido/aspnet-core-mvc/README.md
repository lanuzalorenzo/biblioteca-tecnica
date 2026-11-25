# ASP.NET Core MVC

ASP.NET Core es la plataforma de Microsoft para construir aplicaciones y servicios web sobre .NET. Una petición entra por un servidor, recorre una cadena de componentes y termina en el código que la atiende; el patrón MVC reparte ese código entre un modelo que representa el dominio, una vista que lo presenta y un controlador que coordina ambos. La misma infraestructura sirve para devolver páginas HTML y para publicar una API que consuma otro sistema.

El punto de partida es .NET 10, la versión de soporte extendido vigente. Las ideas del patrón y del pipeline no han cambiado desde las primeras versiones, pero el arranque sí: `Startup` y `ConfigureServices` dieron paso a un único `Program.cs` con `WebApplication.CreateBuilder`. Los ejemplos usan ese modelo, `System.Text.Json`, `fetch` y EF Core 10; lo que sigue siendo válido del modelo anterior se señala cuando hace falta.

## Contenido

| Nota | Qué cubre |
|---|---|
| [Historia de ASP.NET Core MVC](historia-de-asp-net-core-mvc.md) | De Web Forms a .NET 11: qué se dejó atrás y por qué |
| [Qué es ASP.NET Core](que-es-asp-net-core.md) | Plataforma, servidores, mapa de tecnologías y relación con .NET |
| [Instalación y primer proyecto](instalacion-y-primer-proyecto.md) | SDK, plantillas, estructura inicial y primer endpoint |
| [Compilación y estructura](compilacion-y-estructura.md) | `dotnet watch`, archivos del proyecto, `.csproj` y qué se versiona |
| [Paquetes NuGet](paquetes-nuget.md) | Referencias, metapaquetes, marcos compartidos y auditoría |
| [Arranque de la aplicación](arranque-de-la-aplicacion.md) | `Program.cs`, host, servicios, pipeline y orden de las llamadas |
| [Modelos de ejecución](modelos-de-ejecucion.md) | Kestrel, proxy inverso, HttpSys y alojamiento en IIS |
| [Configuración y servicios](configuracion-y-servicios.md) | Contenedor, tiempos de vida y composición del pipeline |
| [Configuración de la aplicación](configuracion-de-la-aplicacion.md) | Orígenes, entorno, opciones tipadas y secretos |
| [Entornos de ejecución](entornos-de-ejecucion.md) | Development, Staging, Production y configuración por entorno |
| [Inyección de dependencias](inyeccion-de-dependencias.md) | El patrón, el contenedor y sus límites |
| [Ciclo de vida](ciclo-de-vida.md) | Arranque, apagado y servicios en segundo plano |
| [Arquitectura modular](arquitectura-modular.md) | OWIN, pipeline y composición por middlewares |
| [Middlewares propios](middlewares-personalizados.md) | Clases, `IMiddleware`, extensores y ramas con `Map` |
| [Middlewares adicionales](middlewares-adicionales.md) | Compresión y reescritura de URL |
| [Archivos estáticos](archivos-estaticos.md) | `wwwroot`, opciones, documentos por defecto y seguridad |
| [HTTPS y cookies](https-y-cookies.md) | Certificado de desarrollo, redirección, HSTS y consentimiento |
| [Routing](routing.md) | Endpoint routing, plantillas, restricciones y generación de URL |
| [CORS](cors.md) | Peticiones cruzadas, preflight y políticas |
| [Autenticación con cookies](autenticacion-con-cookies.md) | Esquema, claims, login, logout y tokens para API |
| [Autorización](autorizacion.md) | `[Authorize]`, roles, políticas y 401 frente a 403 |
| [Sesiones y estado](sesiones.md) | Sesión, TempData y qué no guardar |
| [Caché](cache.md) | Memoria, distribuida, respuestas y salida |
| [Diagnóstico y errores](diagnostico-y-errores.md) | Página de desarrollo, manejadores, 404 y reejecución |
| [Trazas](trazas.md) | `ILogger`, niveles, filtros y qué no registrar |
| [Health checks](health-checks.md) | Liveness, readiness y protección del detalle |
| [Internacionalización](internacionalizacion.md) | Cultura, recursos, localizadores y middleware |
| [El patrón MVC](mvc.md) | Responsabilidades, recorrido de una petición y coste |
| [El modelo de dominio](modelo-de-dominio.md) | Entidades, servicios, persistencia y validación |
| [Acceso a datos](acceso-a-datos.md) | Entity Framework Core 10, consultas, migraciones y errores frecuentes |
| [Rutas de MVC](rutas-mvc.md) | Convención, atributos, generación de URL y áreas |
| [Controladores y acciones](controladores-y-acciones.md) | Convenciones, resultados, verbos y asincronía |
| [Enlace de modelos](enlace-de-modelos.md) | Orígenes, objetos complejos, archivos y sobrepublicación |
| [Validación de datos](validacion-de-datos.md) | Anotaciones, `ModelState`, reglas propias y cliente |
| [Razor](razor.md) | Sintaxis, codificación, layouts, parciales y componentes |
| [Layouts y parciales](layouts-y-parciales.md) | Reutilización de marcado y cuándo usar cada pieza |
| [Formularios y helpers](formularios-y-helpers.md) | Tag helpers, listas, validación y antiforgery |
| [AJAX](ajax.md) | `fetch`, parciales, JSON, errores y estados de carga |
| [API HTTP](apis-rest.md) | REST, `[ApiController]`, Problem Details, OpenAPI y consumo |
| [Razor Pages](razor-pages.md) | Páginas, `PageModel`, handlers y filtros |
| [Despliegue y calidad](despliegue-y-calidad.md) | Publicación, IIS, Linux, contenedores, pruebas y migraciones |

Las notas se leen en ese orden, pero cada una se sostiene sola. Quien ya conozca MVC puede empezar por routing y controladores; quien venga de otra plataforma encontrará en las primeras el mapa de piezas y el arranque real de un proyecto.
