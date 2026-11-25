# Trazas y registro de lo que pasa

ASP.NET Core incorpora un sistema de registro propio, pensado para anotar lo que hace la aplicación sin obligar a montar una biblioteca externa. La pieza central es `ILogger`: se pide por inyección de dependencias y se escribe en él con métodos que declaran la importancia del mensaje. El destino de esas anotaciones no está fijado en el código, sino en los proveedores que se registren durante el arranque. Esa separación permite que el mismo mensaje acabe en la consola, en el canal de depuración del IDE o en un servicio remoto sin tocar la clase que lo emite.

## Proveedores y destinos

Cada destino es un paquete NuGet independiente, y una aplicación puede tener varios activos a la vez. Los que mantiene el propio *framework* son estos:

- `Microsoft.Extensions.Logging.Console`, para volcar las trazas a la consola.
- `Microsoft.Extensions.Logging.Debug`, para enviarlas a la ventana de depuración del IDE mediante `Debug.WriteLine`.
- `Microsoft.Extensions.Logging.TraceSource`, para apoyarse en `System.Diagnostics.TraceSource`, la infraestructura clásica de .NET.
- `Microsoft.Extensions.Logging.EventLog`, para el registro de eventos de Windows, válido solo en esa plataforma.

La plantilla arrastra los dos primeros, así que un proyecto recién creado ya escribe en consola y en depuración. Cuando hace falta otro destino —Serilog, NLog o un proveedor propio— se añade el paquete y se registra durante el arranque, sin cambiar una línea de las clases que registran.

## De dónde sale el logger

`WebApplication.CreateBuilder` ya deja configurado lo básico: la consola y el canal de depuración como destinos, y la sección `Logging` de los ajustes como fuente de configuración. En la mayoría de los escenarios no hay que hacer nada más para empezar a ver trazas.

Para escribir se pide `ILogger<T>` al contenedor, con `T` igual a la clase que emite el mensaje. Ese tipo se convierte en la categoría del registro, y es lo que después permite filtrar por origen:

```csharp
public class InventarioService
{
    private readonly ILogger<InventarioService> _logger;

    public InventarioService(ILogger<InventarioService> logger)
    {
        _logger = logger;
    }

    public void Revisar(string almacen)
    {
        _logger.LogInformation("Revisando el almacén {Almacen}", almacen);
    }
}
```

En el arranque se puede pedir el logger de una categoría concreta a partir de `app.Logger` o de la fábrica:

```csharp
var logger = app.Services.GetRequiredService<ILoggerFactory>()
    .CreateLogger("Inicializacion");

logger.LogInformation("Pipeline configurado");
```

La fábrica tiene una versión sin tipo genérico, que recibe un nombre libre. Ese texto pasa a ser la categoría del logger, y conviene elegirlo pensando en los filtros: no tiene por qué coincidir con una clase, basta con que describa el origen del mensaje.

## Niveles de traza

Los niveles ordenan los mensajes por importancia y son la base de cualquier filtro posterior. Se declaran en la enumeración `LogLevel` y conviene elegirlos con criterio, porque un registro que lo anota todo acaba siendo tan inútil como uno vacío.

| Nivel | Cuándo se usa | Ejemplo |
|---|---|---|
| `Trace` | Detalle técnico para depurar; puede contener datos sensibles, así que no se activa en producción | «Conectando a la base con el usuario admin» |
| `Debug` | Cambios y estados puntuales, útiles mientras se desarrolla | «Entrando en SetEstado con el valor 1» |
| `Information` | Flujo normal de la aplicación, con valor a largo plazo | «Recibida una petición a /test» |
| `Warning` | Algo anómalo que no detiene el proceso pero merece revisión | «No se encontró test.txt» |
| `Error` | Un fallo que aborta la operación en marcha, aunque la aplicación siga viva | «Clave duplicada al insertar el registro» |
| `Critical` | Un fallo que exige atención inmediata | «No queda espacio en disco» |

Para cada nivel hay un método extensor sobre `ILogger`: `LogTrace()`, `LogDebug()`, `LogInformation()`, `LogWarning()`, `LogError()` y `LogCritical()`. Todos comparten firma y aceptan el mensaje suelto o una plantilla con marcadores, cuyos valores se sustituyen en el momento de escribir:

```csharp
_logger.LogInformation("Arrancó a las {Hora:t}", DateTime.Now);
```

Las sobrecargas permiten registrar una excepción junto al mensaje. Es la forma correcta de anotar un fallo controlado: la traza conserva el mensaje y la pila completa, sin construir el texto a mano.

```csharp
try
{
    ProcesarCola();
}
catch (Exception ex)
{
    _logger.LogWarning(ex, "Falló el procesamiento de la cola");
}
```

También se puede asociar un identificador a cada entrada, útil para buscar después un suceso concreto en un registro largo. Los identificadores se declaran como constantes en una clase propia y se pasan como primer argumento:

```csharp
public static class Eventos
{
    public const int Arranque = 10;
}

_logger.LogInformation(Eventos.Arranque, "Pipeline configurado");
```

Ninguno de estos métodos tiene variante asíncrona, y no es un olvido: escribir en el registro debe ser tan rápido que no compensa pagar el coste de una llamada asíncrona. Si un destino remoto es lento, el proveedor se encarga de agrupar y enviar por su cuenta.

## Configuración y filtrado

`WebApplication.CreateBuilder` lee la configuración del registro de una sección llamada `Logging` en los ajustes. La sección es opcional, pero cuando existe permite decidir qué se escribe y dónde sin recompilar. En este ejemplo la consola muestra solo avisos y errores, mientras que el canal de depuración admite información y niveles superiores:

```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Debug"
    },
    "Console": {
      "LogLevel": {
        "Default": "Warning"
      }
    },
    "Debug": {
      "LogLevel": {
        "Default": "Information"
      }
    }
  }
}
```

El nombre de cada proveedor en la sección es un alias que define el propio paquete. Los que reconoce el *framework* son `Console`, `Debug`, `EventLog`, `EventSource`, `TraceSource`, `AzureAppServicesFile` y `AzureAppServicesBlob`; los dos últimos solo actúan si se añade su paquete, que no viene en la plantilla. Un nombre mal escrito no da error: simplemente no encuentra a quién aplicar la regla.

Las opciones viven en cualquiera de los orígenes de ajustes, no solo en `appsettings.json`. Una variable de entorno llamada `Logging__Console__LogLevel__Default` con el valor `Warning` hace lo mismo que el bloque anterior: el doble guion bajo sustituye al separador de secciones.

La regla general se escribe en `Logging:LogLevel` y afecta a todos los proveedores; cada proveedor puede después endurecerla o relajarla. El valor `None` silencia una categoría por completo, y las claves admiten prefijos de categoría:

```json
{
  "Logging": {
    "LogLevel": {
      "Default": "None",
      "Microsoft.AspNetCore.Server.Kestrel": "Trace",
      "MiAplicacion": "Information"
    }
  }
}
```

Como los ajustes se recargan al modificarse el archivo, el nivel de traza se puede subir o bajar en caliente, sin reiniciar la aplicación. Es la vía rápida para investigar un fallo en un entorno que ya está en marcha.

## Configuración desde código

Cuando la configuración declarativa no basta, el arranque admite ajustar el registro con `builder.Logging`:

```csharp
builder.Logging.ClearProviders();
builder.Logging.AddConsole();
builder.Logging.SetMinimumLevel(LogLevel.None);
builder.Logging.AddFilter("MiAplicacion", LogLevel.Trace);
builder.Logging.AddFilter<ConsoleLoggerProvider>("Microsoft", LogLevel.Trace);
```

`ClearProviders()` retira todo lo que hubiera puesto la plantilla y deja el terreno limpio; después, `AddConsole()` o `AddDebug()` vuelven a añadir los destinos deseados. El orden importa: lo que se añada después de limpiar es lo único que queda activo.

La configuración desde código y la de los ajustes se combinan: el código decide qué proveedores existen y los ajustes afinan qué escribe cada uno. Para cambios de día a día, los ajustes; para decisiones estructurales del proyecto, el arranque.

## Qué no se escribe en una traza

Contraseñas, tokens, números de tarjeta y datos personales no van al registro. Una traza con una cadena de conexión o una cookie es una fuga, y los registros suelen tener menos protección que la base de datos. Si hace falta correlacionar una petición, se usa un identificador, no el contenido. Para datos de diagnóstico que pueden ser sensibles, se redacta antes de escribir o se deja fuera.
