# Puesta en producción segura

Abrir un restaurante no empieza cuando se enciende el cartel de la puerta. Antes hay que comprobar que la cámara frigorífica mantiene la temperatura, que el almacén está separado de la zona de cocina, que cada persona sabe qué le corresponde y que existe un plan para cuando algo se estropea. El día de la apertura no se estrena la cocina: se confirma que lo que ya funcionaba en pruebas sigue funcionando con clientes dentro.

Publicar software se parece a eso. El código que arranca en mi portátil no demuestra nada sobre el servicio que atenderá a otras personas: cambian los permisos, las dependencias, la red y los datos. Este módulo reúne lo que necesito para leer, ejecutar y probar una aplicación antes de exponerla, y para entender qué protege el lenguaje y qué debe proteger el entorno.

## Contenido

| Nota | Qué trata |
|---|---|
| [Fundamentos de programación para administradores de sistemas](fundamentos-de-programacion.md) | Cómo se traduce y ejecuta el código, y cómo se recorre un programa ajeno |
| [Introducción práctica a Python orientada a la seguridad](python-para-seguridad.md) | Sintaxis, entornos virtuales, dependencias y una primera comprobación automatizada |
| [Java y ejecución real](java-y-ejecucion-real.md) | Bytecode, JVM, memoria, proceso y secretos en artefactos compilados |
| [Pruebas de software](pruebas-de-software.md) | Casos, cobertura, mutación y conversión de un hallazgo en prueba de regresión |
| [Seguridad en lenguajes y entornos de ejecución (sandboxes)](sandboxes-y-aislamiento.md) | Memoria, tipos, `eval()` y aislamiento con contenedores |

## Límites

Este módulo describe prácticas defensivas y de revisión. Nada de lo que aparece aquí autoriza a examinar sistemas ajenos.

- **Las pruebas se ejecutan solo sobre lo propio o lo autorizado por escrito.** Un escaneo, una petición HTTP o un script de comprobación contra un servicio de terceros no son un ensayo: son tráfico real.
- **El laboratorio va aislado.** Las máquinas de prueba no comparten red con la organización ni con la red doméstica, y se descartan al terminar.
- **No se publican secretos ni datos reales.** Los ejemplos usan dominios reservados, credenciales ficticias y cifras inventadas.
- **Los identificadores CWE y las referencias a versiones son orientativos.** Antes de citarlos en un informe se contrastan con la fuente vigente; un número memorizado no es una prueba.
- **Un control no se da por implantado porque esté escrito.** Se comprueba leyendo la configuración real y ejecutando una prueba que falle cuando el control desaparece.

## Cómo se leen

El recorrido va de dentro hacia fuera. Las dos primeras notas explican cómo se escribe y se ejecuta el software y cómo se lee un script; la tercera baja al artefacto compilado y al proceso que ve el sistema operativo; la cuarta convierte una revisión en pruebas repetibles; la quinta separa lo que garantiza el lenguaje de lo que solo puede garantizar el aislamiento.

Cada nota se sostiene por separado, pero el orden ayuda: sin entender qué se ejecuta cuesta interpretar una prueba, y sin pruebas la corrección de un fallo queda en una promesa. Los enlaces internos llevan a la nota que amplía el tema, no a material externo.
