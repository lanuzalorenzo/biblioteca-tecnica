# Fundamentos y arquitectura

Angular es un marco de trabajo, no una biblioteca de utilidades. Una biblioteca se llama cuando hace falta; un marco decide dónde se coloca el código y qué piezas se conectan entre sí. En Angular esa estructura se apoya en componentes, servicios, rutas y plantillas, y la CLI genera el esqueleto para que la aplicación se compile, se pruebe y se empaquete con las mismas reglas.

## De la página al documento vivo

En una web tradicional cada enlace pide al servidor un documento completo. El navegador lo descarga, lo interpreta y vuelve a empezar. El modelo es sencillo y el servidor manda, pero cada acción paga el coste de una navegación entera.

Una SPA cambia el reparto: el servidor entrega una página mínima con el código de la aplicación y, a partir de ahí, el navegador pide datos —normalmente JSON— y compone la vista. La URL sigue cambiando, pero la gestiona el enrutador del cliente mediante la API de historial del navegador. La ventaja es la continuidad: el estado de la interfaz no se pierde entre pantallas y solo se transfiere lo que cambia. El coste es que la primera carga incluye más código y que el arranque depende de que JavaScript se ejecute.

Angular no obliga a que todo ocurra en el navegador. Una aplicación puede renderizarse en el servidor o generarse de forma estática y después hidratarse en el cliente. La arquitectura de componentes es la misma; cambia dónde se ejecuta la primera representación.

## Las piezas y su responsabilidad

| Pieza | Responsabilidad |
|---|---|
| Componente | Una parte de la interfaz con su plantilla, estilos y lógica |
| Plantilla | HTML con sintaxis de Angular para mostrar datos y reaccionar a eventos |
| Directiva | Comportamiento que se aplica a un elemento o a un fragmento de plantilla |
| Tubería | Transformación de un valor para presentarlo |
| Servicio | Lógica compartida: estado, acceso a API, reglas de negocio |
| Inyector | Construye y entrega las dependencias que pide cada clase |
| Enrutador | Asocia una URL con un componente y gestiona la navegación |
| Formularios | Capturan, validan y envían la entrada de la persona usuaria |
| Cliente HTTP | Realiza peticiones a servicios remotos y devuelve observables |

La regla que ordena el resto: **el componente pinta y reacciona; el servicio decide y obtiene datos**. Cuando una consulta, un cálculo o una sesión aparecen dentro de un componente, se duplican en cuanto otro componente los necesita. Cuando todo se mete en un servicio, la vista pierde capacidad de decidir qué mostrar. La frontera no es rígida, pero conviene tenerla escrita.

Un componente puede ser contenedor o de presentación. El contenedor conoce los servicios, pide datos y decide qué pasa; el de presentación recibe datos por entradas, emite eventos por salidas y no sabe de dónde vienen. Esta separación facilita probar la vista sin red y reutilizarla en otra pantalla.

## El árbol de componentes

La interfaz se describe como un árbol. En la raíz está el componente que arranca la aplicación; dentro, otros componentes; y así hasta las hojas. Cada hijo puede recibir datos del padre y notificarle eventos. Cuando dos ramas lejanas necesitan el mismo estado, no se encadena el dato por todos los niveles: se mueve a un servicio compartido y ambas lo consumen.

Ese árbol también explica el alcance de los estilos. Por defecto, Angular encapsula el CSS de un componente para que sus reglas no se escapen a los hijos ni al resto de la página. La encapsulación es una ayuda, no una frontera de seguridad: el CSS no protege datos ni permisos.

## La estructura de un proyecto

Un proyecto generado por la CLI separa el código de la aplicación de la configuración del proyecto:

```
angular.json          configuración de build, serve y test
package.json          dependencias y scripts de npm
tsconfig.json         opciones del compilador TypeScript
src/
  index.html          documento que carga la aplicación
  main.ts             punto de arranque
  styles.css          estilos globales
  app/
    app.ts            componente raíz (en versiones anteriores, app.component.ts)
    app.html          plantilla del componente raíz
    app.config.ts     providers de la aplicación
    app.routes.ts     definición de rutas
```

Dentro de `src/` vive lo que se modifica a diario. En la raíz viven las decisiones de compilación: qué dependencias entran, a qué versión de JavaScript se compila, qué presupuestos de tamaño se aplican y qué configuración usa cada entorno.

`angular.json` es el archivo propio de la CLI. Define los proyectos del espacio de trabajo —una aplicación, varias, o una biblioteca—, sus constructores (*builders*) y las configuraciones de `development` y `production`. `tsconfig.json` controla el compilador: el nivel de comprobación, el destino de JavaScript y la resolución de módulos. `package.json` declara dependencias y scripts, pero los scripts de Angular se ejecutan a través de la CLI.

Dos archivos que ya no se generan y que aparecen en proyectos antiguos:

- **`tslint.json`.** TSLint está retirado. El análisis estático se hace con ESLint y `angular-eslint`, que incluye reglas específicas para plantillas y componentes.
- **`.browserslistrc`.** La lista de navegadores soportados se declara en la clave `browserslist` de `package.json` o en un archivo de configuración de Browserslist. IE11 quedó fuera del soporte hace años y no debe añadirse sin una razón muy justificada.

## La CLI

La interfaz de línea de comandos es la vía normal para crear y mantener el proyecto. Todos sus comandos empiezan por `ng`:

```bash
ng new tienda --routing --style=css
cd tienda
ng serve
```

`ng new` pregunta por el nombre, el formato de estilos, si se quieren rutas y qué runner de pruebas usar. Las opciones permiten automatizar la respuesta:

```bash
ng new tienda --routing --style=scss --ssr=false --package-manager=npm
```

`--skip-install` evita instalar dependencias en ese momento; `--skip-tests` no genera archivos de prueba; `--strict` activa las comprobaciones de TypeScript. En proyectos actuales el modo estricto es lo esperable, no una excepción.

Los comandos que se usan a diario:

```bash
ng serve                 # servidor de desarrollo con recarga
ng serve --port 4300     # otro puerto si 4200 está ocupado
ng generate component usuarios/tarjeta
ng generate service datos/usuarios
ng generate guard sesion/canje
ng build                 # compilación de producción
ng test                  # pruebas unitarias
ng update                # actualización guiada de dependencias
ng add @angular/material # instala y configura una dependencia
```

`ng generate` crea archivos con la estructura de la versión instalada. `ng update` no solo cambia números de versión: aplica migraciones automáticas cuando conoce el cambio y avisa cuando hace falta intervenir a mano. `ng add` instala una biblioteca y ejecuta su esquema de configuración si lo trae.

Las opciones de `ng serve` que más se usan son `--port`, `--host` para escuchar en otra interfaz y `--open` para abrir el navegador. La recarga en caliente preserva parte del estado; el reemplazo de módulos en caliente (*HMR*) va un paso más allá y sustituye módulos sin recargar la página, aunque no todos los cambios se pueden aplicar así.

## Qué ocurre al compilar

El código fuente es TypeScript y plantillas HTML. El build hace varias cosas:

1. Compila TypeScript al destino declarado en `tsconfig.json`.
2. Compila las plantillas en modo AOT (*ahead of time*), comprobando nombres y tipos.
3. Resuelve las dependencias y elimina el código que no se usa (*tree shaking*).
4. Empaqueta, minifica y añade un hash al nombre de los archivos para evitar cachés antiguas.
5. Comprueba los presupuestos de tamaño configurados en `angular.json`.

El resultado queda en `dist/`. En desarrollo se sirve sin minificar y con mapas de código para depurar; en producción se optimiza. Un build de producción que supera un presupuesto no falla por capricho: está avisando de que la primera carga crece. La respuesta no es subir el límite sin mirar, sino dividir la aplicación y cargar partes bajo demanda.

La compilación AOT explica por qué una plantilla puede romper el build: Angular la convierte en código TypeScript y comprueba que las propiedades y los métodos existen. Un error como `{{ usuario.nombre }}` sobre un objeto que no tiene `nombre` se detecta antes de abrir el navegador si el modo estricto de plantillas está activo.

## Detección de cambios

Cuando cambia un dato, Angular tiene que saber qué partes de la vista volver a evaluar. Durante años lo hizo con Zone.js, una biblioteca que intercepta eventos, temporizadores y promesas para avisar al marco de que algo ha podido cambiar. Ese modelo funciona, pero obliga a recorrer más de lo necesario y mezcla el cambio de estado con el momento en que ocurre.

Las señales cambian el planteamiento: un valor reactivo avisa de quién depende de él, y la vista puede actualizarse sin recorrer el árbol entero. El modo sin Zone.js (`provideZonelessChangeDetection()`) elimina la dependencia de los interceptores y apoya la detección en las señales y en las notificaciones explícitas. No es obligatorio migrar de golpe: una aplicación puede seguir con Zone.js y usar señales donde aporten claridad.

La estrategia `OnPush` reduce el trabajo en componentes que solo cambian cuando llega una entrada nueva, se emite un evento o se notifica un cambio. Se apoya en no mutar los objetos de entrada: si se modifica un array en el sitio y se conserva la misma referencia, el componente puede no enterarse. Con señales, la dependencia es explícita y el problema desaparece en la parte que las usa.

## Angular no es AngularJS

AngularJS (1.x) es el framework anterior. Compartió nombre y algunos conceptos —directivas, servicios, inyección—, pero no es compatible: no usa controladores con `$scope`, ni `$digest`, ni la misma forma de declarar componentes. Su soporte terminó en diciembre de 2021. El código de AngularJS que se encuentre hoy es legado y no se migra copiando fragmentos: se reescribe la aplicación o se convive con ella en una isla aparte.

Tampoco es un framework solo para el navegador ni un sustituto del backend. Angular resuelve la interfaz y la comunicación; las reglas que no pueden confiar en el cliente —permisos, validación definitiva, cálculo de precios— siguen viviendo en el servidor.

## Decisiones que conviene tomar pronto

- **Tamaño de los componentes.** Un componente que pinta una tarjeta y otro que gestiona la página son unidades distintas. Si un archivo mezcla consultas, formato y navegación, probablemente son tres responsabilidades.
- **Dónde vive el estado.** El estado local se queda en el componente; el compartido sube a un servicio; el remoto se cachea con una política explícita.
- **Rutas y carga.** Una aplicación pequeña puede registrar todas las rutas de golpe. Una grande debe dividir por funcionalidad y cargar cada parte cuando se visita.
- **Formularios.** Se elige un enfoque —plantilla o reactivo— y se mantiene en toda la aplicación. Mezclarlos sin criterio complica la validación.
- **Pruebas.** Lo que tiene lógica se prueba sin navegador; lo que depende de la interacción se prueba con el componente montado; los flujos críticos se reservan para extremo a extremo.

## Para reconocer una aplicación ordenada

Una aplicación Angular sana se reconoce por detalles concretos: los componentes no construyen sus dependencias con `new`; las llamadas HTTP viven en servicios; las rutas no están todas en un archivo gigante; los formularios validan en un solo sitio; las plantillas no contienen reglas de negocio; y el build de producción cabe en el presupuesto sin trucos. Ninguno de esos puntos es una regla del marco, pero todos evitan el mismo problema: que la aplicación funcione hoy y no se pueda cambiar mañana.
