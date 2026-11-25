# Una arquitectura modular

ASP.NET Core se construyó con dos ideas fijas: huir del bloque monolítico de las versiones anteriores y separar la aplicación del servidor donde corre. Esa separación es la que permite ejecutar el mismo código en Windows, Linux o macOS, y también la que deja elegir qué piezas entran en cada proyecto. El estándar OWIN, anterior al producto, sirvió de base conceptual.

## La especificación OWIN

OWIN, *Open Web Interface for .NET*, es una especificación abierta que define cómo se comunican los servidores y las aplicaciones .NET. La iniciaron dos miembros del equipo de ASP.NET, Louis Dejardin y Benjamin Vanderveen, y toma la idea de iniciativas parecidas de Ruby, Python o Node. La versión 1.0 se publicó en octubre de 2012 y el proyecto mantiene su sitio en `owin.org`.

El objetivo era romper el acoplamiento histórico. En ASP.NET clásico, la aplicación, el framework, ASP.NET y el servidor formaban una sola pieza: cambiar una capa obligaba a revisar las demás, y usar un framework fuera de su servidor de siempre no era posible.

Los componentes de esa pila se entienden de abajo arriba: el servidor, casi siempre IIS; ASP.NET, que corre encima; un framework como MVC o Web Forms, construido sobre ASP.NET; y la aplicación, escrita con ese framework. Todo se cargaba junto, aunque la aplicación aprovechara una parte pequeña.

OWIN propone una capa intermedia entre el servidor y la aplicación, con cuatro actores:

- El host es el proceso donde vive todo: IIS o una simple aplicación de consola.
- El servidor se ejecuta dentro del host, habla HTTP y traduce cada petición al formato que define la especificación.
- Los middlewares forman la cadena que recorre la petición; pueden leerla, modificarla o responder sin dejar pasar.
- El framework —MVC, Web Forms, Web Pages o SignalR— se construye sobre esa cadena y ya no conoce el servidor concreto.

Esa separación tiene consecuencias visibles. Una aplicación escrita con SignalR 2.0, compatible con OWIN, podía correr sobre ASP.NET e IIS o dentro de un servicio de Windows, siempre que existieran los adaptadores adecuados. ASP.NET Core y sus frameworks de más alto nivel, MVC y SignalR incluidos, se construyeron ya con esta independencia.

Los middlewares permiten además sacar del núcleo las funciones transversales —seguridad, registro, compresión— y convertirlas en piezas opcionales que comparten todos los frameworks.

## El pipeline y los middlewares

La modularidad llega al contenido: la aplicación carga solo los módulos que necesita. Si usa MVC, añade MVC; si además usa SignalR, añade SignalR; si necesita autenticación por cookies o soporte para CORS, añade el middleware correspondiente. Nada de eso entra en el pipeline si no se registra: la aplicación ejecuta solo los middlewares que haya añadido.

Por cada petición, el servidor crea un diccionario en memoria con los datos del contexto —la solicitud, el entorno, el cliente— y lo hace viajar por una cadena de middlewares llamada pipeline. La petición recorre la cadena en un sentido y la respuesta vuelve por el mismo camino en sentido inverso, de modo que cada middleware ve la petición al entrar y la respuesta al salir.

Ese doble paso permite cuatro comportamientos:

- Ejecutar algo y dejar seguir la petición. Un middleware de registro anota la solicitud y pasa el control al siguiente.
- Esperar a la respuesta y modificarla. Un gestor de errores puede cambiar un 500 por una página propia, y el registro puede anotar lo que se devolvió al cliente.
- Cortar el proceso y responder. Un middleware de autorización comprueba la cookie y devuelve la redirección al login sin ejecutar nada más.
- Terminar la petición. Es lo que hace un framework: MVC ejecuta la aplicación y devuelve el resultado, que sale por la cadena en orden inverso.

Toda aplicación arranca con el pipeline vacío, así que sin middlewares no responde a nada. Se añaden durante la inicialización, sobre `app`, y el orden importa: si la autorización va antes que el registro, las peticiones de un usuario sin autenticar se cortan antes de que el registro las vea.

## Una cadena, no una lista de features

La diferencia con ASP.NET clásico no es solo estética. Allí los módulos se activaban con entradas en `Web.config` y el orden lo decidía el servidor; aquí el orden lo escribe el código y se puede leer. Esa claridad permite razonar sobre un fallo: si una cabecera no llega, se sabe qué componente debía añadirla y qué había delante. También permite probar la composición sin levantar IIS, porque el pipeline es código.

La contrapartida es que nada viene puesto. Una aplicación nueva no sirve archivos estáticos, no captura errores y no autentica hasta que se le añaden los middlewares. Esa es la razón de que el arranque de un proyecto ocupe una nota propia y de que el orden de las llamadas sea un tema recurrente.
