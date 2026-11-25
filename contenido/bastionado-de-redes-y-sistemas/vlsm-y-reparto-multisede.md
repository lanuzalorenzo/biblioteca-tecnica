# VLSM y reparto por sedes

Repartir direcciones recuerda a llenar un maletero: primero entran las maletas grandes y, en los huecos que quedan, se colocan los bultos pequeños. VLSM traslada esa lógica a la red: cada segmento recibe el tamaño que necesita y los bloques se ordenan de mayor a menor.

El método de cálculo, con prefijos, alineación y ejemplos resueltos, está en [Direccionamiento IP, subredes y enrutamiento](../redes/direccionamiento-y-enrutamiento.md). Este apunte se queda con la decisión de seguridad: qué zonas deben existir, cuánto espacio se les reserva y qué hacer cuando el conjunto no cabe.

## Qué decide el bastionado

El cálculo dice si un bloque cabe. La seguridad decide qué no se puede sacrificar para que quepa:

- La red de **gestión** de los dispositivos no comparte subred con usuarios.
- La **DMZ** tiene su propio espacio, separado de los servidores internos.
- Los **invitados** no reciben direcciones del rango corporativo.
- Los **servidores** no se mezclan con los puestos de trabajo.
- Los **dispositivos industriales o IoT** no comparten red con equipos de oficina.

Si el reparto no deja sitio para una de esas zonas, el problema no es de aritmética: es de diseño. Se amplía el bloque base, se reduce otra zona o se replantea la segmentación. Lo que no se hace es meter invitados en la red interna para «aprovechar» direcciones.

## Criterios de tamaño

| Zona | Qué debe cubrir | Si se queda corta |
|---|---|---|
| Gestión | Un equipo por dispositivo de red y crecimiento | Se comparte con usuarios y se pierde el aislamiento |
| Servidores | Un rango por servicio o por grupo | Se mezclan servicios de distinta criticidad |
| Usuarios | Puestos actuales más previsión | Se recurre a DHCP de otra zona |
| Invitados | Aforo máximo previsto | Se les da acceso a la red corporativa |
| DMZ | Servicios publicados y balanceadores | Se publica desde la red interna |
| Enlaces | Un bloque por conexión entre routers | Se usan direcciones de una LAN |

La puerta de enlace consume una dirección; si el requisito ya la incluye, no se suma otra vez.

La previsión no es adivinar: se basa en el inventario, en la plantilla y en los servicios que la organización ya ha anunciado. Una zona sin previsión se queda sin direcciones en el peor momento.

## La viabilidad es una decisión de seguridad

Un reparto puede ser correcto bloque a bloque y, aun así, no caber. La comprobación no se hace fila por fila, sino sobre el conjunto: la suma de todos los bloques debe entrar en el espacio base y cada bloque debe empezar en una dirección alineada a su tamaño.

Cuando el conjunto no cabe, la tentación es recortar la zona que menos se ve: gestión, invitados o DMZ. Es justo la decisión que debilita el diseño. El bastionado exige mantener las zonas y buscar espacio en otro sitio.

## Cuando el reparto falla

Un caso típico: varias LAN de tamaños distintos consumen todo el bloque base y los enlaces entre routers ya no tienen dónde ir. Cada prefijo individual está bien calculado; el problema es que se asignaron las zonas sin reservar los enlaces.

La salida no es meter los enlaces en la LAN de usuarios ni usar direcciones de una zona existente. Se amplía el bloque base, se reordena el reparto o se pasa a un prefijo mayor. Si la organización no puede ampliar, la conversación es sobre qué zona se queda fuera, no sobre cómo disimular el hueco.

Este es el punto que más cuesta ver: **que cada prefijo esté bien no significa que el reparto quepa**. La comprobación se hace sobre la suma y sobre el espacio disponible.

## Enlaces punto a punto

Un enlace entre dos routers necesita dos direcciones. Un `/30` ofrece cuatro; un `/31` usa sus dos extremos, sin red ni difusión, pero no todos los equipos lo admiten. El detalle está en el módulo de redes.

Desde la seguridad, los enlaces importan por dos motivos: transportan el tráfico entre zonas y suelen ser el punto donde se aplican las ACL. Un enlace sin direcciones reservadas se convierte en una excepción que nadie documenta.

## Reservar para lo que no existe

Un plan de seguridad no solo cubre lo que hay. Conviene reservar bloques para:

- Una DMZ o una zona de servicios publicados.
- Un segmento de invitados o de proveedores.
- Dispositivos industriales o IoT.
- Crecimiento de una sede que puede duplicar su plantilla.
- Enlaces temporales de migración.

La reserva se documenta. Un hueco sin dueño se acaba ocupando con lo primero que aparece, y entonces la zona deja de tener un propósito claro.

## Auditoría del reparto

1. Comprueba que cada zona tiene su bloque y su responsable.
2. Verifica que la suma cabe en el espacio base y que no hay solapamientos.
3. Revisa que los bloques empiezan en una dirección alineada a su tamaño.
4. Confirma que los enlaces y las reservas están fuera de los rangos dinámicos.
5. Mira si alguna zona ha crecido hasta invadir la previsión de otra.
6. Actualiza el plan antes de añadir una sede o un servicio, no después.

## Qué comprobar

- ¿Existe una zona separada para gestión, servidores, usuarios, invitados y DMZ?
- ¿Los enlaces entre routers tienen su propio espacio?
- ¿La previsión de crecimiento está escrita y actualizada?
- ¿El reparto sigue cabiendo tras el último servicio publicado?
- ¿Alguien responde del plan y de sus cambios?

## Errores que se repiten

- Repartir de menor a mayor y dejar sin sitio a los bloques grandes.
- Olvidar que la puerta de enlace consume una dirección.
- Asignar bloques sin comprobar la alineación.
- Dar por viable un reparto porque cada prefijo individual está bien.
- Recortar la zona de gestión o la DMZ para que quepa todo lo demás.
- No reservar espacio para zonas futuras y renumerar cuando llegan.

## Fuentes

- RFC 950 (subredes), RFC 3021 (enlaces `/31`) y RFC 4632 (CIDR).
