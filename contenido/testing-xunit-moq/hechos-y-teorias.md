# Hechos y teorías

xUnit distingue dos formas de declarar una prueba. Un **hecho** es un caso único, sin datos externos. Una **teoría** es el mismo caso ejecutado con varios conjuntos de datos. La diferencia no es de estilo: cambia cómo se descubre la prueba, cómo se informa de un fallo y qué se puede parametrizar.

## Hechos: `[Fact]`

Un hecho se escribe cuando el escenario es uno y los valores están en el cuerpo de la prueba:

```csharp
public static class Validador
{
    public static bool EsPar(int numero) => numero % 2 == 0;
}

public class ValidadorTests
{
    [Fact]
    public void EsPar_DevuelveTrue_CuandoNumeroEs2()
    {
        var resultado = Validador.EsPar(2);

        Assert.True(resultado);
    }

    [Fact]
    public void EsPar_DevuelveFalse_CuandoNumeroEs3()
    {
        var resultado = Validador.EsPar(3);

        Assert.False(resultado);
    }
}
```

Dos hechos para dos caminos es correcto y perfectamente legible. El problema aparece cuando la misma estructura se repite diez, veinte o doscientas veces porque la tabla de entrada tiene doscientos casos.

## Teorías: `[Theory]`

Una teoría declara los parámetros y el cuerpo una sola vez; los datos llegan desde atributos:

```csharp
public class ValidadorTests
{
    [Theory]
    [InlineData(2, true)]
    [InlineData(4, true)]
    [InlineData(3, false)]
    [InlineData(-1, false)]
    public void EsPar_DevuelveLoEsperado(int numero, bool esperado)
    {
        var resultado = Validador.EsPar(numero);

        Assert.Equal(esperado, resultado);
    }
}
```

El orden de los parámetros del método debe coincidir con el orden de los valores de cada `InlineData`. Un desajuste de tipos o de posición no siempre falla al compilar; puede aparecer como una excepción al ejecutar. Por eso el resultado esperado va al final, como convención: deja claro qué se está afirmando.

En el explorador cada fila aparece como una prueba independiente, con sus datos en el nombre. Un fallo señala el caso concreto, no la teoría entera.

### Límites de `InlineData`

`InlineData` admite constantes de compilación: números, cadenas, booleanos, enumeraciones, `null` y arrays de estos. No admite objetos creados con `new` ni valores calculados. Cuando los datos son complejos, hay que recurrir a otra fuente.

## `ClassData`: los datos en una clase

Una clase de datos implementa `IEnumerable<object[]>` y devuelve una fila por caso:

```csharp
public class CasosDeParidad : IEnumerable<object[]>
{
    public IEnumerator<object[]> GetEnumerator()
    {
        yield return new object[] { 2, true };
        yield return new object[] { 4, true };
        yield return new object[] { 3, false };
        yield return new object[] { -1, false };
    }

    IEnumerator IEnumerable.GetEnumerator() => GetEnumerator();
}

public class ValidadorTests
{
    [Theory]
    [ClassData(typeof(CasosDeParidad))]
    public void EsPar_DevuelveLoEsperado(int numero, bool esperado)
    {
        Assert.Equal(esperado, Validador.EsPar(numero));
    }
}
```

El uso de `object[]` pierde el tipado: si una fila pone una cadena donde se espera un entero, el error aparece en ejecución. `TheoryData<T1, T2>` evita esa pérdida y además implementa la interfaz necesaria:

```csharp
public class CasosDeParidad : TheoryData<int, bool>
{
    public CasosDeParidad()
    {
        Add(2, true);
        Add(4, true);
        Add(3, false);
        Add(-1, false);
    }
}
```

Cuando los datos se generan o se leen de un archivo, `ClassData` permite hacerlo, pero conviene recordar que se evalúa al descubrir la prueba, no al ejecutarla. Un archivo que falta o una base de datos que no responde rompe la ejecución antes de que empiece el primer caso.

## `MemberData`: los datos en un miembro

`MemberData` apunta a un miembro estático que devuelve las filas. Sirve cuando los datos ya viven en una clase o cuando se quiere reutilizarlos entre varias teorías:

```csharp
public class ValidadorTests
{
    public static IEnumerable<object[]> Casos =>
        new[]
        {
            new object[] { 2, true },
            new object[] { 4, true },
            new object[] { 3, false },
        };

    [Theory]
    [MemberData(nameof(Casos))]
    public void EsPar_DevuelveLoEsperado(int numero, bool esperado)
    {
        Assert.Equal(esperado, Validador.EsPar(numero));
    }
}
```

El miembro puede ser una propiedad, un campo o un método; debe ser estático y accesible desde la clase de prueba. Un método permite además recibir parámetros desde el atributo, lo que ayuda a compartir un generador entre teorías con configuraciones distintas.

## Un atributo de datos propio

Cuando la misma fuente de datos se repite en varias teorías, se puede encapsular en un atributo que herede de `DataAttribute`:

```csharp
public class CasosDeParidadAttribute : DataAttribute
{
    public override IEnumerable<object[]> GetData(MethodInfo testMethod)
    {
        yield return new object[] { 2, true };
        yield return new object[] { 4, true };
        yield return new object[] { 3, false };
        yield return new object[] { -1, false };
    }
}
```

```csharp
[Theory]
[CasosDeParidad]
public void EsPar_DevuelveLoEsperado(int numero, bool esperado)
{
    Assert.Equal(esperado, Validador.EsPar(numero));
}
```

El atributo puede leer un archivo JSON, consultar una tabla de configuración o generar combinaciones. Dos cautelas: la lectura ocurre en el descubrimiento, y el resultado debe ser estable entre ejecuciones. Un atributo que depende de la hora o de un servicio externo hace que la suite deje de ser reproducible.

## Elegir la forma

| Situación | Herramienta |
|---|---|
| Un caso, valores locales | `[Fact]` |
| Pocos casos, valores constantes | `[InlineData]` |
| Muchos casos, filas tipadas | `TheoryData<T...>` con `[ClassData]` |
| Datos compartidos entre clases | `[MemberData]` |
| Fuente reutilizada con lógica propia | Atributo derivado de `DataAttribute` |

La teoría no sustituye al hecho cuando el caso es único. Tampoco conviene forzar en una tabla casos que necesitan escenarios distintos: si cada fila requiere una preparación diferente, probablemente son pruebas diferentes. La tabla funciona cuando comparten Arrange, Act y Assert, y solo cambian los datos.
