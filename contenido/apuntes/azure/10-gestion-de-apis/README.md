# Gestión de APIs en Azure

Una API publicada sin intermediario acaba resolviendo una por una las mismas preguntas: quién puede llamarla, cuántas veces, con qué clave, qué versión y qué se hace cuando el backend falla. Azure API Management pone esa capa delante: un gateway que recibe la petición, aplica las reglas y decide si llega al servicio.

La pieza no sustituye al backend ni lo protege de un diseño inseguro. Sirve para separar la política de acceso del código de negocio y para cambiarla sin desplegar la aplicación.

## Qué compone el servicio

- **Gateway.** Es el punto de entrada. Recibe la petición, ejecuta las políticas y la reenvía al backend.
- **Plano de administración.** Publica APIs, versiones, productos y políticas.
- **Portal de desarrolladores.** Documenta la API y entrega las claves a quien se suscribe.
- **Portal de administración.** Vista del equipo que opera el servicio.

El gateway puede ser gestionado por Microsoft o autoalojado en Kubernetes, con la misma configuración. La elección depende de dónde tenga que quedar la petición: si el backend no sale a internet, el gateway se acerca.

## Cuándo hace falta

Tiene sentido cuando hay varias APIs, varios consumidores o ambos, y las reglas de acceso cambian con frecuencia. También cuando hay que publicar una API de un servicio antiguo sin tocarlo: el gateway traduce la ruta y la forma.

No hace falta para una API única, con un solo consumidor y autenticación resuelta en el propio servicio. La capa añade coste, latencia y un componente más que operar.

## Lo que se aprende aquí

El módulo recorre las tres decisiones que más se atascan: cómo se identifica y se limita a un consumidor con suscripciones y claves, cómo se aplica una cuota y un límite por segundo, y cómo se valida un token antes de que la petición toque el backend. Al final queda claro qué protege la clave de suscripción y qué no.
