# Modelos de ejecución

Una aplicación ASP.NET Core no vive dentro de IIS ni de Apache: arranca como un programa propio que levanta su servidor web y se queda a la espera de peticiones. Esa diferencia con ASP.NET clásico explica por qué `dotnet run` deja un proceso escuchando y por qué el servidor se puede cambiar sin tocar el código de la aplicación.

## La aplicación arranca su servidor

En ASP.NET 4.x, el código se ejecutaba dentro de un servidor ya instalado en la máquina, casi siempre IIS. La aplicación era una pieza que ese servidor cargaba cuando llegaba la primera petición. En ASP.NET Core la relación se invierte: el servidor forma parte de la aplicación y se inicia desde su código de arranque, de modo que el mismo binario puede correr en Windows, Linux o macOS sin depender de un servicio del sistema.

Ese servidor es un componente intercambiable. La aplicación decide cuál usa y, en la práctica, el que viene por defecto es también el más habitual: Kestrel. Es multiplataforma, ligero y está pensado para atender peticiones con poco coste. Aparece en los mensajes de consola en cuanto se ejecuta el proyecto:

```text
$ dotnet run
info: Microsoft.Hosting.Lifetime[0]
      Now listening on: https://localhost:7123
info: Microsoft.Hosting.Lifetime[0]
      Application started. Press Ctrl+C to shut down.
info: Microsoft.Hosting.Lifetime[0]
      Hosting environment: Development
info: Microsoft.Hosting.Lifetime[0]
      Content root path: /home/ana/MiAplicacion
```

## Kestrel solo o detrás de un proxy

Las primeras versiones de Kestrel no estaban preparadas para mirar a internet sin ayuda. La versión actual sí: puede ser el servidor frontal y recibir el tráfico directamente. Aun así, muchos despliegues lo esconden detrás de IIS, Nginx o Apache porque estos ofrecen cosas que Kestrel no cubre por sí solo: reparto de peticiones entre varios servidores internos, comprobaciones de salud, balanceo de carga o reglas de seguridad.

En ese caso, el servidor frontal se configura como proxy inverso: recibe la petición, la reenvía a Kestrel y devuelve al cliente la respuesta que produzca la aplicación. Es el mismo esquema que usan otras tecnologías, donde Apache o Nginx reenvían hacia Tomcat, Jetty o un proceso de Node.

## HttpSys, la alternativa de Windows

Además de Kestrel, ASP.NET Core incluye HttpSys, un servidor que solo funciona en Windows. Se apoya directamente en el controlador Http.sys del sistema, la API HTTP del núcleo, y puede dar servicio sin IIS ni ningún otro intermediario. Es una tecnología madura y ofrece funciones propias del sistema, como autenticación de Windows, compartición de puertos o HTTPS con SNI.

Su versión anterior se llamaba WebListener, así que todavía se encuentra documentación con ese nombre. Lo normal sigue siendo Kestrel; HttpSys tiene sentido en servidores Windows e intranets donde no se puede usar IIS, o cuando se necesita alguna de esas funciones del sistema.

## Alojamiento dentro o fuera del proceso de IIS

Durante las primeras versiones, un proyecto ASP.NET Core sobre IIS funcionaba siempre fuera de proceso. IIS recibía la petición, el módulo de ASP.NET Core la reenviaba por HTTP a Kestrel en otro proceso y Kestrel ejecutaba el código. Ese salto interno se pagaba en rendimiento, y es el mismo esquema que se usa en Linux con Apache o Nginx.

Desde ASP.NET Core 2.2 existe un segundo modelo, el alojamiento dentro del proceso, que evita ese salto. En lugar de mandar la petición a Kestrel, IIS carga la aplicación en su propio proceso de trabajo, `w3wp.exe`, y usa un servidor llamado IISHttpServer. El resultado es bastante más rápido y desde ASP.NET Core 3.0 es el modo predeterminado cuando la aplicación corre sobre IIS.

Para volver al modelo de fuera de proceso se declara en el proyecto:

```xml
<PropertyGroup>
  <TargetFramework>net10.0</TargetFramework>
  <!-- El valor por defecto de AspNetCoreHostingModel es InProcess -->
  <AspNetCoreHostingModel>OutOfProcess</AspNetCoreHostingModel>
</PropertyGroup>
```

Con IIS o IIS Express hace falta además el componente ASP.NET Core Module, que se instala con el paquete de *hosting* de Windows y es el que sabe arrancar y comunicarse con la aplicación.

## Arranque desde Visual Studio

Desde Visual Studio, F5 arranca la aplicación con el perfil de ejecución seleccionado. Los perfiles se declaran en `Properties/launchSettings.json`, que se crea con el proyecto, y el primero de la lista suele ser IIS Express, es decir, el modelo de dentro del proceso. Al desplegar el menú de la barra de herramientas aparecen los demás, entre ellos uno con el nombre del proyecto que lanza Kestrel directamente y prescinde de IIS Express.

Ese perfil tiene una consecuencia práctica: la compilación automática deja de funcionar. Por debajo ejecuta `dotnet run`, y para recompilar al guardar hace falta `dotnet watch run`.

## Elegir el modelo

La decisión se toma por el entorno, no por preferencia. En Windows con IIS, el alojamiento dentro del proceso es la opción por defecto y la de mejor rendimiento. En Linux, Kestrel detrás de Nginx o en un contenedor es lo habitual. Kestrel directo a internet solo tiene sentido si no hace falta lo que aporta un proxy y el certificado y los límites se gestionan con cuidado.
