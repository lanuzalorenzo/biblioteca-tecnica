# Componentes y plantillas

Un componente es la unidad con la que se construye la interfaz. Junta tres cosas: una clase con el estado y el comportamiento, una plantilla que describe lo que se ve y unos estilos que se aplican a esa vista. El decorador `@Component` añade los metadatos que permiten a Angular crear el componente y conectarlo con su selector.

```typescript
import { Component, input, output } from '@angular/core';

@Component({
  selector: 'app-etiqueta-estado',
  template: `
    <span class="etiqueta" [class.activa]="activa()">
      {{ texto() }}
    </span>
    <button type="button" (click)="cambiar.emit(!activa())">
      Cambiar
    </button>
  `,
  styles: `
    .etiqueta { padding: .25rem .5rem; border-radius: .25rem; }
    .activa { background: #d1fae5; }
  `,
})
export class EtiquetaEstadoComponent {
  readonly texto = input.required<string>();
  readonly activa = input(false);
  readonly cambiar = output<boolean>();
}
```

El selector es la etiqueta con la que se usa el componente en otra plantilla:

```html
<app-etiqueta-estado
  texto="Publicado"
  [activa]="estaPublicado"
  (cambiar)="estaPublicado = $event"
/>
```

## Metadatos que importan

- **`selector`**: nombre del elemento. La convención es un prefijo de la aplicación y guiones (`app-`), para no chocar con etiquetas HTML ni con otras bibliotecas.
- **`template` o `templateUrl`**: plantilla en línea o en archivo aparte. Un HTML de varias decenas de líneas se lee mejor en su archivo.
- **`styles` o `styleUrl`**: estilos en línea o en archivo. `styleUrls` acepta varios archivos; `styleUrl` es la forma actual para uno.
- **`imports`**: componentes, directivas, tuberías y módulos que la plantilla necesita. Es la lista de dependencias de la vista.
- **`providers`**: servicios con alcance de este componente y sus hijos. Se usa cuando se quiere una instancia nueva, no la global.
- **`changeDetection`**: estrategia de detección. `OnPush` reduce el trabajo cuando el componente solo cambia por entradas, eventos o señales.

El componente no necesita declararse en ningún sitio si es standalone. Se importa en el componente que lo usa o se registra en una ruta.

## Entradas y salidas

Una entrada recibe datos del padre. Una salida notifica eventos al padre. La forma actual usa funciones:

```typescript
import { Component, input, output, model } from '@angular/core';

@Component({ /* ... */ })
export class FiltroComponent {
  readonly etiqueta = input('Buscar');
  readonly termino = model('');          // entrada y salida a la vez
  readonly buscar = output<string>();

  aplicar(): void {
    this.buscar.emit(this.termino());
  }
}
```

`input.required<T>()` obliga a que el padre pase el valor; `input(valorInicial)` lo hace opcional. `output<T>()` crea un emisor; `model<T>()` crea un enlace bidireccional y se consume con `[(termino)]`.

La forma clásica sigue funcionando y aparece en mucho código:

```typescript
import { Component, Input, Output, EventEmitter } from '@angular/core';

@Component({ /* ... */ })
export class FiltroComponent {
  @Input({ required: true }) etiqueta!: string;
  @Output() buscar = new EventEmitter<string>();

  emitir(texto: string): void {
    this.buscar.emit(texto);
  }
}
```

Las dos formas no se mezclan en la misma propiedad. Las funciones tienen ventajas: el tipo se deduce, el valor se lee como señal y el compilador detecta mejor los usos. Los decoradores siguen siendo necesarios en código antiguo y en algunas integraciones.

Una entrada no se modifica desde el hijo. Si el hijo necesita transformar el dato, lo copia o lo deriva; mutar el objeto recibido produce efectos que el padre no espera y rompe `OnPush`.

## El ciclo de vida

Un componente pasa por estados desde que se crea hasta que se destruye. Angular ofrece hooks para intervenir en cada uno:

| Hook | Cuándo se ejecuta | Uso típico |
|---|---|---|
| `ngOnChanges` | Antes de `ngOnInit` y cada vez que cambia una entrada clásica | Reaccionar a un valor nuevo del padre |
| `ngOnInit` | Una vez, tras la primera comprobación de entradas | Cargar datos iniciales |
| `ngDoCheck` | En cada ciclo de detección | Comprobaciones que Angular no hace solo |
| `ngAfterContentInit` | Tras proyectar el contenido | Acceder a lo que el padre puso dentro |
| `ngAfterContentChecked` | Tras cada comprobación del contenido | Sincronizar con contenido proyectado |
| `ngAfterViewInit` | Tras inicializar la vista y sus hijos | Medir el DOM o inicializar una librería |
| `ngAfterViewChecked` | Tras cada comprobación de la vista | Ajustes que dependen del DOM ya pintado |
| `ngOnDestroy` | Justo antes de destruir | Cancelar suscripciones, temporizadores y listeners |

```typescript
import { Component, OnInit, OnDestroy } from '@angular/core';

@Component({ /* ... */ })
export class RelojComponent implements OnInit, OnDestroy {
  hora = new Date();
  private intervalo?: ReturnType<typeof setInterval>;

  ngOnInit(): void {
    this.intervalo = setInterval(() => (this.hora = new Date()), 1000);
  }

  ngOnDestroy(): void {
    clearInterval(this.intervalo);
  }
}
```

El constructor se usa para recibir dependencias, no para lógica que dependa de entradas: en ese momento las entradas todavía pueden no estar asignadas. `ngOnInit` es el punto de arranque de la lógica de inicialización.

Para efectos sobre el DOM hay alternativas más precisas que `ngAfterViewInit`: `afterNextRender` ejecuta una función una vez que el navegador ha pintado, y `afterRenderEffect` reacciona a cambios de render. `DestroyRef` permite registrar limpieza sin implementar `OnDestroy`:

```typescript
import { Component, DestroyRef, inject } from '@angular/core';

@Component({ /* ... */ })
export class PanelComponent {
  private readonly destroyRef = inject(DestroyRef);

  constructor() {
    const id = setInterval(() => { /* ... */ }, 5000);
    this.destroyRef.onDestroy(() => clearInterval(id));
  }
}
```

## Plantillas: lo que se puede escribir

Una plantilla es HTML con expresiones. Entre llaves se muestra un valor:

```html
<p>Total: {{ total() | currency:'EUR' }}</p>
<p>Cliente: {{ cliente?.nombre ?? 'Sin asignar' }}</p>
```

Las expresiones de plantilla son un subconjunto: no llevan asignaciones, `new`, `++` ni funciones flecha. Se permiten operadores, llamadas a métodos, acceso a propiedades, `?.`, `??` y tuberías. La lógica compleja se queda en la clase; la plantilla decide cómo mostrarla.

Las variables de referencia dan acceso a un elemento o a un componente:

```html
<input #campo type="text" (keyup.enter)="buscar(campo.value)" />
<button type="button" (click)="campo.focus()">Enfocar</button>
```

También se puede obtener una referencia desde la clase con `viewChild`:

```typescript
import { Component, ElementRef, viewChild } from '@angular/core';

@Component({ /* ... */ })
export class BuscadorComponent {
  private readonly campo = viewChild.required<ElementRef<HTMLInputElement>>('campo');

  enfocar(): void {
    this.campo().nativeElement.focus();
  }
}
```

`viewChild` devuelve una señal; el `required` garantiza que la vista tiene la referencia. La forma clásica es `@ViewChild('campo') campo!: ElementRef`.

## Contenido proyectado

Un componente puede recibir HTML entre su etiqueta de apertura y cierre. Ese contenido se coloca con `ng-content`:

```typescript
@Component({
  selector: 'app-panel',
  template: `
    <section class="panel">
      <header><ng-content select="[cabecera]" /></header>
      <div><ng-content /></div>
    </section>
  `,
})
export class PanelComponent {}
```

```html
<app-panel>
  <h2 cabecera>Título del panel</h2>
  <p>Contenido libre.</p>
</app-panel>
```

`select` permite repartir el contenido por huecos. Sin `select`, el `ng-content` recibe todo lo que no haya encajado en otro. El contenido proyectado pertenece al padre: sus estilos y su lógica se evalúan en el contexto de quien lo escribe, no en el del panel.

Para leerlo desde la clase se usan `contentChild` y `contentChildren` (o `@ContentChild`/`@ContentChildren`). Es útil cuando el componente necesita saber qué le han pasado, por ejemplo para coordinarlo.

## Estilos y host

Los estilos del componente se encapsulan por defecto: Angular añade atributos a los elementos para que las reglas no se salgan. El elemento anfitrión se selecciona con `:host`:

```css
:host {
  display: block;
  border: 1px solid #cbd5e1;
}

:host(.destacado) {
  border-color: #2563eb;
}
```

`ViewEncapsulation.None` quita la encapsulación y hace que los estilos sean globales; `ShadowDom` usa el shadow DOM nativo. La opción por defecto, `Emulated`, funciona en todos los navegadores y suele ser la correcta. Cambiarla sin necesidad complica el estilo de los hijos.

## Comunicación y responsabilidad

Un componente de presentación recibe lo que muestra y emite lo que ocurre. Un contenedor inyecta servicios, pide datos y decide qué componente mostrar. Esta división no es una obligación del marco, pero resuelve dos problemas: la vista se puede probar con datos fijos y la lógica de datos no se repite en cada plantilla.

Cuando dos componentes hermanos necesitan hablarse, no se pasan el dato por el padre con una cadena de entradas y salidas. Se mueve el estado a un servicio y ambos lo leen. El árbol de componentes es para la interfaz; el estado compartido no tiene por qué recorrerlo.

## `OnPush` y señales

Con la estrategia `OnPush`, el componente solo se comprueba cuando:

- cambia una entrada por referencia,
- se emite un evento desde su plantilla,
- se marca explícitamente con `markForCheck`,
- cambia una señal de la que depende la vista.

Eso obliga a tratar los datos como inmutables. En lugar de `lista.push(item)`, se crea otra lista: `lista = [...lista, item]`. Con señales, la actualización se hace con `set` o `update`, y la dependencia queda registrada.

```typescript
import { ChangeDetectionStrategy, Component, signal } from '@angular/core';

@Component({
  selector: 'app-contador',
  template: `
    <p>{{ total() }}</p>
    <button type="button" (click)="sumar()">Sumar</button>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ContadorComponent {
  private readonly valor = signal(0);
  readonly total = this.valor.asReadonly();

  sumar(): void {
    this.valor.update((v) => v + 1);
  }
}
```

## Errores que se repiten

- **Lógica de negocio en la plantilla.** Una plantilla con comparaciones, cálculos y llamadas encadenadas no se puede probar y se reevalúa en cada ciclo.
- **Llamar a un método que crea objetos en la plantilla.** `{{ calcular() }}` se ejecuta muchas veces; si devuelve un objeto nuevo, además rompe la comparación. Se usa una propiedad o un `computed`.
- **Mutar una entrada.** El hijo cambia un objeto que no le pertenece y el padre se entera tarde o nunca.
- **Solicitar el DOM antes de que exista.** `ngOnInit` no garantiza que la vista esté pintada; para medir o enfocar se usa `ngAfterViewInit` o `afterNextRender`.
- **Olvidar cancelar.** Un `setInterval` o una suscripción sin limpieza sobrevive al componente y sigue consumiendo.

Un componente bien hecho tiene una responsabilidad clara, una plantilla legible y un contrato de entradas y salidas que se entiende sin abrir la clase. Lo demás —cuántos niveles tiene el árbol, qué componente contiene a cuál— es una decisión de diseño que se toma con el caso delante, no con una receta.
