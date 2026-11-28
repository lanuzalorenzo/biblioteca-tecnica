# Qué es .NET MAUI y cuándo no usarlo

.NET MAUI (*Multi-platform App UI*) es la forma de Microsoft de construir aplicaciones con C# y XAML sobre .NET. Un mismo proyecto compila para Android, iOS, macOS y Windows, y la interfaz no se dibuja con HTML dentro de un navegador: cada control de la pantalla es el control nativo de la plataforma, envuelto por una capa común. Un botón es un botón de Android; una lista, la lista del sistema. Esa diferencia explica tanto lo que MAUI aporta como lo que cuesta mantenerlo.

MAUI no nace de cero. Continúa a Xamarin.Forms, del que hereda el modelo de XAML, el enlace de datos y el patrón MVVM, pero cambia la pieza que traduce cada control: los *renderers* de Xamarin dan paso a *handlers* más ligeros, y el proyecto único sustituye a la maraña de proyectos por plataforma. Con .NET 10 comparte *runtime*, bibliotecas y herramientas con el resto de la plataforma, así que una biblioteca de lógica escrita para una API se puede referenciar desde el cliente sin duplicarla.

Para un cliente Android como el que se está construyendo en [Comicteca](https://github.com/lanuzalorenzo/comicteca), la pregunta útil no es si MAUI puede hacerlo. Casi cualquier pantalla se puede hacer. La pregunta es si el coste de mantener un cliente nativo se paga con lo que ese cliente aporta frente a una aplicación web instalable o frente a un envoltorio de la web.

## Qué aporta

- **Un solo lenguaje y un solo *runtime*.** La lógica, los modelos, la validación y el acceso a la API viven en C#, y se comparten con el resto de la solución. No hay que reescribir el dominio en JavaScript ni mantener dos implementaciones de las mismas reglas.
- **Controles nativos.** El resultado se integra con el sistema: temas, tipografías, accesibilidad, gestos, teclado, portapapeles y menús contextuales. Una lista larga se desplaza con el comportamiento de la plataforma, no con el de una página web.
- **Acceso al dispositivo.** Cámara, almacenamiento, notificaciones, biometría, red y sensores se usan a través de las API de .NET para Android o de las interfaces comunes de MAUI. El límite lo pone el sistema operativo y sus permisos, no el navegador.
- **Trabajo sin conexión.** Una base de datos local, una caché de archivos y una cola de operaciones pendientes son piezas normales de una aplicación instalada. La web puede aproximarse con *service workers*, pero el control del almacenamiento y del ciclo de vida es menor.
- **Un proyecto único.** `UseMaui`, `SingleProject` y las carpetas `Platforms/` permiten tener el código común y el específico de Android en el mismo proyecto, con recursos, iconos y manifiesto incluidos.
- **Herramientas de .NET.** Depuración, pruebas, analizadores, `dotnet build`, `dotnet publish` y el resto del ecosistema funcionan igual que en una biblioteca o en una API. La curva de entrada para alguien que ya programa en C# es corta.

## Controles nativos, no una web disfrazada

La diferencia con un envoltorio web no es estética. En MAUI, XAML describe un árbol de controles; un *handler* crea el control nativo correspondiente y le aplica propiedades. El sistema mide, coloca y pinta ese control. En una aplicación web dentro de un WebView, el árbol es DOM, el motor que lo pinta es el navegador y el puente entre C# y JavaScript añade una capa en cada interacción.

Eso no convierte a MAUI en una bala de plata. Un control nativo sigue necesitando un *handler* que exponga sus propiedades, y algunas funciones de Android llegan antes a Kotlin que a la capa común. Cuando la interfaz depende de una API muy reciente o de un comportamiento muy concreto del sistema, el código específico de plataforma crece y la ventaja del proyecto único se estrecha.

## La forma de una solución

La estructura que mejor envejece separa lo que se puede probar en cualquier equipo de lo que necesita Android:

```
Comicteca.Core/        net10.0          dominio, contratos, servicios, DTO
Comicteca.App/         net10.0-android  arranque, XAML, permisos, plataforma
Comicteca.Core.Tests/  net10.0          unitarias e integración con servidor falso
```

`Core` no referencia MAUI ni Android. Describe qué necesita —un almacén de sesión, un reloj, un cliente HTTP— mediante interfaces, y la aplicación Android aporta las implementaciones. Esa frontera es la que permite ejecutar la mayor parte de las pruebas en Linux y la que evita que un detalle de la pantalla se cuele en la lógica de negocio.

La app Android queda fina: arranca, compone dependencias, pide permisos, muestra XAML y traduce eventos del sistema. Todo lo que se pueda contar sin mirar la pantalla pertenece a `Core`.

## Cuándo no usarlo

MAUI es una mala elección en varios escenarios conocidos:

- **El producto es principalmente contenido y se actualiza a diario.** Una PWA o una *Trusted Web Activity* evitan la instalación, el canal de distribución y la firma. Si la aplicación no necesita hardware ni almacenamiento propio, el cliente nativo solo añade mantenimiento.
- **El equipo es web y no tiene experiencia en .NET.** Blazor Hybrid permite reutilizar componentes Razor dentro de una carcasa nativa, pero sigue exigiendo compilar, firmar y distribuir una aplicación. Si nadie va a mantener ese proceso, la deuda aparece en la primera actualización de Android.
- **La interfaz es un juego, 3D o vídeo intensivo.** Unity, Unreal o el desarrollo nativo ofrecen un control del *render* que MAUI no pretende dar.
- **Se depende de una API de Android que aún no está expuesta.** En ese caso, Kotlin y Jetpack Compose llegan antes y sin puente. MAUI permite código específico, pero cada excepción reduce la parte compartida.
- **El objetivo incluye Linux de escritorio.** MAUI cubre Android, iOS, macOS y Windows; Linux no es una plataforma oficial. Hay iniciativas de la comunidad, pero no son una base que se pueda prometer.
- **El tamaño del binario o el arranque son críticos.** Una aplicación MAUI incluye el *runtime* de .NET y las dependencias de MAUI. Una app nativa mínima pesa menos y arranca antes; en un dispositivo muy limitado, la diferencia se nota.
- **Se necesita publicar cambios sin instalar nada.** La actualización de una app instalada pasa por un APK nuevo o por una tienda. La web actualiza al recargar.
- **Solo hay equipos macOS para iOS y ninguno para Android, o al revés.** Compilar para iOS exige macOS; para Android se puede trabajar en Linux, Windows o macOS, pero hace falta el SDK y un JDK compatibles.

## Comparación con TWA, PWA y Blazor Hybrid

| Enfoque | Qué se ejecuta | Distribución | Acceso al dispositivo | Actualización |
|---|---|---|---|---|
| **MAUI** | C# y controles nativos sobre .NET | APK, tienda o canal propio | Amplio, con permisos del sistema | APK nuevo o tienda |
| **TWA** | Una web abierta en el motor de Chrome, sin barra de direcciones | APK o tienda; requiere *Digital Asset Links* | El de la web y sus APIs | Inmediata al publicar la web |
| **PWA** | La web en el navegador, instalable | Sin tienda; desde el navegador | Limitado y desigual según el navegador | Inmediata al publicar la web |
| **Blazor Hybrid** | Componentes Blazor dentro de un WebView, en una carcasa MAUI | Como MAUI | El de la carcasa y el puente | APK nuevo o tienda |

La **TWA** no es una aplicación nativa: es una ventana de Chrome sin barra que carga un sitio propio. Para que se comporte como app, el sitio debe ser una PWA y el dominio debe declarar el vínculo con la aplicación mediante *Digital Asset Links*; si la verificación falla, Android muestra la barra del navegador. Su ventaja es que el contenido se actualiza al instante; su límite, que no hay acceso arbitrario al hardware y que la experiencia depende de Chrome.

Una **PWA** se instala desde el navegador, usa un *service worker* para funcionar sin conexión y un manifiesto para el icono y la pantalla de inicio. No pasa por una tienda y no tiene firma de aplicación. En Android el soporte es bueno; en iOS es más restringido y cambia con las versiones. Es la opción más barata cuando la web ya existe y el requisito es «que se pueda abrir como una app».

**Blazor Hybrid** comparte el modelo de componentes de Blazor dentro de una aplicación MAUI o WPF. La interfaz se pinta en un WebView, pero el código se ejecuta en .NET y puede llamar a APIs del dispositivo a través del anfitrión. Sirve para un equipo que ya domina Razor y quiere una app instalable sin aprender XAML; no convierte la interfaz en nativa ni elimina el coste de firmar y distribuir.

La decisión práctica suele reducirse a tres preguntas: ¿hace falta hardware o almacenamiento que la web no da?, ¿la experiencia sin conexión es un requisito o un extra?, ¿hay alguien que mantenga el canal de distribución y las actualizaciones del sistema?

## El coste de mantener un cliente nativo

Un cliente nativo no se termina cuando compila. Mantenerlo implica:

- **Seguir a Android.** Cada año sube el nivel de API exigido, cambian los permisos, se endurecen las restricciones de segundo plano y aparecen requisitos nuevos para notificaciones, almacenamiento o pantalla completa. Una app que no se revisa deja de comportarse bien aunque nadie haya tocado su código.
- **Seguir a .NET y a MAUI.** Las versiones de .NET se suceden cada noviembre; las cargas de trabajo, el SDK de Android y el JDK deben ser compatibles entre sí. Actualizar MAUI puede cambiar controles, estilos o el comportamiento del recorte.
- **Probar en dispositivos reales.** El emulador detecta muchos fallos, pero no todos: fabricantes, capas de personalización, memoria, batería, sensores y permisos concedidos o revocados a mano. La matriz crece con cada versión de Android que aún se soporte.
- **Custodiar la clave de firma.** La clave identifica la aplicación y permite actualizarla. Si se pierde, no se puede publicar una versión que sustituya a la anterior con el mismo paquete; si se filtra, cualquiera puede firmar una actualización maliciosa. Es un secreto de larga vida y no cabe en el repositorio.
- **Mantener un canal de distribución.** Sin tienda, hay que decidir cómo llega el APK, cómo se avisa de una versión nueva, cómo se verifica y qué se hace si una actualización sale mal. Ese proceso también se documenta y se prueba.
- **Sostener dos superficies.** La API y el cliente evolucionan juntos. Un cambio incompatible en el servidor puede dejar versiones antiguas del APK sin funcionar; hacen falta versionado, mensajes de error claros y una política de actualización.
- **Asumir la observabilidad del lado del cliente.** El servidor no ve un cierre inesperado, un fallo de render o un error de permisos. Alguien tiene que recoger esos fallos, con consentimiento y sin datos personales.

## El caso de Comicteca

Comicteca es una aplicación de biblioteca de cómics con un repositorio público en <https://github.com/lanuzalorenzo/comicteca>. El cliente Android se está construyendo; esta biblioteca recoge la base técnica del módulo, no un informe de resultados. La decisión de mantener un cliente nativo se justifica si la lectura sin conexión, el almacenamiento local y la integración con el sistema son parte del producto; si el objetivo fuera solo consultar el catálogo, una PWA cubriría lo mismo con menos piezas.

## Lista de decisión

- ¿Qué hace la app que una web instalada no pueda hacer?
- ¿La experiencia sin conexión es imprescindible o deseable?
- ¿Quién mantiene el SDK, el APK, la clave y las actualizaciones dentro de un año?
- ¿Hay dispositivos y versiones de Android que se deban soportar de verdad?
- ¿El equipo puede probar en un móvil real y en un emulador?
- ¿La distribución será una tienda, un canal privado o ambas?
- ¿El producto acepta que una actualización tarde días o necesita cambios instantáneos?

Si la respuesta a la primera pregunta es «nada» y a la última «instantáneos», MAUI sobra. Si hay hardware, almacenamiento y una persona responsable del ciclo de vida, el marco ofrece una base coherente para no escribir dos veces la misma aplicación.
