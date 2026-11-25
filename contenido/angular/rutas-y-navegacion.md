# Rutas y navegación

Una SPA necesita una correspondencia entre la dirección del navegador y lo que se muestra. El enrutador de Angular mantiene esa tabla, escucha los cambios de URL, carga el componente que toca y deja el resto de la interfaz intacta. También decide qué ocurre cuando la ruta no existe, cuándo se puede entrar y qué datos hay que tener antes de pintar.

## Configurar el enrutador

Las rutas se declaran en un archivo de rutas y se registran con `provideRouter`:

```typescript
import { Routes } from '@angular/router';
import { InicioComponent } from './inicio/inicio.component';

export const routes: Routes = [
  { path: '', component: InicioComponent, title: 'Inicio' },
  { path: 'cuenta', loadComponent: () => import('./cuenta/cuenta.component').then((m) => m.CuentaComponent), title: 'Cuenta' },
  { path: '**', loadComponent: () => import('./no-encontrado/no-encontrado.component').then((m) => m.NoEncontradoComponent), title: 'No encontrado' },
];
```

```typescript
import { ApplicationConfig } from '@angular/core';
import { provideRouter, withComponentInputBinding, withInMemoryScrolling } from '@angular/router';
import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(
      routes,
      withComponentInputBinding(),
      withInMemoryScrolling({ scrollPositionRestoration: 'enabled' }),
    ),
  ],
};
```

`provideRouter` sustituye a `RouterModule.forRoot` en una aplicación standalone. `withComponentInputBinding` enlaza los parámetros de ruta con entradas del componente; `withInMemoryScrolling` restaura la posición al volver atrás o hacer scroll al inicio al navegar.

La aplicación necesita una base para construir las URL. La CLI añade `<base href="/">` en `index.html`. Si se publica en una subcarpeta, ese valor debe reflejarla o el enrutador generará direcciones incorrectas. La estrategia por defecto usa la API de historial (`/cuenta`); la estrategia hash (`/#/cuenta`) evita configurar el servidor, a costa de una URL menos limpia.

## La tabla de rutas

Cada ruta es un objeto con una propiedad `path` y un destino:

```typescript
const routes: Routes = [
  { path: '', redirectTo: 'inicio', pathMatch: 'full' },
  { path: 'inicio', component: InicioComponent },
  { path: 'autores/:id', component: AutorComponent },
  { path: 'autores/:id/libros', component: LibrosAutorComponent },
  { path: '**', component: NoEncontradoComponent },
];
```

- **`path`** es el patrón. Una cadena vacía representa la raíz; `:id` captura un segmento; `**` captura cualquier cosa que no haya encajado antes.
- **`component`** carga un componente ya importado.
- **`loadComponent`** lo carga bajo demanda y genera un fragmento aparte.
- **`redirectTo`** redirige; con `pathMatch: 'full'` solo cuando la URL coincide entera, no cuando empieza por ese path.
- **`children`** declara rutas hijas que se pintan dentro del componente padre.
- **`title`** fija el título del documento.
- **`data`** transporta datos estáticos o resueltos.
- **`canActivate`**, **`canDeactivate`**, **`canMatch`** y **`resolve`** añaden comprobaciones y datos previos.

El orden importa. Angular recorre la tabla de arriba abajo y se queda con la primera coincidencia, así que `**` va al final. Una ruta con `path: ''` y `pathMatch: 'full'` no debe quedar después de una ruta hija que también empiece por la raíz.

## Navegar desde la plantilla

```html
<nav>
  <a routerLink="/inicio" routerLinkActive="activo" [routerLinkActiveOptions]="{ exact: true }">
    Inicio
  </a>
  <a routerLink="/autores" routerLinkActive="activo">Autores</a>
</nav>

<router-outlet />
```

`routerLink` genera la URL a partir de la definición, de modo que cambiar el patrón no obliga a buscar enlaces a mano. `routerLinkActive` añade una clase cuando la ruta está activa; sin `exact`, `/autores` también se marca activa en `/autores/7`. `RouterOutlet` es el hueco donde se inserta el componente de la ruta.

Los enlaces relativos se construyen con una ruta relativa:

```html
<a [routerLink]="['../']">Volver</a>
```

Desde la clase se navega con `Router`:

```typescript
import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';

@Component({ /* ... */ })
export class AutorComponent {
  private readonly router = inject(Router);

  abrir(id: number): void {
    this.router.navigate(['/autores', id]);
  }

  abrirConFiltro(id: number): void {
    this.router.navigate(['/autores', id], {
      queryParams: { tab: 'libros' },
      fragment: 'titulo',
    });
  }
}
```

`navigate` recibe un array de segmentos; `navigateByUrl` recibe una URL completa. Para volver atrás está `Location.back()`, que usa el historial del navegador.

## Leer los parámetros

Una ruta como `autores/:id` recibe el valor en `ActivatedRoute`. Hay dos formas de leerlo, y la diferencia importa cuando se navega entre dos URL que usan el mismo componente.

### Snapshot

```typescript
import { Component, OnInit, inject } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

@Component({ /* ... */ })
export class AutorComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  id = '';

  ngOnInit(): void {
    this.id = this.route.snapshot.paramMap.get('id') ?? '';
    this.cargar(this.id);
  }

  private cargar(id: string): void { /* ... */ }
}
```

`snapshot` es una foto del estado en ese instante. Sirve si el componente se destruye y se crea en cada navegación. Si se pasa de `/autores/1` a `/autores/2`, Angular reutiliza el mismo componente y **no vuelve a ejecutar `ngOnInit`**: el snapshot se queda con el valor viejo.

### Observable

```typescript
import { Component, DestroyRef, inject, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

@Component({ /* ... */ })
export class AutorComponent implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly destroyRef = inject(DestroyRef);
  id = '';

  ngOnInit(): void {
    this.route.paramMap
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe((params) => {
        this.id = params.get('id') ?? '';
        this.cargar(this.id);
      });
  }

  private cargar(id: string): void { /* ... */ }
}
```

`paramMap` emite cada vez que cambian los parámetros. `takeUntilDestroyed` cancela la suscripción al destruir el componente. También se puede convertir en señal:

```typescript
import { toSignal } from '@angular/core/rxjs-interop';

readonly id = toSignal(this.route.paramMap.pipe(map((p) => p.get('id') ?? '')));
```

Con `withComponentInputBinding`, el parámetro llega como entrada y el problema desaparece:

```typescript
import { input } from '@angular/core';

readonly id = input.required<string>();
```

Angular actualiza la entrada cuando cambia el parámetro, aunque reutilice el componente.

### Consulta, matriz y fragmento

No todos los parámetros van en el path:

- **De consulta:** `?tab=libros&page=2`, se leen con `queryParamMap`.
- **Matriz:** `autores/7;vista=compacta`, se declaran en el segmento y se leen con `paramMap`.
- **Fragmento:** `#comentarios`, se lee con `fragment`.

```typescript
this.route.queryParamMap.subscribe((params) => {
  this.tab = params.get('tab') ?? 'resumen';
});
```

Para navegar con parámetros opcionales de matriz:

```typescript
this.router.navigate(['/autores', { id: 7, vista: 'compacta' }]);
```

La URL resultante es `/autores;id=7;vista=compacta`. Es útil cuando el parámetro forma parte de la identidad del recurso, pero para filtros y paginación se prefieren los parámetros de consulta: son los que espera cualquier analítica y cualquier enlace compartido.

## Rutas hijas y varios outlets

Una ruta hija se pinta dentro del componente padre, no en el outlet raíz. El padre conserva su cabecera y su estructura; solo cambia la zona interior.

```typescript
const routes: Routes = [
  {
    path: 'cuenta',
    component: CuentaComponent,
    children: [
      { path: '', redirectTo: 'perfil', pathMatch: 'full' },
      { path: 'perfil', component: PerfilComponent },
      { path: 'facturas', component: FacturasComponent },
    ],
  },
];
```

```html
<!-- cuenta.component.html -->
<h1>Mi cuenta</h1>
<nav>
  <a routerLink="perfil" routerLinkActive="activo">Perfil</a>
  <a routerLink="facturas" routerLinkActive="activo">Facturas</a>
</nav>
<router-outlet />
```

Las URL resultantes son `/cuenta/perfil` y `/cuenta/facturas`. El `router-outlet` de `CuentaComponent` es distinto del raíz; cada nivel de rutas tiene el suyo. Sin `children`, se podría declarar cada URL por separado, pero se perdería la parte común y se duplicaría la lógica que no cambia.

Los outlets con nombre permiten pintar varias zonas a la vez:

```html
<router-outlet />
<router-outlet name="lateral" />
```

```typescript
{ path: 'ayuda', outlet: 'lateral', component: AyudaComponent }
```

No es una función que se necesite a diario; complica las URL y la lectura. Se usa cuando la interfaz tiene paneles independientes que cambian por separado.

## Carga bajo demanda

Cargar toda la aplicación al inicio hace crecer el primer paquete. Las rutas permiten dividir por funcionalidad:

```typescript
{
  path: 'informes',
  loadChildren: () =>
    import('./informes/informes.routes').then((m) => m.INFORMES_ROUTES),
}
```

```typescript
// informes.routes.ts
import { Routes } from '@angular/router';

export const INFORMES_ROUTES: Routes = [
  { path: '', loadComponent: () => import('./lista-informes.component').then((m) => m.ListaInformesComponent) },
  { path: ':id', loadComponent: () => import('./detalle-informe.component').then((m) => m.DetalleInformeComponent) },
];
```

El bundler crea un fragmento por cada import dinámico. La ruta no descarga ese código hasta que se visita. Para que la navegación posterior sea instantánea se puede precargar en segundo plano:

```typescript
provideRouter(routes, withPreloading(PreloadAllModules));
```

La precarga no reduce el paquete inicial, pero aprovecha el tiempo muerto. En conexiones lentas o dispositivos modestos, conviene medir antes de activarla para todo.

## Guardias funcionales

Una guardia decide si se puede entrar, salir o cargar una ruta. La forma actual es una función que usa `inject` y devuelve un booleano o un `UrlTree`:

```typescript
import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { SesionService } from './sesion.service';

export const sesionGuard: CanActivateFn = () => {
  const sesion = inject(SesionService);
  const router = inject(Router);

  return sesion.activa()
    ? true
    : router.createUrlTree(['/entrar'], { queryParams: { volver: router.url } });
};
```

```typescript
{ path: 'cuenta', component: CuentaComponent, canActivate: [sesionGuard] }
```

Devolver un `UrlTree` redirige sin lanzar una navegación adicional. Devolver `false` cancela la navegación y deja la URL anterior. Una guardia también puede devolver una promesa u observable; el enrutador espera el resultado.

Otros tipos:

- **`CanDeactivateFn`** impide salir de una ruta con cambios sin guardar.
- **`CanMatchFn`** decide si una ruta es candidata; sirve para variantes de la misma URL según el rol o el entorno.
- **`ResolveFn`** obtiene datos antes de activar la ruta, de modo que el componente recibe el dato ya listo.

```typescript
export const cambiosSinGuardar: CanDeactivateFn<FormularioComponent> = (componente) =>
  componente.formulario.pristine ||
  confirm('Hay cambios sin guardar. ¿Salir igualmente?');
```

```typescript
export const autorResolver: ResolveFn<Autor> = (ruta) =>
  inject(AutoresService).obtener(Number(ruta.paramMap.get('id')));
```

Las guardias se ejecutan de fuera hacia dentro al entrar (`canActivate`, `canMatch`) y de dentro hacia fuera al salir (`canDeactivate`). No son un mecanismo de seguridad: el cliente puede modificarse y las API deben comprobar permisos por su cuenta. Sirven para la experiencia de navegación, no para proteger datos.

## Título y datos de la ruta

```typescript
{
  path: 'autores/:id',
  component: AutorComponent,
  title: 'Autor',
  data: { seccion: 'autores' },
}
```

El título se puede construir con una función o con una estrategia propia que combine el título de la ruta con el nombre de la aplicación. `data` es estático; si el dato depende de una petición, se obtiene con `resolve` o dentro del componente.

El componente lee la ruta con `ActivatedRoute` o, si usa `withComponentInputBinding`, recibe el dato como entrada. La segunda forma reduce el acoplamiento: el componente no sabe que existe una URL, solo recibe un `id`.

## Cuando la ruta no existe

La ruta comodín debe ser la última:

```typescript
{ path: '**', component: NoEncontradoComponent }
```

Un `redirectTo` en el comodín también es válido, pero una página de error explica mejor qué pasó. Si la aplicación está detrás de un servidor, este debe devolver `index.html` para cualquier ruta que no sea un archivo, o al recargar en `/autores/7` recibirá un 404 antes de que Angular arranque.

## Errores que se repiten

- **Olvidar el comodín o ponerlo antes.** Las rutas posteriores nunca se alcanzan.
- **Confiar en `snapshot` al reutilizar el componente.** Al cambiar solo el parámetro, `ngOnInit` no se ejecuta.
- **No cancelar la suscripción a `paramMap`.** Se acumulan peticiones al navegar.
- **Usar `pathMatch: 'prefix'` en una redirección vacía.** Cualquier URL empieza por la raíz y la redirección se come el resto.
- **Poner una guardia y creer que protege el backend.** El cliente no es una frontera de seguridad.
- **Cargar todo de golpe.** Una ruta `loadChildren` bien colocada reduce el paquete inicial sin cambiar la experiencia.

Una tabla de rutas sana se lee de arriba abajo y cuenta una historia: qué es público, qué exige sesión, qué se carga aparte y qué ocurre cuando nada coincide. Si para entenderla hay que abrir cinco archivos y ninguna ruta tiene título, la navegación funciona pero la aplicación no se puede mantener.
