# Integración continua

La integración continua es la práctica de compilar y probar cada cambio en un entorno limpio, con la mayor frecuencia posible. Su valor no está en ejecutar pruebas —eso ya se hace en local—, sino en hacerlo sin la máquina de quien desarrolla: sin rutas absolutas, sin dependencias instaladas a mano, sin datos que solo existen en un equipo.

Martin Fowler la describió como integrar los cambios varias veces al día para detectar los problemas pronto. En la práctica, un pipeline responde a una pregunta: ¿este commit funciona en un entorno que no es el mío?

## El recorrido mínimo

Todo pipeline de .NET sigue los mismos pasos, cambie la herramienta:

1. Descargar el código del repositorio.
2. Instalar el SDK en la versión que el proyecto declara.
3. Restaurar dependencias.
4. Compilar en `Release`.
5. Ejecutar las pruebas.
6. Publicar resultados y artefactos.

Si un paso falla, los siguientes no se ejecutan y el cambio queda marcado. Esa es la utilidad: el fallo se ve antes de hacer merge, no después de desplegar.

## Un pipeline en GitHub Actions

GitHub Actions lee los workflows de `.github/workflows/`. Un ejemplo para .NET 10:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: "10.0.x"
          cache: true

      - name: Restaurar
        run: dotnet restore

      - name: Compilar
        run: dotnet build --configuration Release --no-restore

      - name: Probar
        run: >-
          dotnet test --configuration Release --no-build
          --collect:"XPlat Code Coverage"
          --results-directory TestResults

      - name: Publicar cobertura
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: cobertura
          path: TestResults/**/coverage.cobertura.xml
```

`setup-dotnet` con `cache: true` guarda el caché de NuGet entre ejecuciones. `--no-restore` y `--no-build` evitan repetir trabajo y, sobre todo, garantizan que se prueba exactamente el binario que se compiló. `if: always()` publica la cobertura también cuando las pruebas fallan, que es cuando más interesa.

La cobertura necesita `coverlet.collector` en el proyecto de pruebas. Sin ese paquete, `--collect` no produce archivo.

## El equivalente en Azure DevOps

```yaml
trigger:
  - main

pr:
  - main

pool:
  vmImage: ubuntu-latest

steps:
  - task: UseDotNet@2
    inputs:
      version: "10.0.x"

  - script: dotnet restore
    displayName: Restaurar

  - script: dotnet build --configuration Release --no-restore
    displayName: Compilar

  - script: >-
      dotnet test --configuration Release --no-build
      --collect:"XPlat Code Coverage"
      --results-directory $(Build.SourcesDirectory)/TestResults
    displayName: Probar

  - task: PublishCodeCoverageResults@2
    condition: always()
    inputs:
      summaryFileLocation: "$(Build.SourcesDirectory)/TestResults/**/coverage.cobertura.xml"
```

Los pasos son los mismos. Lo que cambia es el dialecto del YAML y el nombre de las tareas. Aprender uno de los dos basta para leer el otro.

## Fijar el entorno

Un pipeline reproducible no depende de la última versión del SDK ni de un paquete que se actualiza solo. Tres medidas lo consiguen:

**`global.json`.** Fija la versión del SDK y el modo de resolución:

```json
{
  "sdk": {
    "version": "10.0.100",
    "rollForward": "latestPatch"
  }
}
```

Sin él, una imagen del runner con un SDK más nuevo puede cambiar el comportamiento de la compilación sin que nadie haya tocado el código.

**Dependencias fijadas.** Los paquetes con versión exacta y, si el proyecto lo usa, un archivo de bloqueo (`packages.lock.json`) que se restaura en modo bloqueado. Dependabot o Renovate proponen actualizaciones; el pipeline decide si entran.

**Servicios externos controlados.** Ninguna prueba unitaria debe llamar a una API real. Las de integración usan contenedores o dobles. Una prueba que depende de un servicio de terceros falla cuando el tercero falla, y entonces no informa de nada útil.

## Etapas y velocidad

Una suite grande no debe ejecutarse entera en cada guardado. Estructura habitual:

| Etapa | Qué ejecuta | Cuándo |
|---|---|---|
| Rápida | Unitarias, análisis, formato | Cada push y pull request |
| Integración | Base de datos, HTTP, contenedores | Cada pull request |
| Nocturna | Funcionales, carga, mutaciones | Programada |

El objetivo es que la etapa rápida termine en pocos minutos. Si tarda más, el equipo empieza a ignorar el resultado o a hacer merge sin esperar. Las pruebas lentas se separan por categoría, no se eliminan.

En GitHub Actions se pueden definir trabajos en paralelo con `needs` para las dependencias; en Azure DevOps, etapas y trabajos. La matriz (`strategy.matrix`) permite probar varias versiones de .NET o varios sistemas operativos:

```yaml
strategy:
  matrix:
    dotnet: ["10.0.x"]
    os: [ubuntu-latest, windows-latest]
```

Cada combinación multiplica el tiempo. Se usa cuando la biblioteca se publica para esos destinos, no por cubrir todas las combinaciones posibles.

## Pruebas inestables

Una prueba que falla y pasa sin cambios de código es peor que una prueba ausente: enseña al equipo a reintentar el pipeline y a desconfiar del rojo. Cuando aparece:

1. Se identifica el patrón: hora, orden, paralelismo, recurso compartido, espera fija.
2. Se corrige la causa. Casi siempre es estado compartido o una espera por tiempo.
3. Si no se puede corregir de inmediato, se marca y se aparta de la etapa rápida con un ticket y una fecha. No se deja suelta.

Reintentar el pipeline no es una solución; es una forma de ocultar el problema.

## Lo que no debe hacer el pipeline

- **Guardar secretos en el YAML.** Las credenciales van en el almacén de secretos del servicio y se inyectan como variables. Un secreto en el repositorio se considera expuesto aunque el repositorio sea privado.
- **Dar permisos de más.** El workflow declara solo los permisos que necesita; `contents: read` es el punto de partida.
- **Publicar desde una pull request.** El despliegue se ata a una rama protegida y a un entorno con aprobación, no a cualquier push.
- **Mezclar compilación y despliegue en el mismo paso.** Se separan para poder repetir el despliegue sin recompilar y para saber qué artefacto exacto se publicó.

## La puerta de entrada

El pipeline solo sirve si frena algo. La rama principal debe exigir que los checks pasen antes de hacer merge, con revisión y sin push directo. Un pipeline que se ejecuta pero no bloquea es un panel informativo.

El orden razonable para un cambio: rama corta, pull request, pipeline en verde, revisión, merge con squash. Las pruebas que fallan en la rama se arreglan antes de hacer merge; no se posponen a un commit posterior.

La integración continua no sustituye a las pruebas bien escritas. Solo garantiza que se ejecutan en un entorno honesto. Si la suite es lenta, frágil o no comprueba nada, automatizarla únicamente hace que el problema sea más visible.
