# Patrones de fiabilidad

Un fallo transitorio es el que se arregla repitiendo; un fallo permanente es el que empeora si se repite. Distinguirlos es la primera decisión de todos los patrones de este módulo. Los ejemplos se ejecutaron con .NET 10.0.404 el 24 de noviembre de 2026.

## Reintentos con espera

Un reintento tiene sentido cuando el fallo es de red, de tiempo o de capacidad momentánea. No lo tiene ante un `400`, un `401` o un `404`: la petición volverá a fallar igual, y repetirla añade carga.

La espera entre intentos crece de forma exponencial y lleva un componente aleatorio para que varios clientes no reintenten a la vez. El patrón se llama *exponential backoff with jitter*:

```csharp
static async Task<int> ConReintentos(Func<int, Task<int>> accion, int maximo = 4)
{
    var azar = new Random(7);
    for (var intento = 1; intento <= maximo; intento++)
    {
        try { return await accion(intento); }
        catch (Exception ex) when (intento < maximo)
        {
            var espera = TimeSpan.FromMilliseconds(20 * Math.Pow(2, intento - 1))
                         + TimeSpan.FromMilliseconds(azar.Next(0, 10));
            await Task.Delay(espera);
        }
    }
    throw new InvalidOperationException("sin intentos");
}
```

La salida con una operación que falla dos veces y acierta a la tercera:

```text
intento 1 falla (TimeoutException); espera 23 ms
intento 2 falla (TimeoutException); espera 48 ms
reintento: resultado 42 tras 3 llamadas
```

El número de intentos se limita siempre. Un reintento sin tope convierte un fallo del servidor en una tormenta de peticiones. En producción, `Microsoft.Extensions.Http.Resilience` o Polly envuelven esta lógica y añaden el presupuesto de tiempo y la telemetría.

## Interruptor

El interruptor, o *circuit breaker*, cuenta los fallos de una dependencia y, al pasar el umbral, deja de llamarla durante un tiempo. Mientras está abierto, la respuesta es inmediata y barata: el sistema no espera a que una dependencia muerta conteste.

Tiene tres estados. **Cerrado** deja pasar las llamadas y cuenta los fallos. **Abierto** las rechaza sin llamar. **Semiabierto**, tras el enfriamiento, deja pasar una de prueba: si acierta, cierra; si falla, vuelve a abrir.

```csharp
sealed class Cortacircuitos(int umbral, TimeSpan enfriamiento)
{
    private int _fallos;
    private DateTime _abre;
    private int _probando;

    public async Task<T> Ejecutar<T>(Func<Task<T>> accion)
    {
        if (DateTime.UtcNow < _abre)
            throw new InvalidOperationException("circuito abierto");
        if (_fallos >= umbral && Interlocked.Exchange(ref _probando, 1) == 1)
            throw new InvalidOperationException("circuito abierto");
        try
        {
            var r = await accion();
            _fallos = 0;
            Volatile.Write(ref _probando, 0);
            return r;
        }
        catch
        {
            if (++_fallos >= umbral) _abre = DateTime.UtcNow + enfriamiento;
            Volatile.Write(ref _probando, 0);
            throw;
        }
    }
}
```

```text
circuito 1: dependencia caida
circuito 2: dependencia caida
circuito 3: dependencia caida
circuito 4: circuito abierto
circuito 5: circuito abierto
circuito tras enfriamiento: ok
```

Un interruptor se pone por dependencia, no por aplicación: la base de datos y el servicio de correo no deben compartir el mismo contador. Y se combina con el reintento dejando el interruptor por fuera: la llamada completa cuenta como un fallo, no cada intento.

## Idempotencia

Una operación es idempotente cuando repetirla produce el mismo estado que ejecutarla una vez. Es la única forma segura de reintentar una escritura: la red puede haber entregado la petición y perdido la respuesta, y el cliente no lo sabe.

La clave de idempotencia viaja con la petición y se guarda con el resultado. Si llega otra con la misma clave, se devuelve el resultado guardado en lugar de ejecutar otra vez:

```csharp
var aplicados = new HashSet<string>();
foreach (var mensaje in new[] { "pedido-1", "pedido-1", "pedido-2" })
{
    if (!aplicados.Add(mensaje)) continue; // ya estaba: se descarta
    // aplicar el efecto una sola vez
}
```

```text
idempotencia: pedido-1 aplicado
idempotencia: pedido-1 repetido, se descarta
idempotencia: pedido-2 aplicado
idempotencia: pedidos aplicados 2
```

En un servicio real el conjunto vive en Redis o en la base de datos, con el identificador y el resultado, y caduca después de un plazo mayor que el de los reintentos. La idempotencia no se delega al cliente: el servidor es quien decide si ya vio esa clave.

## Mensajes venenosos

Un mensaje venenoso es el que no se puede procesar: un JSON mal formado, una referencia a un pedido que no existe, un dato que rompe una regla. Reintentarlo no lo arregla; solo consume la cola.

La cola de servicio se configura con un número máximo de entregas. Al agotarlo, el mensaje pasa a la cola de mensajes muertos (*dead-letter queue*) en lugar de volver a la principal. Allí se inspecciona, se corrige si procede y se reinyecta.

Lo que no se hace es reintentar para siempre ni borrar el mensaje sin mirarlo. Un mensaje muerto es una señal: o el contrato cambió, o el productor envía algo que el consumidor no entiende, o falta un dato. La cola de muertos se vigila como una métrica más.

## CQRS: lectura y escritura separadas

CQRS separa el modelo de escritura del de lectura. La escritura valida y guarda; la lectura proyecta los datos en la forma que la pantalla necesita. Cada lado escala y se optimiza por su cuenta.

Merece la pena cuando las lecturas y las escrituras tienen formas muy distintas, cuando una consulta cruza muchos agregados o cuando la lectura necesita otra base de datos. No merece la pena en un CRUD simple: añade dos modelos, una sincronización y una consistencia eventual que hay que explicar.

La separación no obliga a dos bases de datos ni a un bus. Se puede empezar con dos modelos sobre el mismo almacén y separar la infraestructura solo cuando el coste de la consulta lo justifique.

## Elegir sin acumular

Cada patrón añade una pieza que hay que operar. Se empieza por el fallo que se ha visto, no por la lista completa: un reintento si hay timeouts, un interruptor si una dependencia arrastra al resto, idempotencia si se reintenta una escritura, cola de muertos si hay consumo por mensajes, y CQRS solo si la lectura y la escritura se estorban.
