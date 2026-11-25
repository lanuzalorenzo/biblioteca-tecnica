# Standalone frente a NgModule

Durante años, un componente no existía por sí solo: había que declararlo en un `NgModule`, importar allí lo que necesitaba y exportarlo si otro módulo quería usarlo. Ese modelo ordenaba la aplicación, pero añadía un archivo y una indirección por cada pieza. Los componentes standalone eliminan esa capa: un componente declara sus propias dependencias y se importa donde se usa. NgModule sigue existiendo y sigue siendo válido, sobre todo en código antiguo y en bibliotecas, pero ya no es la unidad por defecto.

## Qué resolvía el módulo

Un `NgModule` es una clase decorada con `@NgModule` que agrupa piezas y declara su visibilidad:

```typescript
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';

import { AppComponent } from './app.component';
import { TarjetaUsuarioComponent } from './usuarios/tarjeta-usuario.component';
import { ResumenPipe } from './usuarios/resumen.pipe';

@NgModule({
  declarations: [AppComponent, TarjetaUsuarioComponent, ResumenPipe],
  imports: [BrowserModule, FormsModule],
  exports: [TarjetaUsuarioComponent, ResumenPipe],
  providers: [],
  bootstrap: [AppComponent],
})
export class AppModule {}
```

Cada propiedad tiene una función:

- **`declarations`**: componentes, directivas y tuberías que pertenecen a ese módulo. Un elemento solo puede declararse en uno.
- **`imports`**: módulos cuyas piezas exportadas quedan disponibles para las declaraciones propias.
- **`exports`**: lo que el módulo ofrece a quien lo importe. Un componente declarado y no exportado es privado del módulo.
- **`providers`**: servicios e inyección de dependencias con alcance de módulo.
- **`bootstrap`**: componente raíz que arranca al cargar la aplicación.

El problema aparece con el tamaño. Un componente reutilizable obliga a declararlo, exportarlo desde su módulo, importar ese módulo en el consumidor y repetir el ciclo si se mueve. Además, saber qué puede usar una plantilla exige mirar dos archivos: el componente y el módulo que lo contiene. Los módulos de funcionalidad, los módulos compartidos y el módulo raíz acaban formando una red que hay que mantener a mano.

## El componente standalone

Un componente standalone declara en su propio decorador lo que su plantilla necesita:

```typescript
import { Component } from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-tarjeta-usuario',
  imports: [DatePipe, FormsModule],
  templateUrl: './tarjeta-usuario.component.html',
  styleUrl: './tarjeta-usuario.component.css',
})
export class TarjetaUsuarioComponent {
  nombre = 'Ana';
  alta = new Date('2024-03-01');
}
```

La propiedad `imports` sustituye a la suma de módulos del contexto. `DatePipe` se importa porque la plantilla lo usa; `FormsModule` se importa porque hay un `[(ngModel)]`. Si mañana la plantilla deja de usar el formulario, se puede quitar el import y el build lo nota. La dependencia queda a la vista y el componente se puede copiar a otro proyecto con sus imports.

Desde Angular 19, `standalone` es el valor por defecto y no hace falta escribir `standalone: true`. En versiones anteriores había que declararlo explícitamente. Un componente standalone **no se declara** en `declarations`; se importa en el `imports` de otro componente o se registra en una ruta.

## Arranque sin módulo

El punto de entrada de una aplicación standalone es `main.ts`:

```typescript
import { bootstrapApplication } from '@angular/platform-browser';
import { App } from './app/app';
import { appConfig } from './app/app.config';

bootstrapApplication(App, appConfig).catch((error) =>
  console.error(error),
);
```

`appConfig` reúne los providers globales:

```typescript
import { ApplicationConfig } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withFetch } from '@angular/common/http';
import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(withFetch()),
  ],
};
```

Cada `provide...` registra una pieza del marco. `provideRouter` sustituye a `RouterModule.forRoot`, `provideHttpClient` sustituye a `HttpClientModule` y las variantes con `with...` añaden comportamiento: `withFetch()` usa la API Fetch como transporte, `withInterceptors(...)` registra interceptores funcionales, `withComponentInputBinding()` enlaza parámetros de ruta con entradas de componente.

El componente raíz se importa directamente en `bootstrapApplication`. No hay un `AppModule` que lo declare y lo arranque.

## Rutas sin módulo

Una ruta puede apuntar a un componente importado de forma estática o cargarlo bajo demanda:

```typescript
import { Routes } from '@angular/router';
import { InicioComponent } from './inicio/inicio.component';

export const routes: Routes = [
  { path: '', component: InicioComponent },
  {
    path: 'cuenta',
    loadComponent: () =>
      import('./cuenta/cuenta.component').then((m) => m.CuentaComponent),
  },
  {
    path: 'informes',
    loadChildren: () =>
      import('./informes/informes.routes').then((m) => m.INFORMES_ROUTES),
  },
  { path: '**', loadComponent: () => import('./no-encontrado/no-encontrado.component').then((m) => m.NoEncontradoComponent) },
];
```

`loadComponent` carga un componente suelto; `loadChildren` carga un conjunto de rutas hijas, que a su vez pueden vivir en su propio archivo. En ambos casos el bundler genera un fragmento aparte y la primera carga no incluye ese código.

## Cuándo sigue teniendo sentido un NgModule

NgModule no está obsoleto. Sigue siendo la forma de publicar muchas bibliotecas y aparece en aplicaciones que empezaron antes del cambio. También puede ser útil como frontera organizativa en equipos grandes, aunque la misma frontera se consigue con carpetas, rutas y providers.

Los casos habituales:

- **Bibliotecas con API de módulo.** Muchas exponen `MiBibliotecaModule.forRoot()` y componentes declarados dentro. Se importan tal cual.
- **Aplicaciones existentes.** Migrar todo de golpe no aporta valor si el código funciona. Se migra por partes.
- **Interoperabilidad.** Un componente standalone puede importar un NgModule; un NgModule puede importar componentes standalone en su `imports`. La convivencia es posible y no exige reescribir ambos lados.

Lo que no se puede hacer es declarar un componente standalone en `declarations`: el compilador lo rechaza. Se importa donde se usa.

## Tabla de decisión

| Necesidad | Standalone | NgModule |
|---|---|---|
| Componente nuevo en una aplicación actual | Sí, por defecto | No hace falta |
| Biblioteca que ya expone un módulo | Se importa el módulo | Se conserva |
| Dependencias de una plantilla | `imports` del componente | `imports` del módulo |
| Arranque | `bootstrapApplication` | `platformBrowserDynamic().bootstrapModule` |
| Rutas principales | `provideRouter` | `RouterModule.forRoot` |
| Rutas hijas | `loadChildren` con rutas | `RouterModule.forChild` |
| Servicio global | `providedIn: 'root'` o `provide...` | `providers` del módulo raíz |
| Visibilidad de una pieza | Se importa donde se usa | `exports` del módulo |

## Migrar sin romper

El cambio se hace de abajo arriba. Primero se convierten los componentes hoja, que no dependen de nada interno; después los contenedores; al final se sustituye el arranque por `bootstrapApplication` y se retira el módulo raíz. La CLI incluye esquemas de migración que añaden `imports`, quitan `standalone: true` cuando ya es el valor por defecto y convierten rutas. El resultado se revisa: una migración automática no decide si un servicio debe ser global o de componente.

Durante la transición conviven ambos modelos. La regla práctica es no crear un módulo nuevo para código nuevo y no borrar un módulo que aún presta un servicio o una configuración difícil de mover. La arquitectura no gana nada por eliminar un archivo si el reemplazo introduce un provider duplicado.

## Errores frecuentes

- **Importar `CommonModule` por costumbre.** Los bloques `@if` y `@for` no lo necesitan; las tuberías sí se importan una a una. Añadirlo sin uso solo engorda el componente.
- **Poner un servicio en los `providers` de un componente sin querer.** Eso crea una instancia por componente, no una compartida. Si el estado debe ser único, va en la raíz.
- **Registrar dos veces la misma ruta.** Un `provideRouter` en el arranque y otro en una ruta hija compiten. Las rutas hijas se declaran con `children` o con `loadChildren`, no con un segundo `forRoot`.
- **Suponer que un componente standalone es global.** No lo es: hay que importarlo en cada componente que use su selector.
- **Mezclar el arranque de ambos modelos.** `bootstrapApplication` y `bootstrapModule` no se usan a la vez en la misma aplicación.

## Cómo se reconoce un proyecto coherente

Un proyecto standalone bien organizado tiene un `main.ts` corto, un `app.config.ts` con los providers globales y componentes que declaran solo lo que usan. Si aparece un `AppModule` vacío, un módulo `SharedModule` que exporta todo y componentes que importan veinte cosas para usar una, la migración se hizo por cumplir el trámite y no por reducir dependencias. El objetivo no es tener cero módulos: es que cada pieza diga lo que necesita sin obligar a mirar tres archivos.
