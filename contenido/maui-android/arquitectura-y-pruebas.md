# Arquitectura y pruebas

Un cliente móvil se prueba en dos mundos que no se parecen. En Linux se ejecuta la lógica, se simulan respuestas y se comprueba el contrato con la API en segundos. En un emulador o en un móvil se ejecuta la app real, con permisos, ciclo de vida, almacenamiento y pantalla. Pretender cubrir el segundo con el primero produce una falsa confianza; renunciar al primero porque «es una app» convierte cada prueba en manual y lenta.

La arquitectura de la solución decide cuánto cae en cada lado. Si el dominio y los servicios no conocen MAUI, la mayor parte se prueba en Linux. Si la lógica vive en el *code-behind* de una página, casi todo exige un dispositivo. El cliente Android de Comicteca está en construcción; lo que sigue es el reparto de pruebas y los límites que hay que asumir, no un informe de resultados.

## La frontera que hace testeable el cliente

La regla es sencilla: el código que se puede contar sin mirar la pantalla no depende de MAUI. `Core` define el dominio y los contratos; la app implementa lo específico de Android.

| Capa | Dónde vive | Cómo se prueba |
|---|---|---|
| Dominio, casos de uso, validación | `Core` (`net10.0`) | Unitarias en Linux |
| Cliente HTTP, serialización, errores | `Core` | Unitarias con handler falso e integración con servidor local |
| Caché y cola de operaciones | `Core` con una abstracción de almacenamiento | Unitarias con almacén en memoria |
| ViewModels | `Core` o biblioteca `net10.0` | Unitarias, si no usan tipos de MAUI |
| Navegación, páginas, XAML | App Android | Emulador o dispositivo |
| Permisos, ciclo de vida, Keystore | App Android | Emulador o dispositivo |
| Firma, instalación, actualización | APK | Dispositivo real |

Los ViewModels pueden usar `CommunityToolkit.Mvvm`, que no depende de MAUI, y hablar con la vista a través de interfaces propias (`IDialogService`, `INavigationService`). Así una prueba puede comprobar que un comando deja el estado en «cargando», que un error muestra el mensaje correcto o que una lista vacía cambia la pantalla, sin abrir Android.

Lo que no se hace es duplicar la lógica para poder probarla. Si una regla solo existe en la página, se mueve; si una dependencia de Android contamina el dominio, se envuelve en una interfaz. La prueba señala el sitio de la frontera, no al revés.

## Qué se prueba en Linux

El proyecto de pruebas referencia `Core` y se ejecuta con `dotnet test` en cualquier equipo con el SDK de .NET 10. No necesita Android SDK, emulador ni dispositivo. Ahí entran:

- **Reglas de negocio.** Cálculos, validaciones, estados de una descarga, decisiones de caché.
- **Serialización y contratos.** Que un JSON real de la API se deserialice con los campos esperados y que un cambio de nombre no pase inadvertido.
- **Errores del cliente HTTP.** Un 401, un 404, un 500, un tiempo agotado, una respuesta vacía o un cuerpo que no es JSON.
- **Cabeceras y autenticación.** Que la petición lleve el token y la correlación, y que no los lleve cuando no debe.
- **Caché y cola.** Que una operación pendiente se reintente una vez, que no se duplique y que se descarte al cerrar sesión.

### Un handler falso

Para una prueba unitaria, el cliente HTTP se sustituye por un `HttpMessageHandler` que devuelve una respuesta fija. No hay red, no hay puerto y el caso se repite siempre igual:

```csharp
internal sealed class RespuestaFija(HttpStatusCode codigo, string cuerpo)
    : HttpMessageHandler
{
    protected override Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, CancellationToken cancellationToken)
        => Task.FromResult(new HttpResponseMessage(codigo)
        {
            Content = new StringContent(cuerpo, Encoding.UTF8, "application/json")
        });
}
```

```csharp
[Fact]
public async Task Listar_ConServicioNoDisponible_DevuelveLaCopiaLocal()
{
    using var cliente = new HttpClient(
        new RespuestaFija(HttpStatusCode.ServiceUnavailable, "{}"))
    {
        BaseAddress = new Uri("https://api.example")
    };
    var servicio = new ComicService(cliente, new CacheEnMemoria(3));

    Assert.Equal(3, (await servicio.ListarAsync()).Count);
}
```

El test comprueba la decisión de negocio —seguir con la caché— y no la implementación de `HttpClient`. Cuando se añada resiliencia, el handler falso permitirá contar reintentos y comprobar que un 429 respeta la espera sin dormir la prueba.

### Un servidor local

Para probar el contrato completo, incluida la ruta, el método y el cuerpo, se levanta un servidor Kestrel en el puerto efímero del bucle local. El proyecto de pruebas añade una `FrameworkReference` a `Microsoft.AspNetCore.App`:

```csharp
var builder = WebApplication.CreateBuilder();
builder.WebHost.UseUrls("http://127.0.0.1:0");
var app = builder.Build();
app.MapGet("/api/comics", () => Results.Ok(new[] { new { Id = "A-1" } }));
await app.StartAsync();

var direccion = app.Services.GetRequiredService<IServer>()
    .Features.Get<IServerAddressesFeature>()!.Addresses.First();
var cliente = new HttpClient { BaseAddress = new Uri(direccion) };
// Ejercitar el cliente real contra el servidor falso.
```

El servidor se detiene al terminar la prueba. No es la API de producción: es un doble que permite fijar respuestas, demoras y errores, y comprobar que el cliente envía lo que el servidor espera y entiende lo que devuelve. No sustituye a una prueba contra el servidor real en un entorno de staging, que se hace antes de una entrega y no en cada cambio.

## Qué exige emulador o móvil

El APK se puede compilar en Linux si están la carga de trabajo de Android, el SDK y un JDK compatible. Ejecutarlo con interfaz exige un emulador con aceleración por hardware o un dispositivo conectado. Lo que no se puede comprobar en una prueba de `Core`:

- **Ciclo de vida.** Girar la pantalla, cambiar de tema, volver desde segundo plano, matar el proceso y restaurar.
- **Permisos.** Conceder, denegar y revocar notificaciones o cámara; volver a pedir; explicar el rechazo.
- **Almacenamiento seguro.** Guardar, leer y recuperar tras reiniciar; simular una clave invalidada.
- **Capturas y vista reciente.** Que `FLAG_SECURE` haga lo que se espera en el fabricante concreto.
- **Enlaces profundos y notificaciones.** Que abran la pantalla correcta y no dupliquen la actividad.
- **Red real.** Cambio de Wi-Fi a datos, modo avión, latencia, portal cautivo.
- **Rendimiento y tamaño.** Arranque en frío, desplazamiento de listas, memoria, peso del APK.
- **Release con recorte.** Fallos que no aparecen en `Debug`.
- **Firma e instalación.** Actualización sobre la versión anterior, mismo paquete y misma clave.

El emulador cubre la mayoría de los casos funcionales y permite automatizar. El dispositivo real sigue siendo necesario para el rendimiento, la cámara, la batería, las capas de fabricante y la instalación de un APK firmado. Un emulador con Android 14 no demuestra que la app funcione en un móvil de gama baja con Android 10.

### Pruebas de interfaz y de humo

La automatización de interfaz se reserva para los caminos que un fallo dejaría inutilizables: abrir, iniciar sesión, ver la lista, abrir un cómic, cerrar sesión y volver a entrar. Appium o el paquete de pruebas de UI de MAUI, si el proyecto lo adopta, permiten escribir esos recorridos; su coste es alto y su estabilidad, menor que la de una prueba unitaria.

Una prueba de interfaz que depende de un texto, una animación o una espera fija se rompe sin que haya un fallo real. Se usan identificadores estables, esperas por condición y pocos recorridos. El resto se cubre con una lista de humo manual ejecutada antes de cada entrega, con pasos y resultado esperado. La lista también es documentación: dice qué se considera «funciona».

## Cobertura y sus límites

La cobertura se mide sobre `Core`, que es donde vive la lógica. Coverlet recoge líneas y ramas:

```bash
dotnet test --collect:"XPlat Code Coverage"
```

Se excluyen del cálculo el código generado, las páginas XAML, los adaptadores de plataforma y el arranque, porque una prueba en Linux no los ejecuta. Un umbral acordado para `Core` evita que la cifra baje sin que nadie lo note; no se persigue el 100 %, que suele producir pruebas de getters y setters sin valor.

La cobertura no dice si la app se ve bien, si el ciclo de vida guarda el estado o si un permiso se pide en el momento correcto. Tampoco detecta una prueba que ejecuta código sin afirmar nada. Para eso están la revisión, las pruebas de mutación —si el proyecto las adopta— y la prueba manual en el dispositivo.

## Observabilidad: responsabilidad del cliente

El servidor ve peticiones; no ve el cierre inesperado, el fallo de render, la pantalla que no carga por un permiso denegado ni la versión antigua que ya no entiende la API. Esa parte la tiene que contar el cliente. Sin ella, un fallo se convierte en «a mí no me funciona» y se depura a ciegas.

Las piezas mínimas son:

- **Registro estructurado.** `ILogger` con niveles, categorías y un identificador de correlación que también viaje al servidor en una cabecera. Nunca tokens, datos personales ni cuerpos completos.
- **Captura de excepciones no controladas.** El manejador de Android y el de .NET recogen el fallo, guardan un resumen local y, si el usuario lo autoriza, lo envían.
- **Cola local acotada.** Los eventos y los errores se guardan en un búfer con límite y caducidad; una app sin red no debe llenar el almacenamiento.
- **Señales de uso.** Arranque, tiempo de la primera carga, éxito de sincronización, aciertos de caché, errores por código. Sirven para detectar una regresión sin leer cada traza.
- **Símbolos de la versión.** El archivo de correspondencia de R8 y los símbolos de compilación se conservan con el APK para poder leer un fallo de `Release`.

```csharp
using (_logger.BeginScope(new Dictionary<string, object>
{
    ["CorrelationId"] = correlacion
}))
{
    _logger.LogInformation("Sincronización completada: {Total} elementos", total);
}
```

La correlación la genera el cliente si no viene del servidor; el servidor la registra y la devuelve. No se usa como autenticación: es una etiqueta para seguir un recorrido, no una credencial.

Un informe de fallos puede contener la URL que provocó el error. Si esa URL lleva un token en la consulta, el informe lo filtra. Por eso los tokens van en cabeceras y las URLs se sanean antes de registrarse. La observabilidad también es una decisión de privacidad: qué se recoge, cuánto se guarda, quién lo lee y cómo se borra.

## Integración continua

Un reparto razonable de trabajos:

| Trabajo | Dónde | Qué ejecuta |
|---|---|---|
| `core` | Linux | `dotnet test` de `Core` y de integración con servidor falso |
| `android` | Linux | Carga de trabajo, SDK y JDK; `dotnet build -f net10.0-android -c Release` |
| `humo` | Emulador o dispositivo | Recorridos críticos, programados o antes de una entrega |
| `firma` | Equipo del propietario o CI restringido | `dotnet publish` firmado y verificación del APK |

El trabajo de `core` es el más rápido y el que debe bloquear cualquier cambio. El de `android` detecta que el proyecto compila, pero no que la app funcione. El de humo es caro y se reserva; si se ejecuta en cada *pull request*, conviene que sea estable y que no dependa de la red externa. La firma no se hace en un `pull request` abierto: las claves no deben estar disponibles para código que aún no se ha revisado.

## Lo que queda pendiente

Este módulo es una base, no el tratado completo. Falta:

- **XAML y MVVM en detalle.** Enlaces, comandos, validación, navegación con Shell, ciclo de vida de los ViewModels y organización de recursos y estilos.
- **`HttpClient` con resiliencia.** Tiempos, reintentos con espera, cortocircuito, idempotencia y tratamiento de la red intermitente.
- **Observabilidad a fondo.** Exportadores, informes de fallos, consentimiento, retención y alertas.
- **Rendimiento y tamaño.** Arranque en frío, listas largas, imágenes, memoria y recorte.
- **El caso de Comicteca cuando la app esté validada.** Entonces se podrán describir decisiones y resultados comprobados; hoy no hay APK probado ni cifras que presentar.

## Lista de comprobación

- ¿La lógica de negocio está fuera de las páginas y se prueba en Linux?
- ¿Las dependencias de Android están detrás de interfaces?
- ¿Los errores del cliente HTTP tienen pruebas con respuestas fijas?
- ¿Hay una prueba de contrato contra un servidor local?
- ¿Los recorridos críticos tienen una lista de humo en dispositivo?
- ¿La cobertura se mide en `Core` y se interpreta con sus límites?
- ¿El cliente registra fallos y correlación sin datos sensibles?
- ¿La versión de `Release` se prueba con el recorte activo?
