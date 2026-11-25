# Auditoría y mejora

Una auditoría es la ITV de la seguridad: no evita el accidente, pero comprueba si los frenos funcionan antes de salir a la carretera. Su valor no está en el informe que produce, sino en lo que cambia después. Un documento con hallazgos que nadie corrige es más caro que no haber mirado.

## Saber dónde estamos

Antes de implantar medidas hay que conocer el nivel de seguridad existente y decidir qué nivel se necesita para proteger los procesos críticos. Es la pareja **AS IS / TO BE**: el punto de partida y el de llegada.

Sin esa foto inicial, cualquier inversión es una apuesta. La auditoría inicial es el método para obtenerla: revisa sistemas, ordenadores, routers, salas de servidores y controles de acceso, tanto tecnológicos como físicos. No se limita a lo que aparece en un inventario; comprueba si lo que debería estar, está, y si funciona como se cree.

## Qué es una auditoría

Su finalidad es obtener **evidencias** de cómo los sistemas cumplen los requisitos de seguridad. Esas evidencias sirven para conocer el estado actual, para un proceso de mejora continua y para demostrar cumplimiento ante terceros.

Debe realizarla personal cualificado. En ciertos casos hacen falta servicios especializados o auditorías forenses, sobre todo después de una brecha de datos, una botnet o un ransomware. La auditoría forense no busca solo qué falló: recoge evidencia que pueda resistir una revisión posterior.

Dos referencias habituales del cumplimiento legal y normativo son:

- **RGPD.** Reglamento europeo de protección de datos personales.
- **SGSI.** Sistema de Gestión de la Seguridad de la Información, con la ISO/IEC 27001 como norma de referencia.

Una auditoría legal comprueba que la organización cumple lo que la ley exige. Una auditoría técnica comprueba que los controles funcionan. No son intercambiables: se puede cumplir el expediente y tener un cortafuegos mal configurado, o al revés.

## La política de auditorías

El primer paso es detallar los **elementos clave** que se van a auditar: ficheros, bases de datos, páginas web, equipos y programas. Para cada activo se revisa si dispone de:

- Sistemas antimalware.
- Gestión de permisos.
- Cumplimiento legal.
- Políticas de prevención de fraude y fuga de datos.
- Sistema de actualizaciones.
- Monitorización de recursos.

Conviene apoyarse en un esquema de mejora continua o en un modelo de madurez, para que los resultados no queden en un informe sino en mejoras concretas. La política también fija quién audita, con qué alcance y con qué periodicidad; sin eso, cada revisión se improvisa.

## Tipos de auditoría

- **Test de penetración o hacking ético.** Busca debilidades explotables, con autorización y alcance.
- **Auditoría de red.** Revisa topología, segmentación y tráfico.
- **Auditoría de seguridad perimetral.** Comprueba la frontera: cortafuegos, accesos remotos, servicios expuestos.
- **Auditoría web.** Analiza aplicaciones y portales.
- **Auditoría forense.** Investiga un incidente y recoge evidencia.
- **Auditoría legal.** Verifica obligaciones normativas.

Cada tipo exige un procedimiento y un registro de logs propios. El informe debe decir qué se revisó, qué se encontró y qué se corrigió.

Una prueba de penetración sin autorización escrita no es una auditoría: es un acceso no autorizado. El alcance tiene que estar pactado antes de empezar, incluir qué sistemas se pueden probar, qué técnicas están permitidas y qué hacer si se encuentra un fallo crítico durante la prueba.

## Periodicidad

Las auditorías se planifican de forma periódica. El criterio habitual fija un mínimo **cada seis meses** y añade dos disparadores:

- Después de un cambio significativo en los sistemas.
- Después de implantar una medida relevante, para comprobar que cumple el objetivo.

La auditoría no es un evento único: es un ciclo. Un cambio de proveedor, una migración a la nube o la apertura de un servicio nuevo pueden alterar el riesgo más que el paso del calendario. Esperar a la fecha semestral para revisar un cambio profundo deja abierta una ventana innecesaria.

## De la auditoría a la mejora

Analizar el resultado es tan importante como obtenerlo. Hay que identificar las causas de lo que salió mal, evaluar las medidas, implantarlas y volver a revisarlas. El ciclo PDCA —planificar, hacer, verificar, actuar— encaja con esta idea.

Un hallazgo sin responsable y sin plazo es un hallazgo que se repite. La auditoría debe cerrar con acciones, fechas y una forma de comprobar que la corrección funciona. El informe que solo enumera problemas deja el trabajo a medias.

Un hallazgo bien cerrado suele responder a estas preguntas:

- Qué se encontró y con qué evidencia.
- Qué riesgo implica y a quién afecta.
- Quién es el responsable de corregirlo.
- Para cuándo se espera la corrección.
- Cómo se comprobará que la corrección funciona.

La auditoría documenta; la corrección es otro paso. Confundir ambos convierte la revisión en una ilusión de seguridad.

## Ejemplo

Una organización detecta que muchos usuarios comparten credenciales y que las copias no se prueban. La auditoría documenta ambos hallazgos, prioriza la revisión de permisos y la política de respaldo, asigna responsables y fija una comprobación a los tres meses. La siguiente auditoría verifica si la corrección funcionó.

El ejemplo tiene dos enseñanzas. La primera es que un hallazgo puede ser organizativo —compartir credenciales— y no solo técnico. La segunda es que la comprobación posterior es parte del ciclo: sin ella, no se sabe si la medida resolvió el problema o solo lo tapó.

## Cierre

La auditoría compara el estado real con el exigido. AS IS y TO BE convierten la seguridad en un objetivo medible; los tipos de auditoría cubren red, web, perímetro, forense y legal; la periodicidad mínima es semestral, más tras cambios. Sin acciones y verificación no hay mejora. Con el estado comprobado, el siguiente paso es clasificar lo que ocurre cuando algo falla.
