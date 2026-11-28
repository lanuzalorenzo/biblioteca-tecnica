# Proyecto y ciclo de vida

Una aplicación MAUI para Android se organiza en dos velocidades. La solución se monta una vez y cambia poco; el ciclo de vida se ejecuta en cada arranque, cada cambio de pantalla y cada vuelta desde segundo plano. Confundir ambos planos lleva a meter lógica de negocio en `OnResume` o a inicializar la aplicación entera antes de que el usuario vea nada.

## La solución

La estructura de referencia separa el código portable del código de plataforma:

| Proyecto | Marco | Responsabilidad |
|---|---|---|
| `Comicteca.Client` | `net10.0` | DTO, rutas y validación compartidos con la web |
| `Comicteca.App.Core` | `net10.0` | Dominio, contratos, servicios y reglas del cliente |
| `Comicteca.App` | `net10.0-android` | Arranque, XAML, navegación, permisos y plataforma |
| `Comicteca.App.Core.Tests` | `net10.0` | Pruebas unitarias e integración con servidor falso |

`Comicteca.App.Core` es una biblioteca `net10.0` con `Nullable` y avisos como errores. No referencia MAUI ni Android: declara lo que necesita mediante interfaces —un almacén de sesión, un reloj, un cliente HTTP, un registro de trazas— y la app aporta las implementaciones. `Comicteca.Client` guarda el contrato compartido y tampoco depende de Android. Esa frontera permite compilar y probar la mayor parte del código en Linux.

El proyecto Android referencia `App.Core`, que a su vez referencia `Client`, y añade lo propio del cliente:

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net10.0-android</TargetFramework>
    <OutputType>Exe</OutputType>
    <UseMaui>true</UseMaui>
    <SingleProject>true</SingleProject>
    <ApplicationId>com.ejemplo.comicteca</ApplicationId>
    <ApplicationDisplayVersion>0.1.0</ApplicationDisplayVersion>
    <ApplicationVersion>1</ApplicationVersion>
    <SupportedOSPlatformVersion>24.0</SupportedOSPlatformVersion>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include="..\Comicteca.App.Core\Comicteca.App.Core.csproj" />
  </ItemGroup>
</Project>
```

`ApplicationId` es la identidad del paquete: no se cambia entre versiones si se quiere actualizar la app. `ApplicationVersion` es el `versionCode` de Android y debe crecer con cada APK distribuido. `SupportedOSPlatformVersion` fija el mínimo de API; se elige por las funciones que se usan y por los dispositivos que se quieren atender. El identificador del ejemplo es ficticio.

## El proyecto Android

Dentro de la app, la plantilla deja cuatro piezas: `MauiProgram.cs` construye el anfitrión y registra servicios; `App.xaml.cs` crea la ventana; `Platforms/Android/MainActivity.cs` es la actividad que Android lanza; y `AndroidManifest.xml` declara permisos y componentes.

El registro de dependencias ocurre una sola vez:

```csharp
public static MauiApp CreateMauiApp()
{
    var builder = MauiApp.CreateBuilder();
    builder.UseMauiApp<App>();

    builder.Services.AddSingleton<ISessionStore, SecureSessionStore>();
    builder.Services.AddSingleton<ISyncService, SyncService>();
    builder.Services.AddTransient<LibraryViewModel>();

    return builder.Build();
}
```

`CreateMauiApp` se ejecuta en el hilo de arranque. No es el sitio para una llamada de red, una lectura pesada ni una espera bloqueante: si tarda, Android muestra la pantalla en blanco o mata la actividad. La inicialización costosa va después, en una tarea asíncrona que la primera página espera con un indicador.

La ventana se crea en `App`; el servicio de sincronización llega por el constructor y la ventana se suscribe a sus eventos:

```csharp
protected override Window CreateWindow(IActivationState? activationState)
{
    var ventana = new Window(new AppShell());
    ventana.Resumed += async (_, _) => await _sync.RefrescarAsync();
    return ventana;
}
```

La actividad principal solo necesita los atributos de la plantilla. `SingleTop` evita una segunda instancia al llegar desde una notificación o un enlace; `ConfigurationChanges` evita que Android recree la actividad al girar la pantalla o cambiar el tema.

```csharp
[Activity(
    Theme = "@style/Maui.SplashTheme",
    MainLauncher = true,
    LaunchMode = LaunchMode.SingleTop,
    ConfigurationChanges = ConfigChanges.ScreenSize | ConfigChanges.Orientation)]
public class MainActivity : MauiAppCompatActivity
{
}
```

## El ciclo de vida de Android

Android no tiene un «abrir» y un «cerrar». Tiene una actividad con estados y un proceso que el sistema puede matar cuando necesita memoria:

| Momento | Qué significa | Qué conviene hacer |
|---|---|---|
| `OnCreate` | La actividad se crea | Componer la interfaz y restaurar estado pequeño |
| `OnStart` | Va a ser visible | Empezar a observar datos visibles |
| `OnResume` | Está en primer plano e interactiva | Reanudar temporizadores y refrescos |
| `OnPause` | Pierde el foco, sigue parcialmente visible | Pausar animaciones y guardar borradores |
| `OnStop` | Deja de ser visible | Cancelar trabajos ligados a la pantalla y persistir estado |
| `OnRestart` | Vuelve tras `OnStop` | Reanudar sin recrear la actividad |
| `OnDestroy` | Se destruye | Liberar recursos y desuscribirse |
| `OnSaveInstanceState` | El sistema puede matar el proceso | Guardar solo estado pequeño y serializable |

La diferencia entre `OnPause` y `OnStop` importa: una llamada o un diálogo del sistema puede pausar la actividad sin sacarla de la pantalla; `OnStop` sí indica que el usuario ya no la ve. Los trabajos que no deben seguir cuando la app está oculta se cancelan ahí. Los que deben sobrevivir pertenecen a otro mecanismo, como un servicio en primer plano o el planificador del sistema.

MAUI expone además eventos en `Window`: `Created`, `Activated`, `Deactivated`, `Stopped`, `Resumed` y `Destroying`. Su traducción a los callbacks de Android no es idéntica en todas las versiones, así que se usan para presentación y sincronización, no para decisiones de negocio que deban ser exactas. Si el dato no se puede reconstruir al volver, se persiste.

### Muerte del proceso

`OnSaveInstanceState` no es un almacén. Solo sirve para el estado de interfaz que el sistema puede devolver al recrear la actividad: la pestaña seleccionada, el texto de un filtro, la posición de una lista. Un token, una sesión o un borrador grande no van ahí. Si el proceso muere, la app arranca leyendo su estado persistido y, si no lo encuentra, vuelve a un punto seguro: el acceso o la última lista sincronizada.

`SingleTop` y `OnNewIntent` también afectan a la navegación. Un enlace profundo que llega con la app abierta no debe apilar una segunda copia: se interpreta el intent, se valida el destino y se navega sobre la instancia existente.

## Arranque

Un arranque predecible sigue este orden:

1. Android crea el proceso y la actividad; MAUI construye el anfitrión y resuelve dependencias.
2. Se crea la ventana con la pantalla inicial, que muestra datos cacheados o un esqueleto.
3. Una tarea asíncrona comprueba la sesión guardada, intenta renovarla en silencio y decide entre la pantalla principal y el acceso.
4. Se lanza la primera sincronización sin bloquear la interfaz; si falla, se conserva lo que ya había y se ofrece reintentar.

El usuario debe ver algo antes de que termine la red. Si el token no se renueva, se navega al acceso y se explica que la sesión ha caducado. Si no hay red, se abre la copia local y se marca «sin conexión». El arranque no debe terminar en una pantalla vacía ni en un cierre inesperado.

## Configuración por entorno

Todo lo que viaja en el APK se puede extraer, así que la configuración solo contiene valores públicos: la dirección de la API, el identificador de la aplicación en el proveedor de identidad y poco más. Las credenciales se quedan en el servidor.

El entorno se decide al compilar, no con un selector en la app:

```csharp
internal static class AppConfig
{
#if DEBUG
    public const string ApiBaseUrl = "https://api-staging.example";
#else
    public const string ApiBaseUrl = "https://api.example";
#endif
}
```

Para valores que deban cambiar sin tocar la lógica, un `appsettings.json` se incluye como `MauiAsset` y se lee del paquete con `FileSystem.OpenAppPackageFileAsync`. Ese archivo tampoco es un lugar para secretos: un `client_id` de OAuth es público por diseño y un `client_secret` en un cliente nativo no protege nada. Si se necesita un valor privado, la app pide al servidor que actúe de intermediario.

Las variantes `Debug` y `Release` cambian el registro de trazas y el optimizador. Lo que no conviene es dejar en `Release` un menú oculto para cambiar de servidor: acaba siendo una puerta que nadie revisa.

## Permisos mínimos

Android pide declarar los permisos en el manifiesto y, para los peligrosos, solicitarlos en tiempo de ejecución. La lista mínima de un cliente que habla con una API y muestra notificaciones es corta:

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
```

`INTERNET` y `ACCESS_NETWORK_STATE` son normales y se conceden al instalar. `POST_NOTIFICATIONS` es peligroso desde Android 13: si la app no lo necesita, no se declara; si lo necesita, se pide cuando la función tiene sentido, no al abrir por primera vez.

```csharp
var estado = await Permissions.CheckStatusAsync<Permissions.PostNotifications>();
if (estado != PermissionStatus.Granted)
    estado = await Permissions.RequestAsync<Permissions.PostNotifications>();
```

Un rechazo no es un error fatal. La función que dependía del permiso se desactiva y se explica qué se pierde; volver a preguntar en cada arranque solo consigue que el usuario bloquee la solicitud.

Para elegir un archivo se usa el selector del sistema, que no exige permiso de almacenamiento. Para guardar una imagen se usa el almacenamiento propio o el contrato de medios, no un acceso global. La cámara, la ubicación o los contactos solo aparecen si una pantalla concreta los usa y el usuario entiende para qué. Cada permiso declarado es una línea que hay que justificar en una revisión.

## Lista de comprobación

- ¿`App.Core` compila sin MAUI y sin Android?
- ¿`CreateMauiApp` termina rápido y sin red?
- ¿La pantalla inicial muestra algo antes de la primera respuesta?
- ¿El estado sobrevive a la muerte del proceso?
- ¿Los trabajos se cancelan en `OnStop` y no se confía en el orden de los eventos?
- ¿La configuración de `Release` no contiene secretos ni servidores de pruebas?
- ¿Cada permiso tiene una pantalla y una explicación?
- ¿`ApplicationId` y `versionCode` están decididos antes de distribuir?
