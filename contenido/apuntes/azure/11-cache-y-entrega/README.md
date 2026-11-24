# Caché y entrega de contenido

Casi todo el contenido de una aplicación se pide muchas veces y cambia poco. Guardar una copia cerca del cliente evita recorrer la misma distancia y ejecutar el mismo trabajo en cada petición. La caché es esa copia; la entrega es el camino que la acerca.

Hay dos cachés distintas y conviene no mezclarlas. La **caché de respuesta** guarda la respuesta HTTP completa en un borde, como Front Door o una CDN. La **caché de datos** guarda el resultado de una consulta o un cálculo en un almacén como Redis, para que el origen no lo repita.

## Qué se gana y qué se paga

Se gana latencia, carga en el origen y coste de cómputo. Se paga con una copia que puede estar desactualizada y con una invalidación que hay que diseñar. Una caché sin política de caducidad es una fuente de errores difíciles de reproducir: el usuario ve el precio de ayer y nadie sabe por qué.

## Tres piezas

- **Redis.** Almacén en memoria para datos compartidos entre instancias: sesión, resultado de consultas, contadores y bloqueos. Tiene caducidad por clave y desalojo cuando se llena.
- **CDN.** Red de nodos que sirve archivos estáticos desde el punto más cercano. Trabaja con TTL y purga por URL.
- **Front Door.** Entrada global con enrutado, WAF, comprobaciones de estado y caché. Es la puerta única para un servicio repartido por regiones.

## Lo que se aprende aquí

El módulo fija primero la diferencia entre caducar e invalidar, con un caso concreto de precio que cambia. Después recorre las tres piezas y termina con el camino completo de una petición, desde el cliente hasta el origen y la caché de datos.
