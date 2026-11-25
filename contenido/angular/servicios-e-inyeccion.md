# Servicios e inyección de dependencias

Un componente debe ocuparse de la vista: mostrar datos, reaccionar a eventos y decidir qué parte de la interfaz se ve. Cuando necesita hablar con una API, guardar una sesión, calcular un total o compartir estado con otra pantalla, esa responsabilidad sale a un servicio. El servicio es una clase normal; lo que la convierte en pieza de Angular es el decorador `@Injectable` y el inyector que la construye y la entrega.

## Un servicio mínimo

```typescript
import { Injectable, computed, signal } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class CarritoService {
  private readonly lineas = signal<Linea[]>([]);
  readonly contenido = this.lineas.asReadonly();
  readonly total = computed(() =>
    this.lineas().reduce((suma, linea) => suma + linea.precio * linea.cantidad, 0),
  );

  agregar(linea: Linea): void {
    this.lineas.update((lineas) => {
      const existente = lineas.find((l) => l.id === linea.id);
      return existente
        ? lineas.map((l) => (l.id === linea.id ? { ...l, cantidad: l.cantidad + 1 } : l))
        : [...lineas, { ...linea, cantidad: 1 }];
    });
  }

  vaciar(): void {
    this.lineas.set([]);
  }
}
```

`providedIn: 'root'` registra el servicio en el inyector raíz y hace que Angular lo elimine del bundle si nadie lo inyecta (*tree shaking*). No hace falta añadirlo a ningún array de providers.

Un servicio no tiene por qué ser global. Si solo lo usa un componente y su estado debe empezar de cero cada vez, se declara en sus `providers`:

```typescript
@Component({
  selector: 'app-editor',
  providers: [BorradorService],
  /* ... */
})
export class EditorComponent {
  private readonly borrador = inject(BorradorService);
}
```

Cada instancia de `EditorComponent` recibe su propio `BorradorService`. Es la diferencia entre un estado compartido y un estado local con nombre.

## Inyección: constructor o `inject`

La forma clásica recibe la dependencia en el constructor:

```typescript
export class AutoresComponent {
  constructor(private readonly autores: AutoresService) {}
}
```

La forma actual usa `inject` en el inicializador de un campo:

```typescript
import { Component, inject } from '@angular/core';

export class AutoresComponent {
  private readonly autores = inject(AutoresService);
}
```

Ambas funcionan. `inject` se lee mejor cuando hay varias dependencias, permite tipar sin modificadores en el constructor y se puede usar en funciones de guardia, resolutores e interceptores. Solo se puede llamar dentro de un contexto de inyección: el constructor, un inicializador de campo o una fábrica de providers. Fuera de ese contexto hay que envolver la llamada con `runInInjectionContext`.

La clase no construye sus dependencias. Esto no es un detalle estético:

```typescript
// Acopla el componente a la implementación y a su constructor.
const servicio = new AutoresService(new HttpClient(...));

// El inyector decide cómo construirla y permite sustituirla en pruebas.
private readonly servicio = inject(AutoresService);
```

La segunda forma permite pasar una implementación falsa en un test, cambiar la configuración en un entorno y compartir la misma instancia entre varios consumidores.

## El inyector es jerárquico

Angular no tiene un único contenedor de dependencias. Tiene un árbol de inyectores:

```
Inyector raíz
  └── Inyector de ruta
        └── Inyector de componente
              └── Inyector de componente hijo
```

Cuando una clase pide una dependencia, Angular la busca en el inyector más cercano y sube hasta encontrarla. Si no existe, lanza un error. Esto explica tres comportamientos:

- Un servicio `providedIn: 'root'` se resuelve en la raíz y es el mismo para toda la aplicación.
- Un servicio declarado en `providers` de un componente crea una instancia nueva para ese componente y sus hijos. Otro componente hermano no la comparte.
- Un módulo cargado bajo demanda crea un inyector hijo. Un servicio declarado en sus `providers` vive ahí y no es visible para el resto.

El ámbito se elige por el ciclo de vida que se quiere, no por comodidad. Si dos pantallas deben ver el mismo carrito, el servicio va en la raíz. Si el formulario de edición debe descartar sus cambios al cerrarse, el servicio va en el componente del formulario.

## Proveedores: cambiar la implementación

Un provider indica al inyector qué construir para un token. El token puede ser una clase o un `InjectionToken`:

```typescript
import { InjectionToken } from '@angular/core';

export interface Configuracion {
  apiUrl: string;
  idioma: string;
}

export const CONFIGURACION = new InjectionToken<Configuracion>('configuración');
```

```typescript
export const appConfig: ApplicationConfig = {
  providers: [
    { provide: CONFIGURACION, useValue: { apiUrl: 'https://api.ejemplo.com', idioma: 'es' } },
  ],
};
```

```typescript
private readonly config = inject(CONFIGURACION);
```

Las variantes de provider:

| Forma | Qué hace |
|---|---|
| `useClass` | Construye una clase distinta para el mismo token |
| `useValue` | Entrega un objeto o valor ya creado |
| `useFactory` | Construye con una función y sus dependencias |
| `useExisting` | Alias: devuelve otra instancia ya registrada |

```typescript
{ provide: AutoresService, useClass: AutoresDePruebaService }
{ provide: CONFIGURACION, useValue: { apiUrl: '/api', idioma: 'es' } }
{ provide: Registro, useFactory: (config: Configuracion) => new Registro(config), deps: [CONFIGURACION] }
{ provide: AutoresService, useExisting: AutoresLocalesService }
```

`useClass` es la base de las pruebas: se registra una implementación falsa sin tocar el componente. `useValue` sirve para configuración y constantes. `useFactory` cuando la construcción depende de otros servicios o del entorno.

Un `InjectionToken` evita usar cadenas como tokens y permite tipar el valor. Es la forma correcta de inyectar configuración que no es una clase.

## Estado compartido con señales

Un servicio puede mantener estado y exponerlo como señales de solo lectura:

```typescript
@Injectable({ providedIn: 'root' })
export class SesionService {
  private readonly usuarioState = signal<Usuario | null>(null);
  readonly usuario = this.usuarioState.asReadonly();
  readonly activa = computed(() => this.usuarioState() !== null);
  readonly inicial = computed(() => this.usuarioState()?.nombre.charAt(0).toUpperCase() ?? '?');

  entrar(usuario: Usuario): void {
    this.usuarioState.set(usuario);
  }

  salir(): void {
    this.usuarioState.set(null);
  }
}
```

Los componentes leen `sesion.activa()` y se actualizan solos cuando cambia. La escritura queda encapsulada en métodos: nadie desde fuera puede hacer `set` sobre el estado interno. Esa es la diferencia entre un servicio que modela una regla y un objeto global que cualquiera modifica.

Con RxJS, el patrón equivalente usa `BehaviorSubject`:

```typescript
private readonly usuarioSubject = new BehaviorSubject<Usuario | null>(null);
readonly usuario$ = this.usuarioSubject.asObservable();
```

`BehaviorSubject` emite el valor actual a quien se suscribe. Las señales son más directas para estado síncrono; los observables siguen siendo mejores para flujos con varios eventos, cancelación y operadores. Se puede convertir uno en otro con `toSignal` y `toObservable`.

## Efectos y límites

`effect` ejecuta una función cuando cambian las señales que lee. Sirve para efectos secundarios: guardar una preferencia, sincronizar con una API del navegador, registrar una traza. No sirve para calcular estado derivado —para eso está `computed`— ni para mantener dos señales sincronizadas a mano, que acaba en bucles y parpadeos.

```typescript
constructor() {
  effect(() => {
    localStorage.setItem('tema', this.tema());
  });
}
```

Los efectos se ejecutan en un contexto de inyección y se destruyen con el servicio o componente que los crea. Si el efecto hace una petición, hay que pensar en la cancelación: un efecto que se dispara con cada tecla y lanza una petición por tecla necesita `switchMap` o una espera, no un `effect` ingenuo.

## Servicios y pruebas

Un servicio con lógica pura se prueba sin Angular:

```typescript
describe('CarritoService', () => {
  it('suma cantidades del mismo producto', () => {
    const carrito = new CarritoService();
    carrito.agregar({ id: 1, nombre: 'Libro', precio: 20 });
    carrito.agregar({ id: 1, nombre: 'Libro', precio: 20 });

    expect(carrito.contenido()).toHaveLength(1);
    expect(carrito.total()).toBe(40);
  });
});
```

Si el servicio inyecta `HttpClient`, se usa `TestBed` con `provideHttpClient()` y `provideHttpClientTesting()`, y se responde con `HttpTestingController`. La prueba comprueba la URL, el método y el cuerpo, no la red real.

## Errores que se repiten

- **Crear servicios con `new`.** Se pierde la inyección, el singleton y la posibilidad de sustituirlos.
- **Poner estado global en un servicio de componente.** Cada componente tiene su copia y los datos se desincronizan.
- **Declarar el mismo servicio en dos módulos.** Cada módulo obtiene una instancia distinta; si debía ser único, va en la raíz.
- **Guardar secretos en el servicio o en el bundle.** El cliente es público; una clave en el código no es un secreto.
- **Sincronizar señales con `effect`.** Se genera un ciclo difícil de seguir; se usa `computed` o se deriva el valor en el momento de leerlo.
- **No limpiar suscripciones.** Un servicio global que se suscribe a un flujo eterno debe cancelar cuando se destruye el ámbito que lo creó.

Un buen servicio tiene un nombre que dice qué regla representa, una API pequeña y un ámbito justificado. Si un servicio acaba con treinta métodos y conoce la plantilla de cinco componentes, ha dejado de ser un servicio y se ha convertido en la aplicación entera dentro de una clase.
