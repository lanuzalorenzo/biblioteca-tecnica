# Enrutamiento avanzado, ACL y seguridad de la red

Cuando la red deja de caber en una tabla de rutas escrita a mano, aparece el enrutamiento dinámico; cuando deja de ser de confianza, aparecen las listas de control. Las dos cosas se aprenden juntas porque responden a la misma pregunta: qué tráfico tiene derecho a pasar y por dónde.


## Enrutamiento dinámico

Un protocolo de enrutamiento intercambia información entre routers para que cada uno sepa cómo llegar a las redes que no tiene conectadas.

- **Vector distancia:** decide por número de saltos y por la información que le pasan los vecinos. Sencillo, converge despacio y no conoce la topología.
- **Estado de enlace:** cada router construye un mapa completo de la red y calcula el camino de menor coste. Converge rápido y escala mejor.

**OSPF** es el estándar abierto que se estudia: divide la red en áreas para no propagar toda la información a todos, elige el camino por coste —ligado al ancho de banda— y usa un router frontera para conectar áreas con el área troncal. Dos comprobaciones que explican casi todos sus fallos: los routers de un área deben compartir la misma configuración de área, y las vecindades solo se forman si coinciden temporizadores y redes anunciadas.

En una red pequeña, el enrutamiento estático sigue siendo mejor opción: es predecible, no gasta CPU ni ancho de banda y no tiene convergencia que esperar. Se cambia a dinámico cuando hay más rutas de las que se pueden mantener a mano o cuando la red cambia.

## Listas de control de acceso

Una ACL es una lista ordenada de reglas que permite o deniega tráfico por origen, destino, protocolo y puerto. Se evalúa de arriba abajo y **la primera coincidencia decide**: una regla amplia colocada antes deja inútiles todas las que vienen detrás.

Hay dos familias:

- **Estándar:** filtra solo por dirección de origen. Se coloca cerca del destino, porque en otro sitio bloquearía tráfico legítimo hacia otras redes.
- **Extendida:** filtra por origen, destino, protocolo y puerto. Se coloca cerca del origen, para no gastar ancho de banda en tráfico que se va a descartar.

Y una regla implícita que se olvida: al final de toda lista hay una denegación de todo. Un administrador que añade un `permit` al principio y no prueba pierde horas buscando por qué no pasa nada.

Las listas se escriben con máscara wildcard, que es la inversa de la máscara de red: un `/24` se expresa como `0.0.0.255`. Es el detalle que más se falla en un examen y en producción.

## Traducción de direcciones

NAT permite que una red privada salga a Internet con una o pocas direcciones públicas. En su forma más usada, la traducción se distingue por el puerto de origen, y el router mantiene la tabla de qué conexión pertenece a qué equipo.

Consecuencias que hay que tener presentes: rompe las conexiones entrantes, complica los protocolos que llevan direcciones dentro del mensaje y hace que el registro del servidor web vea siempre la misma dirección. Para publicar un servicio se usa una redirección de puerto concreta, no una apertura general.

## El resto de la seguridad de acceso

- **DHCP snooping** para que solo el servidor legítimo reparta direcciones.
- **Inspección de ARP** para que nadie se declare la puerta de enlace.
- **Seguridad de puerto** para fijar qué equipo entra por cada boca.
- **802.1X** cuando hace falta identificar al usuario antes de dar red.
- **Segmentación**: servidores, puestos, invitados y gestión en redes distintas, y una DMZ para lo que se publica.

Ninguna de estas medidas sustituye a las otras: cada una cierra una puerta distinta.

## Diagnosticar sin adivinar

El orden ahorra tiempo: dirección y máscara del equipo, puerta de enlace, tabla de rutas del router, conectividad con el destino y, solo después, la ACL. Órdenes de referencia en un router de configuración habitual: `show ip interface brief`, `show ip route`, `show ip ospf neighbor`, `show access-lists`, y un `traceroute` hacia el destino para ver por dónde se va y dónde se corta.

Una ACL denegando tráfico no da error: da silencio. Por eso se prueba con un caso que debe pasar y otro que debe fallar, y se anota el número de coincidencias de cada regla.

## Lo que se comprueba

Que las rutas dinámicas convergen y que el camino elegido es el esperado; que las ACL hacen lo que dicen, probadas en los dos sentidos; que la traducción de direcciones permite salir pero no entrar sin regla; que no hay un resolutor ni un relay abierto; y que un fallo de un enlace no deja la red sin servicio.

## Errores que se repiten

- Poner un `permit any` al principio de la lista.
- Confundir la máscara wildcard con la de red.
- Colocar una ACL estándar cerca del origen.
- Anunciar en OSPF redes que no deben enrutarse.
- Abrir puertos «para probar» y no cerrarlos.

## Fuentes

- RFC 2328 (OSPF versión 2) y RFC 3022 (NAT).
- Documentación oficial de configuración de routers y ACL.
- IEEE 802.1X y las recomendaciones de segmentación de red.
