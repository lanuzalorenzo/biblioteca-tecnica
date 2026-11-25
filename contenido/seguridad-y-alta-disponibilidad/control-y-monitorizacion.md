# Seguridad activa: control de la red

Poner cámaras en un pasillo no impide el robo, pero cambia lo que se puede hacer después. En una red, la monitorización cumple ese papel: ver qué pasa, detectar lo que no cuadra y dejar rastro para reconstruirlo. Sin ella, un incidente se descubre por sus consecuencias.


## Ver la red desde dentro

Dos aproximaciones distintas:

- **Contadores:** cuántos bytes y paquetes pasan por una interfaz, agrupados por puerto y protocolo. Cuestan poco, no guardan el contenido y sirven para saber si lo que ocurre es normal. Se consultan por SNMP; en versión 1 y 2c el tráfico viaja sin cifrar, así que en producción se usa SNMPv3 con autenticación.
- **Captura:** copiar los paquetes y analizarlos. Da el detalle y consume CPU y disco. Herramientas: `tcpdump` en consola, Wireshark para leer la captura.

Para capturar en un switch gestionable no se intercala un hub —el apaño que se usaba en 2015 ya no tiene sentido con conmutación—: se configura **espejo de puertos** (SPAN en Cisco, port mirroring en el resto), que replica el tráfico de uno o varios puertos hacia el de análisis.

## De los datos a las conclusiones

Capturar es fácil; interpretar, no. De ahí que existan sistemas que aplican reglas sobre el tráfico:

- **IDS:** analiza y avisa. Se coloca fuera del camino del tráfico, mirando una copia.
- **IPS:** además bloquea. Va en línea, y por eso un falso positivo corta servicio.

Dos formas de decidir qué es un ataque:

- **Por firmas:** patrones conocidos. Preciso con lo que ya se ha visto, ciego ante lo nuevo. Snort y Suricata son las referencias.
- **Por comportamiento:** se aprende lo normal y se avisa de la desviación. Detecta lo desconocido y genera más ruido.

Un IDS sin nadie que lo ajuste termina ignorado: el trabajo real es reducir falsos positivos y decidir qué se atiende. Lo que sostiene el conjunto es un **SIEM** que recoge registros de red, equipos y aplicaciones, los correlaciona y conserva. La hora de todos ellos tiene que venir del mismo origen (NTP); sin eso, relacionar dos eventos es imposible.

## VPN: el túnel

Una red privada virtual lleva tráfico privado por una red pública. Dos escenarios:

- **Sitio a sitio:** une dos sedes de forma permanente. El túnel lo levantan los routers o cortafuegos.
- **Acceso remoto:** un usuario suelto entra en la red de la empresa desde cualquier sitio.

Y dos familias de tecnología:

| Familia | Qué usa | Cuándo encaja |
|---|---|---|
| IPsec | IKEv2 para negociar, ESP para cifrar | Interoperabilidad, sitio a sitio, exigencia de norma |
| TLS | OpenVPN y similares, sobre TCP o UDP | Atraviesa redes restrictivas con facilidad |
| WireGuard | Curva25519 y ChaCha20, muy simple | Enlaces modernos, configuración mínima y auditable |

La práctica de 2015 montó una VPN de acceso remoto y otra entre hosts. Lo que ha cambiado es la herramienta y el criterio: WireGuard ha desplazado a las configuraciones largas de OpenVPN en muchos despliegues, y el certificado de servidor se ha vuelto obligatorio también dentro. Lo que no ha cambiado: una VPN solo cifra el trayecto; no autentica al usuario ni limita a qué puede acceder una vez dentro. Eso lo hace la segmentación.

## Anonimato: TOR

TOR enruta el tráfico por tres saltos —entrada, intermedio y salida— de forma que ningún nodo conoce a la vez quién eres y a dónde vas. Su uso legítimo incluye periodismo, investigación y acceso a servicios bloqueados; el mismo diseño sirve para delinquir, y esa dualidad es la que hace su tratamiento delicado.

Límites que conviene tener claros:

- El nodo de salida ve el tráfico si el destino no va por HTTPS; TOR no cifra el extremo final, solo el camino hasta la salida.
- No protege del propio equipo, de una sesión iniciada con identidad real ni de un fallo de configuración que escape del proxy.
- Su uso en una red corporativa suele estar prohibido por política, y detectarlo es parte del trabajo de control.

La práctica de 2015 se hizo para entender el mecanismo, no como herramienta operativa. Rehacerla hoy exige fijar antes el alcance: qué se prueba, en qué red y con qué autorización.

## Lo que se mide y con qué se queda

Un cuadro de mando mínimo: disponibilidad de enlaces, errores y descartes por interfaz, ocupación de las subredes críticas, sesiones activas por usuario, alertas del IDS por severidad y eventos de autenticación fallida. De todo lo que se puede medir, solo se conserva lo que alguien va a mirar o lo que una norma obliga a guardar.

Medir sin umbral no sirve: cada indicador necesita un valor normal, uno de aviso y uno de actuación, decididos antes de que ocurra el incidente. Y una persona con nombre y hora asignada para mirarlo, porque un cuadro de mando que nadie abre es decoración.

## Errores que se repiten

- Mirar un IDS sin ajustarlo y acabar ignorándolo.
- Capturar en un puerto de usuario y creer que se ve toda la red: sin espejo de puertos solo se ve lo que pasa por esa boca.
- Dejar los registros de red en el propio equipo comprometido.
- Dar por hecho que una VPN protege un puesto: el túnel acaba en la red interna, no en una jaula.

## Fuentes

- RFC 4301 (IPsec) y RFC 5905 (NTP).
- Documentación oficial de Snort, Suricata, Wireshark y WireGuard.
- Especificación de TOR y su documentación de diseño.
