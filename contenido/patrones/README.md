# Patrones de fiabilidad

Un sistema distribuido falla de formas que un programa de un solo proceso no conoce: la red se corta a mitad de una respuesta, un servicio tarda más de lo que tarda en morir, un mensaje llega dos veces. Los patrones de este módulo no eliminan el fallo; deciden qué hace el sistema cuando ocurre.

## Cinco respuestas al fallo

- **Reintentar con espera.** Repite la operación que falló de forma transitoria, dejando pasar cada vez más tiempo entre intentos.
- **Cortar el circuito.** Deja de llamar a una dependencia que falla, para no sumar carga ni esperar inútilmente.
- **Hacer idempotente la operación.** Permite repetirla sin que el efecto se duplique.
- **Tratar el mensaje venenoso.** Saca del bucle el mensaje que nunca se podrá procesar y lo deja aparte.
- **Separar lectura y escritura (CQRS).** Da a cada lado el modelo que necesita, en lugar de forzar uno solo.

Cada uno resuelve un problema distinto y ninguno es gratuito. Un reintento sobre una operación que no es idempotente duplica el efecto; un circuito sin reintento convierte un fallo pasajero en una caída; CQRS en un CRUD pequeño añade dos modelos y una sincronización.

## Lo que se aprende aquí

El módulo explica cuándo usar y cuándo no cada patrón, y muestra tres de ellos con código .NET ejecutado: el reintento con espera exponencial, el interruptor y la idempotencia. El mensaje venenoso y CQRS se explican con su criterio y su límite, sin convertirlos en receta.
