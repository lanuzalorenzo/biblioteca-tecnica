# Cobertura de código

La cobertura mide qué parte del código se ejecutó durante las pruebas. Es una métrica de alcance, no de calidad: dice qué líneas pasaron por el runner, no si sus resultados se comprobaron. Sirve para encontrar huecos, no para certificar una suite.

## Líneas y ramas

La **cobertura de líneas** cuenta las líneas ejecutables que se visitaron al menos una vez. No todas las líneas del archivo cuentan: los `using`, las declaraciones de tipos, los campos y las llaves no son código ejecutable. El denominador son las líneas que el compilador puede ejecutar.

La **cobertura de ramas** cuenta los caminos lógicos recorridos. Un `if`/`else` tiene dos ramas; un `switch` con tres casos y un `default`, cuatro; un operador ternario, dos. Un 100 % de líneas puede convivir con un 50 % de ramas: la línea del `if` se ejecutó, pero solo por el camino verdadero.

```csharp
public static decimal CalcularDescuento(bool esSocio, decimal importe)
{
    if (esSocio)
    {
        return importe * 0.9m;
    }

    return importe;
}
```

Una prueba con `esSocio = true` da 100 % de líneas en el método, pero deja la rama falsa sin recorrer. La cobertura de ramas lo delata.

También cuentan como ramas las expresiones que esconden una decisión:

- El operador ternario `condicion ? a : b`.
- El encadenamiento nulo `objeto?.Metodo()`.
- El `??` y el `??=`.
- El `catch` de una excepción.
- Cada `await`: una `Task` puede completarse o fallar, y la segunda rama rara vez se cubre.

Por eso la cobertura de ramas baja en código asíncrono sin que haya un fallo real. Es una limitación de la métrica, no una señal de alarma automática.

## Medir con Coverlet

Coverlet es la herramienta libre de referencia para .NET. Se integra con `dotnet test` mediante el paquete `coverlet.collector`:

```bash
dotnet add tests/Tienda.Tests package coverlet.collector
dotnet test --collect:"XPlat Code Coverage"
```

El resultado queda en `tests/Tienda.Tests/TestResults/<guid>/coverage.cobertura.xml`. Para convertirlo en un informe navegable se usa ReportGenerator:

```bash
dotnet tool install -g dotnet-reportgenerator-globaltool

reportgenerator \
  -reports:"tests/**/TestResults/**/coverage.cobertura.xml" \
  -targetdir:"coverage" \
  -reporttypes:"Html;TextSummary"
```

El informe HTML permite entrar por ensamblado, clase y método, y ver qué líneas y ramas quedaron sin cubrir. El resumen de texto es útil para publicar una cifra en el pipeline.

## Umbrales

Un umbral convierte la cobertura en una puerta. Con `coverlet.msbuild`:

```bash
dotnet test /p:CollectCoverage=true \
  /p:CoverletOutputFormat=cobertura \
  /p:Threshold=80 \
  /p:ThresholdType=line \
  /p:ThresholdStat=total
```

El build falla si la cobertura total baja de 80. Los umbrales pueden ser por tipo (`line`, `branch`, `method`) y por estadística (`total`, `average`, `minimum`). Un umbral global alto sobre un proyecto con mucho código generado es difícil de cumplir, y por sí solo no dice dónde está el hueco; uno por ensamblado o por carpeta obliga a mirar.

Dos reglas para que el umbral no se convierta en teatro:

1. **No se baja para pasar.** Si la cobertura cae, se añade la prueba que falta o se excluye código que no debería medirse.
2. **No se persigue el 100 %.** Hay código que no se puede probar de forma razonable: el arranque, las migraciones, los adaptadores de infraestructura. Excluirlo explícitamente es más honesto que escribir pruebas vacías.

## Excluir lo que no se mide

Se puede excluir por atributo:

```csharp
[ExcludeFromCodeCoverage]
public static class MigracionesDeArranque { }
```

O por configuración, con un `coverlet.runsettings`:

```xml
<RunSettings>
  <DataCollectionRunSettings>
    <DataCollectors>
      <DataCollector friendlyName="XPlat code coverage">
        <Configuration>
          <ExcludeByAttribute>ExcludeFromCodeCoverage,GeneratedCode</ExcludeByAttribute>
          <ExcludeByFile>**/Migrations/**</ExcludeByFile>
        </Configuration>
      </DataCollector>
    </DataCollectors>
  </DataCollectionRunSettings>
</RunSettings>
```

```bash
dotnet test --settings coverlet.runsettings --collect:"XPlat Code Coverage"
```

Las migraciones generadas, los archivos `*.g.cs`, el código de arranque y los DTO sin lógica son candidatos habituales. La exclusión debe ser visible y revisable; una lista larga de exclusiones suele indicar que se está midiendo el proyecto equivocado.

## Leer el informe

Un informe de cobertura no se lee solo por el porcentaje global. Interesa:

- **Líneas rojas en clases de negocio.** Un cálculo sin cubrir es un caso que nadie probó.
- **Ramas parciales.** La línea se ejecutó, pero no por todos sus caminos. Es el hueco más informativo.
- **Métodos con cobertura cero.** Pueden ser código muerto, una funcionalidad sin pruebas o una exclusión olvidada.
- **Cobertura alta con pruebas débiles.** Muchos `Assert.True(true)` ejecutan líneas sin comprobar nada.

La cobertura no distingue una prueba que afirma el resultado de una que solo llama al método. Esa es su límite estructural.

## Complementos

El **análisis de mutaciones** cubre parte de ese hueco. Stryker.NET introduce cambios pequeños en el código —negar una condición, cambiar un operador, devolver otra constante— y comprueba si alguna prueba falla. Si el mutante sobrevive, la suite ejecutó esa línea pero no la vigilaba. Es más lento que la cobertura y se ejecuta en una etapa aparte, pero mide la fuerza de las aserciones, no su presencia.

```bash
dotnet tool install -g dotnet-stryker
dotnet stryker
```

También ayuda revisar la cobertura por cambio: en una pull request, ¿las líneas nuevas están cubiertas? Un umbral sobre el diff evita que la deuda crezca sin exigir que todo el proyecto llegue a un número.

## Qué cifra tiene sentido

No hay un número universal. Un dominio con reglas fiscales, sanitaria o financiera justifica cobertura alta y pruebas de ramas. Una capa de adaptación con dos líneas por método aporta poco aunque esté al 100 %. Una cifra razonable se negocia por área y se revisa cuando el código cambia.

Lo que no tiene sentido es usar la cobertura como sustituto de la revisión. Un proyecto al 95 % puede tener un fallo grave en el único camino que nadie probó; un proyecto al 60 % puede tener las reglas críticas perfectamente cubiertas. La métrica orienta la conversación; no la cierra.
