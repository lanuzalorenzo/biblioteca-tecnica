# Medidas, políticas y estándares

Un edificio puede tener cerradura, conserje y cámara, pero si nadie ha decidido quién tiene llave, qué se puede hacer dentro y qué normas son obligatorias, cada vecino improvisa. Con un plan de seguridad ocurre lo mismo: la tecnología no sustituye a la decisión, y una recomendación no obliga por sí sola. Este apunte separa cuatro piezas que suelen confundirse: la medida técnica, la política, la guía y el estándar.

## Qué puede hacer una medida técnica

Una medida técnica se apoya en tecnología para proteger un activo o un servicio. Unas evitan que la amenaza llegue; otras actúan cuando ya ha llegado. No son alternativas, sino turnos distintos:

| Antes del incidente | Durante y después |
|---|---|
| Antimalware, cortafuegos, copias, DLP, VPN, IDS | EDR/XDR, IPS, plan de contingencia, restauración |

Hay herramientas que aparecen en los dos lados. EDR y XDR detectan y además contienen o eliminan; la verificación de integridad puede devolver un archivo alterado; el *virtual patching* bloquea la explotación de un fallo que no se puede parchear.

Conviene situar estas:

- **Antimalware.** La base; hoy suele incluir cortafuegos y otras funciones.
- **EDR y XDR.** Detección y respuesta en el terminal y más allá.
- **Cortafuegos.** Permiten o bloquean tráfico según reglas.
- **Copias de seguridad.** La medida preventiva central; permiten recuperar.
- **DLP.** Evita que la información sensible salga sin autorización.
- **Verificación de integridad.** Compara huellas y avisa si algo cambió.
- **Conexiones seguras.** VPN y encapsulado para que el tráfico interceptado no se lea.
- **IDS.** Avisa de comportamientos anómalos en red o en el host.
- **Virtual patching.** Protege sistemas obsoletos que no se pueden actualizar.
- **SIEM.** Centraliza eventos y ayuda a detectar lo anómalo.

Acumular prevención no compensa la falta de respuesta. Cuando el incidente ya está dentro, alguien tiene que contenerlo.

## Mitigación temporal: el hueco entre el aviso y el parche

Un parche no llega el día en que se publica la vulnerabilidad. Hay que comprobarlo, desplegarlo y confirmar que no rompe nada, y mientras tanto el sistema sigue expuesto. La mitigación temporal reduce esa exposición sin sustituir la actualización.

La diferencia está en el alcance y en la caducidad. El parche corrige la causa; la mitigación corta la ruta concreta que necesita la explotación. En red suele hacerlo un IPS o un WAF; en el host, un control de ejecución o un programa eBPF. Si bloquea una operación que también usa el tráfico legítimo, el servicio se cae: por eso se prueba antes y se limita a lo imprescindible.

Tres comprobaciones antes de darla por buena:

- **Cubre la explotación.** Se reproduce el ataque y se confirma que el control lo detiene.
- **No rompe el uso normal.** La misma prueba se repite con peticiones legítimas.
- **Se puede retirar y deja rastro.** Hay que saber qué se cargó, quién lo firmó y cuándo se quitó; si no, el control se convierte en deuda invisible.

eBPF permite ejecutar programas pequeños en puntos del kernel sin reiniciar el sistema, y el kernel valida cada programa antes de cargarlo. Esa validación limita el riesgo de ejecutar código ajeno, pero no decide si la regla es correcta: eso sigue siendo una decisión del operador. La firma del artefacto acredita que procede de quien lo firmó y que no se alteró, no que la política sea correcta.

Planificar también es parte de la medida. NIST SP 800-40 Rev. 4 trata el parcheo como mantenimiento planificado, y NIST SP 800-53 Rev. 5 (SI-2) exige plazos de remediación. La mitigación cubre ese plazo; no lo amplía.

## Tres niveles de obligación

- **Recomendación:** una buena práctica. No obliga.
- **Política:** una instrucción de cumplimiento obligatorio; incumplirla puede tener consecuencias.
- **Estándar:** una especificación técnica reconocida. Es voluntaria hasta que una ley, un contrato o una certificación la exigen.

Las políticas se aplican sobre personas, procesos y máquinas. Si son tan rígidas que impiden trabajar, la organización las rodea. La seguridad sostiene la actividad; no la reemplaza.

### Políticas de comportamiento

- Continuidad del negocio.
- Cumplimiento legal: RGPD, LOPDGDD y normativa aplicable.
- Relación con proveedores.
- Concienciación y formación.
- Uso del correo.
- Uso aceptable de dispositivos corporativos.
- Contraseñas: no compartirlas, no apuntarlas.
- Protección del puesto: bloquear la sesión y despejar la mesa.

### Políticas de configuración

- Auditoría de sistemas.
- Antimalware.
- Gestión de móviles y equipos: cifrado, bloqueo, MDM.
- Control de acceso con roles y permisos.
- Copias de seguridad, ligadas a la continuidad.
- Gestión de registros.
- Respuesta a incidentes, con plan y escalado.
- Actualizaciones.
- Borrado seguro.
- Teletrabajo: VPN y doble factor.

El control de acceso se presenta a veces como si fuera Zero Trust. Zero Trust es un modelo de arquitectura, no una política concreta; la política traduce el «no confiar por defecto» en reglas verificables.

## Dónde buscar método

Las guías son documentos de referencia, no obligatorios, elaborados por organizaciones con prestigio. Sirven para no inventar un control desde cero. Las fuentes habituales son INCIBE, CCN-CERT, ENISA y ECSO.

Su valor está en la independencia frente a intereses comerciales; su límite, en que no reemplazan una política interna hecha a medida.

## Cuándo una guía se vuelve exigible

Un estándar es una especificación técnica de aplicación repetida, aprobada por un organismo reconocido. Por sí mismo es voluntario; solo obliga si una ley, un contrato o una certificación lo imponen. Al certificarse, la organización debe cumplir los controles que declara aplicables y justificar las exclusiones.

Estándares relevantes:

- **ISO/IEC 27000:** vocabulario y visión general de la familia. La norma certificable es la 27001.
- **ISO/IEC 27032:** directrices de ciberseguridad.
- **ISO/IEC 27033:** seguridad de redes.
- **ISO/IEC 27034:** seguridad de aplicaciones.
- **ISO/IEC 27035:** gestión de incidentes.
- **ISO/IEC 27036:** seguridad en relaciones con terceros.
- **NIST Cybersecurity Framework:** identificar, proteger, detectar, responder, recuperar y gobernar.

El **ENS** no pertenece a la familia ISO: es un marco normativo español para la Administración Pública. Su exigencia alcanza también a los contratistas, que deben acreditar un nivel equivalente.

Al citar ISO conviene indicar el año: la familia se revisa y los números de control cambian entre ediciones.

## Vida útil y economía circular

El esquema de extraer, fabricar, consumir y desechar tiene un límite. La economía circular plantea cerrar el círculo: alargar la vida de lo que funciona, recuperar piezas y dar salida a los materiales.

En tecnología choca con la obsolescencia programada: equipos que no se actualizan, componentes que no se sustituyen y residuos electrónicos. Un plan de securización puede incluir criterios de compra, reutilización y eliminación segura. No es un adorno: un equipo sin actualizaciones es una vulnerabilidad que permanece en la red porque nadie decidió retirarlo.

## Cómo se ordena todo

1. El **análisis de riesgos** decide qué proteger y con qué prioridad.
2. Las **medidas técnicas** reducen el riesgo.
3. Las **políticas** convierten las decisiones en obligaciones.
4. Las **guías** aportan método sin imponer.
5. Los **estándares** permiten demostrar el cumplimiento y certificarse.
6. Los **procedimientos** explican cómo se hace todo lo anterior.

## Errores que se repiten

- Llamar política a una recomendación y sancionar su incumplimiento.
- Copiar una guía sin adaptarla al negocio.
- Certificar una norma y excluir controles sin justificarlo.
- Comprar herramientas antes de decidir qué riesgo cubren.
- Citar ISO sin año y comparar ediciones distintas.

## Fuentes

- ISO/IEC 27000, 27001, 27032, 27033, 27034, 27035 y 27036.
- NIST. *Cybersecurity Framework*.
- NIST. *SP 800-40 Rev. 4, Guide to Enterprise Patch Management Planning*, y *SP 800-53 Rev. 5*, control SI-2 (corrección de fallos).
- Linux kernel. Documentación de BPF y del verificador.
- ENS. *Esquema Nacional de Seguridad* (Real Decreto 311/2022).
- INCIBE, CCN-CERT, ENISA y ECSO: guías de buenas prácticas.
