# Formularios

Un formulario recibe datos, los valida y los envía. Angular ofrece dos enfoques para hacerlo: uno guiado por la plantilla, donde el modelo se declara en el HTML, y otro reactivo, donde el modelo se construye en la clase y la plantilla solo se conecta. Ambos usan las mismas reglas de validación del navegador, pero no se organizan igual.

| Criterio | Guiado por plantilla | Reactivo |
|---|---|---|
| Modelo | Se deduce del HTML con `ngModel` | Se declara en la clase |
| Módulo | `FormsModule` | `ReactiveFormsModule` |
| Validaciones | Atributos HTML y directivas | Funciones en el control |
| Pruebas | Requieren montar la vista | Se prueban sin DOM |
| Formularios dinámicos | Costosos | Naturales con `FormArray` |
| Curva inicial | Baja | Media |

La recomendación práctica es usar reactivos en formularios con reglas, campos dinámicos o pruebas; dejar los de plantilla para formularios pequeños y estáticos. Lo importante es no mezclar los dos modelos en el mismo formulario: `ngModel` y `formControlName` sobre el mismo control no se llevan bien.

## Formularios guiados por plantilla

Se importa `FormsModule` y se le da un nombre al formulario:

```typescript
import { Component } from '@angular/core';
import { FormsModule, NgForm } from '@angular/forms';

@Component({
  selector: 'app-alta',
  imports: [FormsModule],
  templateUrl: './alta.component.html',
})
export class AltaComponent {
  modelo = { nombre: '', correo: '', acepta: false };

  guardar(formulario: NgForm): void {
    if (formulario.invalid) return;
    console.log(formulario.value);
  }
}
```

```html
<form #formulario="ngForm" (ngSubmit)="guardar(formulario)">
  <label>
    Nombre
    <input
      name="nombre"
      [(ngModel)]="modelo.nombre"
      required
      minlength="3"
      #nombre="ngModel"
    />
  </label>

  @if (nombre.invalid && (nombre.touched || nombre.dirty)) {
    <p class="error">
      @if (nombre.errors?.['required']) { El nombre es obligatorio. }
      @if (nombre.errors?.['minlength']) { Debe tener al menos 3 caracteres. }
    </p>
  }

  <label>
    Correo
    <input name="correo" type="email" [(ngModel)]="modelo.correo" required email />
  </label>

  <label>
    <input name="acepta" type="checkbox" [(ngModel)]="modelo.acepta" required />
    Acepto las condiciones
  </label>

  <button type="submit" [disabled]="formulario.invalid">Enviar</button>
</form>
```

Cada control con `ngModel` necesita un `name` dentro de un formulario; ese nombre es la clave con la que aparece en `formulario.value`. `#formulario="ngForm"` exporta la directiva del formulario y permite consultar `valid`, `invalid`, `dirty`, `touched` y `value`.

`ngModelGroup` agrupa campos en un objeto anidado:

```html
<div ngModelGroup="direccion">
  <input name="calle" [(ngModel)]="modelo.calle" />
  <input name="ciudad" [(ngModel)]="modelo.ciudad" />
</div>
```

El valor resultante tiene la forma `{ direccion: { calle, ciudad } }`. Es útil para enviar un JSON con la estructura que espera la API.

Las validaciones se declaran con atributos HTML: `required`, `minlength`, `maxlength`, `pattern`, `min`, `max`, `email`. Para una validación propia se escribe una directiva que implemente `Validator` y se registre con `NG_VALIDATORS`; en formularios reactivos basta una función, por eso se prefieren cuando la regla se complica.

## Formularios reactivos

Se importa `ReactiveFormsModule` y se construye el modelo en la clase. `FormBuilder` reduce el ruido:

```typescript
import { Component, inject } from '@angular/core';
import {
  FormBuilder,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';

@Component({
  selector: 'app-alta',
  imports: [ReactiveFormsModule],
  templateUrl: './alta.component.html',
})
export class AltaComponent {
  private readonly fb = inject(FormBuilder);

  readonly formulario = this.fb.nonNullable.group({
    nombre: ['', [Validators.required, Validators.minLength(3)]],
    correo: ['', [Validators.required, Validators.email]],
    acepta: [false, Validators.requiredTrue],
  });

  guardar(): void {
    if (this.formulario.invalid) {
      this.formulario.markAllAsTouched();
      return;
    }

    const datos = this.formulario.getRawValue();
    console.log(datos);
  }
}
```

```html
<form [formGroup]="formulario" (ngSubmit)="guardar()">
  <label>
    Nombre
    <input formControlName="nombre" />
  </label>

  @if (formulario.controls.nombre.touched && formulario.controls.nombre.invalid) {
    <p class="error">El nombre es obligatorio y debe tener al menos 3 caracteres.</p>
  }

  <label>
    Correo
    <input formControlName="correo" type="email" />
  </label>

  <label>
    <input formControlName="acepta" type="checkbox" />
    Acepto las condiciones
  </label>

  <button type="submit">Enviar</button>
</form>
```

`this.fb.nonNullable` hace que los controles tengan un valor inicial no nulo y que el tipo resultante no incluya `null`. `formulario.controls.nombre` está tipado: el compilador conoce los campos y sus valores. `getRawValue()` incluye también los controles deshabilitados; `value` los omite.

La estructura anidada usa `formGroupName`:

```html
<form [formGroup]="formulario">
  <div formGroupName="direccion">
    <input formControlName="calle" />
    <input formControlName="ciudad" />
  </div>
</form>
```

```typescript
readonly formulario = this.fb.nonNullable.group({
  nombre: [''],
  direccion: this.fb.nonNullable.group({
    calle: [''],
    ciudad: [''],
  }),
});
```

## Validaciones

Los validadores incorporados cubren lo común:

```typescript
const formulario = this.fb.nonNullable.group({
  nombre: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(60)]],
  correo: ['', [Validators.required, Validators.email]],
  edad: [18, [Validators.min(18), Validators.max(120)]],
  codigo: ['', [Validators.pattern(/^[A-Z]{3}-\d{4}$/)]],
  web: ['', [Validators.pattern(/^https?:\/\/.+/)]],
});
```

Un validador es una función que recibe un control y devuelve `null` si es válido o un objeto de errores si no:

```typescript
import { AbstractControl, ValidationErrors } from '@angular/forms';

export function sinEspacios(control: AbstractControl): ValidationErrors | null {
  const valor = String(control.value ?? '');
  return valor.trim() === valor ? null : { espacios: true };
}
```

```typescript
nombre: ['', [Validators.required, sinEspacios]]
```

Para comparar dos campos se valida el grupo, no cada control por separado:

```typescript
export function clavesIguales(grupo: AbstractControl): ValidationErrors | null {
  const clave = grupo.get('clave')?.value;
  const repetida = grupo.get('repetirClave')?.value;
  return clave === repetida ? null : { clavesDistintas: true };
}
```

```typescript
readonly formulario = this.fb.nonNullable.group(
  {
    clave: ['', Validators.required],
    repetirClave: ['', Validators.required],
  },
  { validators: clavesIguales },
);
```

El error queda en `formulario.errors?.['clavesDistintas']`, no en un control concreto. La plantilla lo muestra junto al grupo.

### Mostrar errores sin ruido

Un formulario recién abierto no debe estar lleno de mensajes rojos. Se muestra el error cuando el campo se ha tocado o modificado:

```html
@if (formulario.controls.correo.touched && formulario.controls.correo.hasError('email')) {
  <p class="error">El correo no tiene un formato válido.</p>
}
```

`touched` indica que el campo perdió el foco; `dirty`, que su valor cambió. `hasError('email')` es más legible que inspeccionar el objeto de errores. Para formularios largos, `updateOn: 'blur'` evita validar en cada tecla:

```typescript
correo: ['', { validators: [Validators.required, Validators.email], updateOn: 'blur' }]
```

La validación del cliente mejora la experiencia, pero no sustituye a la del servidor. Cualquiera puede enviar una petición sin pasar por el formulario.

## Enviar y reiniciar

```typescript
enviar(): void {
  if (this.formulario.invalid) {
    this.formulario.markAllAsTouched();
    return;
  }

  this.servicio.crear(this.formulario.getRawValue()).subscribe({
    next: () => {
      this.formulario.reset();
    },
    error: () => {
      this.error.set('No se pudo guardar. Inténtalo de nuevo.');
    },
  });
}
```

`reset()` devuelve los controles a su valor inicial y limpia el estado de validación. `reset(valores)` fija otros valores. `patchValue` cambia solo los campos indicados; `setValue` exige el objeto completo y falla si falta una clave.

Mientras la petición está en marcha, el botón se deshabilita y se muestra un estado:

```html
<button type="submit" [disabled]="formulario.invalid || guardando()">
  {{ guardando() ? 'Guardando…' : 'Guardar' }}
</button>
```

## Campos dinámicos

`FormArray` representa una lista de controles. Sirve para teléfonos, líneas de una factura o pasos variables:

```typescript
readonly formulario = this.fb.nonNullable.group({
  nombre: ['', Validators.required],
  telefonos: this.fb.array([this.fb.nonNullable.control('')]),
});

get telefonos() {
  return this.formulario.controls.telefonos;
}

agregarTelefono(): void {
  this.telefonos.push(this.fb.nonNullable.control(''));
}

quitarTelefono(indice: number): void {
  this.telefonos.removeAt(indice);
}
```

```html
<div formArrayName="telefonos">
  @for (control of telefonos.controls; track control; let i = $index) {
    <input [formControlName]="i" placeholder="Teléfono" />
    <button type="button" (click)="quitarTelefono(i)">Quitar</button>
  }
</div>
<button type="button" (click)="agregarTelefono()">Añadir teléfono</button>
```

El `track control` es correcto aquí porque cada control es un objeto estable. Si se usara el índice, al eliminar un elemento se reutilizarían nodos con el estado equivocado.

## Formularios y señales

Los formularios reactivos siguen exponiendo observables (`valueChanges`, `statusChanges`). Se pueden llevar a señales:

```typescript
import { toSignal } from '@angular/core/rxjs-interop';

readonly valor = toSignal(this.formulario.valueChanges, {
  initialValue: this.formulario.getRawValue(),
});
```

Eso permite derivar una vista previa con `computed` sin suscribirse a mano. No conviene convertir todo el formulario en señales y seguir usando `setValue`: se acaba con dos fuentes de verdad. Se elige una dirección y se respeta.

## Errores que se repiten

- **Mezclar `ngModel` y `formControlName`.** Angular avisa o el comportamiento se vuelve imprevisible. Se elige un enfoque por formulario.
- **Olvidar el `name` en un control con `ngModel`.** El control no se registra en el formulario.
- **Mostrar errores desde el primer segundo.** Se usa `touched` o `dirty` para no castigar a quien aún no ha escrito.
- **Confiar solo en la validación del cliente.** El servidor valida otra vez; el cliente solo mejora la experiencia.
- **Usar `setValue` con un objeto parcial.** Falla si falta una clave; para cambios parciales se usa `patchValue`.
- **Validar la contraseña en cada control.** La comparación es una regla del grupo; se valida en el grupo.
- **No limpiar el estado tras enviar.** El formulario conserva `touched` y errores; `reset` devuelve un estado limpio.

Un formulario bien construido tiene un modelo claro, validaciones en un solo sitio y mensajes que dicen qué corregir. El resto —qué módulo se importa, si el modelo vive en la plantilla o en la clase— es una decisión de estilo que debe mantenerse coherente en toda la aplicación.
