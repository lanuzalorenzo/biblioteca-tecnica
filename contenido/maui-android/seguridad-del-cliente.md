# Seguridad del cliente

Una aplicación instalada no es un entorno de confianza. El APK se puede copiar, descomprimir y examinar; el dispositivo puede estar modificado; el usuario puede hacer capturas, conectarlo a un equipo y leer sus registros. La seguridad del cliente consiste en reducir la exposición y en no convertir un dato robado en un acceso permanente. Las decisiones que protegen los datos —quién puede leer qué y qué operación se autoriza— siguen estando en el servidor.

## El modelo de amenaza

Antes de elegir controles conviene nombrar lo que se intenta evitar:

- **Lectura del APK.** Cualquiera con el archivo puede extraer cadenas, recursos y código compilado. Los identificadores públicos y las direcciones de la API se conocen; los secretos no deben estar ahí.
- **Dispositivo perdido o compartido.** Otra persona puede abrir la app, ver la pantalla reciente o restaurar una copia de seguridad.
- **Registros y capturas.** `adb logcat`, un informe de fallos o una captura de pantalla pueden revelar más de lo que parece.
- **Sesión robada.** Un token copiado del almacenamiento o de una copia de seguridad permite actuar hasta que caduque o se revoque.

Un control como `FLAG_SECURE` frena una captura accidental, pero no impide fotografiar la pantalla con otro móvil. `SecureStorage` protege un token en reposo, pero no frente a un dispositivo con *root* y herramientas adecuadas. La defensa se organiza en capas y se acepta que ninguna capa es absoluta.

## Inicio de sesión con MSAL, PKCE y el navegador del sistema

El flujo correcto para una aplicación nativa es el de código de autorización con PKCE, descrito en la recomendación de OAuth 2.0 para aplicaciones nativas. La app no recibe la contraseña: abre el navegador del sistema, el proveedor de identidad autentica a la persona y devuelve un código que se canjea por tokens. PKCE añade un verificador que impide que un código interceptado se use desde otro cliente.

MSAL.NET implementa ese flujo y gestiona la caché de tokens. La aplicación es un **cliente público**: no tiene ni puede tener un secreto de cliente. El identificador de la aplicación es público y no otorga acceso por sí solo.

```csharp
var app = PublicClientApplicationBuilder
    .Create(clientId)
    .WithAuthority($"https://login.microsoftonline.com/{tenantId}")
    .WithRedirectUri($"msal{clientId}://auth")
    .Build();
```

El redirect URI debe estar registrado en el proveedor de identidad y coincidir exactamente. En Android, MSAL usa una actividad propia para recibir la respuesta; el esquema `msal{clientId}://auth` es el habitual. Si se activa el *broker* del sistema, el flujo pasa por la cuenta del dispositivo y mejora el inicio de sesión único, a cambio de una configuración adicional que se prueba en un móvil real.

La primera vez se abre la interfaz interactiva; las siguientes se intenta renovar en silencio antes de molestar al usuario:

```csharp
var cuentas = await app.GetAccountsAsync();
try
{
    return await app.AcquireTokenSilent(scopes, cuentas.FirstOrDefault())
        .ExecuteAsync();
}
catch (MsalUiRequiredException)
{
    return await app.AcquireTokenInteractive(scopes)
        .WithParentActivityOrWindow(Platform.CurrentActivity)
        .WithUseEmbeddedWebView(false)
        .ExecuteAsync();
}
```

`WithUseEmbeddedWebView(false)` no es un detalle estético. Un WebView embebido lo controla la aplicación, puede recibir credenciales y no comparte la sesión del navegador; el flujo nativo exige el navegador del sistema o el broker. Tampoco se implementa el protocolo a mano: MSAL resuelve PKCE, la validación del estado, la renovación y los errores del proveedor.

Los *scopes* se piden por lo que la API necesita. La duración del token de acceso la fija el proveedor de identidad: la app no la negocia ni la alarga. MSAL renueva en silencio cuando corresponde y pide interacción cuando el proveedor la exige.

## Dónde se guarda la sesión

`SecureStorage` de MAUI guarda valores pequeños cifrados con una clave del Keystore de Android. Es el sitio para un identificador de sesión propio o un valor pequeño, no para un token de acceso ni para un refresh token: MSAL no expone este último y no se debe extraer.

```csharp
await SecureStorage.Default.SetAsync("session_id", sessionId);
var sessionId = await SecureStorage.Default.GetAsync("session_id");
```

El almacén puede fallar. Una restauración desde otra copia, un cambio de clave o una actualización del sistema pueden dejar el valor ilegible. El código debe tratar ese fallo como «no hay sesión»: borra el resto, navega al acceso y vuelve a empezar. No se reintenta en bucle ni se muestra la excepción al usuario.

MSAL mantiene la caché de tokens y, en los destinos móviles de MAUI, la serialización viene configurada por defecto. Si se necesita controlarla, se usa el serializador de la plataforma (`TokenCacheHelper.EnableSerialization` en el ejemplo de MSAL, o el equivalente) con un almacén cifrado y un tamaño acotado. Lo que no se hace es guardar un refresh token suelto ni escribir la caché en `Preferences`, en un archivo de texto, en `localStorage` de un WebView o en un log.

## Cierre de sesión

Cerrar sesión no es navegar a la pantalla de acceso. Hay que eliminar la cuenta de la caché de MSAL, borrar los valores propios y cancelar el trabajo que iba en nombre de esa persona:

```csharp
foreach (var cuenta in await app.GetAccountsAsync())
{
    await app.RemoveAsync(cuenta);
}

SecureStorage.Default.RemoveAll();
```

Después se detienen las sincronizaciones, se limpian las listas en memoria y se navega al acceso. Si la app guarda una cola de operaciones pendientes, esa cola se descarta o se marca para no ejecutarse con la sesión siguiente.

Queda un límite que conviene decir en voz alta: la sesión del navegador del sistema no se puede borrar desde la app. Al cerrar sesión en MSAL se elimina la cuenta de la aplicación, pero la cookie del navegador puede mantener la sesión del proveedor. Si el requisito es cerrar también esa sesión, se abre la URL de cierre del proveedor en el navegador y se acepta que el resultado depende de su política. Para un dispositivo compartido, la solución real es revocar la sesión en el servidor y no confiar solo en el botón local.

## Manifiesto: copias, HTTP y componentes

El manifiesto de Android es parte de la superficie de ataque. Estos ajustes se declaran en `Platforms/Android/AndroidManifest.xml`:

```xml
<application
    android:allowBackup="false"
    android:fullBackupContent="false"
    android:dataExtractionRules="@xml/data_extraction_rules"
    android:usesCleartextTraffic="false"
    android:networkSecurityConfig="@xml/network_security_config">
</application>
```

`allowBackup="false"` impide que el sistema copie los datos de la app en la nube. En Android 12 y posteriores, la transferencia entre dispositivos se controla además con `dataExtractionRules`; sin ese archivo, algunas migraciones pueden conservar datos que se creían excluidos. Las reglas excluyen las preferencias que contienen la sesión:

```xml
<data-extraction-rules>
  <cloud-backup>
    <exclude domain="sharedpref" path="." />
  </cloud-backup>
  <device-transfer>
    <exclude domain="sharedpref" path="." />
  </device-transfer>
</data-extraction-rules>
```

`usesCleartextTraffic="false"` bloquea HTTP sin TLS. La política de red lo hace explícito y permite limitar las autoridades de confianza:

```xml
<network-security-config>
  <base-config cleartextTrafficPermitted="false">
    <trust-anchors>
      <certificates src="system" />
    </trust-anchors>
  </base-config>
</network-security-config>
```

Confiar solo en las autoridades del sistema evita que un certificado instalado a mano por el usuario permita interceptar el tráfico. Tiene un coste: rompe los proxies corporativos que dependen de una CA propia. En un cliente para el propietario, la restricción es razonable; si se necesita soportar una red con CA interna, se añade una configuración específica y se documenta. El *pinning* de certificados no se implanta sin un plan de rotación: un pin caducado deja la app sin conexión y no se arregla con una actualización del servidor.

Los componentes exportados también se revisan. Solo la actividad de lanzamiento y los receptores que deban atender enlaces del sistema llevan `android:exported="true"`. Una actividad interna expuesta sin necesidad permite que otra app la abra con datos que no espera. `android:debuggable` queda en `false` en `Release`; si aparece en `true`, la build no es la que se distribuye.

## Capturas y vista reciente

`FLAG_SECURE` impide que Android capture el contenido de la ventana para una captura de pantalla o una grabación, y oculta la miniatura en la vista de aplicaciones recientes. Se activa en `MainActivity.OnCreate` con `Window.SetFlags(WindowManagerFlags.Secure, WindowManagerFlags.Secure)` antes de mostrar la interfaz.

Es útil en pantallas con datos de sesión o contenido privado. No es una garantía: algunos fabricantes se comportan distinto, una cámara externa sigue viendo la pantalla y la marca no protege los datos en disco. Se combina con no mostrar más de lo necesario y con cerrar la sesión al abandonar un dispositivo compartido.

## Recorte, R8 y compilación de release

En `Release`, el compilador de Android recorta código no usado y R8 reduce el bytecode de las dependencias Java. El objetivo es menor tamaño y menos superficie, no solo velocidad. El recorte se controla con `PublishTrimmed` y `TrimMode`, y puede romper el código que depende de reflexión, serialización o nombres de tipo.

La solución no es desactivar el recorte en cuanto aparece un aviso. Se corrige la causa: serialización con generadores de código fuente, anotaciones `DynamicDependency` en los puntos reflexivos y reglas de conservación para las bibliotecas que las necesiten.

```csharp
[JsonSerializable(typeof(ComicDto))]
internal partial class ComicJsonContext : JsonSerializerContext;

var comic = JsonSerializer.Deserialize(json, ComicJsonContext.Default.ComicDto);
```

Cada APK de `Release` se prueba en un dispositivo o emulador: arranque, acceso, renovación de sesión, listas, imágenes y cierre. Un fallo de recorte no aparece en `Debug`, y una app que compila no está probada. Si R8 ofusca el bytecode, el archivo de correspondencia se guarda junto al APK y se sube al servicio de fallos, nunca al repositorio público.

## Qué no se registra

Los registros de Android son accesibles con `adb logcat`, se adjuntan a informes de fallos y pueden acabar en una herramienta de terceros. Por eso no se escriben:

- Tokens de acceso o de actualización, códigos de autorización ni cookies.
- Cabeceras `Authorization` completas, aunque sea en nivel `Debug`.
- Contraseñas, PIN, datos de tarjeta o identificadores personales.
- URLs con parámetros sensibles, cuerpos de respuesta completos o el contenido de un cómic privado.
- Contraseñas del almacén de claves o secretos de configuración.

Un mensaje útil puede conservar la operación y el resultado sin el dato:

```csharp
_logger.LogInformation("Catálogo actualizado: {Total} cómics", total);
```

En `Release` se sube el nivel mínimo a `Warning`, se filtran las categorías ruidosas —`System.Net.Http` puede registrar cabeceras en `Trace`— y se revisa que las excepciones no arrastren la URL completa. Un registro que ayuda a depurar hoy puede ser una filtración mañana; la regla es que el dato sensible no llegue a la función que escribe.

## Lista de comprobación

- ¿El inicio de sesión usa el navegador del sistema o el broker, con PKCE y sin secreto de cliente?
- ¿El redirect URI está registrado y coincide exactamente?
- ¿La caché de tokens se persiste cifrada y se recupera de un fallo sin bucle?
- ¿El cierre de sesión borra cuenta, almacén y trabajo pendiente?
- ¿`allowBackup` y las reglas de extracción excluyen la sesión?
- ¿El tráfico sin TLS está bloqueado y las CA de usuario, valoradas?
- ¿Solo los componentes necesarios están exportados?
- ¿`FLAG_SECURE` está activo donde hay datos sensibles?
- ¿El APK de `Release` se probó con el recorte activo?
- ¿Los registros, los informes de fallos y el archivo de R8 están libres de secretos?
