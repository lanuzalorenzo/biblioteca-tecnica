# VLSM y reparto por sedes

Repartir direcciones recuerda a llenar un maletero: primero entran las maletas grandes y, en los huecos que quedan, se colocan los bultos pequeños. Si se empieza por lo menudo, lo grande ya no entra. VLSM traslada esa lógica a la red: cada segmento recibe el tamaño que necesita y los bloques se ordenan de mayor a menor.

No se trata de que todos los segmentos midan lo mismo, sino de que el conjunto quepa y de que cada bloque empiece donde le corresponde. Es planificación, y en seguridad también es una manera de guardar sitio para zonas que todavía no existen.

## Requisitos antes de calcular

1. Enumera los segmentos y los equipos de cada uno.
2. Suma la interfaz del router a cada LAN: la puerta de enlace consume una dirección.
3. Calcula el menor número de bits de host que cumpla `2^h - 2 >= hosts`.
4. Convierte ese número en prefijo: `32 - h`.
5. Ordena los segmentos de mayor a menor.
6. Asigna bloques consecutivos y alineados.
7. Calcula red, rango útil y difusión.
8. Comprueba solapamientos, suma total y alineación.

La condición es «mayor o igual», no «mayor que». Si `2^h - 2` coincide exactamente con los hosts necesarios, ese prefijo vale. Si el enunciado ya incluye la puerta de enlace, no se suma otra vez.

## Viabilidad del conjunto

Antes de asignar nada hay que comprobar que los requisitos caben:

`suma de 2^h de todos los segmentos <= 2^(32 - prefijo base)`

Que la suma quepa es necesario, pero no suficiente. Cada bloque debe poder empezar en un múltiplo de su tamaño. Por eso se ordena de mayor a menor y se comprueba el resultado; un reparto con los prefijos correctos puede ser inviable por la colocación.

## Ejemplo: cuatro zonas y dos enlaces

Sobre `172.20.10.0/25`, con 128 direcciones:

- LAN de usuarios: 60 equipos más el router, 61 hosts.
- LAN de servidores: 30 equipos más el router, 31 hosts.
- LAN de gestión: 10 equipos más el router, 11 hosts.
- LAN de invitados: 10 equipos más el router, 11 hosts.
- Dos enlaces punto a punto entre routers.

| Segmento | Hosts | Prefijo | Red | Rango útil | Difusión |
|---|---:|---|---|---|---|
| Usuarios | 61 | `/26` | `172.20.10.0/26` | `.1`–`.62` | `.63` |
| Servidores | 31 | `/27` | `172.20.10.64/27` | `.65`–`.94` | `.95` |
| Gestión | 11 | `/28` | `172.20.10.96/28` | `.97`–`.110` | `.111` |
| Invitados | 11 | `/28` | `172.20.10.112/28` | `.113`–`.126` | `.127` |
| Enlace 1 | 2 | `/30` | `172.20.10.128/30` | `.129`–`.130` | `.131` |
| Enlace 2 | 2 | `/30` | `172.20.10.132/30` | `.133`–`.134` | `.135` |

Las cuatro LAN suman `64 + 32 + 16 + 16 = 128`, es decir, todo el `/25`. Los enlaces no caben. No es un error de cálculo: cada bloque es correcto, pero el conjunto no es viable. La solución es ampliar el bloque base a `172.20.10.0/24`; las LAN ocupan la primera mitad y los enlaces la segunda. Quedan libres `.136` a `.255`.

Este es el punto que más cuesta ver: **que cada prefijo esté bien no significa que el reparto quepa**. La comprobación se hace sobre la suma y sobre el espacio disponible, no sobre cada fila por separado.

## Enlaces punto a punto

Un enlace entre dos routers necesita dos direcciones. Un `/30` ofrece cuatro: red, dos extremos y difusión. Un `/31` usa sus dos direcciones como extremos, sin red ni difusión, pero no todos los equipos lo admiten. Cuando el bloque base está justo, pasar los enlaces a `/31` puede salvar el diseño; cuando las LAN ya consumen todo, no hay prefijo que lo arregle.

## Orden y alineación

Asignar de mayor a menor reduce la fragmentación: si se empieza por los bloques pequeños, los grandes ya no pueden ocupar el inicio y aparecen huecos difíciles de reutilizar.

Al pasar de un bloque al siguiente, no se suma dos a la difusión «para dejar margen». Se suma el tamaño a la dirección de red y se comprueba que el resultado es múltiplo de ese tamaño. Es el error más común al hacer el reparto en una hoja de cálculo.

## Reservar para lo que no existe

Un plan de direcciones de seguridad no solo cubre lo que hay. Conviene reservar bloques para:

- Una DMZ o una zona de servicios publicados.
- Un segmento de invitados o de proveedores.
- Dispositivos industriales o IoT, que no deben compartir red con los puestos.
- Crecimiento de una sede que puede duplicar su plantilla.
- Enlaces temporales de migración.

La reserva se documenta. Un hueco sin dueño se acaba ocupando con lo primero que aparece, y entonces la zona deja de tener un propósito claro.

## Errores que se repiten

- Repetir el mismo prefijo para segmentos de tamaños muy distintos.
- Olvidar que la interfaz del router consume una dirección.
- Asignar bloques que no empiezan en un múltiplo de su tamaño.
- Sumar dos a la difusión o no comprobar la alineación del siguiente bloque.
- Dar por viable un reparto porque cada prefijo individual está bien.
- No reservar espacio para zonas futuras y renumerar cuando llegan.

## Fuentes

- RFC 950 (subredes), RFC 3021 (enlaces `/31`) y RFC 4632 (CIDR).
