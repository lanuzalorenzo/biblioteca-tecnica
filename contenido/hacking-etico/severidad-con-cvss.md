# Severidad con CVSS

La ficha técnica de un coche indica potencia, consumo y emisiones en un ciclo homologado. Sirve para comparar modelos, pero no dice cómo conducirás, por qué carretera ni con qué neumáticos. CVSS es esa ficha aplicada a una vulnerabilidad: describe el fallo en abstracto, no la situación concreta de quien lo tiene delante.

## Qué mide y qué no mide

CVSS (*Common Vulnerability Scoring System*) responde a dos preguntas: qué difícil es explotar técnicamente el fallo y cuánto daño puede causar si se explota. Todo lo demás queda fuera.

No dice si el componente afectado está instalado, si está expuesto a internet, cuánto vale el dato que protege, si hay un atacante interesado ni cuánto costaría el incidente. Por eso una puntuación de 9.8 en un servidor apagado no es el riesgo de nadie, y un 5.3 en el sistema que cobra cada minuto sí puede serlo. La puntuación ordena hallazgos; la prioridad la decide el contexto. Cómo se integra la nota en un informe se explica en [Documentar un hallazgo](documentar-un-hallazgo.md).

## Las tres capas

| Capa | Quién la fija | Qué cambia entre un caso y otro |
|---|---|---|
| Base | Quien publica la vulnerabilidad, como el fabricante o el NVD | Nada: describe el fallo en abstracto |
| Temporal | Quien evalúa, según lo que se sabe | Aparece un exploit público, se publica un parche |
| Entorno | Quien evalúa, según su despliegue | El activo no está expuesto o el dato es crítico |

La calculadora permite rellenar las tres, pero solo la base es obligatoria: temporal y entorno se construyen encima. Si una métrica queda en «no definida» (*Not Defined*, `X`), la herramienta usa el valor de la capa inferior.

## Las ocho métricas base

| Métrica | La pregunta que responde | Valores |
|---|---|---|
| **AV** — vector de ataque | ¿Desde dónde se explota? | Red, adyacente, local, físico |
| **AC** — complejidad | ¿Necesita condiciones fuera del control del atacante? | Baja, alta |
| **PR** — privilegios requeridos | ¿Hace falta una cuenta, y de qué nivel? | Ninguno, bajo, alto |
| **UI** — interacción de usuario | ¿Tiene que hacer algo la víctima? | Ninguna, requerida |
| **S** — alcance | ¿El impacto se queda en el componente vulnerable o sale de él? | Sin cambio, con cambio |
| **C** — confidencialidad | ¿Se expone información? | Alta, baja, ninguna |
| **I** — integridad | ¿Se puede modificar información? | Alta, baja, ninguna |
| **A** — disponibilidad | ¿Se puede dejar el servicio sin servicio? | Alta, baja, ninguna |

Leídas en lenguaje corriente: **AV** es la puerta de entrada —red significa «desde cualquier sitio», físico significa «hay que tocar la máquina»—. **AC** mide si el ataque funciona siempre o solo con una condición afortunada, como ganar una carrera de procesos. **PR** distingue el fallo que cualquiera explota del que exige una cuenta; su peso depende de **S**, porque una cuenta de invitado vale mucho más si el fallo permite salir de su espacio. **UI** separa el ataque directo del que necesita un clic o un archivo abierto. **S** es la métrica que más se malinterpreta: vale «con cambio» cuando explotar el componente afecta a otro con distinto nivel de privilegio o confianza, y entonces la fórmula sube la nota. **C**, **I** y **A** son el daño: leer datos, cambiarlos, tumbarlos.

## Cómo se lee un vector

`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H` se lee así: atacable por red, con complejidad baja, sin credenciales, sin interacción de la víctima, sin salir del componente, con impacto alto en confidencialidad, integridad y disponibilidad. Resultado: **9.8**. Es el perfil típico de una ejecución remota de código sin autenticación.

El mismo fallo cambia de nota con una sola métrica, y esa es la lección:

| Vector | Puntuación | Qué se ha movido |
|---|---:|---|
| `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H` | 9.8 | Referencia |
| `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H` | 8.8 | La víctima tiene que abrir algo |
| `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H` | 10.0 | El impacto escapa del componente |
| `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N` | 7.5 | Solo se leen datos, no se modifican |
| `CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:N` | 5.3 | Complejidad alta y víctima implicada |
| `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N` | 5.3 | Fuga de información parcial y remota |
| `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L` | 6.3 | Hace falta cuenta e impacto moderado en los tres pilares |
| `CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N` | 3.3 | Local, con cuenta y solo lectura parcial |

Las puntuaciones están calculadas con la fórmula oficial; se reproducen pegando el vector en la calculadora.

## La escala de severidad

| Puntuación | Etiqueta |
|---:|---|
| 0.0 | Ninguna |
| 0.1 – 3.9 | Baja |
| 4.0 – 6.9 | Media |
| 7.0 – 8.9 | Alta |
| 9.0 – 10.0 | Crítica |

La etiqueta es normativa; el plazo no. Cada organización decide qué hace con un 9.8: la política habitual exige corrección en días para crítica y alta, y deja media y baja para el ciclo planificado. Ese calendario es una decisión interna, no una regla de CVSS, y no se cita como estándar.

## La calculadora y la versión

La calculadora oficial de FIRST está en <https://www.first.org/cvss/calculator/3.1>. Se marcan las ocho métricas base, la herramienta genera el vector y la puntuación, y después se añaden las temporales y las de entorno. Antes de calcular una nota a mano conviene pegar el vector: evita errores aritméticos y deja la decisión documentada.

Cada versión de CVSS tiene sus propias métricas y su propia fórmula, y las puntuaciones **no se comparan entre versiones**. FIRST publicó la 4.0 en 2023 y mantiene la 3.1 en su archivo porque sigue en uso en muchos informes y normativas. Estas notas explican la 3.1, la más extendida; si el encargo exige la 4.0, se aplican sus métricas. Al citar una nota hay que escribir siempre la versión: «9.8, CVSS 3.1», nunca «9.8» a secas.

La precaución no es teórica. En el NVD, CVE-2013-0941 figura con CVSS **2.0** (2.1) y CVE-2012-2532 con 2.0 (5.0); ninguno de los dos tiene vector 3.x. Comparar esos números con un 3.1 es sumar unidades distintas.

## Errores frecuentes

- **Usar la base como riesgo.** La base describe el fallo; el riesgo incluye exposición, activo y probabilidad de que alguien lo intente.
- **Puntuar sin comprobar el componente.** Un CVE de un módulo que no está instalado no aplica, por alta que sea su nota.
- **Mezclar versiones.** Comparar un 2.0 con un 3.1, o promediar notas de versiones distintas, no significa nada.
- **Sumar o promediar puntuaciones.** Diez fallos de 5.0 no son «50»: la prioridad se decide hallazgo a hallazgo, con su contexto.
- **Olvidar el vector.** Una nota sin vector no se puede revisar ni defender ante otro equipo.
- **Creer que CVSS es la única señal.** Fuera del marco hay otros indicadores, como la probabilidad de explotación o los catálogos de vulnerabilidades ya explotadas; complementan, no sustituyen.

## Procedimiento

1. Identifica el CVE y anota la fuente y la versión de CVSS que vas a usar.
2. Comprueba si el componente afectado existe en el activo y en qué versión.
3. Rellena la base desde la descripción del fallo, o copia la publicada comprobando que es la misma versión.
4. Añade la temporal: ¿hay exploit público?, ¿hay parche?, ¿la información está confirmada?
5. Añade el entorno: exposición del activo, criticidad de los datos y requisitos de confidencialidad, integridad y disponibilidad.
6. Registra vector, puntuación, versión y fecha en el hallazgo.
7. Decide la prioridad con el contexto del negocio, no solo con el número.

## Resumen

- CVSS puntúa la severidad técnica de un fallo, no el riesgo de la organización.
- Tres capas: base (el fallo), temporal (lo que se sabe) y entorno (el despliegue).
- Cada métrica tiene una pregunta concreta; el vector es la prueba de cómo se respondió.
- La escala cualitativa es estándar; los plazos de corrección son política de cada organización.
- Una puntuación sin versión y sin vector no sirve para comparar ni para auditar.

## Glosario

| Término | Definición |
|---|---|
| CVSS | Sistema de puntuación de severidad técnica de vulnerabilidades. |
| Vector | Cadena con las métricas elegidas y su valor. |
| Base | Puntuación intrínseca del fallo, independiente del tiempo y del despliegue. |
| Temporal | Ajuste por madurez del exploit, remedio disponible y confianza del informe. |
| Entorno | Ajuste por el activo concreto donde vive el componente afectado. |
| CNA | Entidad autorizada a asignar CVE y, a veces, a puntuar la vulnerabilidad. |
| NVD | Base de datos del NIST que recoge CVE y sus puntuaciones. |

## Fuentes

- [CVSS v3.1 Specification Document](https://www.first.org/cvss/v3-1/specification-document): definición de métricas, fórmulas y escala cualitativa.
- [CVSS v3.1 Calculator](https://www.first.org/cvss/calculator/3.1): herramienta oficial.
- NVD: [CVE-2013-0941](https://nvd.nist.gov/vuln/detail/CVE-2013-0941) y [CVE-2012-2532](https://nvd.nist.gov/vuln/detail/CVE-2012-2532), ambas con CVSS 2.0.
