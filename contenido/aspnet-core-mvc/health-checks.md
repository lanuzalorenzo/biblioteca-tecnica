# Comprobaciones de estado

Un orquestador necesita saber si el servicio sigue vivo antes de enviarle tráfico. Un balanceador necesita distinguir una aplicación que responde de una que responde pero no puede hablar con su base de datos. Para eso están los *health checks*: endpoints que resumen el estado de los componentes de la aplicación en una respuesta corta.

## El chequeo mínimo

`AddHealthChecks` registra los servicios y `MapHealthChecks` publica el endpoint. Con eso, una petición a `/health` devuelve `200` y el texto `Healthy`:

```csharp
builder.Services.AddHealthChecks();

var app = builder.Build();
app.MapHealthChecks("/health");
```

El endpoint requiere el paquete `Microsoft.AspNetCore.Diagnostics.HealthChecks` o el metapaquete `Microsoft.AspNetCore.App`. Sin comprobaciones adicionales solo confirma que la aplicación puede atender una petición; no dice nada del resto del sistema.

## Comprobaciones propias

La potencia llega cuando se añaden chequeos. `AddCheck` acepta un nombre y una función que devuelve `Healthy`, `Degraded` o `Unhealthy`:

```csharp
builder.Services.AddHealthChecks()
    .AddCheck("Discos", () =>
    {
        const long minimo = 10_000_000_000;
        foreach (var disco in DriveInfo.GetDrives())
        {
            if (disco.AvailableFreeSpace < minimo)
            {
                return HealthCheckResult.Degraded(
                    $"Quedan menos de 10 GB en {disco.Name}");
            }
        }
        return HealthCheckResult.Healthy();
    });
```

El resultado global es el peor de todos: si un chequeo falla, el endpoint responde `Unhealthy`. Para reutilizar la lógica se implementa `IHealthCheck` en una clase y se registra con `AddCheck<T>`:

```csharp
public class DiscosHealthCheck : IHealthCheck
{
    public Task<HealthCheckResult> CheckHealthAsync(
        HealthCheckContext context, CancellationToken cancellationToken)
    {
        const long minimo = 10_000_000_000;
        foreach (var disco in DriveInfo.GetDrives())
        {
            if (disco.AvailableFreeSpace < minimo)
            {
                return Task.FromResult(HealthCheckResult.Degraded(
                    $"Quedan menos de 10 GB en {disco.Name}"));
            }
        }
        return Task.FromResult(HealthCheckResult.Healthy());
    }
}

builder.Services.AddHealthChecks().AddCheck<DiscosHealthCheck>("Discos");
```

Un chequeo no debe tardar: si consulta una base de datos, se le pone un tiempo máximo y se trata el *timeout* como `Unhealthy`. Un *health check* lento bloquea al orquestador y acaba provocando reinicios en cascada.

## Paquetes de terceros

El proyecto `AspNetCore.Diagnostics.HealthChecks` amplía el *framework* con comprobaciones para SQL Server, MySQL, PostgreSQL, Redis, RabbitMQ, Elasticsearch, Azure y API externas. Cada comprobación vive en su propio paquete NuGet, así que se instala solo la que se usa.

También hay un panel —`HealthChecks.UI`— que recopila el estado de varios servicios y lo muestra en una página. Es útil en un entorno de operación, pero añade un componente y una superficie que hay que proteger: el panel no debe quedar accesible desde internet sin autenticación.

## Qué se publica

Un endpoint de salud es información sobre la infraestructura. En un entorno público conviene separar dos respuestas:

- **Liveness**: el proceso está vivo y puede atender. No consulta dependencias, porque un fallo de la base de datos no debe reiniciar la aplicación.
- **Readiness**: la aplicación puede recibir tráfico, con sus dependencias disponibles. Es la que usa el balanceador para decidir si manda peticiones.

```csharp
app.MapHealthChecks("/health/live", new HealthCheckOptions
{
    Predicate = _ => false
});

app.MapHealthChecks("/health/ready");
```

`Predicate = _ => false` excluye todos los chequeos y deja solo la comprobación de que el proceso responde. La ruta de *readiness* ejecuta los registrados.

## Proteger el detalle

Por defecto, la respuesta es un texto corto (`Healthy`, `Degraded` o `Unhealthy`). Eso es lo que debe ver el balanceador. El detalle de cada chequeo, con nombres de servicios y mensajes de error, se expone con `ResponseWriter` y debe quedar en una ruta interna o protegida. Publicar el estado de la base de datos y de los discos en internet da al atacante un mapa de la infraestructura sin coste.

## Comprobarlo en local

Con la aplicación en marcha, `curl -i http://localhost:5000/health` debe devolver 200 y el texto. Si devuelve 503, algún chequeo está en `Unhealthy`; el detalle de la respuesta o la traza dice cuál. Es una comprobación que conviene incluir en el despliegue: si el endpoint no responde en verde, la versión nueva no debería recibir tráfico.
