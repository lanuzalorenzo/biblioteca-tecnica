# TypeScript aplicado a Angular

TypeScript es JavaScript con un sistema de tipos que se comprueba antes de ejecutar. El navegador nunca ve esos tipos: el compilador los borra y genera JavaScript. Su valor está en el momento de escribir: una función que espera un número y recibe un texto falla en el editor o en el build, no cuando alguien pulsa un botón en producción.

Angular no solo usa TypeScript en las clases; también compila las plantillas con esa información. Un `[disabled]="usuario.activo"` sobre un objeto que no tiene `activo`, o un evento mal escrito, pueden detectarse en la compilación si el modo estricto está activo.

## Lo mínimo que se usa a diario

```typescript
interface Usuario {
  id: number;
  nombre: string;
  correo: string;
  alta: Date;
  activo: boolean;
}

const usuario: Usuario = {
  id: 7,
  nombre: 'Marta',
  correo: 'marta@ejemplo.com',
  alta: new Date('2025-01-15'),
  activo: true,
};

function saludar(nombre: string): string {
  return `Hola, ${nombre}`;
}
```

La inferencia evita repetir tipos obvios: `const total = 0` ya es un número y `const nombres = ['Ana', 'Luis']` ya es `string[]`. El tipo se escribe cuando aclara una frontera: la firma de una función, la forma de un dato que llega de una API o el contrato de un servicio.

`interface` y `type` cubren casos parecidos. `interface` se puede ampliar y es la forma habitual de describir objetos; `type` brilla para uniones, intersecciones y alias:

```typescript
type Estado = 'borrador' | 'publicado' | 'archivado';

type Respuesta<T> =
  | { ok: true; datos: T }
  | { ok: false; error: string };
```

Una unión de literales como `Estado` evita los `enum` en la mayoría de los casos: no genera código en tiempo de ejecución, se serializa tal cual y el compilador comprueba que no se asigne un valor inventado.

## Nulos y opcionales

Con `strictNullChecks`, `null` y `undefined` no son compatibles con cualquier tipo. Esa incomodidad es el objetivo: obliga a decidir qué ocurre cuando un dato no está.

```typescript
interface Usuario {
  id: number;
  nombre: string;
  telefono?: string;        // puede faltar
  segundoApellido: string | null; // existe, pero puede ser nulo
}

function mostrarTelefono(usuario: Usuario): string {
  return usuario.telefono ?? 'Sin teléfono';
}
```

`?.` encadena el acceso sin romper si un tramo es nulo; `??` elige un valor por defecto solo cuando el izquierdo es `null` o `undefined`, a diferencia de `||`, que también sustituye `0` y `''`.

El operador `!` afirma que un valor no es nulo. Se usa cuando el compilador no puede saberlo y la persona que escribe sí:

```typescript
const campo = formulario.get('correo')!;
```

Es una promesa, no una comprobación. Si el campo desaparece, el error salta en ejecución. Conviene reducirlo a los puntos donde la estructura es fija —por ejemplo, un control que se acaba de crear— y no usarlo para silenciar dudas.

## `any` y `unknown`

`any` desactiva la comprobación. Todo cabe, nada se avisa y el error se traslada al navegador. `unknown` acepta cualquier valor, pero obliga a comprobarlo antes de usarlo:

```typescript
function esUsuario(valor: unknown): valor is Usuario {
  return (
    typeof valor === 'object' &&
    valor !== null &&
    'id' in valor &&
    'nombre' in valor
  );
}

function procesar(dato: unknown): string {
  if (!esUsuario(dato)) {
    throw new Error('El dato no tiene forma de usuario');
  }
  return dato.nombre;
}
```

Ese `valor is Usuario` es un predicado de tipo. Sirve para validar la respuesta de una API antes de confiar en ella; el tipo declarado no demuestra que el JSON remoto lo cumpla.

## Genéricos y tipos de utilidad

Un genérico describe una relación entre la entrada y la salida:

```typescript
function primero<T>(lista: readonly T[]): T | undefined {
  return lista[0];
}

const numero = primero([10, 20, 30]); // number | undefined
const nombre = primero(['Ana', 'Luis']); // string | undefined
```

En Angular aparecen por todas partes: `Observable<Usuario[]>`, `Signal<number>`, `WritableSignal<string[]>`, `FormGroup<FormularioAlta>`, `HttpClient.get<Usuario>(url)`. El genérico no cambia lo que ocurre en ejecución; documenta y comprueba qué se transporta.

Los tipos de utilidad recortan o transforman una forma existente:

```typescript
type UsuarioSinId = Omit<Usuario, 'id'>;
type UsuarioParcial = Partial<Usuario>;
type UsuarioPublico = Pick<Usuario, 'id' | 'nombre'>;
type PorId = Record<number, Usuario>;
```

`Partial` es útil para un formulario de edición; `Omit` para separar el dato que se envía del que devuelve el servidor; `Record` para indexar por clave.

## Clases, acceso y decoradores

Las clases de Angular son clases normales con un decorador que añade metadatos. Los modificadores de acceso se usan para expresar la intención:

```typescript
export class Contador {
  private valor = 0;

  get actual(): number {
    return this.valor;
  }

  incrementar(paso = 1): void {
    this.valor += paso;
  }
}
```

`private` es una comprobación del compilador, no una cápsula en tiempo de ejecución. `readonly` impide reasignar la propiedad, aunque no congela el objeto: un array `readonly` no se puede reemplazar, pero sus elementos pueden seguir siendo mutables si el tipo lo permite.

Los decoradores de Angular —`@Component`, `@Injectable`, `@Pipe`, `@Directive`— no se escriben a mano para crear funcionalidad propia; los procesa el compilador. Un `@Injectable()` en un servicio no lo convierte en singleton por sí solo: eso lo decide el inyector y el ámbito donde se registra.

## Tipar la respuesta de una API

El tipo de una respuesta remota es una declaración de intenciones. El servidor puede devolver otra cosa, así que conviene separar el contrato externo del modelo interno:

```typescript
interface UsuarioApi {
  user_id: number;
  full_name: string;
  email: string;
  created_at: string;
}

interface Usuario {
  id: number;
  nombre: string;
  correo: string;
  alta: Date;
}

function aUsuario(dto: UsuarioApi): Usuario {
  return {
    id: dto.user_id,
    nombre: dto.full_name,
    correo: dto.email,
    alta: new Date(dto.created_at),
  };
}
```

La función de conversión es pequeña y se prueba sola. Si el nombre de un campo cambia, el error aparece en un punto, no en cada plantilla que lo usa. En proyectos grandes, la validación en ejecución —con un esquema o comprobaciones explícitas— cubre lo que el tipo no puede: que el JSON remoto cumpla lo prometido.

## Tipos en la plantilla

La compilación de plantillas comprueba que las expresiones encajan con la clase. Hay tres ajustes que conviene conocer en `tsconfig.json`:

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitOverride": true,
    "noPropertyAccessFromIndexSignature": true
  },
  "angularCompilerOptions": {
    "strictTemplates": true,
    "strictInjectionParameters": true
  }
}
```

`strictTemplates` detecta propiedades inexistentes, argumentos de tipo incorrecto y eventos mal tipados. A veces una biblioteca mal tipada obliga a usar `$any(valor)` en la plantilla; es una escape hatch, no una solución. Si aparece muchas veces, el problema está en el tipo de la biblioteca o en la conversión que falta.

`strictInjectionParameters` obliga a que las dependencias inyectadas tengan un tipo utilizable. Sin él, un parámetro sin tipo se convierte en `any` y se pierde la comprobación.

## Promesas, observables y señales

Son tres formas de representar algo que cambia o que llega después, y no se sustituyen entre sí:

- **`Promise<T>`** representa un único resultado futuro. Se resuelve o se rechaza una vez. `async`/`await` la hace legible.
- **`Observable<T>`** representa un flujo: puede emitir cero, uno o muchos valores, y se puede cancelar. Es la pieza central de RxJS y del cliente HTTP de Angular.
- **`Signal<T>`** representa un valor reactivo legible. Se lee llamándolo (`total()`); `computed` deriva y `effect` reacciona.

```typescript
import { signal, computed } from '@angular/core';

const precio = signal(12);
const cantidad = signal(3);
const total = computed(() => precio() * cantidad());
```

Un `Signal` no sustituye a un observable en una petición HTTP, pero puede envolver su último valor con `toSignal`. Del mismo modo, `toObservable` permite llevar una señal a un operador de RxJS. La elección depende de si el problema es un valor actual o un flujo con varios eventos y cancelación.

## Errores de tipo que se repiten

- **Declarar `any` para salir del paso.** El error desaparece del editor y reaparece en ejecución. `unknown` más una comprobación es casi siempre la alternativa.
- **Usar `as` para forzar una respuesta.** `respuesta as Usuario` no convierte nada: solo silencia al compilador. Si el JSON no coincide, el fallo llega más tarde y más lejos.
- **Confundir `readonly` con inmutable.** `readonly` impide reasignar; no impide modificar el contenido de un objeto.
- **Tipar solo la clase y no la plantilla.** Sin `strictTemplates`, un componente puede compilar con una plantilla que usa propiedades inexistentes.
- **Abusar de `!`.** Cada exclamación es una suposición. Si el dato puede faltar de verdad, el tipo debe decirlo.

## Cómo se nota un proyecto bien tipado

Las funciones tienen firmas que se pueden leer sin abrir el cuerpo; los servicios declaran qué devuelven; las respuestas de API se convierten en la frontera; los formularios tienen un tipo; y `any` aparece solo en puntos justificados. El resultado no es un código más largo, sino un código en el que el compilador puede avisar antes de que lo haga la persona que usa la aplicación.
