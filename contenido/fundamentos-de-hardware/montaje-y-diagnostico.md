# Montaje, diagnóstico y mantenimiento

Montar un equipo tiene una parte de destreza y otra, más importante, de método: por dónde se empieza, qué se comprueba antes de encender y cómo se aísla un fallo sin cambiar piezas a ciegas.


## Antes de montar

- **Electricidad estática.** El cuerpo acumula carga y una descarga invisible daña componentes. Se descarga tocando una superficie metálica conectada a tierra y se manipula por los bordes, nunca por los contactos.
- **Espacio y orden.** Los tornillos clasificados; una pieza perdida dentro de la caja no siempre se ve.
- **Documentación a mano.** El manual de la placa dice qué ranura hacer coincidir con qué canal de memoria, y ese dato no se adivina.

## El orden del montaje

1. Procesador en la placa, con la muesca alineada y sin forzar. La pasta térmica, una cantidad fina y uniforme.
2. Disipador, siguiendo el patrón de apriete del fabricante.
3. Memoria en las ranuras del canal correcto, oyendo o notando el cierre de las pestañas.
4. Placa en la caja, con los separadores colocados en su sitio: uno de más hace cortocircuito.
5. Fuente y cableado, pasando los cables por detrás cuando la caja lo permite: mejora el flujo de aire y el mantenimiento.
6. Almacenamiento y tarjetas.
7. Revisión final: nada suelto, ningún conector a medias, ventiladores que giran libremente.

El equipo se enciende por primera vez con lo imprescindible: placa, procesador, un módulo de memoria y vídeo. Si arranca, se añade el resto de uno en uno; si no arranca, el problema está en esas cuatro piezas.

## Diagnóstico por descarte

El método es ordenado, no creativo:

- **¿Se enciende?** Sin ventiladores ni luces, se mira la fuente y el botón; con las conexiones comprobadas, se prueba la fuente en otro equipo o con un comprobador.
- **¿Da imagen?** Sin imagen, se revisa la memoria —un módulo, otra ranura—, la tarjeta o el cable de la pantalla.
- **¿Arranca y no llega al sistema?** El firmware avisa con pitidos o códigos, o con una luz de diagnóstico en placas modernas. El manual traduce el código.
- **¿Arranca el sistema y falla después?** El problema deja de ser hardware de arranque: disco, memoria en uso o software.

El registro del sistema y las herramientas de comprobación de memoria y de estado del disco convierten una sospecha en un dato. Cambiar piezas por probar es rápido, caro y no enseña nada.

## Mantenimiento preventivo

- **Limpieza:** el polvo obstruye disipadores y aumenta la temperatura. Aire comprimido y sujeciones para que los ventiladores no giren en vacío.
- **Temperaturas:** se vigilan; una subida progresiva suele ser polvo o pasta seca.
- **Actualizaciones de firmware:** con precaución y con corriente estable; un corte a mitad deja el equipo sin arranque.
- **Sustitución de piezas de desgaste:** batería de la placa, que guarda la configuración y la hora; ventiladores; pasta térmica en equipos con años.
- **Inventario y etiquetas:** qué equipo es, de quién, con qué garantía. Sin eso, el mantenimiento se convierte en arqueología.

## Cuándo se repara y cuándo se sustituye

La decisión tiene tres datos: coste de la pieza, valor del equipo y coste de la interrupción. Un disco que falla en un equipo de cinco años se sustituye; una placa, en un equipo fuera de garantía y sin soporte del sistema operativo, no. Lo que no se hace es mantener vivo un equipo sin actualizaciones de seguridad porque «todavía funciona».

## Lo que se comprueba

Que el equipo arranca con lo mínimo y va añadiendo piezas sin fallos; que las temperaturas están en rango en carga; que memoria y disco pasan sus comprobaciones; que la hora y la configuración sobreviven a un corte de corriente; y que el inventario refleja la pieza cambiada.

## Errores que se repiten

- Montar sin descargar la estática.
- Forzar el procesador o el conector de memoria.
- Olvidar un separador de placa y provocar un cortocircuito.
- Cambiar piezas sin comprobar antes la fuente.
- Actualizar el firmware con el equipo colgado de una regleta compartida.

## Fuentes

- Manuales de placa y de caja de los fabricantes.
- Documentación de las herramientas de comprobación de memoria y de estado del disco.
- Especificaciones de seguridad eléctrica y manipulación de componentes.
