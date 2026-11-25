# Seguridad del cliente

La seguridad de una aplicación web no se resuelve en el navegador. Cualquiera puede modificar el JavaScript, saltarse una guardia o enviar una petición con `curl`. El cliente puede mejorar la experiencia y reducir la superficie de ataque, pero las decisiones que protegen datos —quién puede leer qué, cuánto cuesta una operación, qué se guarda— se toman en el servidor. Dicho eso, hay dos clases de fallo que sí se gestionan, en parte, desde el cliente: la ejecución de código ajeno y el envío de peticiones en nombre de la persona usuaria.

## XSS: ejecutar lo que no debería ejecutarse

Un ataque de *cross-site scripting* introduce código en una página para que se ejecute con el origen de la aplicación. Si el código malicioso se ejecuta, puede leer el DOM, enviar peticiones con la sesión de la víctima y acceder a lo que JavaScript pueda ver.

Angular escapa por defecto los valores que se interpolan:

```html
<p>{{ comentario }}</p>
```

Si `comentario` contiene `<img src=x onerror=alert(1)>`, se muestra como texto. El navegador no lo interpreta como HTML. Esa es la primera defensa y cubre la mayoría de los casos.

El peligro aparece cuando se pide explícitamente interpretar HTML:

```html
<div [innerHTML]="htmlDelUsuario"></div>
```

Angular sanitiza el valor antes de insertarlo: elimina etiquetas y atributos peligrosos, pero conserva el marcado permitido. La sanitización no convierte el HTML en confiable; solo reduce el riesgo. Para contenido generado por la propia aplicación —por ejemplo, un fragmento de una plantilla— se puede desactivar la comprobación con `DomSanitizer`:

```typescript
import { Component, inject } from '@angular/core';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';

@Component({ /* ... */ })
export class AvisoComponent {
  private readonly sanitizer = inject(DomSanitizer);

  readonly html: SafeHtml = this.sanitizer.bypassSecurityTrustHtml(
    '<strong>Aviso:</strong> revisa la configuración.',
  );
}
```

`bypassSecurityTrustHtml` debe recibir contenido que controle el equipo, nunca una cadena que venga de la URL, de un formulario o de una API sin validar. Los métodos de `DomSanitizer` son una promesa de confianza; si esa promesa se rompe, la protección desaparece.

Los contextos que Angular vigila incluyen:

- HTML insertado con `innerHTML` o `outerHTML`.
- URLs en `href` y `src`, donde bloquea esquemas como `javascript:`.
- Estilos enlazados con `[style...]`.
- Atributos que pueden contener código, como `srcdoc` en un `iframe`.

Para un `iframe` o una URL de confianza se usan `bypassSecurityTrustResourceUrl` y `bypassSecurityTrustUrl`. Para un script, `bypassSecurityTrustScript`; para estilos, `bypassSecurityTrustStyle`. Todos tienen el mismo contrato: solo con contenido propio y revisado.

### Qué hacer además de confiar en Angular

- **No concatenar HTML.** La interpolación y el binding de propiedades cubren casi todo. Si hace falta HTML enriquecido, se sanitiza en el servidor o con una biblioteca revisada, y se limita a un subconjunto de etiquetas.
- **Evitar `eval`, `new Function` y `setTimeout` con cadenas.** Son ejecución dinámica y escapan a la sanitización.
- **Validar las URLs.** Una URL que llega de fuera y se usa en un `href` puede acabar en otro origen; se comprueba el esquema y el destino.
- **Configurar una política de seguridad de contenido (CSP).** Restringe qué scripts, estilos y conexiones permite el navegador. Es defensa en profundidad: no arregla una inyección, pero limita su alcance. Angular puede usar un nonce para sus estilos si la aplicación lo configura.
- **Cuidar las dependencias.** Una biblioteca de terceros puede insertar HTML sin sanitizar. El lockfile, la revisión de versiones y `npm audit` reducen el riesgo; no lo eliminan.

## XSSI: leer una respuesta ajena

*Cross-site script inclusion* (XSSI) explota la posibilidad de incluir un recurso de otro origen como script. Si una API devuelve JSON y el navegador lo ejecuta como JavaScript, un sitio malicioso puede intentar leer su contenido. El prefijo `)]}',` al inicio de la respuesta impide que el JSON sea válido como script.

El `HttpClient` de Angular reconoce ese prefijo y lo elimina antes de entregar el cuerpo. La protección es automática para las respuestas que pasan por el cliente; si se usa `fetch` directamente o se parsea un texto a mano, esa limpieza no ocurre. No se debe “arreglar” el JSON quitando el prefijo en el servidor para que encaje con un consumidor que no lo entiende: se cambia el consumidor.

El JSONP, que consistía en cargar datos como script, es una técnica obsoleta y peligrosa. No se usa para APIs nuevas; CORS es el mecanismo correcto para leer respuestas de otro origen.

## CSRF: actuar en nombre de la sesión

Un ataque de *cross-site request forgery* hace que el navegador de la víctima envíe una petición autenticada a la aplicación, sin que la víctima lo sepa. Funciona porque el navegador adjunta las cookies de sesión automáticamente, incluso cuando la petición se origina en otro sitio.

La defensa habitual es el patrón *cookie-to-header*: el servidor entrega un token en una cookie legible por JavaScript y espera recibirlo en una cabecera en cada petición que modifica estado. Un sitio ajeno puede provocar la petición, pero no puede leer la cookie de otro origen ni añadir la cabecera.

`HttpClient` implementa este patrón por defecto para peticiones del mismo origen:

- Lee la cookie `XSRF-TOKEN`.
- Envía su valor en la cabecera `X-XSRF-TOKEN`.
- Lo hace en métodos que no son `GET`/`HEAD`.

Los nombres se cambian si el backend usa otros:

```typescript
provideHttpClient(
  withXsrfConfiguration({
    cookieName: 'csrf-token',
    headerName: 'X-CSRF-Token',
  }),
)
```

El servidor debe generar el token, asociarlo a la sesión y rechazar la petición si la cabecera no coincide. Angular solo transporta el valor; no valida nada. Si el backend no comprueba la cabecera, la protección es decorativa.

Detalles que importan:

- **La cookie del token no puede ser `HttpOnly`** en este patrón, porque JavaScript necesita leerla. La cookie de sesión sí debe ser `HttpOnly`, `Secure` y con `SameSite` adecuado.
- **En peticiones entre orígenes** el token no se envía por defecto. Hay que configurar CORS con credenciales y decidir explícitamente si se comparte. Compartir sesión entre orígenes multiplica la superficie.
- **`SameSite=Lax` o `Strict`** reduce el envío de cookies en navegaciones cruzadas, pero no sustituye al token: hay flujos y navegadores que no encajan en una regla única.

Una API que usa solo un token `Bearer` en la cabecera `Authorization` no depende de cookies y, por tanto, no sufre CSRF clásico. A cambio, el token debe guardarse con cuidado: si se pone en `localStorage`, cualquier XSS puede leerlo. Un token en memoria y una cookie `HttpOnly` para renovar la sesión reducen el impacto, a costa de más complejidad.

## Dónde guardar secretos

No hay secretos en el cliente. Todo lo que llega al navegador —código, variables de entorno, claves de API, mensajes— es público. Una clave en `environment.ts` acaba en el bundle; ofuscarla solo retrasa a quien la busca.

Las claves que deben permanecer privadas viven en el servidor, que actúa de intermediario. Si una aplicación necesita llamar a un servicio de terceros con una clave, la llamada pasa por el backend. El cliente recibe un token de sesión de corta duración, no la credencial maestra.

Tampoco se registran datos sensibles en la consola ni en servicios de trazas. Un interceptor que imprime la petición completa puede dejar un token en los logs del navegador o en una herramienta de monitorización.

## HTTPS y cabeceras

El transporte debe ser HTTPS en todo el sitio, no solo en el login. Sin él, cualquier red intermedia puede leer o modificar la sesión. HSTS indica al navegador que no vuelva a usar HTTP para ese dominio.

Las cabeceras de seguridad se configuran en el servidor: `Content-Security-Policy`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Permissions-Policy` y, si aplica, `Strict-Transport-Security`. GitHub Pages y otros alojamientos estáticos fijan algunas y no permiten cambiarlas; conviene saber cuáles antes de prometer un control.

## Lista de comprobación

- ¿Se evita `innerHTML` con datos de usuario? Si se usa, ¿está sanitizado y limitado?
- ¿Cada `bypassSecurityTrust...` recibe solo contenido propio y revisado?
- ¿Las URLs externas se validan antes de usarlas?
- ¿El backend valida el token CSRF y no solo lo emite?
- ¿La cookie de sesión es `HttpOnly`, `Secure` y con `SameSite`?
- ¿Los tokens se guardan en el lugar menos expuesto posible?
- ¿Hay secretos en el bundle, en el repositorio o en los logs?
- ¿HTTPS es obligatorio y la CSP está probada?
- ¿Las dependencias se actualizan y se revisan?

Angular elimina una parte importante del trabajo, sobre todo la inyección accidental en plantillas. Lo que no puede hacer es decidir por el equipo qué contenido es confiable. Esa decisión es humana, y es la que separa una aplicación que usa las protecciones del marco de otra que las desactiva para salir de un problema puntual.
