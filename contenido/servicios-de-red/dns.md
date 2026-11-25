# DNS: el servicio que sostiene a los demás

Si el DNS falla, no falla un servicio: fallan todos. La web no encuentra su nombre, el correo no entrega, el dominio no autentica y el usuario concluye que «no hay internet». Es la pieza más pequeña y la que más veces se lleva la culpa de otra cosa.


## Qué hace

Traduce nombres a direcciones y devuelve otra información asociada a un dominio. La resolución es **jerárquica y distribuida**: un resolutor pregunta a la raíz, esta le indica el servidor del dominio de primer nivel, y así hasta el servidor autoritativo del dominio consultado. El resultado se guarda en caché durante el tiempo indicado por el TTL.

- **Servidor autoritativo:** guarda la zona del dominio y responde por ella. Es la fuente de la verdad.
- **Resolutor o recursivo:** pregunta por el cliente y cachea. No tiene la zona.
- **Reenviador:** el resolutor de la red, que reenvía a otro externo.

Mezclar los dos papeles en el mismo servidor es cómodo en un laboratorio y peligroso en una red: un resolutor abierto a Internet se usa para amplificar ataques. Un recursivo solo atiende a sus clientes; un autoritativo, a quien pregunte por su zona.

## Los registros que se usan

| Tipo | Qué declara |
|---|---|
| `A` / `AAAA` | Dirección IPv4 / IPv6 de un nombre |
| `CNAME` | Alias hacia otro nombre; no se pone en la raíz del dominio |
| `MX` | Servidores que reciben correo, con su prioridad |
| `TXT` | Texto libre: SPF, verificaciones de dominio |
| `NS` | Servidores autoritativos de la zona |
| `SOA` | Datos de la zona: servidor principal, contacto, tiempos |

Dos reglas que provocan la mitad de los errores: un `CNAME` no puede convivir con otros registros en el mismo nombre, y el TTL bajo se usa cuando se prevé un cambio inminente, no como costumbre, porque aumenta las consultas.

## Zona y delegación

Una **zona** es la parte del árbol que un servidor administra. Se declara en un fichero con su `SOA`, sus servidores y sus registros; en la configuración moderna se escribe con la herramienta del servidor y se valida antes de recargar.

Delegar un subdominio significa entregar su zona a otro servidor: se hace con registros `NS` en el padre. Es lo que permite que el departamento de sistemas gestione `aula.empresa.test` sin tocar la zona principal.

## Resolución en la práctica

- **Comprobar siempre por el servidor correcto.** Una consulta contestada por el resolutor de la operadora no demuestra nada sobre el DNS interno.
- **La caché engaña.** Un cambio reciente puede tardar en propagarse; el TTL decide cuánto. Antes de tocar nada, se comprueba si el problema es del servidor o de una copia antigua.
- **Registro inverso:** traducir dirección a nombre. El correo lo usa para decidir si un servidor es legítimo, y por eso un servidor de correo necesita su inverso configurado.

```bash
dig +short A intranet.empresa.test @10.0.0.53
dig +trace ejemplo.test          # solo tiene sentido en una zona pública
dig -x 10.0.0.20 +short
```

`dig` con `@servidor` evita la ambigüedad de no saber quién contestó; sin él, se consulta al resolutor del equipo, que puede tener una respuesta cacheada de hace horas.

## Seguridad del nombre

- **Restringir la recursión** a la red propia. Un resolutor abierto multiplica tráfico en un ataque de amplificación.
- **Actualizaciones dinámicas autenticadas.** Permitir que cualquier equipo registre su nombre en la zona es una forma sencilla de envenenar el DNS.
- **DNSSEC** firma los registros para que el receptor compruebe que la respuesta es auténtica. No cifra la consulta; verifica su origen.
- **Cifrado del transporte:** consultas por HTTPS o por TLS evitan que un intermediario lea qué dominios se consultan.
- **Registro de consultas** con retención: es la única forma de investigar después qué nombre resolvió un equipo comprometido.

## Lo que se comprueba

Que el servidor autoritativo responde por su zona y que el recursivo no atiende a Internet; que los registros publicados son los esperados, comprobados desde fuera de la red; que el inverso del servidor de correo coincide; que la zona valida antes de recargar; y que un cambio de registro se propaga en el tiempo previsto.

## Errores que se repiten

- Poner un `CNAME` en la raíz del dominio y romper el correo.
- Un TTL de un día y un cambio urgente.
- Resolutor abierto «para que funcione desde casa».
- Cambiar el DNS y no comprobar desde fuera.
- Diagnosticar por el navegador en lugar de consultar el registro concreto.

## Fuentes

- RFC 1034 y RFC 1035 (DNS), RFC 4033 a 4035 (DNSSEC).
- RFC 8484 (DNS over HTTPS) y RFC 7858 (DNS over TLS).
- Documentación oficial de BIND y Unbound.
