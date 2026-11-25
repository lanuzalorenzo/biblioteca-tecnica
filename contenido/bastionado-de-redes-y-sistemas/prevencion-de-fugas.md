# Prevención de fugas de información

Una empresa descubre que su lista de precios reservada circula por un grupo de mensajería de antiguos empleados. Nadie entró en el servidor: el archivo salió en un correo, en un lápiz de memoria o en una carpeta personal de la nube. La prevención de pérdida de datos no evita que alguien quiera llevarse la información; evita que se la lleve sin dejar rastro y, cuando hace falta, sin que salga.

Este apunte trata el control de la salida como una capa más del bastionado. No reemplaza a los permisos, al cifrado ni a la concienciación: los necesita para funcionar.

## Clasificar, marcar, controlar

DLP es el conjunto de procesos y herramientas que evitan que la información confidencial salga, se use mal o quede accesible a quien no debe.

Se apoya en tres piezas inseparables:

1. **Clasificar.** Distinguir lo confidencial de lo que no lo es. Sin esta decisión, la herramienta no sabe si un documento es un contrato o una circular.
2. **Marcar.** Etiquetar el documento o el correo para que la política lo reconozca.
3. **Controlar.** Decidir qué pasa cuando ese contenido intenta salir: avisar, bloquear, cifrar o pedir autorización.

## El dato en tres situaciones

| Estado | Dónde está | Ejemplo de control |
|---|---|---|
| En reposo | Servidores, equipos, nube | Cifrado, permisos, retención |
| En movimiento | Correo, web, mensajería, USB | Inspección y bloqueo en la salida |
| En uso | Pantalla, portapapeles, impresión | Restricciones de copia, marca de agua, impresión controlada |

Los incidentes reales suelen encadenar los tres: se descarga un documento clasificado, se copia a un dispositivo extraíble y sale del edificio. Vigilar solo el correo deja dos puertas abiertas.

## Clasificación y derechos

Clasificar corresponde al negocio, no al área técnica: la dirección y los responsables de área deciden qué es público, interno, confidencial o restringido. El etiquetado puede hacerse a mano, por reglas automáticas o combinando ambas formas.

La pieza que complementa la clasificación es IRM (*Information Rights Management*): derechos sobre el propio documento, con destinatarios, plazo de validez y condiciones de destrucción. Gracias a ella, un fichero enviado a un proveedor puede caducar a los treinta días o impedir que se reenvíe.

## Señales que busca

| Técnica | Qué busca |
|---|---|
| Palabras clave y expresiones | Patrones como «nómina», un IBAN o un número de tarjeta |
| Huellas de datos | Coincidencia exacta con documentos o bases internas |
| Propiedades del fichero | Etiquetas, autor, extensión, ruta |
| Análisis de comportamiento | Descargas masivas, permisos nuevos, accesos fuera de horario |

Las tres primeras son deterministas y producen menos falsos positivos. La cuarta descubre lo que ninguna regla previó, a cambio de más ruido.

## Por dónde puede salir

- **Correo:** adjuntos y cuerpo, con reglas para destinatarios externos.
- **Navegación y nube:** subida a almacenamiento personal, formularios, correo web.
- **Dispositivos extraíbles:** lápices de memoria, discos y tarjetas.
- **Impresión y capturas:** menos frecuente, pero cubre la fuga en papel.
- **Puestos y servidores:** copia a rutas no autorizadas, permisos nuevos.

## Lo que aporta y lo que no

Aporta detección de amenazas internas y externas, ayuda al cumplimiento normativo y separa roles para autorizar envíos.

Sus límites:

- **Falsos positivos.** Un DLP mal ajustado bloquea presupuestos legítimos y el usuario busca la forma de esquivarlo.
- **Tráfico cifrado.** Sin inspección no se ve nada; con inspección hacen falta base jurídica y transparencia.
- **Nube y dispositivos personales.** El perímetro se difumina y la información sale por canales que el equipo no controla.
- **Cultura.** Sin formación y sin un canal sencillo para compartir de forma segura, la gente usa el móvil personal.

El DLP es una capa, no un sistema completo. Rinde cuando se apoya en una clasificación real, permisos ajustados, cifrado y un camino claro para autorizar excepciones.

## Marco legal

En España, la protección de datos personales se rige por el RGPD y la LOPDGDD. Una fuga puede acarrear sanción administrativa y, según el caso, responsabilidad penal. Vigilar el uso de los equipos de trabajo exige informar al empleado y respetar la proporcionalidad; no todo lo técnicamente posible es legítimo.

Una política de prevención de fugas que intercepta comunicaciones sin base jurídica puede resolver un problema técnico y crear uno legal. La revisión debe incluir a quien responde de protección de datos.

## Qué comprobar

- ¿Existe una clasificación aprobada y conocida, o cada área decide la suya?
- ¿Las reglas cubren correo, nube, dispositivos y permisos, o solo el correo?
- ¿Hay un procedimiento para autorizar un envío excepcional y queda registrado?
- ¿Se revisan los falsos positivos con alguien del negocio?
- ¿La política de vigilancia está informada y es proporcionada?
- ¿Se mide la fuga por canales alternativos, como el móvil personal o la impresión?

## Errores que se repiten

- Comprar la herramienta antes de clasificar la información.
- Bloquear sin avisar y sin un canal para resolver el bloqueo.
- Cubrir solo el correo y olvidar la nube y los dispositivos extraíbles.
- Medir el éxito por número de bloqueos y no por fugas evitadas.
- Ignorar la proporcionalidad y la información al empleado.

## Fuentes

- Reglamento (UE) 2016/679 (RGPD) y Ley Orgánica 3/2018 (LOPDGDD).
- AEPD. Guías sobre videovigilancia y control del uso de herramientas informáticas.
- NIST SP 800-53, familias AC y MP (protección de soportes).
