# Data binding

Una plantilla no es un documento estático: muestra valores de la clase y reacciona a lo que hace la persona que usa la aplicación. El mecanismo que conecta ambos lados se llama *data binding*. Angular distingue cuatro formas, y elegir la correcta evita la mitad de los errores de una vista.

| Forma | Sintaxis | Dirección | Ejemplo |
|---|---|---|---|
| Interpolación | `{{ expresion }}` | Clase → vista | `{{ nombre }}` |
| Propiedad | `[propiedad]="expresion"` | Clase → vista | `[disabled]="guardando"` |
| Evento | `(evento)="accion($event)"` | Vista → clase | `(click)="guardar()"` |
| Bidireccional | `[(propiedad)]="valor"` | Ambos sentidos | `[(ngModel)]="nombre"` |

## Interpolación

La doble llave convierte un valor en texto y lo coloca en el HTML:

```typescript
import { Component, signal } from '@angular/core';

@Component({
  selector: 'app-saludo',
  template: `<p>Hola, {{ nombre() }}. Tienes {{ mensajes() }} mensajes.</p>`,
})
export class SaludoComponent {
  readonly nombre = signal('Ana');
  readonly mensajes = signal(3);
}
```

La expresión puede usar operadores y tuberías, pero no asignaciones ni construcciones que creen objetos. `{{ usuario?.nombre }}` evita romper cuando el usuario aún no ha llegado; `{{ total | currency:'EUR' }}` formatea sin modificar el valor original.

El texto se escapa: si `nombre` contiene `<script>`, se muestra como texto, no se ejecuta. Esa protección es una de las razones por las que no se debe construir HTML a mano sin necesidad.

## Propiedad frente a atributo

La sintaxis con corchetes enlaza una **propiedad del DOM**, no un atributo del HTML. La distinción no es académica:

```html
<!-- Mal: el atributo disabled existe, así que el botón queda deshabilitado -->
<button disabled="{{ guardando }}">Guardar</button>

<!-- Bien: se enlaza la propiedad booleana del DOM -->
<button [disabled]="guardando">Guardar</button>
```

En el primer caso, Angular interpola el texto `false` dentro del atributo. El navegador ve un atributo `disabled` presente y deshabilita el botón: el valor del atributo no importa, solo su presencia. En el segundo, Angular asigna `false` a la propiedad `disabled` del elemento, y el botón queda habilitado.

La regla general: se usan propiedades para el comportamiento y atributos solo cuando no existe una propiedad equivalente. Para atributos HTML sin propiedad se usa el prefijo `attr`:

```html
<td [attr.colspan]="columnas">Total</td>
<button [attr.aria-label]="'Cerrar ' + titulo">×</button>
```

Clases y estilos tienen su propia sintaxis:

```html
<div [class.activo]="activo" [class.compacto]="densidad === 'compacta'"></div>
<div [style.width.px]="ancho" [style.background-color]="color"></div>
```

`[class.activo]` añade o quita una clase según un booleano. `[style.width.px]` asigna una unidad concreta. Para muchas clases a la vez se usa `ngClass`; para muchos estilos, `ngStyle`. Cuando coinciden `[style]` y `[style.color]`, Angular aplica el binding más específico (`[style.color]`), no el orden en que se escriben.

## Eventos

Los paréntesis escuchan un evento del elemento o de un componente:

```typescript
@Component({
  selector: 'app-buscador',
  template: `
    <input
      type="search"
      placeholder="Buscar"
      (input)="texto.set($any($event.target).value)"
      (keyup.enter)="buscar()"
    />
    <button type="button" (click)="limpiar($event)">Limpiar</button>
  `,
})
export class BuscadorComponent {
  readonly texto = signal('');

  buscar(): void {
    console.log(this.texto());
  }

  limpiar(evento: MouseEvent): void {
    evento.stopPropagation();
    this.texto.set('');
  }
}
```

`$event` es el objeto del evento. En un `input` es un `Event`; para acceder al valor hay que decirle al compilador qué elemento es, con `$any($event.target).value` o, mejor, con una variable de referencia:

```html
<input #campo type="search" (input)="texto.set(campo.value)" />
```

Los modificadores de teclado se escriben como sufijo: `keyup.enter`, `keyup.escape`, `keydown.control.s`. Angular no implementa `preventDefault` por devolver `false`; si hace falta, se llama explícitamente a `evento.preventDefault()`.

Los eventos personalizados de un componente se escuchan igual que los del DOM:

```html
<app-filtro (buscar)="aplicarFiltro($event)" />
```

`$event` es el valor emitido por la salida, no un evento del navegador.

## Enlace bidireccional

`[(ngModel)]` combina una entrada y una salida:

```html
<input [(ngModel)]="nombre" />
```

Es azúcar para:

```html
<input [ngModel]="nombre" (ngModelChange)="nombre = $event" />
```

`ngModel` pertenece a `FormsModule`, que hay que importar en el componente standalone o en el módulo que lo use. Sin ese import, Angular no reconoce la directiva y la plantilla falla.

El mismo patrón sirve para un componente propio. Con la API actual, `model()` crea la entrada y la salida con el sufijo `Change`:

```typescript
import { Component, model } from '@angular/core';

@Component({
  selector: 'app-paso',
  template: `
    <button type="button" (click)="bajar()">−</button>
    <span>{{ valor() }}</span>
    <button type="button" (click)="subir()">+</button>
  `,
})
export class PasoComponent {
  readonly valor = model(0);

  subir(): void { this.valor.update((v) => v + 1); }
  bajar(): void { this.valor.update((v) => v - 1); }
}
```

```html
<app-paso [(valor)]="cantidad" />
```

Con decoradores, el contrato equivalente es `@Input() valor` y `@Output() valorChange = new EventEmitter<number>()`. El nombre de la salida debe terminar en `Change` para que la sintaxis de doble enlace funcione.

## Padre e hijo

La comunicación tiene dos direcciones y cada una usa una herramienta distinta:

- **Hacia abajo:** el padre pasa datos por una entrada. El hijo no los modifica.
- **Hacia arriba:** el hijo emite un evento; el padre decide qué hacer con él.

```typescript
@Component({
  selector: 'app-lista',
  template: `
    @for (tarea of tareas(); track tarea.id) {
      <app-tarea
        [titulo]="tarea.titulo"
        [hecha]="tarea.hecha"
        (alternar)="alternar(tarea.id, $event)"
      />
    }
  `,
})
export class ListaComponent {
  readonly tareas = signal([
    { id: 1, titulo: 'Preparar informe', hecha: false },
    { id: 2, titulo: 'Revisar correo', hecha: true },
  ]);

  alternar(id: number, hecha: boolean): void {
    this.tareas.update((tareas) =>
      tareas.map((t) => (t.id === id ? { ...t, hecha } : t)),
    );
  }
}
```

El hijo solo sabe emitir; no conoce la lista ni la regla de negocio. El padre conserva el estado y decide cómo cambia. Esa separación permite probar la tarea aislada y cambiar la lista sin tocar la tarjeta.

Cuando el estado compartido crece o varios componentes lejanos lo necesitan, el padre deja de ser el dueño y el estado se mueve a un servicio. Pasar un dato por cinco niveles con entradas y salidas es una señal de que el diseño se quedó corto.

## Señales en la plantilla

Una señal se lee llamándola:

```typescript
import { Component, computed, signal } from '@angular/core';

@Component({
  selector: 'app-carrito',
  template: `
    <p>{{ unidades() }} artículos, {{ total() | currency:'EUR' }}</p>
    <button type="button" (click)="agregar()">Agregar</button>
  `,
})
export class CarritoComponent {
  readonly precios = signal<number[]>([]);
  readonly unidades = computed(() => this.precios().length);
  readonly total = computed(() => this.precios().reduce((a, b) => a + b, 0));

  agregar(): void {
    this.precios.update((precios) => [...precios, 19.9]);
  }
}
```

La vista se actualiza cuando cambia la señal de la que depende. No hace falta llamar a un método que recalcule: `computed` guarda el resultado y solo lo recalcula cuando cambia una dependencia. Un `effect` no se usa para pintar; sirve para efectos secundarios, como guardar una preferencia o sincronizar con una API externa.

## Errores que se repiten

- **Usar interpolación para una propiedad booleana.** El atributo `disabled` se activa con cualquier valor, incluso `"false"`. Se usa `[disabled]`.
- **Enlazar a un atributo que no existe como propiedad.** `[colspan]` no funciona; hay que usar `[attr.colspan]`.
- **Confundir `$event` con el valor del campo.** En un input, `$event.target` es el elemento; el valor está en `.value`. Una referencia `#campo` evita el cast.
- **Llamar a métodos pesados en la plantilla.** Se ejecutan en cada detección de cambios. Se sustituyen por propiedades o `computed`.
- **Mutar el array o el objeto de una entrada.** Con `OnPush`, el padre puede no detectar el cambio. Se crea una copia.
- **Usar `ngModel` sin `FormsModule`.** El error es de plantilla, no de TypeScript, y confunde al principio.

El data binding no tiene misterio si se recuerda la dirección de cada flecha: llaves para mostrar, corchetes para pasar datos, paréntesis para avisar de lo que ocurre y la combinación de ambos solo cuando de verdad se necesita un valor que viaja en los dos sentidos.
