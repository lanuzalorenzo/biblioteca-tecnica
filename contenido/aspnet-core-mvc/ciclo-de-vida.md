# Ciclo de vida de la aplicación

Una aplicación ASP.NET Core no solo atiende peticiones: arranca, se mantiene viva y se detiene. En cada una de esas fases se puede ejecutar código propio. El arranque sirve para calentar cachés o comprobar dependencias; el cierre, para terminar trabajos a medias; y el tiempo en ejecución, para tareas periódicas que no dependen de que llegue una petición.

## Los tres avisos del host

El host publica tres tokens de cancelación que marcan el estado de la aplicación: `ApplicationStarted`, `ApplicationStopping` y `ApplicationStopped`. Se obtienen de `IHostApplicationLifetime`:

```csharp
public interface IHostApplicationLifetime
{
    CancellationToken ApplicationStarted { get; }
    CancellationToken ApplicationStopping { get; }
    CancellationToken ApplicationStopped { get; }
    void StopApplication();
}
```

El registro se hace sobre el token que interesa. El ejemplo escribe una línea en un archivo cuando la aplicación arranca y otra cuando empieza a detenerse:

```csharp
var logFilePath = Path.Combine(app.Environment.ContentRootPath, "log.txt");

app.Lifetime.ApplicationStarted.Register(() =>
    File.AppendAllText(logFilePath, $"{DateTime.Now}: Starting{Environment.NewLine}"));

app.Lifetime.ApplicationStopping.Register(() =>
    File.AppendAllText(logFilePath, $"{DateTime.Now}: Stopping{Environment.NewLine}"));
```

`ApplicationStopping` avisa de que el cierre ha comenzado; `ApplicationStopped`, de que ya no queda nada que hacer. Entre ambos, el host espera a que terminen los servicios en segundo plano con un tiempo máximo.

## Trabajo en segundo plano

Una tarea periódica no debe vivir dentro de un controlador ni depender de que llegue tráfico. Para eso están los servicios hospedados: una clase que hereda de `BackgroundService` y ejecuta su lógica en `ExecuteAsync` mientras la aplicación siga viva.

```csharp
public class RegistroPeriodico : BackgroundService
{
    private readonly ILogger<RegistroPeriodico> _logger;

    public RegistroPeriodico(ILogger<RegistroPeriodico> logger)
    {
        _logger = logger;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        for (var i = 1; !stoppingToken.IsCancellationRequested; i++)
        {
            _logger.LogInformation("Vuelta {Numero}", i);
            try
            {
                await Task.Delay(TimeSpan.FromMinutes(1), stoppingToken);
            }
            catch (OperationCanceledException)
            {
                break;
            }
        }
    }
}
```

El token que llega como parámetro se cancela cuando la aplicación empieza a cerrarse. Hay que pasarlo a `Task.Delay` y comprobarlo en cada vuelta; así el bucle termina y el cierre no se queda esperando. El servicio se registra como hospedado, no como *singleton* suelto:

```csharp
builder.Services.AddHostedService<RegistroPeriodico>();
```

Al arrancar, el host busca todas las implementaciones registradas con `AddHostedService`, las inicia y las detiene en orden inverso al arranque. Desde .NET 6, una excepción no controlada en un servicio hospedado detiene el host por defecto. Si el fallo es recuperable, se captura y se registra; el `OperationCanceledException` del cierre se trata como salida normal.

## Tareas puntuales frente a tareas continuas

Un evento del ciclo de vida es puntual: se ejecuta una vez. Un servicio hospedado es continuo: se ejecuta mientras la aplicación esté viva. Si la tarea solo tarda unos segundos, va en el evento; si espera, reintenta o duerme entre vueltas, va en un servicio hospedado.

## Limpieza al cerrar

Los servicios registrados en el contenedor que implementan `IDisposable` o `IAsyncDisposable` se liberan al cerrar el host. Un servicio en segundo plano que abre conexiones o escribe archivos debe aprovechar esa liberación o su propio `StopAsync` para dejar el estado consistente. El host espera un tiempo limitado; una tarea que no responde al token de cancelación retrasa el cierre y, al final, el proceso se corta.

## Arranque preparado para producción

El arranque no debe depender de que un servicio externo esté disponible en el instante exacto. Si la base de datos tarda en aceptar conexiones, la aplicación puede reintentar con una política o fallar y dejar que el orquestador la reinicie. Lo que no conviene es un bucle infinito que impida arrancar y oculte el problema. Para eso están las comprobaciones de estado, que separan «el proceso está vivo» de «puede atender».
