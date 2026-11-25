# Qué es ASP.NET Core

ASP.NET Core es la infraestructura sobre la que se construyen las aplicaciones web de Microsoft. No es una versión más de ASP.NET: es un producto escrito desde cero que rompe la compatibilidad con las versiones 4.x y que sirve de suelo común a MVC, Razor Pages, Blazor, SignalR o gRPC.

Entender ese suelo antes de entrar en MVC ahorra muchas confusiones: explica por qué un proyecto web ya no arrastra Web Forms, por qué las dependencias son paquetes y no ensamblados, y por qué la aplicación arranca como un programa de consola que levanta su propio servidor.

## Por qué nació

Desde 2002, ASP.NET incluía todo lo necesario para construir aplicaciones web con las herramientas de Microsoft: infraestructura, Web Forms, seguridad, gestión del estado de la vista y un largo etcétera, todo de una pieza. Usar ASP.NET obligaba a cargar el *framework* entero aunque solo se aprovechara una parte.

Una página informativa atravesaba en cada petición un entramado de módulos, *handlers*, recuperación de estado, construcción de árboles de controles, seguridad y gestión de errores. Algunos componentes se podían desactivar por configuración, pero seguían presentes y consumían memoria y tiempo de proceso.

Ese diseño monolítico también frenaba la evolución del producto. No se podía actualizar un componente por separado y cada versión debía mirar hacia atrás para no romper la retrocompatibilidad, así que los ciclos se medían en años mientras la web cambiaba en meses. Cada entrega añadía funciones y engordaba el conjunto, casi siempre por detrás de lo que pedía el mercado.

Cuando Microsoft construyó otros marcos sobre ASP.NET (MVC, después Web API, Web Pages y más tarde SignalR), todos arrastraban la misma losa. OWIN y Katana sirvieron de aislante entre los marcos de alto nivel y la infraestructura, y las versiones jóvenes de Web API y SignalR se desvincularon de `System.Web`. Con MVC no fue posible: hasta la versión 5 siguió atado a ASP.NET 4.x porque lo usaba en demasiados puntos.

En 2014 Microsoft presentó ASP.NET vNext, conocido internamente como «Project K». La idea era partir de cero: una infraestructura ligera y modular, capaz de correr sobre .NET Framework y sobre el .NET Core que empezaba a asomar, con ejecución multiplataforma y un rendimiento muy superior. El desarrollo se prolongó hasta junio de 2016, cuando se publicó ASP.NET Core 1.0.

## Qué cambió respecto a ASP.NET 4.x

Las diferencias no son cosméticas. Estas son las que más se notan al empezar:

- **No hay retrocompatibilidad a nivel de plataforma.** La infraestructura rompe con todo lo anterior. Algunas tecnologías quedan ancladas en 4.x, como Web Forms, y otras tuvieron que publicar una versión propia, como ASP.NET Core MVC.
- **La aplicación incluye solo lo que usa.** Seguridad, globalización, *tracing*, gestión de errores o sesiones dejan de venir de serie y pasan a ser componentes que se añaden cuando hacen falta.
- **Lo habitual es referenciar paquetes NuGet**, no ensamblados. Eso simplifica el despliegue, la gestión de dependencias y las actualizaciones.
- **Hay un único tipo de proyecto web**, ASP.NET Core, sobre el que se añaden los componentes necesarios. Ya no existe un proyecto para MVC y otro para SignalR; es la continuación de la filosofía «One ASP.NET».
- **Es multiplataforma en diseño y en ejecución.** El mismo código se crea y se ejecuta en Windows, Linux y macOS, y puede alojarse en IIS, en otro servidor, como servicio del sistema o dentro de una aplicación cualquiera. Compilar, empaquetar y ejecutar se puede hacer desde la línea de comandos con el SDK.
- **Hay libertad de herramientas.** Se puede trabajar con Visual Studio, con Visual Studio Code o con un editor de texto simple.
- **El ciclo de trabajo se acorta.** `dotnet watch` recompila y reinicia al guardar los archivos.
- **La estructura del proyecto cambia.** Desaparecen `Global.asax` y `Web.config`, y se separan los archivos de desarrollo de los estáticos que se llevan al servidor.
- **El modelo de alojamiento es otro.** Una aplicación ASP.NET Core es un programa de consola que inicia su propio servidor web.

Ese último punto merece detalle, porque explica media arquitectura. El *framework* trae tres servidores:

- **Kestrel**, la opción por defecto. Es ligero, eficiente y multiplataforma, y puede conectarse directamente a Internet o colocarse detrás de un servidor más completo, como IIS, Nginx o Apache, actuando este como proxy inverso.
- **IISHttpServer**, exclusivo de Windows, que ejecuta la aplicación dentro del proceso de IIS y mejora el rendimiento.
- **HttpSys**, también exclusivo de Windows, construido sobre los controladores HTTP del sistema. Sirve para exponer servicios sin IIS ni proxy inverso y da acceso a funciones propias del sistema, como la autenticación de Windows, la compartición de puertos o HTTP/2 sobre TLS.

ASP.NET Core nació además preparado para la nube, algo que sus antecesores no podían tener en cuenta porque la nube aún no existía como mercado.

## El mapa de tecnologías

Con ASP.NET Core se reorganizó la pila web de Microsoft. Web Forms quedó fuera: sigue soportado en la familia 4.x, pero no llegará nunca a ASP.NET Core. Web API desapareció como *framework* y sus funciones se integraron en MVC.

Web Pages también se retiró, y en su lugar MVC incorporó **Razor Pages**, un enfoque orientado a páginas que recuerda al que ofrecía aquel. SignalR continuó como tecnología para servicios en tiempo real, con una versión específica para ASP.NET Core. Blazor añadió componentes interactivos que se ejecutan en el servidor o en el navegador, y gRPC cubrió los servicios binarios de alto rendimiento.

WCF no aparece en el mapa y, sin embargo, no está en retirada: hay escenarios donde su flexibilidad sigue siendo necesaria y existe un *port* para .NET Core. La recomendación de Microsoft es sencilla: para programar servicios, empezar por MVC o por las API mínimas, y evaluar WCF solo si no cubren la necesidad.

El mapa también muestra la modularización. Ya no hay un bloque único: hay muchas piezas y cada aplicación lleva solo las que necesita, de modo que cada una puede evolucionar y corregirse por su cuenta.

Al principio, ASP.NET Core podía ejecutarse sobre .NET Framework 4.x o sobre .NET Core. La opción dual (*multi-targeting*) existía para facilitar una migración progresiva y permitir reutilizar bibliotecas existentes, pero limitaba el despliegue a Windows cuando se elegía .NET Framework. Esa posibilidad desapareció con ASP.NET Core 3.0: desde entonces, las aplicaciones solo corren sobre .NET moderno. En esa misma etapa llegaron otros marcos construidos encima, como Blazor y los servicios basados en gRPC.

## .NET, la plataforma de debajo

.NET es la plataforma de desarrollo que mantienen Microsoft y la comunidad. Incluye un *runtime*, bibliotecas, herramientas y compiladores. Sus ventajas frente a las versiones tradicionales son la base de todo lo anterior:

- **Está escrito prácticamente desde cero**, lo que permitió optimizar el rendimiento y el aprovechamiento del *hardware*.
- **Es multiplataforma real**: funciona igual en Windows, en las distribuciones más populares de Linux y en macOS, tanto en desarrollo como en explotación.
- **Se maneja desde la línea de comandos.** La CLI de .NET es común a los tres sistemas y cubre el ciclo completo: compilar, ejecutar, depurar y probar.
- **Se despliega con facilidad.** Puede instalarse a nivel de máquina o viajar dentro de la propia aplicación, y varias versiones de SDK y *runtime* conviven en el mismo equipo sin interferirse.
- **Es compatible** con bibliotecas antiguas a través de .NET Standard y de los ensamblados de .NET Framework que cumplen los contratos soportados.
- **Es de código abierto** desde el principio, con la comunidad colaborando y Microsoft sosteniendo la calidad y el soporte.

ASP.NET Core se apoya en .NET, así que hereda esas ventajas sin intermediarios. Por eso el único requisito para desarrollar o ejecutar una aplicación de este tipo es tener el SDK o el *runtime* de .NET instalado.
