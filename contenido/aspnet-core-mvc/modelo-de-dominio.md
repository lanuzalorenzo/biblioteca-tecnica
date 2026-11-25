# El modelo de dominio

El modelo es la representación del dominio sobre el que gira la aplicación. Incluye las entidades de negocio, la lógica que las gestiona, las reglas que aseguran su consistencia y la comunicación con el almacén de datos. MVC no impone cómo implementarlo: esa decisión es del equipo, y es la que más influye en que el sistema se pueda mantener.

## Qué contiene

En un sistema de gestión empresarial, el modelo tendría clientes, facturas y pedidos; en un blog, artículos, comentarios y usuarios. Alrededor de esas entidades aparecen cuatro piezas:

- **Entidades**, que representan los datos y, si el diseño es rico, también las operaciones que tienen sentido sobre ellos.
- **Servicios de dominio o de aplicación**, que ofrecen operaciones de alto nivel: crear una factura, obtener los artículos de un mes, cancelar un pedido.
- **Reglas y validaciones**, que impiden guardar un estado inconsistente.
- **Persistencia**, que traduce las entidades a un almacén y viceversa.

También pueden aparecer objetos de transferencia (DTO) cuando el modelo se comunica con otras capas o con otros sistemas. Su papel es evitar que las entidades salgan del dominio con detalles de persistencia o de presentación.

## Entidades

Lo más frecuente es que las entidades sean clases POCO, con propiedades que reflejan el dominio:

```csharp
public class Post
{
    public int Id { get; set; }
    public string Title { get; set; } = "";
    public string Author { get; set; } = "";
    public string Text { get; set; } = "";
    public DateTime Date { get; set; }
}
```

En un diseño guiado por el dominio, la entidad puede incluir métodos que encapsulan reglas:

```csharp
public class Order
{
    public int Id { get; set; }
    public DateTime OrderDate { get; set; }
    public Customer Customer { get; set; } = new();
    private readonly List<OrderLine> _lines = new();

    public void AddProduct(Product product) { /* ... */ }
    public void Ship() { /* ... */ }
    public void Cancel(string cause) { /* ... */ }
}
```

La segunda forma protege las invariantes: nadie puede añadir una línea saltándose la regla. La primera es más simple y encaja cuando la lógica vive en servicios. Ninguna es correcta por sí sola; la elección depende de la complejidad del dominio y de la comodidad del equipo para probarlo.

## Servicios

Los servicios encapsulan la lógica y el acceso a datos detrás de una interfaz. El controlador solo ve operaciones de alto nivel:

```csharp
public interface ICustomerServices
{
    CustomerDto GetById(int customerId);
    IEnumerable<CustomerSearchResult> SearchCustomers(string searchText, int page);
    void CreateCustomer(CustomerDto customer);
}
```

La interfaz permite cambiar la implementación —base de datos, API remota, repositorio en memoria— sin tocar el controlador. También facilita las pruebas: un doble del servicio devuelve datos controlados y no arrastra la base de datos.

## Persistencia

Entity Framework Core es la opción habitual en .NET, pero no la única. Dapper y los micro-ORM ligeros sirven cuando se quiere controlar el SQL; `SqlClient` o `Npgsql` permiten acceso directo. En aplicaciones pequeñas, el acceso a datos puede vivir dentro de los servicios; en aplicaciones grandes, se separa en un repositorio o en un proyecto propio.

La regla que no cambia es que el modelo no debe depender de la presentación. Si una entidad necesita `HttpContext`, una sesión o un `IActionResult`, la dependencia está en el sitio equivocado. Esa contaminación impide reutilizar el modelo y obliga a levantar una aplicación web para probarlo.

## Inyección de dependencias

El controlador recibe los servicios por constructor, y el contenedor los resuelve:

```csharp
public class CustomerController : Controller
{
    private readonly ICustomerServices _customerServices;

    public CustomerController(ICustomerServices customerServices)
    {
        _customerServices = customerServices;
    }

    public IActionResult Index(int id)
    {
        var customer = _customerServices.GetById(id);
        return customer is null ? NotFound() : View(customer);
    }
}
```

El controlador no sabe si el servicio usa EF Core, Dapper o una API. Solo conoce el contrato. Esa es la ventaja de la inyección y la razón de que el registro se haga en un único sitio.

## Validación en el modelo

El modelo también es responsable de que no entren datos inconsistentes. Puede comprobar que un cliente tiene razón social, que una hora está entre 0 y 23 o que el número de una factura no se ha usado. Esa validación es distinta de la validación de entrada que hace MVC con las anotaciones: la primera protege el dominio y se ejecuta siempre; la segunda comprueba el formulario y puede quedarse corta.

La duplicación se evita poniendo la regla en un único punto del dominio y llamándola desde el controlador o desde el servicio. Si la regla solo vive en el controlador, otra vía de entrada —una API, un proceso en segundo plano— la salta.

## Lo que no debe hacer

El modelo no genera HTML, no formatea mensajes para la interfaz, no redirige ni devuelve códigos de estado. Tampoco accede a la sesión, a las cookies o a la petición. Todo eso son responsabilidades de la vista o del controlador. Mantener esa frontera es lo que permite probar el dominio sin navegador y reutilizarlo en una API, una tarea en segundo plano o una aplicación de escritorio.

## Organización

En un proyecto pequeño, el modelo puede vivir en una carpeta `Models/` con subcarpetas `Entities`, `Services` y `Repositories`. En uno real, conviene separarlo en proyectos: `MiApp.Web` para controladores y vistas, `MiApp.Domain` para entidades y reglas, `MiApp.Data` para persistencia. La separación no es un fin en sí mismo; sirve para que las dependencias apunten hacia dentro y para que el dominio no arrastre ASP.NET Core.

No hay una arquitectura única. La decisión debe responder a las necesidades del sistema, no a una moda. Lo que sí es universal es la dirección de las dependencias y la prohibición de que el dominio conozca la web.
