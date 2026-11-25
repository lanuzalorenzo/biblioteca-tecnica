# Paquetes NuGet y metapaquetes

Una aplicación ASP.NET Core no referencia los ensamblados de sus dependencias: referencia los paquetes NuGet que las distribuyen. Parece un detalle de herramienta, pero de ahí salen la modularidad del *framework*, la resolución de versiones y la forma de auditar qué usa el proyecto.

## La dependencia viaja en un paquete

En ASP.NET 4.x lo habitual era copiar la DLL al proyecto y añadir la referencia en el archivo de proyecto. NuGet se usaba sobre todo para bibliotecas de *frontend* como jQuery o Bootstrap, una práctica hoy desaconsejada: esos recursos tienen su propio gestor, como NPM o LibMan.

En ASP.NET Core el paquete sustituye también a la referencia de servidor. El proyecto declara el paquete y la versión; el SDK resuelve sus dependencias en cascada y descarga lo que falte en la caché local de NuGet. El repositorio guarda la declaración, no los binarios.

La resolución queda escrita en `obj/project.assets.json`, que no se edita ni se versiona. Cuando dos paquetes piden versiones distintas de una misma dependencia, NuGet elige la más baja que satisface todos los rangos y solo sube si otra dependencia exige un mínimo mayor. El SDK avisa cuando la combinación no encaja.

## Tres formas de añadir un paquete

La más rápida desde la consola es `dotnet add package`, ejecutada en la carpeta del proyecto o indicando su ruta. El comando añade la referencia al archivo de proyecto y restaura:

```bash
dotnet add package Microsoft.Extensions.Http --version 10.0.0
```

Desde Visual Studio, el gestor de paquetes se abre con el menú contextual del proyecto o de la solución. Permite buscar, instalar, actualizar y quitar sin tocar XML. Es la vía más cómoda cuando no se recuerda el nombre exacto del paquete.

La tercera vía es editar el archivo del proyecto. Dentro de un `ItemGroup` se declara cada referencia:

```xml
<ItemGroup>
  <PackageReference Include="Microsoft.Extensions.Http" Version="10.0.0" />
</ItemGroup>
```

Si se escribe a mano, conviene ejecutar `dotnet restore` para descargar lo declarado. La compilación y la ejecución también restauran por su cuenta, así que el comando explícito solo hace falta cuando se quiere comprobar antes de compilar o cuando el proyecto se abre en un editor sin esa integración.

## Qué paquetes acepta el proyecto

No todo paquete sirve para cualquier destino. .NET 10 implementa .NET Standard 2.1, así que el proyecto consume sin problema los paquetes dirigidos a ese estándar o a una versión anterior. Un paquete que solo declara destinos de .NET Framework es otro caso: se instala, pero se restaura contra la plataforma del proyecto con un aviso de compatibilidad.

Ese aviso no siempre impide compilar. Muchos paquetes antiguos funcionan a través de un adaptador de compatibilidad, y el resultado es correcto mientras no se usen las partes atadas a Windows. En Linux o macOS el fallo aparece en ejecución, no en la restauración: la aplicación arranca y revienta cuando llama al código que dependía de una API del sistema ausente. Por eso, antes de adoptar un paquete sin soporte para .NET moderno, se comprueba qué hace y en qué plataformas se va a desplegar.

## Metapaquetes y marcos compartidos

Escribir a mano todas las referencias de una aplicación web sería tedioso: casi todas usan Kestrel, configuración, registro de trazas y archivos estáticos. Para eso existen los metapaquetes, paquetes que a su vez referencian otros paquetes. Instalar uno equivale a instalar su lista completa.

`Microsoft.AspNetCore.App` es el metapaquete del *framework*. Los proyectos web lo reciben sin declararlo, porque el SDK ya añade la referencia al marco compartido. Al compilar, esas dependencias no se copian a la salida: se resuelven contra la instalación de .NET del equipo, en la carpeta `shared` que hay junto al SDK. Una sola copia sirve a todas las aplicaciones y llega con imágenes nativas pregeneradas, lo que acelera el arranque.

El marco compartido no se actualiza desde NuGet: cambia cuando se instala otra versión del SDK o del *runtime*. Lo que sí puede hacerse es fijar un paquete individual a una versión concreta, aunque lo normal es no separarse del marco. La lista de lo instalado se consulta con `dotnet --list-runtimes`; la salida muestra cada versión de `Microsoft.AspNetCore.App` y de `Microsoft.NETCore.App` disponible en la máquina.

## Saber qué usa el proyecto

`dotnet list package` enumera las referencias directas con su versión resuelta, y `dotnet list package --outdated` señala las que tienen una más reciente. La segunda orden es la que se ejecuta antes de actualizar un lote: muestra el salto y permite decidir si compensa.

Las dependencias transitivas también cuentan. Un paquete que no se declaró puede entrar por otro y traer una versión vulnerable, que las herramientas de auditoría marcan con su identificador. Antes de publicar, conviene revisar ese árbol y no solo la lista de primer nivel.

## Centralizar versiones

En una solución con varios proyectos, las versiones se centralizan en `Directory.Packages.props` con `ManagePackageVersionsCentrally` activado. Los `.csproj` declaran `PackageReference` sin versión y el archivo común decide cuál se usa. Así una actualización se hace en un sitio y no queda un proyecto con una versión distinta por descuido.
