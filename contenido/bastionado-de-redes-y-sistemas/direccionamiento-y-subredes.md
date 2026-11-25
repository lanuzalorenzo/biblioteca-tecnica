# Direccionamiento y subredes

Una dirección IP funciona como una dirección postal: la primera parte identifica la calle o el código postal y la segunda, el portal concreto. La máscara es la línea que separa ambas; sin ella, la dirección no dice a qué red pertenece. Y en seguridad, saber a qué red pertenece un equipo es lo que permite decidir con quién puede hablar.

Este apunte se queda con lo que el direccionamiento aporta al bastionado: separar zonas, documentar qué hay en cada una y evitar que la comodidad deje equipos fuera de sitio. El cálculo completo, con ejemplos y máscaras, está en [Direccionamiento IP, subredes y enrutamiento](../redes/direccionamiento-y-enrutamiento.md).

## IP, máscara y prefijo

Una IPv4 tiene 32 bits, escritos como cuatro octetos. El prefijo indica cuántos bits iniciales identifican la red; el resto, los hosts. La máscara es la misma información en notación decimal.

| Prefijo | Máscara | Direcciones | Hosts útiles |
|---|---|---:|---:|
| `/24` | `255.255.255.0` | 256 | 254 |
| `/25` | `255.255.255.128` | 128 | 126 |
| `/26` | `255.255.255.192` | 64 | 62 |
| `/27` | `255.255.255.224` | 32 | 30 |
| `/28` | `255.255.255.240` | 16 | 14 |
| `/29` | `255.255.255.248` | 8 | 6 |
| `/30` | `255.255.255.252` | 4 | 2 |

Los hosts útiles son las direcciones totales menos dos, porque la primera identifica la red y la última es la difusión. En un enlace punto a punto se usan casos especiales que se explican más adelante.

## Cálculo rápido

- La red se obtiene aplicando la máscara a la dirección.
- La difusión se obtiene poniendo a uno todos los bits de host.
- El número de direcciones es `2` elevado a los bits de host.
- El rango útil empieza en la red más uno y termina en la difusión menos uno.

Para calcular de cabeza, se busca el octeto de la máscara que no sea `255` ni `0`, se resta su valor a 256 y ese es el tamaño del bloque. Después se localiza el múltiplo inferior en la dirección: ahí empieza la subred.

Un bloque de tamaño `T` debe empezar en una dirección múltiplo de `T`. El siguiente bloque empieza en la dirección de red más `T`, no sumando dos a la difusión.

## Clases históricas y CIDR

Las clases se basaban en el primer octeto: A hasta 126, B hasta 191, C hasta 223, D para multicast y E reservada. Hoy se diseña con CIDR, que expresa el prefijo de forma explícita. La clase no sustituye a la máscara: un diseño actual se lee por el prefijo, no por la letra.

Esto importa al revisar una configuración heredada. Una dirección que «parece de clase C» puede estar funcionando con un prefijo distinto, y una regla escrita para una red antigua puede no cubrir el direccionamiento actual.

## El plan de direcciones como control

Direccionar no es solo asignar números. Un plan ordenado permite responder preguntas de seguridad:

- **Qué zona ocupa cada prefijo.** Usuarios, servidores, invitados, gestión, voz, dispositivos industriales. Si un equipo aparece en la zona equivocada, algo falla.
- **Qué direcciones están reservadas.** Puertas de enlace, impresoras, cámaras, controladores. Una reserva documentada evita que un equipo dinámico ocupe el sitio de un servicio.
- **Qué rangos son privados.** Las direcciones privadas de IPv4 no se enrutan por Internet; se usan dentro de la organización y salen mediante traducción. Eso no las hace seguras: solo limita su visibilidad directa.
- **Qué crece y dónde.** Dejar espacio para una DMZ, una nueva sede o un segmento de invitados evita renumerar media red cuando aparece la necesidad.
- **Quién es el dueño del plan.** Sin responsable, el direccionamiento se convierte en un conjunto de excepciones que nadie puede auditar.

La documentación no es burocracia: es lo que permite que una regla de cortafuegos tenga sentido. Una regla que dice «permitir de la red de usuarios a la de servidores» solo es verificable si ambas redes están definidas y nadie ha metido un servidor en la de usuarios.

## Segmentar no es bloquear

Dividir una red en subredes separa dominios de difusión y ordena el tráfico, pero no impide la comunicación por sí sola. Para que dos segmentos no se hablen hace falta que algo enrute y decida, y que exista una regla que lo impida.

Este es el error más frecuente al presentar un diseño: se enseña un esquema con muchas subredes y se da por hecho que la seguridad está resuelta. Sin control de acceso entre segmentos, la red sigue siendo plana a efectos prácticos.

## IPv6

IPv6 usa 128 bits, escritos en hexadecimal con dos puntos. No tiene difusión; emplea multicast y descubrimiento de vecinos. Cada segmento recibe su prefijo y los equipos pueden configurarse solos con la información que anuncian los routers.

Para el bastionado, el plan de direcciones IPv6 plantea las mismas preguntas que IPv4 —qué zona, qué servicio, qué crece— y añade una: quién puede anunciar prefijos y puertas de enlace. Un anuncio no autorizado desvía tráfico sin tocar la tabla de rutas de nadie.

## Qué comprobar

- Cada subred tiene un propósito documentado y una persona responsable.
- Las puertas de enlace y los servicios críticos tienen direcciones reservadas fuera del rango dinámico.
- No hay solapamientos entre sedes, proveedores o redes heredadas.
- Las reglas de acceso entre segmentos existen y están justificadas; la separación no se da por supuesta.
- El direccionamiento IPv6 está planificado y sus anuncios están controlados.
- El plan se actualiza cuando se añade una sede, un servicio o una zona nueva.

## Errores que se repiten

- Calcular la red por la clase sin atender al prefijo.
- Confundir `.255` con la difusión en cualquier prefijo.
- Asignar a un equipo la dirección de red o la de difusión.
- Suponer que segmentar aplica reglas de seguridad.
- Dejar el direccionamiento en la cabeza de una sola persona.
- Renumerar una red sin actualizar reglas, inventario y documentación.

## Fuentes

- RFC 791 (IPv4), RFC 950 (subredes), RFC 1918 (direcciones privadas) y RFC 4632 (CIDR).
- RFC 8200 (IPv6) y RFC 4861 (descubrimiento de vecinos).
