# IDS e IPS

Una alarma que salta por cualquier cosa acaba como la de un coche en una calle concurrida: nadie la mira. A una empresa le ocurrió con su sistema de prevención de intrusiones: no veía el tráfico cifrado y producía tantos avisos que el equipo aprendió a ignorarlos. Detectar es relativamente fácil; separar lo importante y reaccionar a tiempo, no.

El control de la red, la captura y el SIEM se presentan en [Control de la red](../seguridad-y-alta-disponibilidad/control-y-monitorizacion.md). Aquí se desarrollan los sensores de intrusión: qué diferencian, dónde se colocan, qué límites tienen y cómo se evita que se conviertan en decoración.

## Dos formas de estar en la red

| | IDS | IPS |
|---|---|---|
| Función | Detectar y alertar | Detectar y actuar |
| Situación | Fuera del camino, escuchando | En el camino, en línea |
| Efecto sobre el tráfico | Ninguno | Puede bloquear, descartar o cortar |
| Riesgo propio | No interviene | Un fallo puede cortar el servicio |

Los productos del mercado suelen ofrecer las dos funciones. Eso no cambia el diseño: el que solo observa no puede cortar nada, y el que está en línea y falla abierto se convierte en un pasillo libre.

## Cómo decide

- **Firmas.** Busca patrones de ataques ya conocidos. Acierta con lo viejo y no ve lo nuevo.
- **Anomalías.** Aprende cómo se comporta la red y avisa cuando algo se aparta. Cubre lo desconocido y produce más ruido.
- **Políticas y estado.** Comprueba reglas y coherencia de las sesiones.

Las tres se complementan. Las firmas aportan precisión sobre lo ya visto; las anomalías cubren lo que aún no tiene patrón; las políticas marcan qué se considera aceptable.

## Dónde vive el sensor

| Tipo | Dónde | Ventaja | Límite |
|---|---|---|---|
| NIDS (IDS de red) | Puerto espejo o TAP de un switch | No interfiere, ve un segmento entero | No bloquea |
| NIPS (IPS de red) | En línea entre zonas | Contiene en tiempo real | Puede ser cuello de botella |
| HIDS (IDS de host) | En el propio servidor | Ve lo que pasa dentro del host | Consume recursos, es intrusivo |
| HIPS (IPS de host) | En el host, con respuesta | Bloquea procesos y sesiones locales | Puede romper aplicaciones legítimas |

Para que un NIDS reciba tráfico hay que configurar el switch; conectarlo no basta. Un HIDS exige activar registros, lo que consume almacenamiento.

## Qué se busca

- Cargas con código malicioso conocido.
- Protocolos y servicios prohibidos: FTP o Telnet donde no debería haberlos.
- Secuencias que corresponden a un ataque conocido: escaneos, fuerza bruta, explotación.
- En el host: cambios en ficheros críticos, procesos anómalos, cuentas nuevas, escalada de privilegios.

## Lo que no puede hacer

- **Cifrado.** Sin inspección TLS, el sensor ve paquetes y no contenido. Inspeccionar exige terminación, base jurídica y capacidad de cómputo.
- **Retraso de firmas.** Entre que aparece una amenaza y se publica la regla hay una ventana que el atacante aprovecha.
- **Falsos positivos y negativos.** Los primeros gastan el tiempo del analista; los segundos son el fallo grave, porque dan tranquilidad sin protección.
- **Volumen.** Varios sensores sin correlación producen un muro de alertas que nadie atiende.

## Evasión

- **Inserción:** el atacante manipula paquetes para que el sensor y el destino lean cosas distintas.
- **Fragmentación:** parte el ataque en trozos que no coinciden con ninguna firma.
- **Canales encubiertos:** esconde datos en campos que el sensor no revisa.
- **Suplantación:** disfraza el tráfico malicioso de legítimo.
- **Ataques al sensor:** lo satura, llena sus registros o provoca su modo de fallo. Un sensor que se desconecta al fallar deja de proteger justo cuando hace falta.

Probar estas técnicas sobre una red exige autorización y un alcance acordado. No es una comprobación que se hace «para ver qué pasa» en un entorno ajeno.

## Qué automatizar

Las acciones posibles van de descartar un paquete a cerrar la sesión, bloquear una dirección o una cuenta, registrar el evento o avisar. Elegir cuál se automatiza depende de lo que cuesta equivocarse: cortar una IP sospechosa tiene poco coste; dejar sin cuenta a un empleado por un falso positivo, mucho.

## Dónde encaja hoy

Hoy el sensor de red comparte trabajo con el registro de terminales (EDR), la correlación de un SIEM y el análisis de metadatos (NDR). Snort, Suricata y Zeek son las referencias libres. La decisión de diseño no está en el producto, sino en lo que se hará con la alerta.

## Qué comprobar

- ¿Hay sensores en los puntos donde el tráfico cambia de zona?
- ¿Están afinados y alguien revisa los avisos?
- ¿Se sabe qué pasa con el tráfico cifrado?
- ¿El IPS falla abierto o cerrado, y está decidido a propósito?
- ¿Las alertas llegan a un registro central con contexto suficiente?
- ¿Hay un procedimiento para cerrar un falso positivo sin apagar la regla?

## Errores que se repiten

- Comprar un IPS y no asignar a nadie su ajuste.
- Colocar un NIDS en un puerto de usuario y creer que ve toda la red.
- Bloquear automáticamente cualquier alerta y tumbar servicios legítimos.
- Ignorar el tráfico cifrado y dar por cubierta la aplicación.
- Medir el éxito por número de alertas en lugar de por incidentes atendidos.

## Fuentes

- NIST SP 800-94, *Guide to Intrusion Detection and Prevention Systems*.
- Snort, Suricata y Zeek: documentación oficial.
- MITRE ATT&CK: técnicas de evasión de defensas (TA0005).
- INCIBE. Guías de monitorización y detección.
