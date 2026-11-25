# Inyección de dependencias

La inyección de dependencias es un patrón de diseño que reduce el acoplamiento entre los componentes de una aplicación. Una clase deja de construir por su cuenta los objetos que necesita y los recibe ya preparados; a cambio, el código que la usa decide qué implementación concreta le entrega. ASP.NET Core lo aplica en todos sus componentes internos, así que conviene entenderlo antes de seguir con el arranque.

## Qué problema resuelve

La inyección de dependencias es la técnica con la que se aplica el principio de inversión de dependencias, uno de los cinco SOLID. La idea general es la inversión de control: una clase no crea sus colaboradores, los pide. En inglés se habla de *dependency injection* (DI), *inversion of control* (IoC) y *dependency inversion principle* (DIP); el primero es la técnica y el último, el principio que la justifica. La idea se ve mejor con un ejemplo. Esta clase elimina una factura y avisa al administrador:

```csharp
public class InvoiceServices
{
    public void Remove(int invoiceId)
    {
        using var invoiceRepository = new InvoiceRepository();
        var removed = invoiceRepository.Remove(invoiceId);
        if (removed)
        {
            var notifier = new EmailNotifier();
            notifier.NotifyAdmin($"Factura {invoiceId} eliminada");
        }
    }
}
```

El método funciona, pero arrastra varios problemas:

- Está lleno de fontanería: instancia y libera dependencias en lugar de ocuparse de eliminar la factura y avisar.
- Las mismas líneas se repetirían en cada método que necesite el repositorio o el notificador, lo que va contra el principio de no repetirse.
- La clase queda atada a `InvoiceRepository` y a `EmailNotifier`. Un cambio en cualquiera de las dos puede obligar a tocar `InvoiceServices`.
- La clase no se puede reutilizar sin llevarse esas dos dependencias detrás.
- Las dependencias no se ven por fuera: para conocerlas hay que leer todo el código.
- No se puede probar `Remove` sin probar al mismo tiempo el repositorio y el notificador.

## Las dependencias se reciben

Con inyección de dependencias, la misma clase recibe sus dependencias en el constructor:

```csharp
public class InvoiceServices
{
    private readonly IInvoiceRepository _invoiceRepository;
    private readonly INotifier _notifier;

    public InvoiceServices(IInvoiceRepository invoiceRepository, INotifier notifier)
    {
        _invoiceRepository = invoiceRepository;
        _notifier = notifier;
    }

    public void Remove(int invoiceId)
    {
        var removed = _invoiceRepository.Remove(invoiceId);
        if (removed)
        {
            _notifier.NotifyAdmin($"Factura {invoiceId} eliminada");
        }
    }
}
```

El cambio hace dos cosas. Primero, las dependencias llegan desde fuera y se guardan en campos, así que los métodos trabajan con ellas sin crearlas. Segundo, los tipos son interfaces: a la clase le da igual recibir un `EmailNotifier`, un `TwitterNotifier` o un `MobileNotifier` mientras cumplan el contrato de `INotifier`.

Las ventajas salen de ahí: la clase queda desacoplada de implementaciones concretas, sus dependencias se leen en el constructor, los métodos se centran en su tarea, la clase se puede reutilizar y se puede probar con dobles controlados —fakes, stubs o mocks— sin arrastrar las clases reales.

## El contenedor de dependencias

Para que esto funcione hace falta un componente que cree los objetos y les suministre lo que piden: el contenedor de inversión de control, o contenedor de inyección de dependencias. Actúa como una factoría a la que se le solicitan tipos y que se encarga de instanciarlos con todas sus dependencias.

El contenedor guarda un registro de equivalencias entre interfaces y clases concretas. Para el ejemplo anterior sería algo así:

| Interfaz | Clase concreta |
|---|---|
| `IInvoiceRepository` | `InvoiceRepository` |
| `INotifier` | `EmailNotifier` |

Cuando alguien pide un `InvoiceServices`, el contenedor mira los parámetros de su constructor, ve que necesita `IInvoiceRepository` e `INotifier`, busca en el registro, crea un `InvoiceRepository` y un `EmailNotifier`, y con ellos construye el `InvoiceServices`. Si esos dos tuvieran a su vez otras dependencias, las resolvería igual, hacia abajo, hasta poder crear el objeto pedido.

## Inyección de dependencias en ASP.NET Core

El *framework* trae su propio contenedor y lo usa en todos sus componentes. Cubre los casos habituales y es el que se emplea casi siempre, pero también es intercambiable: cuando hacen falta funciones más avanzadas se puede sustituir por otro, como Autofac.

El registro se hace al arrancar la aplicación, en `builder.Services`, donde se declaran tanto las dependencias propias como las que necesitan los componentes del *framework*:

```csharp
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddScoped<IInvoiceRepository, InvoiceRepository>();
builder.Services.AddScoped<INotifier, EmailNotifier>();
builder.Services.AddScoped<InvoiceServices>();

var app = builder.Build();
```

A partir de ahí, cualquier clase puede pedir lo que tenga registrado y el contenedor se encarga del resto. Un controlador lo recibe por constructor; un middleware, también; una vista, con `@inject`. No hace falta una fábrica ni un localizador de servicios.

## El registro y el consumo no se mezclan

El contenedor se configura en un solo sitio y las clases no lo conocen. Pedir `IServiceProvider` dentro de una clase para resolver dependencias oculta lo que esa clase necesita y complica las pruebas; se usa solo en casos muy concretos, como una factoría que decide la implementación en tiempo de ejecución. Lo normal es declarar las dependencias en el constructor y dejar que el contenedor las resuelva.
