# Firma y distribución

Android no instala una aplicación que no esté firmada. La firma no es un trámite: identifica al autor del paquete, permite que el sistema acepte una actualización como continuación de la anterior y establece una frontera entre lo que el usuario instala y lo que otro podría construir con el mismo nombre. Perder la clave o publicarla son incidentes distintos, y ambos se evitan con un procedimiento, no con buena voluntad.

Este módulo no usa Google Play. El cliente se distribuye al propietario por un canal privado, con un APK firmado y unas instrucciones concretas. Eso elimina la revisión de la tienda, pero traslada al proyecto la custodia de la clave, el control de versiones y la comunicación de cada actualización.

## Qué firma Android y por qué importa

Un APK es un archivo comprimido con código, recursos y un manifiesto. La firma añade una huella criptográfica sobre su contenido. Android comprueba esa huella antes de instalar y, en las actualizaciones, exige que la nueva versión esté firmada con la misma identidad que la instalada.

- **v1 (JAR signing)** firma archivos individuales. Está obsoleta y no protege la totalidad del paquete.
- **v2** firma el APK completo y detecta modificaciones después de la firma.
- **v3** añade información de rotación de clave para que una app pueda cambiar de clave sin perder las actualizaciones.
- **v4** se apoya en un archivo aparte para la instalación incremental; no sustituye a las anteriores.

Una firma con `jarsigner` solo cubre v1. La herramienta correcta es `apksigner`, que aplica v2 y v3 cuando el mínimo de Android lo permite. El APK que se distribuye se verifica antes de entregarlo; no se confía en que «el build lo habrá firmado».

Un **AAB** (*Android App Bundle*) no es instalable directamente: es el formato que Google Play usa para generar APK por dispositivo. Sin Play, el artefacto es un APK. Si en algún momento se necesita un AAB para una tienda, se genera con `bundletool`, pero no se entrega como si fuera una app.

## El almacén de claves, fuera de Git

La clave se guarda en un archivo `.jks` o `.keystore` protegido por contraseña. Se crea una vez, con un alias estable y una validez larga:

```bash
keytool -genkeypair -v \
  -keystore comicteca-release.jks \
  -alias comicteca \
  -keyalg RSA \
  -keysize 4096 \
  -validity 10000
```

`keytool` pide la contraseña del almacén, la de la clave y los datos del certificado. El alias se conserva: cambiarlo no cambia la identidad de la app, pero complica el build. La validez debe superar la vida prevista del producto; una clave caducada impide firmar nuevas versiones.

El archivo y sus contraseñas **no entran en el repositorio**, ni siquiera en una rama privada, ni en un historial que luego se pueda recuperar. Tampoco se envían por chat ni se dejan en un directorio compartido sin cifrar. El procedimiento mínimo:

- Guardar una copia cifrada en dos lugares distintos, uno de ellos sin conexión.
- Anotar alias, contraseñas y fecha de creación en un gestor de contraseñas.
- Probar la restauración de la copia antes de necesitarla.
- Limitar quién puede firmar y dejar constancia de cada build distribuido.
- Añadir `*.jks`, `*.keystore` y los archivos de credenciales al `.gitignore` y comprobar con Gitleaks que no se han colado.

Si la clave se pierde, no se puede publicar una actualización que sustituya a la instalada: hay que desinstalar, perdiendo los datos locales, o cambiar el `ApplicationId` y empezar de cero. Si se filtra, cualquiera puede firmar un APK con la misma identidad; la respuesta es revocar la confianza del servidor, no solo cambiar la contraseña.

## Construir el APK firmado

Antes de compilar se sube `ApplicationVersion` (el `versionCode`) y, si procede, `ApplicationDisplayVersion`. El `versionCode` es un entero que debe crecer en cada entrega; Android rechaza una actualización con un número menor o igual.

```bash
export AndroidSigningStorePass="$(cat ~/.config/comicteca/store.pass)"
export AndroidSigningKeyPass="$(cat ~/.config/comicteca/key.pass)"

dotnet publish Comicteca.App/Comicteca.App.csproj \
  -f net10.0-android \
  -c Release \
  -p:AndroidKeyStore=true \
  -p:AndroidSigningKeyStore="$PWD/comicteca-release.jks" \
  -p:AndroidSigningKeyAlias=comicteca
```

Las contraseñas llegan como variables de entorno y MSBuild las recoge como propiedades `AndroidSigningStorePass` y `AndroidSigningKeyPass`. No se escriben en la línea de comandos —quedan en el historial del shell— ni en un archivo versionado. Si el build se automatiza, las variables se inyectan desde el gestor de secretos del CI y el almacén se monta solo durante el trabajo de firma.

La salida queda en `bin/Release/net10.0-android/publish/`, con un APK sin firmar y otro firmado. Se verifica el firmado:

```bash
apksigner verify --verbose --print-certs \
  bin/Release/net10.0-android/publish/com.ejemplo.comicteca-Signed.apk
```

La salida debe mostrar los esquemas v2 y v3, el número de certificados y la huella SHA-256. Esa huella se compara con la que se anotó al crear la clave. Si `apksigner` no está en el `PATH`, se usa el de `build-tools` del SDK de Android.

También se comprueba la alineación y el contenido del paquete:

```bash
zipalign -c -v 4 bin/Release/net10.0-android/publish/com.ejemplo.comicteca-Signed.apk
```

El build suele alinear el APK; la comprobación detecta una manipulación posterior o una herramienta mal configurada. Un APK desalineado puede instalarse y fallar al cargar recursos nativos.

## Instalación para el propietario

Por USB, con la depuración activada y el dispositivo autorizado:

```bash
adb devices
adb install -r bin/Release/net10.0-android/publish/com.ejemplo.comicteca-Signed.apk
```

`-r` reinstala conservando los datos. Para una instalación limpia se desinstala primero; eso borra la base local y la sesión, y es lo que hay que hacer si se cambia la clave o se prueba desde cero. `adb install -d` permite bajar de versión, pero no es un mecanismo de reversión fiable: los datos pueden quedar en un estado que la versión anterior no entiende.

Sin cable, se copia el APK al dispositivo y se abre desde el gestor de archivos. Android pedirá permitir la instalación desde esa aplicación; es un ajuste por origen, no un permiso global. El archivo debe llegar por un canal autenticado y con una suma de comprobación publicada aparte:

```bash
sha256sum com.ejemplo.comicteca-Signed.apk
```

El propietario compara la suma antes de instalar. Si no coincide, el archivo se descarta. La comprobación no demuestra que el APK sea seguro, pero sí que es el que se generó y no se corrompió al transferirlo.

Actualizar exige el mismo `ApplicationId`, la misma clave y un `versionCode` mayor. Si la app no se actualiza, se revisa en este orden: firma distinta, versión no incrementada, paquete distinto o APK corrupto. El mensaje de Android suele ser genérico; el registro de `adb install` da el motivo.

## Un canal privado, sin Google Play

El repositorio del código de Comicteca es público, así que sus *releases* no son un canal privado: cualquiera puede descargar el APK. El canal de distribución debe ser otro, con autenticación y acceso limitado al propietario. Las opciones razonables son:

- Un release de un repositorio privado de distribución, separado del código y accesible solo a las cuentas autorizadas.
- Un almacenamiento privado con enlaces firmados y caducidad, o una carpeta compartida con permisos nominales.
- Una entrega directa del archivo, con suma de comprobación y confirmación de recepción.

En cualquiera de ellos se publica, junto al APK, la versión, el `versionCode`, la huella de firma, la suma SHA-256 y unas notas breves de cambios. Se conserva la versión anterior mientras la nueva no esté probada. No se envía un enlace público «temporal»: un enlace sin autenticación es público aunque dure poco.

Sin Play no hay actualización automática ni despliegue escalonado. El propietario instala cada versión; la app puede comprobar al arrancar si el servidor declara una versión mínima y mostrar un aviso, pero no puede actualizarse sola. Si un dispositivo se pierde, no existe una retirada remota del APK: se revocan los tokens y las sesiones en el servidor, y se invalida la cuenta. Esa es la palanca real.

Tampoco hay firma gestionada por la tienda. La clave es del proyecto y su custodia es una tarea permanente. La ventaja es que no se depende de una cuenta de desarrollador ni de una revisión; el coste es que el proceso de build, firma, verificación y entrega no lo hace nadie más.

## Por qué un APK no se publica como artefacto de un repositorio público

Publicar un binario en un repositorio público parece cómodo: un enlace, una descarga, una demo. También crea problemas que el código fuente no tiene:

- **No se puede revisar.** Un APK contiene código compilado, recursos y configuración. La revisión de un *pull request* no ve lo que hay dentro; confiar en él exige reproducir el build y comparar, que es justo lo que un artefacto suelto no garantiza.
- **Se separa de la fuente.** El binario puede haberse construido desde una rama, con dependencias distintas o con cambios que nunca llegaron a `main`. Nada en el repositorio obliga a que corresponda al código publicado.
- **Es permanente y indexable.** Un asset de una release pública se puede descargar, replicar y enlazar desde cualquier sitio. Borrarlo después no recupera las copias.
- **Amplía la superficie de confianza.** Cualquiera puede redistribuirlo, modificar el envoltorio o hacerlo pasar por una versión oficial con otra firma. El usuario no tiene forma sencilla de comprobar el origen.
- **Puede filtrar configuración.** Direcciones internas, identificadores de entorno, claves mal puestas o datos de prueba viajan dentro del paquete. La revisión del código no siempre detecta un recurso incrustado.
- **Mezcla código y entrega.** El repositorio público sirve para que el código sea legible y reproducible; el canal de distribución sirve para entregar una versión concreta a una persona concreta. Son responsabilidades distintas.

La alternativa es pública y verificable: se publica el código, las instrucciones de build y la versión de las dependencias; quien quiera un APK lo construye. Si hace falta una demo instalable, se entrega por el canal privado, con suma de comprobación y sin convertir el repositorio en un espejo de binarios. Un `dist/` generado tampoco se versiona por la misma razón: el artefacto se produce, no se archiva en la fuente.

## Lista de comprobación

- ¿La clave está fuera de Git, con copia cifrada y restauración probada?
- ¿El `versionCode` crece en cada entrega y el `ApplicationId` no cambia?
- ¿El APK se firma con v2 y v3 y se verifica con `apksigner`?
- ¿La huella de firma y la suma SHA-256 se publican junto al archivo?
- ¿La instalación y la actualización se probaron en un dispositivo real?
- ¿El canal de distribución es privado, autenticado y separado del repositorio público?
- ¿Se conserva la versión anterior y se sabe cómo volver?
- ¿La pérdida de un dispositivo se cubre revocando sesiones en el servidor?
- ¿El repositorio público contiene fuente e instrucciones, no APK?
