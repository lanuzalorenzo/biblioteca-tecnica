# Por qué probar el código

Una prueba automática es una afirmación ejecutable sobre el comportamiento de un programa. No demuestra que el programa sea correcto, pero sí deja constancia de que un caso concreto funcionaba cuando se escribió y avisa en cuanto deja de hacerlo. Esa diferencia —entre demostrar y vigilar— explica tanto su valor como sus límites.

## El fallo que aparece tarde

Un programa funciona durante meses. Alguien cambia el cálculo de un descuento para un cliente nuevo y la aplicación sigue arrancando, las pantallas siguen abriéndose y el caso nuevo funciona. Lo que se ha roto es el descuento de los clientes antiguos, que nadie vuelve a mirar hasta que llega la primera factura.

Ese fallo tiene dos características que lo hacen caro. La primera es que el cambio que lo provocó no estaba relacionado con el síntoma. La segunda es que aparece lejos del momento en que se introdujo, cuando ya se ha perdido el contexto de lo que se tocó. Una prueba que cubriera el caso antiguo habría fallado en el mismo commit, con el cambio delante y sin necesidad de reconstruir la historia.

Edsger Dijkstra lo resumió en una frase que sigue siendo el mejor contrato del oficio: las pruebas muestran la presencia de errores, no su ausencia. Una suite en verde no certifica un sistema; solo descarta los fallos que alguien se molestó en describir.

## Qué aporta y qué cuesta

Las pruebas se escriben hoy y se cobran mañana. Cuestan código, tiempo de ejecución y mantenimiento; a cambio:

- **Reducen el miedo al cambio.** Refactorizar sin red es reescribir a ciegas. Con pruebas, el compilador avisa de lo que rompe la firma y la suite de lo que rompe el comportamiento.
- **Fijan decisiones.** Una prueba de un caso límite documenta qué se decidió cuando el requisito era ambiguo, y lo hace con un ejemplo que se ejecuta.
- **Localizan el fallo.** Cuando una prueba pequeña falla, el espacio de búsqueda es la unidad que se está probando, no la aplicación entera.
- **Obligan a pensar en el uso.** Escribir la llamada antes que la implementación revela interfaces incómodas, parámetros de más y dependencias ocultas.

El coste también es real. Una prueba mal escrita se convierte en un impuesto: falla por motivos ajenos al código, hay que actualizarla en cada cambio cosmético o depende de la máquina de quien la ejecuta. La calidad de la suite importa más que su cantidad.

## Qué merece una prueba

No todo tiene el mismo rendimiento. Suelen justificar pruebas:

- Las reglas de negocio, especialmente las que tienen ramas, redondeos, fechas o impuestos.
- Los casos límite: listas vacías, cadenas en blanco, cero, negativos, el último elemento, el primer día del mes.
- Los errores esperados: qué excepción se lanza, con qué mensaje y en qué condición.
- Los efectos laterales: qué se guarda, qué se envía, a quién se avisa.
- Los fallos ya corregidos, que vuelven con más frecuencia de la que parece.

No merecen una prueba unitaria los meros accesos a propiedades, los `ToString` generados ni el código de arranque que solo se ejecuta al desplegar. Probar eso añade ruido y no protege ninguna decisión.

## Tipos de prueba y pirámide

Las pruebas de código se agrupan por el alcance que abarcan:

| Tipo | Qué comprueba | Velocidad | Coste de mantenimiento |
|---|---|---|---|
| Unitaria | Una clase o función, con sus dependencias sustituidas | Milisegundos | Bajo |
| Integración | Varias piezas reales: base de datos, HTTP, sistema de archivos | Segundos | Medio |
| Funcional | Un flujo completo desde la entrada hasta el resultado | Segundos o minutos | Alto |
| Extremo a extremo | La aplicación desplegada, a menudo con interfaz | Minutos | Muy alto |

La pirámide de Cohn propone muchas unitarias, menos de integración y pocas funcionales o de extremo a extremo. El motivo es económico: las unitarias son baratas de ejecutar y de cambiar; las de extremo a extremo detectan fallos de integración que las unitarias no ven, pero son lentas y frágiles. Una base ancha de unitarias permite que las pocas pruebas de arriba se dediquen a lo que solo ellas pueden comprobar: el cableado, el enrutado, la configuración y el contrato entre piezas.

La pirámide no es una ley. Un servicio con poca lógica y mucha integración puede necesitar más pruebas de integración que unitarias. Lo que sí es una mala señal es tener cientos de pruebas de interfaz y ninguna de la regla que calcula el precio.

## Diseño que se deja probar

Hay código que no se puede probar sin montar media infraestructura, y casi siempre es por una decisión de diseño, no por la naturaleza del problema. Dos principios de SOLID atacan la raíz:

**Responsabilidad única.** Una clase que genera un documento, le pone la firma y lo envía por correo tiene tres motivos para cambiar y tres razones para fallar. Separarla en tres piezas permite probar cada una con un escenario pequeño.

**Inversión de dependencias.** Una clase no debería construir sus colaboradores complejos; debería recibirlos como abstracciones. Este cambio es el que abre la puerta a sustituirlos en las pruebas:

```csharp
// Difícil de probar: el documento decide cómo se firma y arrastra el servidor.
public class Documento
{
    public string Generar() =>
        _titulo + _cuerpo + new GeneradorFirma().Firma();
}

// Fácil de probar: la firma entra por el constructor.
public class Documento
{
    private readonly IGeneradorFirma _firma;

    public Documento(IGeneradorFirma firma) => _firma = firma;

    public string Generar() => _titulo + _cuerpo + _firma.Firma();
}
```

En la segunda versión, la prueba puede pasar cualquier implementación de `IGeneradorFirma` y no necesita que exista un servidor de firmas. Lo que se gana no es solo comodidad: se ha creado una costura (*seam*), un punto donde el comportamiento se puede sustituir sin tocar la clase.

La inversión de dependencias no consiste en añadir una interfaz a todo. Consiste en no depender de detalles que no controlas: la base de datos, la hora del sistema, el cliente HTTP, el bus de mensajes. Una clase que calcula un total a partir de dos números no necesita interfaces; una que consulta el tipo de cambio, sí.

## Lo que una prueba no arregla

- **No sustituye a un buen diseño.** Se puede mockear una maraña de dependencias y seguir teniendo una maraña. Si una prueba necesita diez dobles para arrancar, el problema está en la clase.
- **No detecta lo que no se le ocurrió a nadie.** Cubre los casos que están escritos; los requisitos olvidados siguen olvidados.
- **No compensa una suite frágil.** Una prueba que falla al azar enseña al equipo a ignorar el rojo, que es peor que no tenerla.
- **No es una métrica de calidad por sí sola.** La cobertura mide líneas ejecutadas, no decisiones verificadas. Se puede tener el 100 % y no comprobar ningún resultado.

La prueba útil es pequeña, determinista y falla por una sola razón. Todo lo demás —herramientas, dobles, cobertura— existe para hacer posible esa definición, no para sustituirla.
