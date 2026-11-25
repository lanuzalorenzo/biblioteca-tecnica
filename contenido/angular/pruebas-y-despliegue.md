# Pruebas y despliegue

Una aplicación Angular se comprueba en varios niveles y se publica como un conjunto de archivos estáticos. Las dos cosas comparten una idea: lo que se ejecuta en producción debe ser el resultado de un proceso repetible, no de pasos manuales que solo una persona conoce.

## Qué se prueba y en qué nivel

| Nivel | Qué comprueba | Herramienta habitual |
|---|---|---|
| Unidad | Una función, una tubería, un servicio sin dependencias | Runner de pruebas |
| Componente | Plantilla, entradas, salidas y estados de la vista | `TestBed` + fixture |
| Integración | Varios componentes, rutas o HTTP simulado | `TestBed`, `HttpTestingController` |
| Extremo a extremo | Un flujo real en un navegador | Playwright, Cypress |

La pirámide no es una ley, pero evita dos extremos: probar cada detalle con el navegador —lento y frágil— o no probar nada porque “el build pasa”. El build demuestra que compila; no demuestra que el botón haga lo que promete.

## El entorno de pruebas

`TestBed` crea un entorno de Angular aislado para cada prueba. Se declara qué se importa y qué se sustituye:

```typescript
import { TestBed } from '@angular/core/testing';
import { ContadorComponent } from './contador.component';

describe('ContadorComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ContadorComponent],
    }).compileComponents();
  });

  it('empieza en cero y suma al pulsar', () => {
    const fixture = TestBed.createComponent(ContadorComponent);
    fixture.detectChanges();

    const boton = fixture.nativeElement.querySelector('button') as HTMLButtonElement;
    expect(fixture.componentInstance.total()).toBe(0);

    boton.click();
    fixture.detectChanges();

    expect(fixture.componentInstance.total()).toBe(1);
  });
});
```

`createComponent` instancia el componente, pero la vista no se renderiza hasta `detectChanges`. En un componente standalone se importa el propio componente; en uno basado en módulos se importa el módulo que lo declara.

Para consultar el DOM se usa `fixture.nativeElement.querySelector` o las utilidades de `@angular/platform-browser/testing`:

```typescript
import { By } from '@angular/platform-browser';

const enlace = fixture.debugElement.query(By.css('a'));
expect(enlace.nativeElement.textContent).toContain('Ver detalle');
```

Las entradas se asignan con `setInput`, que funciona con la API de señales y con la clásica:

```typescript
const fixture = TestBed.createComponent(TarjetaComponent);
fixture.componentRef.setInput('titulo', 'Informe');
fixture.detectChanges();

expect(fixture.nativeElement.textContent).toContain('Informe');
```

Las salidas se comprueban suscribiéndose o espiando el emisor:

```typescript
const emitidos: string[] = [];
fixture.componentInstance.guardar.subscribe((valor) => emitidos.push(valor));

fixture.componentInstance.enviar('nuevo');
expect(emitidos).toEqual(['nuevo']);
```

## Probar servicios

Un servicio con lógica pura no necesita `TestBed`:

```typescript
describe('PrecioService', () => {
  const servicio = new PrecioService();

  it('aplica el descuento sin bajar de cero', () => {
    expect(servicio.conDescuento(100, 0.2)).toBe(80);
    expect(servicio.conDescuento(10, 2)).toBe(0);
  });
});
```

Si el servicio inyecta otro, se sustituye con un doble:

```typescript
const falso = { listar: () => of([{ id: 1, nombre: 'Ana' }]) };

TestBed.configureTestingModule({
  providers: [{ provide: UsuariosService, useValue: falso }],
});

const componente = TestBed.inject(UsuariosService);
```

Para HTTP se usa `provideHttpClientTesting`, como se vio en la nota de datos remotos. La prueba no depende de la red, no es lenta y puede simular errores y tiempos de respuesta.

## Probar rutas

```typescript
import { provideRouter } from '@angular/router';
import { RouterTestingHarness } from '@angular/router/testing';

TestBed.configureTestingModule({
  providers: [provideRouter([
    { path: 'autores/:id', component: AutorComponent },
  ])],
});

const harness = await RouterTestingHarness.create();
const componente = await harness.navigateByUrl('/autores/7', AutorComponent);
expect(componente.id).toBe('7');
```

`RouterTestingHarness` monta la ruta y devuelve el componente activado. Para una guardia se prueba la función directamente, inyectando sus dependencias con `TestBed.runInInjectionContext` o llamándola dentro de un entorno configurado.

## El runner

Durante años el stack de Angular fue Jasmine para escribir y Karma para ejecutar en un navegador. Karma quedó como legado y Angular ha incorporado **Vitest** como runner moderno; los proyectos nuevos pueden generarse con él y la API de `TestBed` se mantiene. En código antiguo es normal encontrar `karma.conf.js`, `jasmine` y el builder de Karma. No es necesario migrar un proyecto que funciona solo por cambiar de runner; sí conviene elegir uno para los nuevos.

La sintaxis de Jasmine (`describe`, `it`, `expect`, `spyOn`) y la de Vitest/Jest (`vi.fn`, `vi.spyOn`) se parecen, pero no son idénticas. Al migrar se revisan los espías, los temporizadores falsos y las utilidades específicas.

Para ejecutar una vez y salir —lo que hace la integración continua— se usa el modo no interactivo del runner:

```bash
ng test --watch=false
```

En Karma se añadía `--browsers=ChromeHeadless`; en Vitest el navegador se sustituye por un entorno DOM simulado o por el modo browser del propio runner. El comando exacto depende de la configuración generada.

## Pruebas de extremo a extremo

Las pruebas E2E abren un navegador y recorren la aplicación como lo haría una persona. Playwright y Cypress son las opciones más extendidas; Protractor, el antiguo runner de Angular, está retirado.

Un flujo crítico típico: entrar, crear un recurso, comprobar que aparece y cerrar sesión. No se prueba cada borde de la interfaz: eso ya lo cubren las pruebas de componente. Se prueba lo que solo falla con la aplicación entera: rutas, cookies, redirecciones, formularios reales y despliegue.

```typescript
// Ejemplo con Playwright
test('crea una tarea y la muestra en la lista', async ({ page }) => {
  await page.goto('/tareas');
  await page.getByLabel('Título').fill('Preparar informe');
  await page.getByRole('button', { name: 'Crear' }).click();

  await expect(page.getByText('Preparar informe')).toBeVisible();
});
```

Los selectores por rol y etiqueta son más estables que los que dependen de clases CSS. Una prueba E2E que se rompe al cambiar un color es una prueba mal escrita.

## Compilar para producción

```bash
ng build
```

El resultado queda en `dist/<proyecto>/browser`. La configuración de producción aplica optimización, minificación, tree shaking, hash en los nombres y presupuestos de tamaño. Los presupuestos se ajustan en `angular.json`; si se superan, el build avisa o falla. Subir el límite sin analizar el bundle solo esconde el problema.

Comandos útiles:

```bash
ng build --configuration development   # build sin optimizar, para depurar
ng build --source-map                  # incluye mapas de código
ng serve --configuration development   # servidor de desarrollo
```

Los mapas de código en producción facilitan depurar pero exponen el código fuente. Se publican solo si el equipo asume esa exposición y los protege detrás de una herramienta de errores; si no, se generan y se guardan como artefacto privado.

## Publicar una SPA

El resultado es estático: HTML, JavaScript, CSS y recursos. Cualquier servidor que entregue archivos puede alojarlo, pero necesita dos configuraciones:

1. **Servir `index.html` para las rutas que no son archivos.** Si se recarga `/autores/7`, el servidor no tiene ese archivo y debe devolver la aplicación para que el enrutador la resuelva. Sin esta regla, la navegación interna funciona y la recarga da 404.
2. **Respetar la base de la aplicación.** Si se publica en `https://ejemplo.com/tienda/`, el `<base href>` debe ser `/tienda/` y el build debe conocer esa base. Si no, los archivos y las rutas se piden en la raíz equivocada.

Las cachés también se configuran:

- `index.html` se sirve sin caché o con una cache muy corta, porque es el punto de entrada y debe apuntar a los archivos nuevos.
- Los archivos con hash en el nombre —`main.abc123.js`— se cachean de forma agresiva e inmutable: si cambia el contenido, cambia el nombre.

Un `Service Worker` puede cachear la aplicación para funcionar sin conexión, pero añade una capa que hay que versionar y limpiar. No se activa por defecto.

## Renderizado en servidor y generación estática

Una SPA sin renderizado en servidor entrega un HTML casi vacío. El contenido aparece cuando se ejecuta JavaScript, lo que perjudica al primer pintado y a los rastreadores que no ejecutan scripts. Angular permite renderizar en el servidor y hidratar después:

```bash
ng add @angular/ssr
ng build
```

El build genera una parte de servidor y otra de navegador. El servidor renderiza el HTML de la ruta, lo envía y el cliente toma el control sin volver a crear el DOM. La hidratación funciona mejor si el HTML del servidor y el del cliente coinciden; un dato que cambia entre ambos produce avisos y repintados.

La generación estática lleva la idea al extremo: se renderizan las rutas conocidas en el build y se publican como HTML. Sirve para documentación, catálogos y páginas que cambian poco. Las rutas con datos por usuario no se prerenderizan.

## Integración continua

Un pipeline mínimo:

```bash
npm ci
ng test --watch=false
ng build
```

`npm ci` instala exactamente lo que fija el lockfile. `ng test` en modo no interactivo comprueba la lógica. `ng build` verifica que la aplicación se puede empaquetar con la configuración de producción. El artefacto de `dist/` se guarda o se publica, no se reconstruye a mano en el servidor.

En el pipeline se añaden las comprobaciones del repositorio: formato, análisis estático con ESLint, auditoría de dependencias y, si hay despliegue, una prueba de humo contra el entorno publicado. Los secretos se guardan en el gestor de secretos del CI, nunca en el repositorio ni en las variables que acaban en el bundle.

## Actualizar Angular

```bash
ng update @angular/core @angular/cli
ng update
```

`ng update` aplica migraciones y avisa de los cambios que requieren intervención. Se actualiza una versión mayor cada vez, se lee la guía de actualización y se ejecutan las pruebas entre pasos. Actualizar Angular y todas las dependencias a la vez convierte un fallo en una incógnita.

## Errores que se repiten

- **Probar solo el “camino feliz”.** Los errores, los estados vacíos y los formularios inválidos son la mitad del comportamiento.
- **Montar la aplicación entera para probar una tubería.** Una función pura se prueba sola.
- **Depender de la red en una prueba unitaria.** Se sustituye con `HttpTestingController`.
- **Usar clases CSS como selectores E2E.** Cambian con el diseño; los roles y las etiquetas no.
- **Olvidar la regla de fallback del servidor.** La aplicación funciona al navegar y falla al recargar.
- **Cachear `index.html`.** El navegador sigue apuntando a archivos que ya no existen.
- **Publicar mapas de código sin decidir.** Se expone el fuente y, a veces, comentarios internos.
- **Subir los presupuestos para que pase el build.** Se pospone una división del bundle que cada vez cuesta más.

Probar y desplegar no son el final del desarrollo: son la forma de saber que lo escrito sigue en pie cuando cambia el entorno. Una prueba que no se ejecuta y un despliegue que solo funciona en la máquina de una persona son dos formas del mismo fallo: el resultado no es reproducible.
