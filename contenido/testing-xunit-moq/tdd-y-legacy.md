# TDD y código heredado

El desarrollo guiado por pruebas invierte el orden habitual: primero se escribe la prueba que describe el comportamiento, después el código que la satisface, y por último se limpia. Aplicado con disciplina, convierte los requisitos en una lista de casos ejecutables y mantiene el diseño pequeño. Aplicado como dogma, produce pruebas de relleno y discusiones sobre porcentajes.

## Rojo, verde, azul

Kent Beck formuló el ciclo en tres estados:

1. **Rojo.** Se escribe una prueba para un comportamiento que aún no existe. Falla por la razón correcta: la funcionalidad no está implementada.
2. **Verde.** Se escribe el código mínimo para que pase. No se busca elegancia, se busca confirmar que la prueba mide lo que se cree.
3. **Azul.** Se refactoriza el código y la prueba sin cambiar el comportamiento. La suite sigue en verde.

El paso más olvidado es el primero. Escribir la prueba después del código comprueba lo que ya se hizo, no lo que se necesita. Verla fallar demuestra que la prueba es capaz de detectar el fallo y que el código la satisface por el motivo correcto.

```csharp
// Rojo: la clase aún no existe o no aplica el descuento.
[Fact]
public void AplicarDescuento_RestaElPorcentaje()
{
    var precio = new Precio(100m);

    var rebajado = precio.ConDescuento(0.15m);

    Assert.Equal(85m, rebajado.Importe);
}
```

```csharp
// Verde: lo mínimo para pasar.
public readonly record struct Precio(decimal Importe)
{
    public Precio ConDescuento(decimal porcentaje) =>
        new(Importe * (1 - porcentaje));
}
```

```csharp
// Azul: se añaden validaciones y se ordena el código, con la prueba como red.
public Precio ConDescuento(decimal porcentaje)
{
    if (porcentaje is < 0 or > 1)
        throw new ArgumentOutOfRangeException(nameof(porcentaje));

    return new Precio(decimal.Round(Importe * (1 - porcentaje), 2));
}
```

Las validaciones añadidas piden sus propias pruebas. El ciclo se repite: cada caso nuevo empieza en rojo.

## Qué aporta y qué no

Ventajas reales:

- **Diseño bajo presión de uso.** La prueba es el primer consumidor de la API. Si es incómoda de escribir, la API también lo será para el resto del código.
- **Cobertura con propósito.** Cada prueba nace de un requisito, no de rellenar un informe.
- **Pasos pequeños.** El ciclo obliga a dividir el trabajo en unidades que se pueden verificar en minutos.
- **Regresión gratuita.** Lo que ya funciona queda protegido por las pruebas que lo hicieron nacer.

Límites que conviene reconocer:

- **Interfaces gráficas.** Probar píxeles y gestos es caro y frágil. El TDD rinde en la lógica que hay detrás, no en la capa visual.
- **Servicios distribuidos.** Los terceros se sustituyen por dobles; la prueba no valida el servicio real, solo el contrato que se cree tener.
- **Datos.** Hace falta un volumen conocido y un esquema estable; sin eso, la prueba de integración no es reproducible.
- **Exploración.** Cuando no se sabe qué se quiere construir, escribir la prueba antes fija una decisión prematura. El TDD sirve para implementar lo entendido, no para descubrirlo.
- **Deuda de pruebas.** Una prueba escrita a toda prisa para cumplir el ciclo se queda en la suite y hay que mantenerla como cualquier otro código.

TDD no es sinónimo de buenas pruebas. Una suite lenta, acoplada a la implementación o llena de casos triviales sigue siendo un problema aunque se haya escrito en rojo, verde y azul.

## Cuándo no empezar por la prueba

Hay trabajos donde el coste de la prueba previa supera el beneficio:

- Un prototipo desechable que se va a tirar en una semana.
- Una migración de datos que se valida con una consulta y una muestra.
- Una interfaz de usuario que aún se está diseñando.
- Un cambio de configuración o de infraestructura que se comprueba desplegando.

La decisión no es «TDD sí o no», sino «qué parte de este trabajo tiene comportamiento verificable y merece la pena fijar». Un prototipo puede tener una prueba de la regla de negocio central y nada más.

## Código heredado

El código heredado no se presta al ciclo: no hay pruebas, las clases están acopladas y cualquier cambio puede romper algo invisible. El orden se invierte: primero se captura lo que hace, después se introduce la costura, y solo entonces se puede refactorizar.

**Pruebas de caracterización.** No describen lo que debería hacer el código, sino lo que hace hoy. Se escriben observando la salida real, incluidos los comportamientos extraños. Su función es detectar cambios accidentales, no aprobar el diseño.

```csharp
[Fact]
public void CalcularTotal_ConDatosHistoricos_MantieneElRedondeoActual()
{
    // Valor capturado de la implementación actual, no del requisito.
    var total = FacturaLegacy.Calcular(100m, 0.21m);

    Assert.Equal(121.00m, total);
}
```

Si más adelante se descubre que el redondeo era un error, la prueba cambia junto con la decisión, y queda registrado que el cambio fue deliberado.

**Costuras.** Para probar una clase heredada hay que poder sustituir sus dependencias. Se empieza por la que impide ejecutar la prueba: un `new` de base de datos, una llamada estática, un `HttpClient` construido dentro. Se extrae a un parámetro de constructor o a un método protegido que se pueda sobrescribir. No se reescribe la clase entera.

**Crecer al lado.** La funcionalidad nueva se escribe en una clase nueva, con responsabilidad única y pruebas, y se conecta a la antigua mediante una llamada. La clase vieja se queda como está. Con el tiempo, la parte nueva absorbe más casos y la vieja se vacía. Es el patrón *strangler* aplicado a código, no a servicios.

**Refactorizar solo lo que se toca.** Arreglar la clase de 3.000 líneas porque se ha cambiado un método es una trampa: el diff se vuelve inreviewable y aparecen fallos difíciles de atribuir. Se mejora la parte que el trabajo obliga a tocar y se deja el resto para cuando haya una razón concreta.

## La regla práctica

Antes de escribir una prueba, conviene responder tres preguntas:

1. ¿Qué comportamiento observable se quiere fijar?
2. ¿Qué haría falta para que la prueba falle si ese comportamiento desaparece?
3. ¿Merece la pena el coste de mantenerla?

Si la respuesta a la tercera es no, la prueba no se escribe. Si la segunda no tiene respuesta, la prueba no comprueba nada. Si la primera es vaga, el problema está en el requisito, no en la herramienta.
