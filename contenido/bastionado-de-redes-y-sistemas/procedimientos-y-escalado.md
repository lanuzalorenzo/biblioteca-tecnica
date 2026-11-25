# Procedimientos, indicadores y escalado

Ante una alarma de incendios, el personal no busca al responsable para saber dónde está el extintor: sigue un plan y una cadena de mando. Un incidente de seguridad necesita lo mismo. Sin un proceso escrito, el aviso llega a quien está más cerca o a nadie, y la respuesta depende de la suerte.

Las medidas técnicas no bastan si no hay quien decida qué hacer con ellas. Este apunte describe cómo se convierte una intención en una respuesta repetible: qué es un proceso, cómo se clasifica un incidente, a quién se escala y cómo se mide.

## Anatomía de un proceso

Un proceso se puede ejecutar y mejorar cuando está descrito con sus entradas, sus salidas, su dueño y sus medidas. La gestión de incidentes en un centro de operaciones de seguridad es un buen ejemplo. Los elementos que no pueden faltar son:

| Elemento | Qué responde | Ejemplo |
|---|---|---|
| Nombre | Qué proceso es | Gestión de incidentes |
| Propietario | Quién responde de él | Responsable de seguridad |
| Destinatario | Para quién trabaja | Usuarios, personal, clientes |
| Objetivo | Qué resultado busca | Recibir, clasificar y resolver incidentes |
| Entradas | De dónde llega el trabajo | Correo, llamadas, formulario |
| Salidas | Qué produce | Informes, estadísticas, cierres |
| Recursos humanos | Quién lo ejecuta | Responsable y técnicos de nivel 1 y 2 |
| Recursos tecnológicos | Con qué se hace | Cola de incidencias, máquinas de prueba, cuadros de mando |
| Mecanismos de control | Cómo se supervisa | Informes de seguimiento, tiempo de respuesta |
| Indicadores | Cómo se mide | Incidentes resueltos, media de resolución |

El proceso es una cadena de entrada, procesado y salida. Sin propietario, nadie decide; sin indicadores, nadie sabe si mejora.

## Tres palabras que se confunden

- **Evento:** un cambio de estado significativo en la infraestructura. La alerta es el aviso que genera.
- **Evento de seguridad:** un evento que incumple una política o directiva de seguridad.
- **Incidente de seguridad:** uno o varios eventos no deseados o no previstos que pueden poner en riesgo sistemas o información.

La diferencia decide la respuesta. No se trata igual una alerta informativa que un incidente confirmado.

## Subir el aviso

Antes de avisar a alguien hay que clasificar. Influyen el sistema afectado, su criticidad y la información comprometida. La taxonomía de INCIBE-CERT es una referencia habitual para ordenar tipos y gravedad.

Con la clasificación hecha se aplica el procedimiento de escalado. Un ejemplo con dos niveles:

- Gravedad baja, media y alta: las resuelve el soporte de nivel 1.
- Gravedad muy alta y crítica: pasan al soporte de nivel 2.

Ningún método sirve para todos: la tipología cambia con la tecnología y cada organización adapta la suya. Lo que no puede faltar es que el procedimiento diga **quién decide, a quién se avisa y en cuánto tiempo**.

## Cerrar y resolver no son lo mismo

El cierre administrativo y la solución técnica son cosas distintas. Un caso incómodo: un ransomware sin herramienta de descifrado y sin copia de seguridad. El incidente se cierra, pero el problema sigue ahí; pagar al atacante no forma parte de la solución.

Por eso se separan dos estados:

- **Resuelto:** la causa se ha eliminado y el servicio funciona.
- **Cerrado:** no queda intervención pendiente, aunque el resultado haya sido negativo.

Un cierre sincero deja aprender algo. Si se anota «resuelto» cuando no lo está, las métricas mienten y el riesgo desaparece del informe sin desaparecer de la realidad.

## Medir para redimensionar

El proceso necesita números:

- Incidentes resueltos por día.
- Media de tiempo de resolución.
- Tiempo hasta la primera respuesta.
- Porcentaje de incidentes que escalan de nivel.
- Reincidencia por tipo.

Con esos datos se decide si falta personal, formación, otra herramienta o un procedimiento distinto. Los indicadores no son un adorno del informe: son la señal para cambiar el proceso.

Un indicador sin umbral no sirve. Cada uno necesita un valor normal, uno de aviso y uno de actuación, decididos antes del incidente, y una persona con nombre y hora asignada para mirarlo.

## Ejemplo

Una empresa recibe el aviso de que su servidor web responde con lentitud. El evento entra por la cola, se clasifica como gravedad media y lo toma el nivel 1. Al revisar los registros, el técnico ve intentos de autenticación repetidos y lo reclasifica como alto. El nivel 2 contiene el acceso, cambia credenciales y comprueba si hubo movimiento lateral. El incidente se cierra cuando el servicio vuelve y la causa está eliminada; si solo se hubiera reiniciado el servidor, estaría cerrado pero no resuelto.

## Errores que se repiten

- Llamar incidente a cualquier alerta y saturar al equipo.
- Escalar sin clasificar antes.
- Cerrar por cansancio y anotar «resuelto».
- Medir solo el tiempo y no la reincidencia.
- Tener un procedimiento que nadie ha leído ni probado.
- No dejar constancia de quién decidió y cuándo.

## Fuentes

- INCIBE-CERT. Taxonomía y guía de gestión de incidentes.
- RTIR (*Request Tracker for Incident Response*) y otras herramientas de gestión de incidentes.
