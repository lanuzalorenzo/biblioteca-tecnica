# Análisis de logs e informe

Un montón de fotos sueltas no cuenta una historia; una línea de tiempo sí. El análisis forense ordena los rastros de la memoria, los registros y el disco hasta reconstruir qué pasó y en qué orden. El informe es la última pieza: lo que no se explica con claridad no sirve como prueba.

## Qué aporta la memoria

La RAM guarda procesos, conexiones, usuarios, claves y malware *fileless*; es la evidencia más volátil y se captura antes que el disco. La captura en vivo no es una foto instantánea y debe documentarse como tal.

El detalle —herramientas, hash, Volatility 3 y plugins— está en [Volcado y análisis de memoria RAM](volcado-y-analisis-de-memoria-ram.md).

## Análisis de logs

Un log es un registro de eventos en un rango de tiempo. Cada entrada incluye fuente, descripción del suceso, prioridad, fecha y hora. Son evidencias digitales de primer orden porque permiten reconstruir la secuencia sin depender de la memoria.

**Windows.** Los logs más relevantes:

| Ruta | Contenido |
|---|---|
| `%WINDIR%\System32\winevt\Logs` | Visor de eventos |
| `%WINDIR%\WindowsUpdate.log` | Actualizaciones (obsoleto desde Windows 10; hoy se consulta en el visor) |
| `%WINDIR%\Logs\CBS\CBS.log` | Windows Resource Protection |
| `%WINDIR%\INF\setupapi.dev.log` | Service packs y hotfixes |

**Linux.** Todos bajo `/var/log/`:

| Fichero | Contenido |
|---|---|
| `syslog` o `messages` | Mensajes generales, según distribución |
| `auth.log` | Conexiones e intentos de acceso, incluido root |
| `kern.log` | Mensajes del kernel |
| `httpd/access_log` | Eventos de Apache |
| `mysql/error.log` | Eventos de MySQL |

En Linux los logs están centralizados en `/var/log/`, lo que facilita el trabajo. La ruta exacta depende de la distribución: Debian y Ubuntu usan `syslog`; RHEL, `messages`; Apache y MySQL cambian de subdirectorio. En Windows están más dispersos y cambian según la versión.

Las herramientas de adquisición y análisis de logs están en la tabla de [metodología y adquisición](metodologia-adquisicion-y-custodia.md). Un SIEM ayuda a correlacionar, pero no sustituye la lectura del analista.

## El informe forense

El informe presenta los resultados y responde a las cinco preguntas iniciales: qué pasó, dónde, quién estuvo implicado, cuándo y con qué medios. Tiene dos partes:

1. **Resumen ejecutivo.** Conclusiones principales, sin tecnicismos, para dirección o juez.
2. **Desglose técnico.** Proceso completo, evidencias, análisis, conclusiones y justificación.

El elemento central es la **línea de tiempo**: la cronología ordenada de los eventos. Sin ella, los hallazgos son una lista de piezas sin relación.

El informe debe incluir además:

- Origen probable del incidente y qué lo desencadenó.
- Hechos y evidencias que sostienen cada conclusión.
- Actores y motivaciones posibles.
- Datos personales comprometidos, si los hay, y su impacto en confidencialidad, integridad y disponibilidad, conforme al RGPD.

Un informe que afirma más de lo que la evidencia permite es peor que un informe incompleto: destruye la credibilidad del resto.

## Cómo se arma la línea de tiempo

La línea de tiempo se construye uniendo fuentes con relojes distintos:

1. **Fijar la referencia.** Anotar la zona horaria y el desfase de cada fuente; un evento en UTC y otro en hora local no se pueden ordenar sin corregirlo.
2. **Extraer los eventos.** Procesos, conexiones, accesos, cambios de fichero y entradas de log, cada uno con su origen.
3. **Normalizar el formato.** Misma unidad y mismo formato de fecha para poder ordenar.
4. **Ordenar y agrupar.** Buscar ráfagas: varios eventos en segundos suelen ser la misma acción.
5. **Contrastar.** Un evento aislado es un indicio; dos fuentes independientes que coinciden son una conclusión defendible.

Los relojes de los equipos pueden estar desviados. Si la desviación es conocida, se corrige y se deja constancia; si no, se marca la incertidumbre en el informe en lugar de inventar una precisión que no existe.

## Lo que sostiene el análisis

- La memoria aporta procesos, red, usuarios, claves y malware *fileless*; se captura antes que el disco.
- `hiberfil.sys` complementa, no sustituye al volcado.
- Los logs de Windows y Linux permiten reconstruir la secuencia.
- El informe tiene resumen ejecutivo y desglose técnico.
- La línea de tiempo es la pieza que une hechos y evidencias.
- Toda conclusión debe poder sostenerse con la evidencia citada.

## Fuentes

- ISO/IEC 27037:2012 e ISO/IEC 27043:2015: preservación de la evidencia e investigación de incidentes.
- NIST. *SP 800-86, Guide to Integrating Forensic Techniques into Incident Response*.
- Volatility 3 Documentation: plugins y análisis de memoria.
- RFC 3227: orden de volatilidad y recogida de evidencia.
- RGPD, en lo relativo a datos personales comprometidos.
