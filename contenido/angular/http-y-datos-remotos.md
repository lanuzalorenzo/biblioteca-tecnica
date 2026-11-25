# HTTP y datos remotos

Una aplicación web casi nunca tiene todos los datos que muestra. Los pide a una API, los transforma y los reparte entre componentes. Angular trae un cliente HTTP basado en observables, con tipado, cabeceras, parámetros, interceptores y pruebas. La parte difícil no es enviar la petición, sino decidir qué se hace mientras llega, qué ocurre si falla y quién cancela cuando la pantalla desaparece.

## Configurar el cliente

```typescript
import { ApplicationConfig } from '@angular/core';
import { provideHttpClient, withFetch, withInterceptors } from '@angular/common/http';
import { authInterceptor } from './auth.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(
      withFetch(),
      withInterceptors([authInterceptor]),
    ),
  ],
};
```

`provideHttpClient` registra el servicio y sustituye a `HttpClientModule`, que solo se usa ya en aplicaciones basadas en NgModule. `withFetch()` selecciona la API Fetch como transporte; el cliente también puede funcionar con el transporte basado en `XMLHttpRequest`, según la versión y la configuración. `withInterceptors` añade funciones que ven y modifican cada petición.

El cliente se inyecta donde se usa:

```typescript
import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Usuario {
  id: number;
  nombre: string;
  correo: string;
}

@Injectable({ providedIn: 'root' })
export class UsuariosService {
  private readonly http = inject(HttpClient);
  private readonly base = '/api/usuarios';

  listar(): Observable<Usuario[]> {
    return this.http.get<Usuario[]>(this.base);
  }

  obtener(id: number): Observable<Usuario> {
    return this.http.get<Usuario>(`${this.base}/${id}`);
  }

  crear(usuario: Omit<Usuario, 'id'>): Observable<Usuario> {
    return this.http.post<Usuario>(this.base, usuario);
  }

  actualizar(id: number, cambios: Partial<Usuario>): Observable<Usuario> {
    return this.http.patch<Usuario>(`${this.base}/${id}`, cambios);
  }

  borrar(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}`);
  }
}
```

El genérico describe el cuerpo de la respuesta. No convierte nada: si el servidor devuelve otra forma, el tipo miente. En la frontera conviene validar o mapear a un modelo propio, sobre todo cuando los nombres de campo no coinciden con los de la interfaz.

## Observables fríos

Un observable de `HttpClient` es frío: la petición no sale hasta que alguien se suscribe. Eso permite componerlo antes de lanzarlo y decidir quién lo consume.

```typescript
export class UsuariosComponent {
  private readonly servicio = inject(UsuariosService);
  readonly usuarios = signal<Usuario[]>([]);
  readonly cargando = signal(false);
  readonly error = signal<string | null>(null);

  cargar(): void {
    this.cargando.set(true);
    this.error.set(null);

    this.servicio.listar().subscribe({
      next: (usuarios) => {
        this.usuarios.set(usuarios);
        this.cargando.set(false);
      },
      error: () => {
        this.error.set('No se pudieron cargar los usuarios.');
        this.cargando.set(false);
      },
    });
  }
}
```

En una plantilla se puede dejar que `async` gestione la suscripción y la cancelación:

```html
@if (usuarios$ | async; as usuarios) {
  <ul>
    @for (usuario of usuarios; track usuario.id) {
      <li>{{ usuario.nombre }}</li>
    }
  </ul>
} @else {
  <p>Cargando…</p>
}
```

El pipe `async` se suscribe al montar, se da de baja al destruir y comparte la suscripción si se usa varias veces con la misma referencia. Para llevar el observable a una señal está `toSignal`, que también cancela al destruir el contexto.

## Operadores que se usan de verdad

RxJS no hace falta entero. Con un puñado de operadores se cubre la mayoría de los casos:

```typescript
import { catchError, map, retry, switchMap, tap, throwError } from 'rxjs';

listarConFiltro(texto: string): Observable<Usuario[]> {
  return this.http.get<Usuario[]>(this.base, {
    params: { q: texto },
  }).pipe(
    map((usuarios) => usuarios.filter((u) => u.correo.includes('@'))),
    retry({ count: 2, delay: 800 }),
    catchError((error) => {
      console.error('Error al listar usuarios', error);
      return throwError(() => new Error('No se pudo obtener la lista'));
    }),
  );
}

buscarPorId(id: number): Observable<Usuario> {
  return this.http.get<Usuario>(`${this.base}/${id}`).pipe(
    tap((usuario) => console.debug('Usuario recibido', usuario.id)),
  );
}
```

- **`map`** transforma el valor emitido.
- **`catchError`** intercepta el error y devuelve otro observable o lo relanza.
- **`retry`** repite la petición ante un fallo transitorio. No se aplica a un `POST` que crea un recurso salvo que la operación sea idempotente.
- **`switchMap`** cambia a una petición nueva y cancela la anterior. Es lo correcto al buscar mientras se escribe.
- **`tap`** observa sin cambiar el flujo; útil para trazas, no para mutar el estado que se devuelve.

```typescript
readonly resultados$ = this.busqueda$.pipe(
  debounceTime(300),
  distinctUntilChanged(),
  switchMap((texto) => this.servicio.listarConFiltro(texto)),
);
```

Sin `switchMap`, una respuesta lenta de una búsqueda anterior puede llegar después y pisar la actual. Ese es el fallo clásico de los buscadores con peticiones superpuestas.

## Promesas y el fin de `toPromise`

`HttpClient` devuelve observables. Si el consumidor trabaja con `async`/`await`, se convierte con `firstValueFrom` o `lastValueFrom`:

```typescript
import { firstValueFrom } from 'rxjs';

async cargar(): Promise<void> {
  try {
    const usuarios = await firstValueFrom(this.servicio.listar());
    this.usuarios.set(usuarios);
  } catch {
    this.error.set('No se pudo cargar la lista.');
  }
}
```

`toPromise()` está obsoleto y se ha retirado de las versiones actuales de RxJS. Su reemplazo no es automático: `firstValueFrom` toma el primer valor y `lastValueFrom` espera al último antes de completar. En una petición HTTP ambos coinciden, porque el observable emite una vez y completa; la diferencia importa en flujos con varios valores.

La promesa no se puede cancelar. Si la pantalla se destruye antes de que llegue la respuesta, el `then` se ejecuta igual. Para ese caso, el observable con `takeUntilDestroyed` o el pipe `async` es más seguro.

## Piezas retiradas

- **`@angular/http` y `HttpModule`.** Pertenecen al cliente HTTP anterior y fueron retirados. El reemplazo es `HttpClient` de `@angular/common/http`, que devuelve observables tipados y ya no obliga a convertir la respuesta con `.json()`.
- **`HttpClientModule`.** Sigue existiendo para aplicaciones con NgModule, pero no se registra en una aplicación standalone: allí se usa `provideHttpClient`.
- **`toPromise()`.** Está obsoleto y se ha retirado de las versiones actuales de RxJS. Se sustituye por `firstValueFrom` o `lastValueFrom`.
- **`XSRFStrategy` y `CookieXSRFStrategy`.** Eran los tokens del cliente antiguo. La configuración actual se hace con `withXsrfConfiguration`.

## Cabeceras y parámetros

`HttpHeaders` y `HttpParams` son inmutables: cada `set` devuelve una instancia nueva.

```typescript
import { HttpHeaders, HttpParams } from '@angular/common/http';

const headers = new HttpHeaders({
  'Content-Type': 'application/json',
  'X-Idioma': 'es',
});

const params = new HttpParams()
  .set('pagina', 2)
  .set('tamano', 25)
  .set('orden', 'nombre');

this.http.get<Usuario[]>(this.base, { headers, params });
```

Los parámetros se codifican en la URL. Para un valor que puede repetirse se usa `append`; `set` reemplaza. `HttpParams` no acepta un objeto plano directamente en todas las versiones: se construye con `.set` o con `new HttpParams({ fromObject: { ... } })`.

Opciones de respuesta:

```typescript
// Texto plano en lugar de JSON
this.http.get('/api/informe', { responseType: 'text' });

// Cuerpo y metadatos (estado, cabeceras)
this.http.get<Usuario>(url, { observe: 'response' });

// Descargar un archivo como blob
this.http.get(url, { responseType: 'blob' });
```

El tipo del observable cambia con `responseType` y `observe`. Si se pide `text`, no se puede esperar un objeto JSON; el compilador lo avisa.

## Interceptores

Un interceptor es una función que recibe la petición y el siguiente manejador. Sirve para añadir una cabecera, registrar la llamada, renovar un token o centralizar errores.

```typescript
import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { SesionService } from './sesion.service';

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const sesion = inject(SesionService);
  const token = sesion.token();

  if (!token || !req.url.startsWith('/api/')) {
    return next(req);
  }

  return next(
    req.clone({
      setHeaders: { Authorization: `Bearer ${token}` },
    }),
  );
};
```

```typescript
provideHttpClient(withInterceptors([authInterceptor, trazaInterceptor]))
```

La petición es inmutable: se clona con los cambios y se pasa al siguiente. El orden del array importa; el primero envuelve al segundo. Un interceptor que añade el token a **todas** las URL lo filtra por origen: enviar una credencial a un dominio ajeno es una fuga.

Para interceptores de clase antiguos existe `withInterceptorsFromDi()`. No se mezclan con los funcionales sin motivo; si una biblioteca trae uno de clase, se registra con esa variante.

Un interceptor de errores puede reintentar, redirigir al login o convertir una respuesta de error en un mensaje de dominio. Debe tener cuidado de no interceptar la petición que él mismo genera, o entra en un bucle.

## Cancelar y evitar carreras

```typescript
import { DestroyRef, inject } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';

export class DetalleComponent {
  private readonly destroyRef = inject(DestroyRef);
  private readonly servicio = inject(UsuariosService);

  cargar(id: number): void {
    this.servicio.obtener(id)
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe((usuario) => this.usuario.set(usuario));
  }
}
```

`takeUntilDestroyed` completa la suscripción al destruir el componente, y con ella se cancela la petición si el transporte lo permite. En una búsqueda, `switchMap` resuelve la carrera entre respuestas; en una lista que se recarga, conviene ignorar la respuesta de una petición que ya no corresponde.

## Pruebas sin red

```typescript
import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';

describe('UsuariosService', () => {
  let servicio: UsuariosService;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [UsuariosService, provideHttpClient(), provideHttpClientTesting()],
    });
    servicio = TestBed.inject(UsuariosService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify());

  it('pide la lista y la devuelve', () => {
    servicio.listar().subscribe((usuarios) => {
      expect(usuarios).toHaveLength(1);
    });

    const peticion = http.expectOne('/api/usuarios');
    expect(peticion.request.method).toBe('GET');
    peticion.flush([{ id: 1, nombre: 'Ana', correo: 'ana@ejemplo.com' }]);
  });
});
```

`HttpTestingController` comprueba que la petición se hizo con la URL y el método esperados, y permite responder sin servidor. `verify()` falla si quedó alguna petición sin resolver.

## Errores que se repiten

- **Suscribirse dentro de otro `subscribe`.** Anida peticiones y pierde la cancelación; se usa `switchMap` o `concatMap`.
- **No tratar el error.** Una petición fallida deja la pantalla en “cargando” para siempre.
- **Reintentar un `POST` no idempotente.** Un fallo de red después de crear el recurso puede duplicarlo.
- **Poner el token en todas las peticiones.** Se filtra por origen y por ruta.
- **Confundir CORS con un problema de Angular.** Lo configura el servidor; el cliente no puede saltarse la política del navegador.
- **Guardar la respuesta en el servicio sin política.** Una caché sin invalidación muestra datos viejos y una sin ámbito crece sin límite.

El cliente HTTP no es más que transporte. La calidad está en la frontera: un modelo validado, un error con mensaje, una cancelación a tiempo y una decisión explícita de qué se cachea. Lo demás se escribe casi solo.
