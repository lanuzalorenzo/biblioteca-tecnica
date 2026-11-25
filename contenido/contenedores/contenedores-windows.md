# Contenedores Windows

Un contenedor Windows no comparte el kernel de Linux: necesita un host Windows con soporte de contenedores y una imagen base de Windows. El modelo es el mismo —proceso aislado, imagen por capas, Dockerfile—, pero cambian el aislamiento, las imágenes disponibles y la red. Sin esas piezas, una imagen `windowsservercore` no arranca en Linux y una imagen Linux no arranca en un motor en modo Windows.

## Dos formas de aislar

- **Aislamiento de proceso**: todos los contenedores comparten el kernel del host. Es el equivalente a Linux y el más eficiente, pero exige que la imagen y el host sean de la **misma versión de Windows**. Una imagen de una versión posterior no arranca en un host anterior.
- **Aislamiento Hyper-V**: cada contenedor corre en una máquina virtual mínima con su propio kernel. Aísla más y permite imágenes de versiones anteriores, a cambio de arranque más lento y más recursos. Es el único modo disponible en las ediciones de cliente de Windows.

En Windows Server se pueden usar ambos; en las ediciones cliente de Windows 11, solo Hyper-V. Windows 10 terminó su soporte en octubre de 2025: no es una plataforma objetivo. Docker Desktop elige el modo según la configuración del host, y no se puede forzar una imagen incompatible: el error aparece al crear el contenedor.

## Imágenes base

Microsoft publica sus imágenes en `mcr.microsoft.com`, no en Docker Hub. Las dos familias principales son:

| Base | Qué incluye | Cuándo se usa |
|---|---|---|
| `nanoserver` | Mínimo, sin shell completa ni GUI | Primera opción para servicios |
| `windowsservercore` | Más componentes y compatibilidad | Cuando falta algo en Nano Server |
| `dotnet/framework/*` | .NET Framework, ASP.NET, WCF | Aplicaciones heredadas |
| `dotnet/runtime` y `dotnet/aspnet` | .NET moderno | Servicios .NET |

Nano Server no soporta .NET Framework ni WCF, así que esas aplicaciones obligan a Server Core. Las imágenes de Server Core pesan varios gigabytes; Nano Server, unos cientos de megabytes. La etiqueta incluye la versión de Windows (`ltsc2022`, `ltsc2025`) y hay que elegir una compatible con el host.

```dockerfile
FROM mcr.microsoft.com/dotnet/sdk:10.0-nanoserver-ltsc2022 AS build
WORKDIR /src
COPY . .
RUN dotnet publish -o /app

FROM mcr.microsoft.com/dotnet/aspnet:10.0-nanoserver-ltsc2022
WORKDIR /app
COPY --from=build /app .
EXPOSE 80
ENTRYPOINT ["dotnet", "MiApi.dll"]
```

La etiqueta exacta depende de la versión de Windows del host; si no coincide, el contenedor no arranca aunque la imagen se descargue. En un clúster se fija la versión que soportan todos los nodos.

## Habilitar el modo Windows

En Windows 11 hay que activar la característica **Containers** en «Activar o desactivar características de Windows» y reiniciar. Después, Docker Desktop ofrece «Switch to Windows containers» en su menú. Al cambiar de modo, el motor deja de ver los contenedores e imágenes Linux, y viceversa.

No se pueden ejecutar contenedores Linux y Windows a la vez en el mismo motor. Durante un tiempo existió LCOW para mezclarlos, pero se retiró. La forma de trabajar con ambos es mantener WSL 2 para los Linux y el terminal de Windows para los Windows; son dos almacenes separados.

## Redes

| Red | Comportamiento |
|---|---|
| `nat` | Red por defecto; salida por un conmutador interno de Hyper-V y DNS propio |
| `transparent` | El contenedor se conecta a la red física y toma IP de ese segmento |
| `ics` | Red ligada a un adaptador de Hyper-V; alcanzable desde ese adaptador |

En `nat` los puertos se publican igual que en Linux y los contenedores se resuelven por nombre. En `transparent` el contenedor aparece como un equipo más de la red, con la IP que le asigne DHCP o una fija. En `ics` la conectividad depende del adaptador virtual al que esté asociada la red.

```bash
docker network ls
docker run -d --network nat -p 8080:80 mi-api:win
docker run -d --network transparent mi-api:win
```

Desde WSL 2 no siempre se alcanza un contenedor Windows por `localhost`; si ocurre, se usa la IP interna del contenedor o una red `ics`. Es una limitación de la convivencia entre los dos planos de red, no del contenedor.

## Construir y ejecutar

El Dockerfile es el mismo que en Linux, con imágenes de Windows. La diferencia aparece en la red durante la construcción: el motor crea un contenedor temporal y elige la primera interfaz disponible. Si esa interfaz no tiene salida a internet, la descarga de paquetes falla.

```powershell
Get-NetIPInterface -AddressFamily IPv4 | Sort-Object InterfaceMetric
Set-NetIPInterface -InterfaceAlias "Ethernet" -InterfaceMetric 4
```

El primer comando muestra el orden de interfaces; el segundo baja la métrica de la que tiene salida. Requiere permisos de administrador. Después, `docker build` descarga las dependencias con normalidad.

```powershell
docker build -t mi-api:win .
docker run -d -p 8080:80 mi-api:win
```

Las rutas del Dockerfile son las de la imagen Windows (`C:\app`, `C:\src`), no las de Linux, aunque la sintaxis `WORKDIR /app` se traduce a `C:\app` en la mayoría de imágenes. Los comandos de shell son de `cmd.exe` o PowerShell, no de `bash`; si el Dockerfile usa `RUN` con sintaxis POSIX, falla.

## Límites del modelo

Los contenedores Windows son útiles para aplicaciones .NET Framework y servicios que dependen de APIs de Windows, pero no son portables a Linux ni al revés. La imagen es grande, el arranque es más lento y la versión del sistema operativo condiciona todo el despliegue. Para servicios nuevos, .NET moderno sobre Linux suele ser más ligero; para lo que ya existe y no se puede migrar, el contenedor Windows sigue siendo una forma razonable de empaquetar.
