# Volcado y análisis de memoria RAM

La memoria es la libreta donde el sistema apunta lo que está haciendo: quién trabaja, qué habla con quién y qué ha ejecutado. Si se apaga el equipo, esa libreta se borra. Por eso, cuando hay que reconstruir un incidente, la memoria se captura antes que cualquier otra cosa.

## Por qué empezar por la memoria

La RAM es la evidencia más volátil del sistema: al apagar o reiniciar se pierde. En ella viven los procesos y sus argumentos, las conexiones de red, los usuarios con sesión abierta, el historial de consola, claves y certificados en uso, y el malware que nunca toca el disco (*fileless*). Todo eso no se recupera después con un análisis del disco.

La contrapartida es que la captura en vivo no es una foto instantánea: la memoria cambia mientras se copia y la propia herramienta de volcado ocupa memoria. El volcado es una aproximación documentada, no una copia exacta de un estado inmutable. Las páginas que el sistema tiene en swap o comprimidas pueden no aparecer.

## Antes de volcar

- **Autorización y alcance.** La memoria contiene datos personales, credenciales y conversaciones. El volcado debe ampararse en una autorización escrita y limitarse al alcance acordado.
- **Registro previo.** Anotar hora, operador, equipo, RAM instalada, sistema operativo, versión del kernel, herramienta y versión.
- **Medio externo.** Ejecutar la herramienta desde un USB de solo lectura y escribir el volcado en otro medio con espacio suficiente —como mínimo, la RAM instalada—. No instalar nada ni escribir en el disco analizado.
- **No apagar ni hibernar.** La hibernación reescribe `hiberfil.sys` y puede destruir el estado que se quiere capturar.
- **Red.** Aislar el equipo preserva el sistema, pero corta sesiones y puede activar mecanismos del malware. Es una decisión que se toma, se justifica y se documenta.
- **Mínima interacción.** Cada comando que se ejecuta modifica la memoria; hay que limitarse a lo imprescindible.

## Herramientas de volcado

| Sistema | Herramienta | Formato | Notas |
|---|---|---|---|
| Windows | Magnet DumpIt | Raw | Ejecutable único; requiere administrador; el volcado se escribe en la carpeta desde la que se lanza. |
| Windows | WinPmem (Velocidex) | Raw | Código abierto; depende de un driver firmado y de la versión de Windows. |
| Windows | FTK Imager | Raw | Interfaz gráfica; permite elegir la ruta de salida. |
| Linux | AVML (Acquire Volatile Memory for Linux) | Raw / LiME | Binario estático en Rust; no requiere compilar en el equipo. Falla si el kernel tiene *lockdown* activo. |
| Linux | LiME (Linux Memory Extractor) | LiME | Módulo del kernel compilado para la versión exacta; no sirve si no se pueden cargar módulos. |
| Virtualización | Snapshot de la VM | `.vmem`, `.vmss` | Captura desde el hipervisor; más consistente si se puede suspender la máquina. |

Las fuentes pasivas de Windows (`hiberfil.sys`, `pagefile.sys`, `MEMORY.DMP`) y el *swap* de Linux complementan el análisis, pero no sustituyen a un volcado completo.

Para inspeccionar en vivo en Windows, Process Explorer y TCPView (Suite Sysinternals) muestran procesos y conexiones; complementan al volcado, no lo sustituyen. `Rootkit Revealer` está descatalogada y Memparser solo sirve para Windows 2000, así que hoy no se usan.

```bash
# Linux con AVML (binario estático)
sudo avml /evidencias/memoria.lime

# Linux con LiME (módulo compilado para el kernel en ejecución)
sudo insmod lime-$(uname -r).ko "path=/evidencias/memoria.lime format=lime"
```

Los comandos de Windows dependen de la herramienta; DumpIt y WinPmem generan un `.raw` que después se analiza igual que un `.lime`.

## Integridad y cadena de custodia

El volcado se trata como cualquier otra evidencia: se calcula su hash al terminar la captura y se vuelve a comprobar tras copiarlo al medio de análisis.

```bash
sha256sum /evidencias/memoria.lime | tee /evidencias/memoria.lime.sha256
```

En la cadena de custodia hay que reflejar que se trata de una **adquisición en vivo**: no es una copia bit a bit de un soporte inalterado. También se anotan el tamaño del volcado frente a la RAM instalada y los errores o avisos de la herramienta, porque un volcado parcial condiciona las conclusiones.

## Preparar Volatility 3

Volatility 3 es la versión mantenida del estándar para analizar memoria. Frente a Volatility 2:

- No usa perfiles: identifica el sistema y el kernel del volcado y descarga las **tablas de símbolos** en formato ISF (*Intermediate Symbol Format*).
- Los plugins llevan prefijo de sistema operativo: `windows.pslist`, `linux.pslist`, `mac.pslist`. Los tutoriales de Volatility 2 (`pslist`, `netscan`, `--profile=...`) no se aplican.
- Funciona con Python 3.8 o superior.

```bash
pipx install volatility3        # deja el comando vol disponible
vol -f memoria.raw banners      # identifica el sistema operativo del volcado
vol -f memoria.raw windows.info
```

Desde el repositorio de código se ejecuta con `python3 vol.py -f memoria.raw windows.info`. La primera ejecución necesita red para descargar los símbolos; en un equipo sin conexión se copian de antemano en el directorio de símbolos o se indica con `--symbol-dirs`. En un volcado de Linux se usa `linux.*` en lugar de `windows.*`; `banners` es genérico y sirve para saber qué sistema se tiene entre manos.

Opciones útiles:

| Opción | Uso |
|---|---|
| `-f` | Fichero de memoria que se analiza. |
| `-o` | Directorio donde volcar los resultados. |
| `-r json` / `-r csv` | Formato de salida para procesar con otras herramientas. |
| `-h` | Ayuda general; `vol <plugin> -h` muestra las opciones de un plugin. |

Las salidas se guardan siempre junto al volcado y se referencian en el informe. El volcado original no se modifica: Volatility solo lee.

## Plugins por objetivo en Windows

| Objetivo | Plugin | Qué aporta |
|---|---|---|
| Identificar el sistema | `windows.info` | Versión, kernel y tiempo de arranque. |
| Procesos activos | `windows.pslist` | Recorre la lista enlazada de procesos. |
| Procesos ocultos o terminados | `windows.psscan` | Escanea el *pool* del kernel y encuentra procesos desenlazados. |
| Jerarquía | `windows.pstree` | Relación padre-hijo. |
| Argumentos | `windows.cmdline` | Línea de comandos de cada proceso. |
| Usuarios | `windows.getsids` | SID propietario de cada proceso. |
| Entorno | `windows.envars` | Variables de entorno por proceso. |
| Red | `windows.netscan` | Conexiones y puertos por escaneo de *pool*; suele ser más completo. |
| Red (alternativa) | `windows.netstat` | Recorre estructuras enlazadas; puede omitir conexiones. |
| Código inyectado | `windows.malfind`, `windows.vadinfo` | Regiones sospechosas con permisos de escritura y ejecución y sin fichero asociado. |
| Ficheros y handles | `windows.filescan`, `windows.handles`, `windows.dumpfiles` | Ficheros abiertos o en caché y extracción de su contenido. |
| Credenciales | `windows.hashdump`, `windows.lsadump`, `windows.cachedump` | Hashes SAM, secretos LSA y credenciales de dominio en caché. |
| Servicios y drivers | `windows.svcscan`, `windows.driverscan`, `windows.modules` | Servicios, drivers y módulos cargados. |
| Registro | `windows.registry.hivelist` | Colmenas cargadas; después, `windows.registry.printkey`. |
| Consolas | `windows.consoles`, `windows.cmdscan` | Historial de comandos y contenido de consolas. |
| Cronología | `timeliner` | Eventos con marca de tiempo. |

En Linux el equivalente básico es `linux.pslist`, `linux.pstree`, `linux.psaux`, `linux.bash` (historial), `linux.sockstat`, `linux.lsmod`, `linux.hidden_modules`, `linux.malfind` y `linux.envars`. Para analizar Linux hacen falta símbolos ISF del kernel, que se generan con `dwarf2json` a partir de un `vmlinux` con información de depuración.

## Sesión de ejemplo

```bash
vol -f memoria.raw banners
vol -f memoria.raw windows.info
vol -f memoria.raw windows.pslist
vol -f memoria.raw windows.psscan
vol -f memoria.raw windows.cmdline
vol -f memoria.raw windows.netscan
vol -f memoria.raw windows.malfind
vol -f memoria.raw -r json -o salida windows.hashdump
```

El orden va de lo general a lo concreto: primero se confirma qué sistema es, después qué procesos había y qué hacían, luego las conexiones y, por último, los indicios de inyección o las credenciales. Comparar `pslist` con `psscan` es obligatorio: una diferencia es una **hipótesis** que se contrasta, no una prueba de ocultación, porque un proceso terminado puede seguir en el *pool*.

## Límites y errores frecuentes

- **Símbolos que no coinciden.** Si el kernel del volcado no casa con los símbolos, los plugins fallan o devuelven basura. Hay que usar el ISF de la versión exacta.
- **Un resultado vacío no prueba ausencia.** Puede faltar la estructura, estar paginada o no haber sido capturada.
- **`malfind` es heurístico.** Genera falsos positivos; se confirma con `vadinfo`, `dumpfiles`, hashes o YARA.
- **Volcado parcial.** Errores de la herramienta, falta de espacio o *lockdown* del kernel dejan un fichero incompleto. El tamaño no siempre coincide con la RAM instalada.
- **`hiberfil.sys` y `pagefile.sys` no son un volcado completo.** Aportan contexto, no sustituyen a la captura.
- **No ejecutar lo extraído.** Los binarios recuperados se analizan en una máquina aislada.
- **Privacidad.** Hashes, credenciales y conversaciones son datos sensibles; el informe no los reproduce si no son necesarios para la conclusión.

## Fuentes

- [Volatility 3 Documentation](https://volatility3.readthedocs.io/) — uso, plugins y símbolos.
- [microsoft/avml](https://github.com/microsoft/avml) — adquisición de memoria en Linux y formatos de salida.
- [LiME (Linux Memory Extractor)](https://github.com/504ensicsLabs/LiME) — módulo de captura y formato LiME.
- [RFC 3227](https://www.rfc-editor.org/rfc/rfc3227) — directrices de recogida y almacenamiento de evidencias; orden de volatilidad.
