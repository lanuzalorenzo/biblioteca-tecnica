# Autorización y alcance

Un permiso de obras sirve para reformar una vivienda concreta, no para tirar tabiques en todo el barrio. El alcance de un test de intrusión cumple esa misma función: dice qué se puede tocar, durante cuánto tiempo y con qué límites, de modo que una autorización puntual no se confunda con un cheque en blanco.

> **Autorización.** Sin un documento firmado por quien puede disponer de los sistemas, el mismo comando deja de ser una prueba y pasa a ser un acceso no autorizado. No se empieza antes de tenerlo, aunque el cliente asegure por teléfono que no hay problema.

## Para qué sirve el alcance

El alcance tiene tres funciones. Jurídicamente, la autorización solo cubre lo que el documento describe. Técnicamente, indica al equipo dónde parar y evita que las pruebas se desborden. Profesionalmente, fija expectativas, esfuerzo, coste y entregables; muchos conflictos nacen de un alcance ambiguo.

La preparación, o *pre-engagement*, suele incluir reuniones, un cuestionario de alcance, una estimación de esfuerzo y una propuesta técnica y económica. Metodologías como PTES o NIST SP 800-115 dedican un apartado específico a esta fase; conviene consultar su versión vigente.

## Elementos de un buen alcance

1. **Objetivo de negocio**: verificar la seguridad antes de un lanzamiento, cumplir un requisito, evaluar un incidente previo o conocer la exposición. Condiciona el diseño de la prueba.
2. **Activos incluidos**: direcciones IP o rangos, dominios, aplicaciones y URL, redes inalámbricas, instalaciones o categorías de personas. Debe permitir decidir sin dudas si un sistema está dentro o fuera; «toda la red de la empresa» es una señal de alarma.
3. **Exclusiones expresas**: sistemas críticos o frágiles, equipos de terceros, entornos de otros clientes, servicios en la nube sin permiso del proveedor y cuentas excluidas.
4. **Técnicas permitidas y prohibidas**: reconocimiento pasivo, escaneo, explotación, ataques a credenciales, ingeniería social, pruebas físicas, postexplotación y movimiento lateral. La denegación de servicio se excluye por defecto salvo acuerdo específico y controlado.
5. **Enfoque**: caja negra, gris o blanca, porque cambia el esfuerzo y el tipo de hallazgos.
6. **Ventana temporal**: fechas, horas y franjas permitidas, a menudo fuera de la mayor actividad.
7. **Origen de las pruebas**: direcciones IP y personas que actuarán, para distinguir al auditor de un atacante y decidir si se avisa al equipo de monitorización.

## Reglas de actuación

Las reglas de actuación (*Rules of Engagement*, RoE) concretan cómo se trabaja:

- **Contactos y escalado**: contacto técnico y de emergencia, con teléfono, y canal para comunicar hallazgos críticos sin esperar al informe.
- **Criterios de parada**: degradación de un servicio, indicios de un incidente real previo o simultáneo, o descubrimiento de que un activo no pertenece al cliente.
- **Datos y evidencias**: recogida, almacenamiento, protección, conservación y destrucción; qué datos personales se pueden ver.
- **Credenciales y accesos creados**: registrar cuentas, archivos o accesos y retirarlos al terminar.
- **Control de cambios**: toda ampliación se documenta y se autoriza por escrito antes de actuar.
- **Entregables y plazos**: documentos, formato, fechas y posible verificación posterior de las correcciones.
- **Responsabilidades y seguros**: límites de cada parte y seguro de responsabilidad profesional o ciberriesgo.

Una prueba interna o con acceso físico añade condiciones propias: coordinación con el cliente, equipos conectados, controles de acceso a la red e identificación del personal que entra en las instalaciones.

## Documentos de autorización

| Documento | Para qué sirve | Quién lo firma |
|---|---|---|
| NDA | Proteger la información intercambiada y los hallazgos. | Cliente y auditor |
| Propuesta técnica y económica | Describir servicio, esfuerzo, precio, plazos y entregables. | Cliente y auditor |
| Contrato de prestación de servicios | Regular responsabilidades, límites, seguro y resolución de conflictos. | Representantes legales |
| Carta de autorización | Acreditar que el titular autoriza las pruebas descritas. | Quien puede disponer de los sistemas |
| Reglas de actuación | Fijar cómo se trabaja, se comunica y se para. | Cliente y auditor |
| Autorizaciones de terceros | Cubrir nube, alojamiento, proveedores y socios. | Titular del activo o su proveedor |
| Acuerdo de encargado del tratamiento | Regular el tratamiento de datos personales (RGPD, art. 28). | Responsable y encargado |
| Autorización de ingeniería social y pruebas físicas | Cubrir actividades sobre personas e instalaciones. | Dirección, con recursos humanos y asesoría jurídica |
| Acta de cierre y certificado de destrucción | Acreditar entregables, retirada de accesos y eliminación de evidencias. | Ambas partes |

La carta de autorización es el documento que se muestra primero si algo sale mal. Debe identificar sistemas, fechas, técnicas, personas autorizadas, direcciones de origen y contactos, y declarar la titularidad o la legitimidad para autorizar. En pruebas físicas se lleva encima para acreditarse. No basta con que exista: si es ambigua, está caducada o no corresponde con lo que se hace, pierde buena parte de su valor.

## Quién autoriza y hasta cuándo

Autoriza el titular o su representante legal, o quien tenga delegación expresa. No basta con que un técnico de sistemas o un responsable de área «deje probar». Un equipo interno de seguridad también necesita autorización formal de la dirección. En organizaciones públicas existen procedimientos propios que deben respetarse.

La autorización caduca: una prórroga exige una ampliación firmada. Se conserva copia durante el plazo contractual y legal, porque es la prueba de que se actuó con permiso.

## Los tres bordes de la autorización

1. **Terceros.** El cliente solo puede autorizar lo que es suyo. En alojamiento compartido, nube, CDN, correo contratado o redes de socios, probar sin permiso del titular es acceder a un sistema ajeno. Si no se puede demostrar la titularidad o la autorización, el activo queda fuera. Hay que comprobar IP y dominios, leer las políticas de pruebas de cada proveedor y pedir autorización expresa cuando corresponda.
2. **Datos personales.** El auditor suele actuar como encargado del tratamiento. Se aplica minimización, se evita copiar datos, las capturas ocultan campos identificativos, las evidencias se cifran y se destruyen en plazo, y se prevé qué hacer si la prueba causa una violación de seguridad (notificación del art. 33 del RGPD, a verificar).
3. **Personas y derechos.** La ingeniería social y la captura de tráfico afectan a personas. La empresa no puede autorizar sin más la lectura de comunicaciones privadas; el secreto de las comunicaciones está protegido constitucionalmente. Las pruebas se limitan a cuentas y equipos de prueba, metadatos o servicios, y se pactan por escrito. Un cliente no puede autorizar un delito: si una instrucción cruza esa línea, la respuesta es no hacerlo y plantearlo por escrito.

## Aplicación al laboratorio

En un laboratorio, el tercero es el resto del mundo. Un laboratorio de máquinas virtuales solo es seguro si está aislado: las máquinas víctima no deben conectarse a la red de la organización, a la red doméstica ni a internet mediante un adaptador mal configurado. Antes de arrancar una máquina vulnerable, comprueba la red interna o de solo anfitrión y documenta una breve declaración de laboratorio: los sistemas son propios, están aislados y no tienen conexión con redes ajenas.

## Un alcance de ejemplo

> **Ejemplo ficticio.** Los dominios usan `.example` y las direcciones pertenecen a rangos reservados para documentación.

Una empresa de logística contrata un pentest externo e interno limitado, en caja gris. Se incluyen el portal de seguimiento, la red del almacén y la red inalámbrica de visitas; se excluyen el ERP en producción, el correo externo, la telemetría de flota, las redes de transportistas y los equipos personales. Se permiten reconocimiento pasivo, escaneo limitado, análisis de vulnerabilidades, explotación no destructiva, ataques a credenciales solo contra cuentas de prueba y captura en el segmento de pruebas. Se prohíben denegación de servicio, ingeniería social, pruebas físicas, persistencia, extracción masiva y modificación de datos.

La ventana es de tres semanas, con pruebas intrusivas de 20:00 a 06:00 y sin actividad en el cierre mensual. Los criterios de parada son degradación del servicio, indicios de incidente real o activo que no pertenece al cliente. Los hallazgos críticos se comunican en 24 horas; las evidencias se cifran, se conservan 90 días y se destruyen con certificado. Cualquier ampliación se pacta por escrito.

## Procedimiento

1. Confirma que existe una carta firmada por quien puede disponer de los sistemas.
2. Verifica que el alcance enumera activos, exclusiones, técnicas, ventana y origen.
3. Comprueba la titularidad de dominios, IP y servicios de terceros, y consigue sus autorizaciones.
4. Revisa las RoE: contactos, parada, evidencias, credenciales y control de cambios.
5. Asegura el acuerdo de encargado del tratamiento y el procedimiento ante una violación de datos.
6. Documenta la declaración de laboratorio o la autorización antes de ejecutar cualquier prueba.
7. Si algo no está claro o cambia, detente y consigue autorización escrita.

## Glosario

| Término | Definición |
|---|---|
| Carta de autorización | Documento firmado que acredita el permiso para probar sistemas concretos. |
| Encargado del tratamiento | Quien trata datos personales por cuenta del responsable. |
| Pre-engagement | Fase previa de definición de alcance, condiciones y documentos. |
| Scope creep | Ampliación del alcance sin autorización escrita. |
| SOW | Documento que describe el trabajo, plazos, esfuerzo y entregables. |

## Fuentes

- Código Penal: artículos 197, 264 y 264 bis.
- RGPD y LOPDGDD, para los datos personales tratados durante las pruebas.
- NIST. *SP 800-115* y PTES, para la fase de preparación y las reglas de actuación.
