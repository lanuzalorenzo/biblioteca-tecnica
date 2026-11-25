# Direccionamiento y subredes

Una dirección IP funciona como una dirección postal: la primera parte identifica la calle o el código postal y la segunda, el portal concreto. La máscara es la línea que separa ambas; sin ella, la dirección no dice a qué red pertenece. Y en seguridad, saber a qué red pertenece un equipo es lo que permite decidir con quién puede hablar.

Este apunte no enseña a calcular subredes: eso está en [Direccionamiento IP, subredes y enrutamiento](../redes/direccionamiento-y-enrutamiento.md). Aquí se trata el plan de direcciones como un control: qué debe estar documentado, qué señales delatan un diseño descuidado y qué se revisa antes de dar por buena una separación de zonas.

## Lo que hay que tener claro

Toda dirección se lee con su prefijo. La dirección de red y la de difusión no se asignan a equipos; el resto forma el rango útil. Un equipo decide si el destino está dentro o fuera comparando su prefijo con la dirección de destino.

Para aplicar controles basta con retener tres ideas:

- El prefijo define la frontera del segmento.
- La puerta de enlace es la salida hacia otras redes.
- Una dirección privada no se enruta por Internet; una pública sí puede ser alcanzada si no hay filtro.

El cálculo de bloques, máscaras y rangos se practica en el módulo de redes. Aquí interesa qué se hace con ese espacio.

## Rangos privados

| Bloque | Máscara | Uso |
|---|---|---|
| `10.0.0.0` | `/8` | Redes internas de cualquier tamaño |
| `172.16.0.0` | `/12` | Redes internas medianas |
| `192.168.0.0` | `/16` | Redes domésticas y pequeñas oficinas |

Estos rangos no deben aparecer como origen en tráfico que llega desde Internet. Ver una dirección privada en el exterior es una señal de filtrado mal puesto, de una traducción mal hecha o de una suplantación.

## El plan como control

Un plan ordenado permite responder preguntas que una lista de direcciones suelta no responde:

- **Qué zona ocupa cada prefijo.** Usuarios, servidores, invitados, gestión, voz, dispositivos industriales.
- **Qué direcciones están reservadas.** Puertas de enlace, impresoras, cámaras, controladores y servicios críticos.
- **Qué rango reparte DHCP.** Un equipo dinámico no debe poder ocupar la dirección de un servidor.
- **Qué pools usan la VPN y los invitados.** Si comparten rango con la red interna, la separación es ficticia.
- **Quién es el dueño del plan.** Sin responsable, el direccionamiento se llena de excepciones que nadie audita.

La documentación no es burocracia: una regla que dice «permitir de usuarios a servidores» solo se puede verificar si ambas redes están definidas y nadie ha metido un servidor en la de usuarios.

## Cómo se audita

1. Contrasta el inventario de subredes con la configuración de routers, switches y DHCP.
2. Busca solapamientos entre sedes, proveedores, redes heredadas y rangos de VPN.
3. Comprueba que las reservas están fuera del rango dinámico.
4. Revisa si hay direcciones estáticas sin documentar o equipos con IP fija dentro del DHCP.
5. Verifica que cada VLAN tiene una subred y un propósito, sin equipos sueltos.
6. Mira los anuncios IPv6 y confirma quién puede enviarlos.

Una subred sin dueño ni propósito es un sitio donde cualquiera conecta lo que necesita, y eso convierte la separación en un dibujo.

## Segmentar no es bloquear

Dividir una red en subredes separa dominios de difusión y ordena el tráfico, pero no impide la comunicación por sí sola. Para que dos segmentos no se hablen hace falta que algo enrute y decida, y que exista una regla que lo impida.

El error más frecuente al presentar un diseño es enseñar muchas subredes y dar por hecho que la seguridad está resuelta. Sin control de acceso entre segmentos, la red sigue siendo plana a efectos prácticos.

## IPv6

IPv6 usa 128 bits, no tiene difusión y emplea multicast y descubrimiento de vecinos. Cada segmento recibe su prefijo y los equipos pueden configurarse solos con lo que anuncian los routers.

Para el bastionado plantea las mismas preguntas que IPv4 y añade una: quién puede anunciar prefijos y puertas de enlace. Un anuncio no autorizado desvía tráfico sin tocar la tabla de rutas de nadie.

## Enlaces punto a punto

Un enlace entre routers necesita dos direcciones. Los detalles de `/30`, `/31` y su encaje en un reparto ajustado están en [VLSM y reparto por sedes](vlsm-y-reparto-multisede.md). Desde el bastionado, lo importante es que los enlaces de gestión y de servicios no roben espacio a las zonas que deben existir.

## Qué comprobar

- Cada subred tiene un propósito documentado y una persona responsable.
- Las puertas de enlace y los servicios críticos están reservados fuera del rango dinámico.
- No hay solapamientos entre sedes, proveedores o redes heredadas.
- Las reglas de acceso entre segmentos existen y están justificadas.
- El direccionamiento IPv6 está planificado y sus anuncios están controlados.
- El plan se actualiza cuando se añade una sede, un servicio o una zona nueva.

## Errores que se repiten

- Suponer que segmentar aplica reglas de seguridad.
- Dejar el direccionamiento en la cabeza de una sola persona.
- Renumerar una red sin actualizar reglas, inventario y documentación.
- Mezclar el rango de invitados o de VPN con el de la red interna.
- Reservar direcciones «sobre la marcha» y perder el control del plan.

## Fuentes

- RFC 1918 (direcciones privadas), RFC 4632 (CIDR) y RFC 4291 (arquitectura IPv6).
- RFC 4861 (descubrimiento de vecinos en IPv6).
