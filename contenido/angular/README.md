# Angular: aplicaciones web con componentes

Angular es un marco de trabajo para construir aplicaciones web cuyo estado vive en el navegador. La página se carga una vez y, a partir de ahí, la vista cambia según la ruta y los datos: no se pide al servidor un documento nuevo por cada clic. Esa forma de trabajar se conoce como aplicación de una sola página (*single page application*, SPA), y exige algo más que pintar HTML: hace falta un enrutador, una forma de componer la interfaz, un mecanismo para compartir estado y otro para hablar con las API.

Angular cubre esas piezas como un conjunto. Los **componentes** encapsulan una parte de la interfaz con su plantilla, sus estilos y su lógica; las **directivas** modifican lo que ocurre en la plantilla; las **tuberías** transforman valores para mostrarlos; los **servicios** sacan de los componentes la lógica compartida y el acceso a datos; la **inyección de dependencias** entrega esos servicios sin construirlos a mano; el **enrutador** decide qué componente corresponde a cada dirección; y los **formularios** y el **cliente HTTP** resuelven la entrada de datos y la comunicación remota.

Todo se escribe en TypeScript. Los tipos desaparecen al compilar, pero mientras se programa detectan errores antes de ejecutar y documentan qué espera cada función. Angular compila las plantillas con conocimiento de esos tipos, así que un fallo de nombre o de tipo en el HTML también puede detectarse en la compilación.

El marco ha cambiado de forma importante en los últimos años. Los componentes **standalone** sustituyen al módulo como unidad de composición por defecto, el control de flujo `@if` y `@for` reemplaza a las directivas estructurales clásicas en el código nuevo, y las **señales** ofrecen una forma explícita de modelar estado reactivo. Estas notas explican el Angular actual y señalan, cuando importa, lo que ha quedado atrás: AngularJS, TSLint, `HttpModule` y la obligación de declarar cada componente en un `NgModule`.

Los ejemplos son autocontenidos: cada uno se puede reproducir en un proyecto recién creado con la CLI y no depende de una aplicación concreta.

## Contenido

| Tema | Qué responde |
|---|---|
| [Fundamentos y arquitectura](fundamentos-y-arquitectura.md) | Qué es una SPA, cómo se organiza una aplicación y qué hace la CLI |
| [Standalone frente a NgModule](standalone-frente-a-ngmodule.md) | Cómo se compone la aplicación hoy y qué queda de los módulos |
| [TypeScript aplicado a Angular](typescript-aplicado.md) | Qué tipos hacen falta y cómo se reflejan en plantillas y servicios |
| [Componentes y plantillas](componentes-y-plantillas.md) | Cómo se construye una pieza de interfaz y qué eventos tiene su ciclo de vida |
| [Data binding](data-binding.md) | Cómo se conectan la clase y la vista en ambos sentidos |
| [Directivas y tuberías](directivas-y-tuberias.md) | Cómo se repite, se oculta y se transforma lo que se muestra |
| [Rutas y navegación](rutas-y-navegacion.md) | Cómo se asocia una URL a un componente y cómo se leen sus parámetros |
| [Servicios e inyección de dependencias](servicios-e-inyeccion.md) | Dónde vive la lógica compartida y cuántas instancias existen |
| [HTTP y datos remotos](http-y-datos-remotos.md) | Cómo se consume una API, se tratan errores y se añaden cabeceras |
| [Formularios](formularios.md) | Cómo se capturan, validan y envían datos |
| [Seguridad del cliente](seguridad-del-cliente.md) | Qué protege Angular, qué no, y dónde está el límite real |
| [Pruebas y despliegue](pruebas-y-despliegue.md) | Cómo se comprueba el comportamiento y se publica el resultado |
