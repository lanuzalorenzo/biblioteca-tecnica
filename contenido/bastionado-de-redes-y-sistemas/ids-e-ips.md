# IDS e IPS

Una alarma que salta por cualquier cosa acaba como la de un coche en una calle concurrida: nadie la mira. A una empresa le ocurrió con su sistema de prevención de intrusiones: no veía el tráfico cifrado y producía tantos avisos que el equipo aprendió a ignorarlos. Detectar es relativamente fácil; separar lo importante y reaccionar a tiempo, no.

La diferencia entre detectar y bloquear, los métodos de análisis y la colocación de los sensores se explican en [Control de la red](../seguridad-y-alta-disponibilidad/control-y-monitorizacion.md). Aquí se trata lo que convierte un sensor en un control útil: cobertura, ajuste, modo de fallo y destino de las alertas.

## Qué se le pide

Un IDS observa y avisa; un IPS observa y actúa. En el diseño importa menos la etiqueta del producto que la respuesta a tres preguntas:

- ¿Qué tráfico ve y cuál se queda fuera?
- ¿Quién decide que una alerta es importante?
- ¿Qué ocurre cuando el sensor falla?

Si no hay respuesta para las tres, el sensor está instalado pero no integrado.

## Qué ve el sensor

Un sensor solo protege lo que ve. La cobertura se decide por zonas, no por número de dispositivos:

- **Borde:** tráfico entre Internet y la organización.
- **Entre segmentos:** el paso entre usuarios, servidores, DMZ y gestión.
- **Host:** lo que ocurre dentro de un servidor crítico y no se ve en la red.
- **Puntos ciegos:** tráfico cifrado, redes de invitados y dispositivos que nunca pasan por el sensor.

La pregunta de auditoría no es «¿cuántos sensores hay?», sino «¿qué flujo importante no pasa por ninguno?».

## Ajuste

Un sensor sin ajuste produce ruido y se acaba ignorando. El trabajo real es un ciclo:

1. Partir de una base de reglas adecuada al entorno.
2. Observar durante un periodo y separar lo normal de lo anómalo.
3. Silenciar o afinar lo que genera falsos positivos sin perder el caso real.
4. Asignar un dueño a cada regla o grupo de reglas.
5. Revisar periódicamente lo silenciado, porque el entorno cambia.

El ajuste no termina nunca. Una regla que se apaga «porque molestaba» y no se vuelve a mirar es una ceguera permanente.

## Modo de fallo

Un IPS en línea puede fallar abierto o cerrado:

- **Abierto:** si el sensor cae, el tráfico sigue. Se protege la disponibilidad y se pierde la inspección.
- **Cerrado:** si el sensor cae, el tráfico se corta. Se protege la inspección y se arriesga el servicio.

La decisión se toma antes del incidente y se documenta. También hay que prever la alta disponibilidad y el bypass: un IPS que se convierte en cuello de botella o en un punto único de fallo acaba retirándose.

## Tráfico cifrado

Sin inspección TLS, el sensor ve paquetes y no contenido. Inspeccionar exige terminar la conexión en un punto controlado, capacidad de cómputo y una base jurídica clara. Si no se inspecciona, hay que asumir el límite y compensarlo con registro de terminales, metadatos y análisis de flujo.

La alternativa no es ignorar el cifrado, sino saber qué se está perdiendo y decirlo.

## Alertas

Una alerta sin destino es un registro que nadie lee. El circuito mínimo:

- Severidad y criterio de escalado.
- Envío a un registro central con contexto: origen, destino, regla, hora.
- Procedimiento para cerrar un falso positivo sin apagar la regla.
- Retención definida y hora sincronizada.
- Responsable con nombre y turno.

El SIEM correlaciona, pero no sustituye al criterio. Un muro de alertas sin prioridad es el mismo problema con otra herramienta.

## Qué exigir en la compra

- Cobertura declarada y límite de caudal sin pérdida de paquetes.
- Modo de fallo configurable y bypass.
- Actualización de firmas y soporte con plazos.
- Exportación de registros y integración con el SIEM.
- Capacidad de inspección TLS, si el caso la justifica.
- Documentación de las reglas y de su mantenimiento.

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
