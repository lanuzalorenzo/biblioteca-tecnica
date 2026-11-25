# Directivas y tuberías

Una plantilla tiene dos necesidades que no cubre el HTML: decidir qué fragmentos existen y transformar los valores antes de mostrarlos. Las directivas resuelven lo primero; las tuberías, lo segundo. Las hay incorporadas y también se pueden escribir propias, lo que permite encapsular un comportamiento que se repite en varias vistas.

## Directivas: comportamiento sobre un elemento

Una directiva es una clase con un decorador `@Directive` que se asocia a un elemento o a un fragmento de plantilla. Un componente es una directiva con plantilla propia. Se distinguen tres grupos:

- **De componente:** crean una vista y tienen selector, plantilla y estilos.
- **Estructurales:** añaden, quitan o repiten fragmentos del DOM. Cambian la estructura.
- **De atributo:** modifican la apariencia o el comportamiento de un elemento que ya existe.

## Control de flujo integrado

El Angular actual incluye bloques de plantilla que se escriben directamente en el HTML. No son directivas que haya que importar; el compilador los traduce a instrucciones internas.

### Condiciones

```html
@if (usuario(); as u) {
  <p>Bienvenida, {{ u.nombre }}</p>
} @else if (cargando()) {
  <p>Cargando…</p>
} @else {
  <p>No hay sesión iniciada.</p>
}
```

El bloque `@if` evalúa la expresión y crea el contenido solo cuando es verdadera. La forma `as u` guarda el valor para no repetir la llamada. Al desaparecer la condición, el contenido se destruye: sus componentes se limpian y sus suscripciones se cancelan si están bien atadas al ciclo de vida.

La versión clásica sigue disponible:

```html
<app-aviso *ngIf="hayError; else sinError" />
<ng-template #sinError><p>Todo correcto.</p></ng-template>
```

`*ngIf` es azúcar sobre un `ng-template` con un property binding. Se encuentra en código existente, pero el bloque `@if` se lee mejor y evita importar `NgIf`.

### Repetición

```html
<ul>
  @for (tarea of tareas(); track tarea.id) {
    <li>
      <span>{{ $index + 1 }}.</span>
      {{ tarea.titulo }}
      @if (tarea.hecha) { <strong>(hecha)</strong> }
    </li>
  } @empty {
    <li>No hay tareas.</li>
  }
</ul>
```

`@for` exige `track`, una expresión que identifique cada elemento. Angular la usa para reutilizar los nodos que no cambian y mover solo los que cambian. `track tarea.id` es lo correcto cuando el elemento tiene identificador; `track $index` solo es aceptable en listas estáticas que nunca se reordenan.

Dentro del bloque hay variables de contexto: `$index`, `$first`, `$last`, `$even`, `$odd` y `$count`. El bloque `@empty` cubre la lista vacía.

La versión clásica usa `*ngFor`:

```html
<li *ngFor="let tarea of tareas; trackBy: porId">{{ tarea.titulo }}</li>
```

`trackBy` cumple la misma función que `track`, con una función que recibe índice y elemento.

### Selección

```html
@switch (estado()) {
  @case ('borrador') { <span>Borrador</span> }
  @case ('publicado') { <span>Publicado</span> }
  @default { <span>Desconocido</span> }
}
```

`@switch` compara con `===` y no reutiliza los bloques entre casos. La versión clásica es `[ngSwitch]` con `*ngSwitchCase` y `*ngSwitchDefault`.

### Carga diferida de un fragmento

```html
@defer (on viewport) {
  <app-grafico-pesado />
} @placeholder {
  <p>El gráfico aparecerá al acercarse.</p>
} @loading {
  <p>Cargando gráfico…</p>
}
```

`@defer` separa el código de un fragmento y lo carga cuando se cumple una condición: entra en pantalla, se pulsa un botón, pasa un tiempo o el navegador está libre. Es una herramienta de rendimiento, no una forma de ocultar contenido: si el fragmento es imprescindible para la primera pantalla, diferirlo empeora la experiencia.

## Directivas de atributo incorporadas

`ngClass` y `ngStyle` aplican varias clases o estilos a la vez:

```typescript
@Component({
  selector: 'app-alerta',
  imports: [NgClass, NgStyle],
  template: `
    <div
      [ngClass]="{
        'alerta': true,
        'alerta--error': nivel() === 'error',
        'alerta--aviso': nivel() === 'aviso'
      }"
      [ngStyle]="{ 'border-left-width': grosor() + 'px' }"
    >
      <ng-content />
    </div>
  `,
})
export class AlertaComponent {
  readonly nivel = input<'info' | 'aviso' | 'error'>('info');
  readonly grosor = input(4);
}
```

Para una sola clase o un solo estilo, `[class.nombre]` y `[style.propiedad]` son más directos y no necesitan importar nada. `ngClass` y `ngStyle` ganan cuando la lista es dinámica y larga.

## Una directiva de atributo propia

Un caso típico: resaltar el fondo de un elemento al pasar el ratón. La directiva se aplica como atributo y no crea una vista.

```typescript
import {
  Directive,
  ElementRef,
  HostBinding,
  HostListener,
  inject,
  input,
} from '@angular/core';

@Directive({
  selector: '[appResaltar]',
  standalone: true,
})
export class ResaltarDirective {
  private readonly elemento = inject(ElementRef<HTMLElement>);
  readonly appResaltar = input('rgb(254 240 138)');

  @HostBinding('style.backgroundColor') fondo: string | null = null;

  @HostListener('mouseenter')
  entrar(): void {
    this.fondo = this.appResaltar();
  }

  @HostListener('mouseleave')
  salir(): void {
    this.fondo = null;
  }
}
```

```html
<p appResaltar>Este párrafo se resalta al pasar el ratón.</p>
<p [appResaltar]="'#bfdbfe'">Este usa otro color.</p>
```

El selector entre corchetes indica que se usa como atributo. `inject(ElementRef)` da acceso al elemento anfitrión. `@HostListener` escucha eventos sobre él y `@HostBinding` enlaza una propiedad del anfitrión; ambos pueden sustituirse por la propiedad `host` del decorador:

```typescript
@Directive({
  selector: '[appResaltar]',
  host: {
    '[style.backgroundColor]': 'fondo',
    '(mouseenter)': 'entrar()',
    '(mouseleave)': 'salir()',
  },
})
```

La forma `host` mantiene la configuración junta y evita decoradores adicionales. `@HostListener('document:click')` permite escuchar eventos globales, pero conviene usarlo con cuidado: un listener en el documento sobrevive mientras la directiva exista y puede capturar clics de toda la página.

Para exponer la directiva a la plantilla se usa `exportAs`:

```typescript
@Directive({ selector: '[appResaltar]', exportAs: 'resaltar', standalone: true })
export class ResaltarDirective {
  activo = false;
}
```

```html
<p appResaltar #r="resaltar">{{ r.activo }}</p>
```

## Una directiva estructural propia

Una directiva estructural recibe un `TemplateRef` —el fragmento que envuelve— y un `ViewContainerRef` —el lugar donde se inserta—. El siguiente ejemplo repite el contenido las veces indicadas:

```typescript
import {
  Directive,
  TemplateRef,
  ViewContainerRef,
  effect,
  inject,
  input,
} from '@angular/core';

@Directive({
  selector: '[appRepetir]',
  standalone: true,
})
export class RepetirDirective {
  readonly appRepetir = input(1);
  private readonly plantilla = inject(TemplateRef<unknown>);
  private readonly contenedor = inject(ViewContainerRef);

  constructor() {
    effect(() => {
      const veces = Math.max(0, this.appRepetir());
      this.contenedor.clear();
      for (let i = 0; i < veces; i++) {
        this.contenedor.createEmbeddedView(this.plantilla, { $implicit: i });
      }
    });
  }
}
```

```html
<p *appRepetir="3">Línea repetida</p>
```

El asterisco es la forma corta de envolver el elemento en un `ng-template` y aplicar la directiva al template. Escribir directivas estructurales propias es poco frecuente: los bloques `@if`, `@for` y `@switch` cubren casi todos los casos y están optimizados por el compilador.

## Tuberías: transformar sin tocar el dato

Una tubería recibe un valor, lo transforma y devuelve el resultado para mostrarlo. El dato original no cambia.

```html
<p>{{ precio | currency:'EUR':'symbol':'1.2-2' }}</p>
<p>{{ fecha | date:'dd/MM/yyyy' }}</p>
<p>{{ nombre | titlecase }}</p>
<p>{{ descripcion | slice:0:120 }}…</p>
```

Las tuberías incorporadas más útiles:

| Tubería | Qué hace | Ejemplo |
|---|---|---|
| `date` | Formatea fechas | `{{ hoy \| date:'longDate' }}` |
| `currency` | Formatea moneda | `{{ precio \| currency:'EUR' }}` |
| `number` | Formatea números | `{{ ratio \| number:'1.0-2' }}` |
| `percent` | Formatea porcentajes | `{{ avance \| percent }}` |
| `uppercase` / `lowercase` / `titlecase` | Cambia mayúsculas | `{{ nombre \| titlecase }}` |
| `slice` | Recorta texto o array | `{{ texto \| slice:0:80 }}` |
| `json` | Muestra un objeto para depurar | `{{ datos \| json }}` |
| `async` | Suscribe a un observable o promesa | `{{ datos$ \| async }}` |
| `keyvalue` | Recorre un objeto | `@for (par of mapa \| keyvalue; track par.key)` |

`date`, `currency` y `number` dependen de la configuración regional. Sin registrar los datos de la localidad, el formato por defecto es el inglés estadounidense. Para usar español:

```typescript
import { registerLocaleData } from '@angular/common';
import localeEs from '@angular/common/locales/es';
import { LOCALE_ID, ApplicationConfig } from '@angular/core';

registerLocaleData(localeEs);

export const appConfig: ApplicationConfig = {
  providers: [{ provide: LOCALE_ID, useValue: 'es' }],
};
```

El código de moneda sigue la norma ISO 4217 (`EUR`, `USD`, `MXN`). El formato de `currency` es `currency:'EUR':'symbol':'1.2-2'`: código, visualización (`symbol`, `code` o `narrowSymbol`) y dígitos enteros y decimales.

## Tuberías propias

Una tubería propia encapsula una transformación que se repite. La clase implementa `PipeTransform` y se decora con `@Pipe`:

```typescript
import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'recortar',
  standalone: true,
})
export class RecortarPipe implements PipeTransform {
  transform(
    valor: string | null | undefined,
    maximo = 80,
    sufijo = '…',
  ): string {
    if (!valor) return '';
    if (valor.length <= maximo) return valor;
    return valor.slice(0, maximo).trimEnd() + sufijo;
  }
}
```

```html
<p>{{ noticia.resumen | recortar:120 }}</p>
```

La tubería se importa en el componente que la usa. Es una clase normal, así que su lógica se prueba sin montar la vista:

```typescript
describe('RecortarPipe', () => {
  const pipe = new RecortarPipe();

  it('deja intacto un texto corto', () => {
    expect(pipe.transform('Hola', 10)).toBe('Hola');
  });

  it('recorta y añade puntos suspensivos', () => {
    expect(pipe.transform('abcdefghij', 4)).toBe('abcd…');
  });
});
```

### Puras e impuras

Por defecto, una tubería es **pura**: Angular la vuelve a evaluar cuando cambia la referencia del valor o alguno de sus argumentos. Es lo que se quiere casi siempre.

Una tubería **impura** (`pure: false`) se evalúa en cada ciclo de detección, incluso si la referencia no cambió. Sirve para reaccionar a mutaciones internas, pero es cara:

```typescript
@Pipe({ name: 'filtrar', standalone: true, pure: false })
export class FiltrarPipe implements PipeTransform {
  transform<T>(items: T[], texto: string): T[] {
    // ...
  }
}
```

Filtrar o ordenar una lista grande con una tubería impura obliga a recorrerla en cada ciclo. Es mejor calcular el resultado en la clase con `computed` y pasarlo ya preparado a la plantilla.

## Cuándo usar cada pieza

- **Una condición o un bucle** se escribe con `@if` y `@for`; son parte del lenguaje de plantillas y el compilador los optimiza.
- **Una variación de estilo** se resuelve con `[class.x]` o `[style.x]`; `ngClass` y `ngStyle` cuando son muchas y dinámicas.
- **Un comportamiento reutilizable sobre elementos** se encapsula en una directiva de atributo.
- **Un formato de presentación** se encapsula en una tubería pura.
- **Una regla de negocio o un filtrado costoso** no va en la plantilla: vive en la clase o en un servicio.

La tentación de meter lógica en la vista siempre está ahí. La prueba para saber si algo pertenece a una tubería es sencilla: si la transformación solo depende del valor y de sus argumentos, y no del resto del estado de la aplicación, encaja. Si necesita consultar un servicio, combinar varias fuentes o decidir navegación, no es una tubería.
