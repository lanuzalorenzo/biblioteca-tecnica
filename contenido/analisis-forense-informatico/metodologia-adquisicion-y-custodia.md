# Metodología, adquisición y cadena de custodia

Un forense digital trabaja como quien acordona una escena: lo primero no es ordenar ni encender luces sin cuidado, sino preservar el espacio, registrar cada detalle y recoger las pruebas sin contaminarlas. En un sistema comprometido, cada acción deja un rastro que se borra con facilidad. El trabajo consiste en congelar la escena y extraer pistas sólidas sin alterar un solo bit.

## Qué busca el análisis forense

El AFI tiene un objetivo: contar la historia de lo que ha sucedido y aportar evidencias que sostengan los hechos. El analista debe poder responder qué pasó, dónde, quién estuvo implicado, cuándo y con qué medios.

Hay dos escenarios que cambian el rigor del método:

- **Requerimiento judicial.** La evidencia debe ser admisible en un proceso penal.
- **Respuesta ante ciberincidentes.** El foco es recuperar la operatividad y entender el ataque.

El método se adapta al escenario, pero la preservación y la documentación no se negocian en ninguno de los dos.

## Las cuatro fases

1. **Identificación.** Determinar qué dispositivos o sistemas contienen evidencia relevante.
2. **Adquisición y preservación.** Obtener una copia fiel sin alterar el original.
3. **Análisis.** Examinar la copia para extraer información.
4. **Documentación y reporte.** Registrar el proceso y presentar conclusiones.

Saltarse una fase invalida el resultado. Una copia perfecta sin cadena de custodia no sirve como prueba; un informe brillante sobre una copia mal hecha tampoco.

## El orden de volatilidad

La evidencia se recoge de lo que desaparece antes a lo que permanece:

| Orden | Tipo de evidencia |
|---|---|
| 1.º | Cachés de memoria y registros de CPU |
| 2.º | Memoria RAM, tabla ARP, procesos, swap y temporales |
| 3.º | Discos duros |
| 4.º | Logs remotos y datos de monitorización |
| 5.º | Configuraciones físicas y topologías de red |

La RAM se pierde al apagar o reiniciar. Por eso se captura primero, antes de tocar el disco. El desarrollo completo está en [Volcado y análisis de memoria RAM](volcado-y-analisis-de-memoria-ram.md).

## Adquirir sin alterar

La adquisición se hace sobre una **copia forense** —una imagen bit a bit—, nunca sobre el original:

- **Write blockers de hardware.** Bloquean cualquier escritura accidental sobre el soporte.
- **Software de clonado.** Genera imágenes que se verifican con un hash.

La integridad se comprueba calculando el hash antes y después: si coinciden, la copia es idéntica al original.

### El manifiesto de hashes

Cuando no se copia el soporte completo y se documenta archivo a archivo, el triaje produce un **manifiesto** con el hash y la ruta de cada fichero:

```bash
find pruebas_forenses -type f -exec sha256sum {} + > lista_hashes.txt
```

El manifiesto por sí solo no prueba nada: cualquiera puede añadir o quitar líneas. Se sella calculando el hash del propio fichero de lista y guardándolo aparte:

```bash
sha256sum lista_hashes.txt > lista_hashes.txt.sha256
sha256sum -c lista_hashes.txt.sha256
```

Si una línea cambia, la comprobación falla. En el informe se cita el hash del manifiesto, no solo los hashes individuales.

## La cadena de custodia

La cadena garantiza que lo analizado fue exactamente lo recogido. Cada persona que toca la evidencia es un eslabón responsable. Como mínimo debe constar:

1. Identificación unívoca: marca, modelo y número de serie.
2. Modo de preservación.
3. Marca de tiempo de la recogida y de quién la hizo.
4. Localización física y responsable en cada momento.
5. Documentación y registros de control.

El debate sobre la cadena se centra en la fiabilidad de la prueba, no en su validez formal. Una ruptura no probada genéricamente no basta para impugnarla: hay que precisar cuándo y por qué actuación se produjo.

## Herramientas del analista

**Hardware.** Clonadores forenses para ATA, SATA, IDE, PCI, SCSI, USB y FireWire; cables, write blockers, destornilladores y material de conservación como bolsas antiestáticas.

**Software por tipo de evidencia.** La columna de adquisición captura o copia; la de análisis interpreta. Confundirlas es el error más común: `tcpdump` captura tráfico, pero no reconstruye un incidente.

| Evidencia | Adquisición | Análisis |
|---|---|---|
| Memoria RAM | WinPmem, AVML, LiME, Magnet RAM Capture, DumpIt | Volatility 3 |
| Disco | Write blocker y clonador, `dcfldd`, FTK Imager, Guymager | Autopsy y The Sleuth Kit, FTK Suite, EnCase |
| Red | `tcpdump`, Wireshark | Wireshark, NetworkMiner |
| Ficheros y metadatos | `find` con hash, ExifTool | ExifTool, bulk_extractor |
| Recuperación de borrados | — | foremost, scalpel, binwalk |
| Dispositivos móviles | Cellebrite | Cellebrite |
| Suites completas | — | SIFT (SANS) |
| Logs (Unix) | `journalctl`, `dmesg` | `grep`, `tail`, shell scripting |
| Logs (Windows) | Visor de eventos, exportación `.evtx` | PowerShell (`Select-String`, `Select-Object`) |
| SIEM / indexado | Exportación de logs | Splunk, Graylog, GoAccess |

## Cuatro criterios para no elegir mal

- **Detección no es forense.** Snort, Suricata y Zeek alertan, pero no reconstruyen por sí solos qué pasó ni en qué orden.
- **Kismet** captura redes inalámbricas: exige autorización expresa y queda fuera de este ámbito.
- **La recuperación de borrados tiene límite físico.** En un SSD con TRIM, los bloques no reclamados ya no están; el resultado no es fiable.
- **Los metadatos contextualizan, no prueban.** ExifTool lee y limpia metadatos; la integridad la demuestra el hash, no la fecha EXIF.

## Lo que sostiene el método

- El AFI reconstruye hechos con evidencia digital sin alterarla.
- El orden de volatilidad manda: primero RAM, después disco.
- La copia forense se verifica con hash y se documenta.
- La cadena de custodia hace que la prueba sea fiable.
- Elegir herramienta exige distinguir adquisición de análisis.

## Fuentes

- ISO/IEC 27037:2012: identificación, recogida, adquisición y preservación de evidencia digital.
- NIST. *SP 800-86, Guide to Integrating Forensic Techniques into Incident Response*.
- RFC 3227: directrices de recogida y almacenamiento de evidencias.
- Documentación de FTK Imager, Autopsy, The Sleuth Kit, ExifTool, foremost, scalpel y binwalk.
