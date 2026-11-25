# HTTP y servicios web

Una aplicación .NET rara vez vive sola. Llama a una API, publica en un bus o sirve endpoints. Probar ese intercambio tiene dos direcciones: el cliente que consume un servicio ajeno y el servidor que expone el propio. Cada una necesita una herramienta distinta.

## Probar el cliente con `HttpMessageHandler`

`HttpClient` no se mockea bien: sus métodos no son virtuales y su constructor espera un manejador. La costura está precisamente ahí. `HttpMessageHandler` es abstracto y su método `SendAsync` es el punto por el que pasa toda petición. Se puede sustituir por un manejador que devuelva respuestas preparadas.

```csharp
public sealed class ManejadorFijo : HttpMessageHandler
{
    private readonly HttpStatusCode _codigo;
    private readonly string _cuerpo;

    public ManejadorFijo(HttpStatusCode codigo, string cuerpo)
    {
        _codigo = codigo;
        _cuerpo = cuerpo;
    }

    public HttpRequestMessage? UltimaPeticion { get; private set; }

    protected override Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request,
        CancellationToken cancellationToken)
    {
        UltimaPeticion = request;
        return Task.FromResult(new HttpResponseMessage(_codigo)
        {
            Content = new StringContent(_cuerpo, Encoding.UTF8, "application/json")
        });
    }
}
```

```csharp
[Fact]
public async Task ObtenerPrecio_EnviaElIdentificador()
{
    var manejador = new ManejadorFijo(HttpStatusCode.OK, """{"precio":10.5}""");
    var cliente = new HttpClient(manejador) { BaseAddress = new Uri("https://api.ejemplo.test") };
    var servicio = new ServicioDePrecios(cliente);

    var precio = await servicio.ObtenerAsync("A-1");

    Assert.Equal(10.5m, precio);
    Assert.Equal("https://api.ejemplo.test/precios/A-1", manejador.UltimaPeticion!.RequestUri!.ToString());
}
```

El manejador puede devolver una secuencia de respuestas para simular un fallo transitorio:

```csharp
public sealed class ManejadorSecuencial : HttpMessageHandler
{
    private readonly Queue<HttpResponseMessage> _respuestas;

    public ManejadorSecuencial(params HttpResponseMessage[] respuestas) =>
        _respuestas = new Queue<HttpResponseMessage>(respuestas);

    protected override Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, CancellationToken cancellationToken) =>
        Task.FromResult(_respuestas.Dequeue());
}
```

Así se prueba que el cliente reintenta una vez y no dos, o que lanza una excepción de dominio cuando el servicio responde 503. Lo que se comprueba es el comportamiento del cliente, no el de la red.

El `HttpClient` debe inyectarse en el servicio que lo usa, no construirse dentro. Si el servicio hace `new HttpClient()`, no hay forma de sustituir el manejador y la prueba depende de la red real.

## Probar el servidor con `WebApplicationFactory`

Para ASP.NET Core, `Microsoft.AspNetCore.Mvc.Testing` levanta la aplicación en memoria y expone un `HttpClient` que habla con ella sin abrir un puerto. El servidor real no arranca, pero pasan el enrutado, el model binding, los filtros, la serialización y el middleware.

```csharp
public class PedidosApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _cliente;

    public PedidosApiTests(WebApplicationFactory<Program> fabrica) =>
        _cliente = fabrica.CreateClient();

    [Fact]
    public async Task GetPedido_Inexistente_Devuelve404()
    {
        var respuesta = await _cliente.GetAsync("/api/pedidos/NO-EXISTE");

        Assert.Equal(HttpStatusCode.NotFound, respuesta.StatusCode);
    }
}
```

`TEntryPoint` es el tipo de la aplicación. Con instrucciones de nivel superior, la clase `Program` es implícita; para poder referenciarla hay que declararla:

```csharp
public partial class Program { }
```

La fábrica se declara como `IClassFixture` y se comparte entre las pruebas de la clase. Crear una por prueba vuelve a arrancar la aplicación cada vez y multiplica el tiempo.

## Sustituir dependencias del servidor

Una prueba de integración no debe golpear la base de datos de producción ni un servicio externo. `WithWebHostBuilder` permite cambiar el contenedor de dependencias:

```csharp
public class PedidosApiTests
{
    private readonly HttpClient _cliente;

    public PedidosApiTests(WebApplicationFactory<Program> fabrica)
    {
        var conexion = new SqliteConnection("Data Source=:memory:");
        conexion.Open();

        _cliente = fabrica
            .WithWebHostBuilder(builder =>
            {
                builder.ConfigureTestServices(services =>
                {
                    services.RemoveAll<PedidosDbContext>();
                    services.RemoveAll<DbContextOptions<PedidosDbContext>>();
                    services.AddDbContext<PedidosDbContext>(o => o.UseSqlite(conexion));
                    services.AddSingleton<IClientePagos, ClientePagosFalso>();
                });
            })
            .CreateClient();
    }
}
```

Sustituir el `DbContext` es habitual: se levanta SQLite en memoria una vez, se siembra y se elimina el proveedor real. Sustituir un cliente HTTP ajeno evita que la prueba dependa de la disponibilidad de un tercero.

Lo que se sustituye en una prueba de integración debe ser lo mínimo. Si se reemplaza todo, la prueba deja de comprobar el cableado, que es precisamente lo que aporta.

## Qué comprobar

Una prueba de extremo a extremo de un endpoint afirma sobre el contrato observable:

- El código de estado.
- La cabecera `Content-Type`.
- El cuerpo deserializado, no el JSON como cadena.
- Los efectos persistidos, consultando el contexto de pruebas.
- La cabecera de autenticación o el rechazo cuando falta.

```csharp
[Fact]
public async Task PostPedido_Valido_Devuelve201YGuarda()
{
    var respuesta = await _cliente.PostAsJsonAsync("/api/pedidos", new { numero = "A-1" });

    Assert.Equal(HttpStatusCode.Created, respuesta.StatusCode);
    var creado = await respuesta.Content.ReadFromJsonAsync<PedidoDto>();
    Assert.Equal("A-1", creado!.Numero);
}
```

Comparar el JSON completo como texto acopla la prueba al orden de las propiedades y a los espacios. Deserializar y afirmar sobre el objeto es más estable.

## `TestServer` y la prueba en memoria

Antes de `WebApplicationFactory`, la prueba de servidor se montaba con `TestServer` y una clase `Startup` propia. Sigue existiendo, pero obliga a mantener una configuración paralela y a registrar el ensamblado de los controladores a mano. `WebApplicationFactory` reutiliza la aplicación real y es la opción actual para ASP.NET Core. `TestServer` queda para escenarios muy concretos o código heredado.

## Dónde encaja en la suite

Estas pruebas son de integración o funcionales: tardan segundos, no milisegundos, y su fallo puede venir del enrutado, de la configuración o de la base de datos. No sustituyen a las unitarias de la lógica de negocio; cubren lo que las unitarias no pueden ver.

Una distribución razonable:

- Unitarias para reglas, cálculos y validaciones.
- Integración para repositorios, clientes HTTP y endpoints críticos.
- Funcionales para los flujos que el usuario completa de principio a fin.

Si una prueba de endpoint necesita veinte peticiones para llegar al caso, probablemente el flujo se puede dividir o la preparación se puede mover a un fixture. La prueba de integración debe seguir siendo legible cuando falla.
