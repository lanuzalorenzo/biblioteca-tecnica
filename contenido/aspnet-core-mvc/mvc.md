# El patrón MVC

El patrón modelo-vista-controlador separa tres responsabilidades que suelen mezclarse en una aplicación web: qué datos y reglas existen, cómo se presentan y quién decide qué hacer con cada petición. Esa separación no es una imposición de ASP.NET Core; es una forma de organizar el código para que se pueda cambiar una parte sin reescribir las otras y para que cada una se pueda probar por separado.

## Las tres piezas

- El **modelo** representa el dominio: entidades, reglas de negocio, servicios y acceso a datos. No sabe que existe HTTP ni una vista.
- La **vista** presenta la información. En una aplicación web genera HTML y CSS, y puede incluir lógica de presentación, pero no decide qué datos se cargan ni qué operación se ejecuta.
- El **controlador** recibe la petición, valida lo que llega, pide al modelo lo que necesita y elige la vista que se devuelve. Es el coordinador, no el lugar donde vive la lógica de negocio.

La regla que sostiene el patrón es la dirección de las dependencias: el controlador conoce al modelo y a la vista; la vista conoce al modelo que recibe; el modelo no conoce a ninguno de los dos. Cuando el modelo empieza a usar `HttpContext`, sesiones o códigos de estado, deja de poder reutilizarse y de poder probarse sin levantar una aplicación web.

## Un recorrido concreto

Una petición a `/Posts/View/18` entra por el servidor y llega al sistema de routing. El routing la traduce a un controlador y una acción: `PostsController.View(18)`. MVC crea el controlador, resuelve sus dependencias por constructor y enlaza el parámetro `18` con el argumento `id`.

La acción pide al servicio de posts el artículo 18. Si no existe, devuelve `NotFound()`; si existe, construye un modelo de vista con los datos que la página necesita y llama a `View(modelo)`. El motor Razor localiza la plantilla `Views/Posts/View.cshtml`, la ejecuta con ese modelo y devuelve el HTML. El resultado recorre el pipeline en sentido inverso hasta el cliente.

Ese recorrido muestra por qué el patrón encaja con HTTP: cada petición es independiente, el controlador traduce la petición a una operación del dominio y la vista solo se ocupa de la representación. La sesión, las cookies y la caché son estado alrededor del patrón, no parte del modelo.

## Qué gana y qué cuesta

Las ventajas son concretas:

- **Separación de responsabilidades.** Cambiar el diseño de una página no obliga a tocar la consulta que la alimenta.
- **Pruebas unitarias.** El controlador se puede probar con un servicio falso; el modelo, sin HTTP; la vista, con pruebas de integración o revisión visual.
- **Control del marcado.** La vista genera el HTML que se decide, sin controles que impongan su propia estructura.
- **URLs limpias.** El routing separa la dirección de la ubicación física de los archivos.
- **Convención sobre configuración.** Carpetas, nombres y firmas siguen reglas previsibles, lo que reduce decisiones arbitrarias.

El coste también existe. Hay más archivos y más pasos para una pantalla simple, la curva de aprendizaje incluye routing, enlace de modelos y Razor, y el equipo debe respetar las convenciones. En un formulario de dos campos, MVC puede parecer excesivo; en un sistema con decenas de pantallas y un dominio que cambia, la separación paga.

## MVC no es la única opción

ASP.NET Core ofrece varias formas de construir una aplicación web sobre la misma base:

- **MVC**, con controladores y vistas, para aplicaciones con muchas pantallas y una separación clara entre dominio y presentación.
- **Razor Pages**, para páginas centradas en un formulario o una vista concreta, con menos ceremonia que un controlador.
- **API mínimas**, para servicios pequeños y endpoints concretos.
- **Blazor**, para interfaces interactivas con componentes y C# en el cliente o en el servidor.

Todas comparten el pipeline, la inyección de dependencias, la configuración y el servidor. Elegir una no cierra las otras: un proyecto puede tener controladores MVC, páginas Razor y endpoints mínimos a la vez. Lo que cambia es dónde se pone el código de cada ruta.

## MVC en ASP.NET Core

ASP.NET Core MVC es una reescritura del MVC clásico sobre la nueva infraestructura. Conserva el patrón, los controladores, las vistas Razor y el enlace de modelos, y añade el pipeline modular, la inyección de dependencias nativa, la ejecución multiplataforma y el routing de endpoints. No hay Web Forms detrás ni `ViewState`: una vista se localiza y se ejecuta, y eso es todo.

Para ponerlo en marcha se registran sus servicios y se mapean sus rutas:

```csharp
builder.Services.AddControllersWithViews();

var app = builder.Build();

app.UseRouting();
app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");
```

`AddControllersWithViews` registra controladores, vistas, filtros, validación y enlace de modelos. `AddControllers` deja fuera las vistas y sirve para una API. `AddMvc` sigue existiendo, pero añade todo y no permite recortar; en código nuevo se usa el extensor específico.

## Qué no es MVC

MVC no es una arquitectura completa de la aplicación. No dice cómo organizar el dominio, cómo persistir los datos ni cómo dividir la solución en proyectos. Eso lo decide el equipo. Tampoco es un patrón de capas: el modelo puede tener sus propias capas, y el controlador no debe convertirse en una capa de negocio. La separación que propone es horizontal —presentación, control, dominio— y deja abiertas las decisiones de arquitectura que van más allá de la interfaz web.
