# Direccionamiento IP, subredes y enrutamiento

Una dirección IP es como la dirección de una casa: la calle dice en qué red estás y el número, qué puerta eres. La máscara es lo que distingue una parte de la otra, y equivocarse en ella deja un equipo aislado sin que nadie vea el error.


## IPv4 y la máscara

Una dirección IPv4 son 32 bits, escritos en cuatro grupos decimales. Cada dirección tiene dos partes: **red** y **host**, y la frontera la marca la máscara.

- Máscara `/24` = `255.255.255.0`: 24 bits de red, 8 de host, 254 direcciones útiles.
- La primera dirección del rango identifica la red; la última es de difusión. Ninguna se asigna a un equipo.
- Las direcciones privadas (RFC 1918) —`10.0.0.0/8`, `172.16.0.0/12` y `192.168.0.0/16`— no se enrutan en Internet; para salir se traducen.

Las clases A, B y C históricas ya no asignan nada: el enrutamiento sin clases (CIDR) permite cualquier longitud de prefijo, y una máscara puede no acabar en un múltiplo de ocho.

## Subredes

Dividir una red es pedir bits de host para usarlos como bits de red. Con `192.168.10.0/24` y préstamo de tres bits salen ocho subredes de 30 direcciones útiles:

| Subred | Rango | Difusión |
|---|---|---|
| 192.168.10.0/27 | .1 – .30 | .31 |
| 192.168.10.32/27 | .33 – .62 | .63 |
| 192.168.10.64/27 | .65 – .94 | .95 |
| 192.168.10.96/27 | .97 – .126 | .127 |
| 192.168.10.128/27 | .129 – .158 | .159 |
| 192.168.10.160/27 | .161 – .190 | .191 |
| 192.168.10.192/27 | .193 – .222 | .223 |
| 192.168.10.224/27 | .225 – .254 | .255 |

Regla práctica: dos subredes con la misma dirección y distinta máscara pueden parecer compatibles y no lo son. El cálculo se comprueba siempre antes de configurar.

## VLSM: cada subred a su medida

Repartir todas las subredes iguales desperdicia direcciones. Con **máscara variable** cada red recibe el tamaño que necesita, de la más grande a la más pequeña para no fragmentar el espacio:

- Sala de servidores: 60 equipos → `/26` (62 útiles).
- Puestos de trabajo: 25 → `/27` (30 útiles).
- Enlace punto a punto entre routers: 2 → `/30` (2 útiles).

El ejercicio de VLSM del módulo es exactamente eso: una red multisede que hay que repartir sin solapar rangos.

## Enrutamiento

Un equipo envía fuera de su subred todo lo que no es local, y lo hace a su **puerta de enlace**. El router recibe, mira su tabla y decide:

- **Ruta conectada:** la subred de una interfaz suya. Es la más fiable.
- **Ruta estática:** la escribe un administrador. Predecible y suficiente para redes pequeñas o para el camino de salida.
- **Ruta dinámica:** la aprende de otro router con un protocolo de enrutamiento.

Los protocolos se dividen por cómo piensan: los **vector distancia** (RIP) deciden por número de saltos y no conocen la topología; los **estado de enlace** (OSPF) construyen un mapa completo y calculan el camino más corto por coste. RIP quedó para prácticas: su límite de 15 saltos y su convergencia lenta lo descartan en redes reales. OSPF es el estándar abierto habitual, con áreas para no propagar toda la información a todos.

## Salir a Internet: NAT

La traducción de direcciones (NAT) permite que muchos equipos privados compartan una dirección pública. En su forma más común, **PAT**, la traducción se distingue por el puerto de origen: el router anota qué conexión pertenece a qué equipo.

Funciona y es la razón de que IPv4 siga vivo, pero rompe lo que espera una conexión entrante y complica protocolos que llevan direcciones dentro del propio mensaje. IPv6 existe para no necesitarlo; mientras convivan, se despliega en doble pila.

## Listas de control de acceso

Una ACL es una lista ordenada de reglas que permite o deniega tráfico por origen, destino, protocolo y puerto. Se aplican en el router y son la primera segmentación real, pero conviene saber qué no hacen: no cifran, no inspeccionan contenido y no sustituyen a un cortafuegos con estado. Un error de orden —una regla de permiso amplia antes de la restricción— deja la lista inútil sin dar ningún aviso.

## Lo que se comprueba

Que la puerta de enlace responde, que la ruta de vuelta existe, que no hay dos subredes solapadas, que el reparto VLSM no deja huecos y que la ACL deniega lo que dice denegar —probándola, no leyéndola—.

El orden de las pruebas ahorra tiempo: primero el equipo consigo mismo (`127.0.0.1`), luego la puerta de enlace, luego un destino de la misma red y por último uno externo. Si falla el primer paso, el problema es del equipo; si falla el último, es de rutas o de traducción. En Linux, `ip route` muestra la tabla; en un router de configuración habitual, `show ip route` y `show interfaces`.

## Errores que se repiten

- Asignar la dirección de red o la de difusión a un equipo.
- Repartir subredes sin ordenar el tamaño: el bloque grande ya no cabe y hay que rehacer todo.
- Configurar la puerta de enlace en el equipo y olvidar la ruta de vuelta en el router.
- Escribir una ACL con un `permit any` delante de la restricción, que la deja sin efecto.

## Fuentes

- RFC 791 (IPv4), RFC 1918 (direcciones privadas) y RFC 4632 (CIDR).
- RFC 3022 (NAT) y RFC 8200 (IPv6).
- RFC 2328 (OSPF versión 2).
