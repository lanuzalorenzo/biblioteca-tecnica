# Despliegue y calidad

Una aplicación que funciona en el equipo de desarrollo no está terminada. Falta publicarla en un entorno donde otro proceso la arranque, donde la configuración venga de fuera y donde un fallo no deje a los usuarios sin servicio. El despliegue es una decisión de infraestructura, pero el código tiene que estar preparado para él.

## Publicar

`dotnet publish` prepara una carpeta con lo necesario para ejecutar la aplicación: los ensamblados propios, las dependencias que no están en el marco compartido, el contenido de `wwwroot`, la configuración y, si se pide, el *runtime*.

```bash
dotnet publish -c Release -o ./publish
```

La compilación en `Release` aplica optimizaciones que `Debug` desactiva y no incluye símbolos de depuración. Publicar en `Debug` es un error frecuente: la aplicación funciona, pero es más lenta y expone detalles que no deberían salir.

Hay dos modos:

- **Dependiente del framework**: la aplicación usa el *runtime* instalado en el servidor. La carpeta pesa menos y varias aplicaciones comparten la misma instalación.
- **Autocontenida**: la carpeta incluye el *runtime*. Pesa más, pero no exige instalar .NET en el servidor y permite fijar la versión exacta.

```bash
dotnet publish -c Release -r linux-x64 --self-contained true -o ./publish
```

La publicación en un solo archivo (`PublishSingleFile`) simplifica la copia, pero no cambia el modelo de ejecución. El recorte (`PublishTrimmed`) y la compilación AOT reducen el tamaño y el arranque, aunque MVC y Razor dependen de reflexión y no son buenos candidatos: se usan con API mínimas y se prueban a fondo antes de adoptarlos.

## Configuración en el servidor

La misma publicación se despliega en varios entornos. Lo que cambia no va en el binario: va en variables de entorno, en un archivo de configuración externo o en un almacén de secretos.

```bash
export ASPNETCORE_ENVIRONMENT=Production
export ASPNETCORE_URLS=http://127.0.0.1:5000
export ConnectionStrings__Default="Server=...;Database=...;"
```

El doble guion bajo sustituye al separador `:` de las claves anidadas. La cadena de conexión y las claves de firma no se copian a `appsettings.json` ni al repositorio. En un contenedor, se pasan como variables o se montan desde un *secret*; en una máquina, desde el gestor de servicios o un archivo con permisos restringidos.

## IIS

En Windows, IIS puede alojar la aplicación dentro de su propio proceso mediante el módulo ASP.NET Core. Hace falta el **Hosting Bundle**, que instala el *runtime* y el módulo, y un sitio con el *pool* de aplicaciones configurado como «Sin código administrado»: la aplicación no se ejecuta como código gestionado por IIS, sino que IIS le pasa la petición.

El módulo genera un `web.config` en la publicación. La carpeta del sitio apunta a la carpeta publicada. El modelo dentro del proceso es el predeterminado y el de mejor rendimiento; el modelo fuera de proceso se usa cuando hace falta aislar la aplicación o depurar con Kestrel.

## Linux y proxy inverso

En Linux, la aplicación se ejecuta como servicio del sistema y Kestrel escucha en `127.0.0.1`. Nginx o Apache reciben el tráfico público y lo reenvían. La configuración del proxy debe pasar las cabeceras `Host`, `X-Forwarded-For` y `X-Forwarded-Proto`, y la aplicación debe confiar en ellas con `ForwardedHeaders` para generar URLs y redirecciones correctas.

```csharp
app.UseForwardedHeaders(new ForwardedHeadersOptions
{
    ForwardedHeaders = ForwardedHeaders.XForwardedFor |
                       ForwardedHeaders.XForwardedProto
});
```

El servicio se declara con un archivo de systemd: usuario sin privilegios, `Restart=always`, variables de entorno y `WorkingDirectory` en la carpeta publicada. El proxy termina TLS y la aplicación no necesita certificado; si se sirve directo, Kestrel lo configura con `UseHttps`.

## Contenedores

Una imagen de contenedor empaqueta la publicación y el *runtime*. El patrón habitual es una compilación en varias etapas: una imagen con el SDK compila, y la imagen final solo lleva el *runtime* y la carpeta publicada.

```dockerfile
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src
COPY . .
RUN dotnet publish -c Release -o /app

FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS final
WORKDIR /app
COPY --from=build /app .
USER $APP_UID
EXPOSE 8080
ENTRYPOINT ["dotnet", "MiAplicacion.dll"]
```

La imagen final no incluye el SDK ni el código fuente, corre con un usuario sin privilegios y escucha en el puerto que el orquestador exponga. La configuración entra por variables de entorno; los secretos, por el mecanismo del orquestador, no dentro de la imagen.

## Protección de datos

Las cookies de autenticación y los tokens antiforgery se cifran con claves de protección de datos. En un solo servidor se guardan en disco y sobreviven al reinicio. En varios nodos o en contenedores efímeros hay que compartirlas: se persisten en un volumen común o se configura un almacén compartido. Si cada instancia genera claves distintas, la cookie emitida por una no la entiende otra y el usuario pierde la sesión en cada petición.

## Base de datos

Las migraciones de Entity Framework Core se aplican como un paso del despliegue, no al arrancar la aplicación en cada instancia. Varias instancias ejecutando `Database.Migrate()` a la vez compiten por el mismo cambio. Lo habitual es un trabajo previo —un *job* de CI/CD o un comando manual— que aplica las migraciones y después despliega el código.

```bash
dotnet ef migrations add InitialCreate
dotnet ef database update
```

Una migración que borra una columna o cambia un tipo puede romper la versión anterior mientras convive con la nueva. En un despliegue sin parada se separa en pasos compatibles: añadir, desplegar, migrar datos, retirar lo viejo.

## Salud y apagado

El orquestador necesita saber si la instancia puede recibir tráfico. Un endpoint de *readiness* que comprueba la base de datos y un *liveness* que solo confirma que el proceso responde cubren las dos preguntas. La aplicación debe atender la señal de apagado, dejar de aceptar peticiones y terminar las que están en marcha antes de que el proceso muera.

## Pruebas

Un proyecto de pruebas es una biblioteca con un *runner*. xUnit es la opción más extendida; MSTest y NUnit también funcionan. `dotnet new xunit` crea el proyecto y `dotnet add reference` lo enlaza a la aplicación.

```bash
dotnet test
dotnet watch test
```

Las pruebas unitarias cubren el dominio y los controladores. Para el controlador se crea la instancia con un servicio falso y se comprueba el resultado y los datos que recibe la vista; no hace falta levantar el servidor. Las pruebas de integración usan `WebApplicationFactory<Program>`, que arranca la aplicación en memoria, con una base de datos de prueba y un cliente HTTP:

```csharp
public class PostsTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public PostsTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.CreateClient();
    }

    [Fact]
    public async Task Get_posts_returns_ok()
    {
        var response = await _client.GetAsync("/api/posts");
        response.EnsureSuccessStatusCode();
    }
}
```

La fábrica permite sustituir servicios con `WithWebHostBuilder` para usar una base de datos en memoria o un servicio falso. Lo que no se prueba en una unidad —el routing, el pipeline, la serialización— se prueba aquí.

Una prueba que solo comprueba que el método no lanza no aporta nada. La que sirve verifica un comportamiento: el código de estado, el contenido, la llamada al repositorio o el error de validación. Y una prueba que falla de forma intermitente se investiga; no se marca como *flaky* y se ignora.

## Antes de dar por desplegado

La lista mínima: la aplicación arranca con la configuración de producción, el endpoint de salud responde, la base de datos tiene las migraciones aplicadas, los archivos estáticos se sirven, la autenticación funciona y los errores no muestran detalles. Si algo falla, el despliegue se revierte; una versión anterior que funciona es mejor que una nueva a medias.
