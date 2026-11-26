# Protocolos de seguridad Wi-Fi

Cada generación de seguridad Wi-Fi ha tapado el agujero de la anterior y ha dejado otro a la vista, como una casa que cambia la cerradura de la puerta y se olvida de la ventana. WEP falló en el diseño, WPA fue un parche sobre hardware viejo y WPA2 acertó con el cifrado pero dejó la contraseña como único secreto. Repasar esa cadena es la mejor forma de entender por qué hoy se configura como se configura y por qué atacar una red WPA2 suele significar atacar a una persona.

## El error de repetir la hoja de cifrado

Un cifrador de flujo, como RC4, fabrica una secuencia de bits aparentemente aleatoria, el keystream, y la combina bit a bit con el mensaje mediante XOR. La operación se deshace a sí misma: si el mensaje es 1011 y el keystream 0110, el cifrado es 1101, y 1101 XOR 0110 devuelve 1011. El peligro es la otra cara: si dos mensajes se cifran con el mismo keystream, al hacer XOR de los dos cifrados el keystream se cancela y queda la XOR de los dos originales. Con una parte previsible en uno de ellos, se deduce la del otro.

Por eso un nonce —un número que se usa una sola vez con una clave, no necesariamente secreto— no puede repetirse. Imagine un cuaderno de hojas de cifrado de un solo uso: la clave es el cuaderno y el nonce es el número de hoja. Usar dos veces la misma hoja equivale a dejar de proteger, y ahí empieza la historia de WEP.

## WEP: un diseño que falló en cada pieza

WEP fue el cifrado del estándar original de 1997 y de 802.11b. Todos los dispositivos comparten una clave estática de 40 o 104 bits. Para cada trama, el emisor genera un vector de inicialización (IV) de 24 bits, lo une a la clave, alimenta RC4 con el resultado y hace XOR del keystream con el mensaje y su CRC-32. El IV viaja en claro para que el receptor repita el cálculo.

| Lo que prometía | Por qué falla |
|---|---|
| Confidencialidad con RC4 | El IV de 24 bits se repite; dos tramas con el mismo IV comparten keystream |
| Integridad con CRC-32 | El CRC no lleva clave y es lineal: se modifica el mensaje y se recalcula |
| Autenticación del AP | El AP no se autentica ante el cliente; un AP falso es indistinguible |
| Clave compartida sencilla | No hay gestión de claves ni protección contra repeticiones |

Sus fallos se suman. Hay 2²⁴ ≈ 16,7 millones de IV posibles y, por la paradoja del cumpleaños, hacia las 5.000 tramas la probabilidad de repetir uno supera el 50 %; en una red activa ocurre en segundos. Ciertos IV débiles filtran información sobre la clave: Fluhrer, Mantin y Shamir lo mostraron en 2001, KoreK refinó los ataques en 2004 y el equipo de Tews los redujo en 2007 a decenas de miles de tramas. La clave es la misma para todos y para siempre, y una trama capturada puede reenviarse.

En 2004 el estándar declaró WEP obsoleto. Configurarlo equivale a no cifrar y un auditor lo registra como hallazgo crítico. Sigue apareciendo en equipos heredados —escáneres de almacén, impresoras, controladores industriales— que se sustituyen o se aíslan en un segmento sin acceso a nada valioso. Las lecciones de diseño son tres: no reutilizar un nonce con un cifrador de flujo, usar un código de integridad con clave y derivar claves de sesión en lugar de compartir una estática.

## WPA y TKIP: un parche con fecha de caducidad

Cuando WEP cayó, la enmienda definitiva (802.11i) aún tardaría años y millones de tarjetas solo sabían hacer RC4 por hardware. La Wi-Fi Alliance publicó en 2003 WPA como solución intermedia, actualizable por firmware. Su cifrado, TKIP (*Temporal Key Integrity Protocol*), mantiene RC4 y corrige lo más grave:

- **Clave por paquete:** cada trama deriva una clave distinta de la clave temporal, la dirección del emisor y un contador de 48 bits.
- **Contador de secuencia (TSC):** descarta tramas repetidas.
- **Integridad Michael:** un MIC de 64 bits con clave que sustituye al CRC. Se diseñó para hardware limitado y su seguridad efectiva se estima en unos 20 bits.
- **Contramedidas:** si se detectan dos fallos de integridad en 60 segundos, la red corta las conexiones y espera un minuto. El precio es que cualquiera puede provocar esa caída a propósito.
- **Gestión de claves por sesión:** el mismo handshake de cuatro mensajes de WPA2, con clave compartida o con 802.1X.

TKIP fue razonable con fecha de caducidad. Sigue basado en RC4, cuyos sesgos se han explotado; en 2008 Beck y Tews demostraron descifrado de tráfico corto e inyección en redes con calidad de servicio. El estándar lo declaró obsoleto en 2012 y no admite las velocidades de 802.11n y posteriores. Una red que se anuncia como WPA2 pero no pasa de 54 Mb/s suele estar usando TKIP.

## WPA2: AES-CCMP y el handshake de cuatro mensajes

La enmienda 802.11i (2004) y su certificación WPA2 trajeron CCMP, que usa AES en modo CCM: una clave de 128 bits cifra los datos y calcula un código de integridad que cubre el contenido y partes relevantes de la cabecera. Cada trama lleva un contador de 48 bits que hace de nonce y de protección contra repeticiones. No se conoce un ataque práctico contra AES-CCMP en sí; TKIP quedó como opción de compatibilidad que conviene desactivar.

Por eso, cuando se ataca una red WPA2 no se ataca el cifrado, sino la gestión de claves y a las personas. En WPA2-Personal (PSK, *Pre-Shared Key*) todos los dispositivos conocen una contraseña de 8 a 63 caracteres. En WPA2-Enterprise cada usuario se autentica con 802.1X contra un servidor. En ambos casos, cliente y AP comparten una PMK (*Pairwise Master Key*) de 256 bits sin enviarla nunca y derivan de ella claves de sesión.

En modo Personal la PMK se calcula con PBKDF2-HMAC-SHA1, 4.096 iteraciones y el SSID como sal. Las iteraciones encarecen cada intento de forma moderada, y como el SSID es la sal, la misma contraseña produce PMK distintas en redes con nombre distinto: los diccionarios precalculados solo sirven para nombres muy comunes, como los de fábrica.

Cada vez que alguien se conecta, AP y cliente mezclan la PMK con dos nonces nuevos (ANonce y SNonce) y las dos MAC para obtener la PTK (*Pairwise Transient Key*). La PTK se divide en KCK, que firma los mensajes del handshake; KEK, que protege la clave de grupo; y TK, que cifra los datos. Los nonces y las MAC viajan en claro; la PMK y la PTK no.

**El handshake de cuatro mensajes**, en tramas EAPOL-Key:

| Mensaje | Quién lo envía | Qué lleva | Qué demuestra |
|---|---|---|---|
| 1 | AP | ANonce | Inicia la derivación de la PTK |
| 2 | Cliente | SNonce y MIC | Que el cliente conoce la PMK |
| 3 | AP | MIC y GTK cifrada | Que el AP conoce la PMK y reparte la clave de grupo |
| 4 | Cliente | Confirmación | Que la instalación terminó y empieza el tráfico |

## La contraseña es el eslabón débil

Quien escucha el handshake captura los nonces, las MAC y los MIC, pero no la PMK. Puede, en cambio, inventar una contraseña, calcular su PMK, su PTK y el MIC, y compararlo con el capturado. Si coincide, la contraseña era esa. Todo ocurre en su equipo, sin conectarse ni enviar nada: es un ataque fuera de línea, sin límite de intentos ni registro en el AP, y se reparte bien entre procesadores de una tarjeta gráfica.

Para tener un orden de magnitud, y sin que sean medidas de un equipo concreto: ocho letras minúsculas dan 26⁸ ≈ 2,1 · 10¹¹ combinaciones, que una GPU actual agotaría en pocos días; cuatro palabras al azar de una lista de 7.776 ofrecen unos 52 bits (≈ 3,7 · 10¹⁵ combinaciones) y exigirían siglos al mismo ritmo. Lo decisivo no es la longitud nominal sino la imprevisibilidad: «Pirineos2019!» cae en minutos ante un diccionario con reglas.

De ahí salen tres corolarios que los clientes rara vez conocen:

- WPA2-Personal no da secreto hacia adelante: quien descubra la contraseña después puede descifrar el tráfico grabado antes, si conserva los handshakes.
- Cualquiera que conozca la contraseña puede capturar el handshake de otro cliente y leer su tráfico; el aislamiento de clientes no lo impide, porque el ataque es pasivo.
- Como el handshake se repite en cada conexión, se puede forzar una reconexión con desautenticaciones falsas, salvo que se use PMF, la protección de tramas de gestión que explico en [Comunicación inalámbrica](comunicacion-inalambrica.md).

## PMKID: sin ningún cliente conectado

En 2018 Jens Steube observó que muchos AP incluyen en el primer mensaje EAPOL un identificador, el PMKID, calculado con la PMK y las direcciones de AP y cliente para el roaming rápido. Ese valor permite verificar contraseñas igual que el MIC, sin que haya ningún cliente conectado: basta con iniciar una asociación. La defensa es la misma: contraseña larga e imprevisible, WPA3 o 802.1X.

## Otros fallos que conviene situar

- **WPS.** El PIN de ocho dígitos se verifica en dos mitades y el último dígito es una suma de comprobación: el espacio real es 10⁴ + 10³ = 11.000 intentos. En 2014 se añadió un ataque fuera de línea contra chips con generadores débiles (Pixie Dust). La defensa es desactivar el PIN.
- **KRACK (2017).** Vanhoef y Piessens forzaron la reinstalación de una clave ya usada retransmitiendo el mensaje 3; el contador volvía a cero y se reutilizaba el keystream. No revela la contraseña, pero permite descifrar e inyectar. Se corrigió con parches.
- **FragAttacks (2021).** Fallos de diseño e implementación en la fragmentación y agregación de tramas que afectaban a todos los protocolos, incluido WPA3. La defensa es actualizar y cifrar también en capas superiores.

## Por qué importa a quien defiende

Una red WPA2 defendible usa contraseña larga y aleatoria —veinte caracteres o una frase de seis palabras—, SSID propio, WPS desactivado, solo AES-CCMP sin TKIP, PMF habilitado, firmware al día, red de invitados separada, cambio de contraseña cuando se va alguien con acceso y, si se puede, 802.1X o WPA3.

Al auditar, lo que anoto es igual de concreto:

- Una red con WEP o TKIP es un hallazgo, aunque el resto de la configuración parezca correcta.
- El handshake o el PMKID se capturan solo con autorización escrita; tenerlos no es tener la contraseña, es el material para probarla.
- Un WPS activo reduce la seguridad a once mil intentos y merece una recomendación inmediata.
- La contraseña se evalúa por imprevisibilidad, no por los símbolos que muestre el formulario.
- Sin PMF, la red es vulnerable a cortes provocados y a la captura forzada del handshake.

## Errores frecuentes

- Decir que «WPA2 está roto»: su cifrado sigue siendo fuerte; lo vulnerable es la contraseña o una implementación sin parchear.
- Creer que capturar el handshake equivale a tener la contraseña: es el material para probarla.
- Suponer que una contraseña compleja para una persona resiste a un diccionario con reglas.
- Mantener TKIP «por compatibilidad» y pagar seguridad y rendimiento a la vez.
- Confundir un fallo de protocolo con uno de implementación: KRACK se corrigió sin cambiar el estándar.
- Desactivar PMF para que conecten equipos antiguos sin valorar el riesgo.

## Glosario

| Término | Definición |
|---|---|
| EAPOL | Tramas del intercambio 802.1X que transportan el handshake de WPA. |
| CCMP | Cifrado de WPA2 basado en AES. |
| MIC | Código que comprueba que una trama no se ha alterado. |
| GTK | Clave de grupo que el punto de acceso comparte con las estaciones. |
| KCK / KEK / TK | Claves derivadas del handshake para integridad, cifrado de claves y tráfico. |
| PBKDF2 | Función de derivación que convierte la contraseña en la PMK. |
| PMK / PTK | Clave maestra y clave de sesión derivada de ella. |
| TKIP | Cifrado intermedio de WPA, obsoleto. |
| WPS | Emparejamiento rápido por PIN; se desactiva. |

## Fuentes

- IEEE 802.11i; Wi-Fi Alliance, certificación WPA2.
- Vanhoef y Piessens, «Key Reinstallation Attacks» (2017); Vanhoef, «Fragment and Forge» (2021).
- Fluhrer, Mantin y Shamir (2001); Tews, Weinmann y Pyshkin (2007).
