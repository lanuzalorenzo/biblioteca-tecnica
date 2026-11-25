# Componentes del equipo

Un ordenador es un conjunto de piezas que se comunican por un bus y compiten por dos recursos: energía y ancho de banda. Entender eso evita dos errores caros: comprar piezas incompatibles y culpar al procesador de un problema que estaba en el disco.


## La placa base

Es lo que conecta todo y decide qué se puede montar.

- **Zócalo del procesador:** determina qué generaciones admite. Un zócalo equivocado no se arregla con una actualización.
- **Chipset:** reparte las líneas de comunicación entre procesador, memoria y periféricos.
- **Ranuras de memoria:** número, tipo y canales. Dos módulos en el canal correcto duplican el ancho de banda.
- **Líneas PCIe:** se reparten entre tarjetas y almacenamiento. Una tarjeta de vídeo potente puede dejar sin líneas a un disco rápido.
- **Factor de forma:** ATX, microATX e ITX, que fijan el tamaño de la caja y la fuente.

Del firmware de la placa depende el arranque: configuración de memoria, orden de arranque, virtualización y arranque seguro. Es la primera pieza que se revisa cuando el equipo no arranca.

## Procesador

Lo que importa hoy no es la frecuencia sino cuántos trabajos hace a la vez y cuánto puede esperar sin ir a memoria.

- **Núcleos e hilos:** más núcleos sirven para muchas tareas simultáneas —máquinas virtuales, compilación—; para una sola tarea, manda el rendimiento por núcleo.
- **Caché:** pequeña y carísima; si falta, cada acceso espera a la memoria.
- **Consumo y calor:** a más vatios, más refrigeración y más ruido. El consumo sostenido dice más que el pico.
- **Conjunto de instrucciones y virtualización:** comprobar que soporta las extensiones que necesitan los hipervisores.

## Memoria

- **DDR4 y DDR5** no son intercambiables: ni la muesca ni el voltaje coinciden.
- **Doble canal** funciona cuando hay dos módulos iguales en las ranuras correctas; con uno solo se pierde ancho de banda sin que nada avise.
- **ECC** detecta y corrige errores de un bit. Se usa en servidores; en un puesto de trabajo, para lo que hace un administrador, no aporta tanto como su coste.
- **Capacidad frente a uso real:** un servidor con hipervisor se queda sin memoria antes que sin procesador.

## Almacenamiento y fuente

El almacenamiento se desarrolla en [el apunte de almacenamiento y periféricos](almacenamiento-y-perifericos.md). De la fuente, tres datos: potencia real, eficiencia certificada y conectores. Una fuente justa provoca reinicios aleatorios que se confunden con fallos de software, y una fuente de mala calidad no protege al resto de componentes.

## Tarjeta gráfica y periféricos

La gráfica integrada basta para ofimática y administración; una dedicada se justifica por cálculo, muchas pantallas o trabajo gráfico. Y cada periférico añade un controlador y un consumo: es donde se acumulan las incompatibilidades pequeñas.

## Refrigeración

La refrigeración no es un accesorio de entusiastas: es lo que mantiene el procesador por debajo del umbral en el que reduce su frecuencia para protegerse. Un disipador de torre con buen flujo de aire basta en un servidor; la refrigeración líquida se justifica por espacio, ruido o consumo alto sostenido.

El flujo importa más que el número de ventiladores: aire frío por delante y por abajo, caliente por detrás y por arriba, y los cables recogidos para que no lo estorben. Un equipo con tres ventiladores mal orientados refrigera peor que uno con dos bien colocados. Y la pasta térmica caduca: en un equipo de cinco años, cambiarla puede bajar la temperatura varios grados.

## Lo que se comprueba antes de montar

Que el zócalo y el chipset admiten el procesador; que la memoria es del tipo y la frecuencia que soporta la placa; que la fuente cubre el consumo con margen; que la caja admite la longitud de la tarjeta y la altura del disipador; y que hay líneas PCIe suficientes para lo que se va a conectar.

## Errores que se repiten

- Comprar memoria de otra generación y descubrirlo al abrir la caja.
- Un solo módulo en un equipo que necesitaba doble canal.
- Fuente de potencia justa y reinicios intermitentes que se achacan al sistema.
- Contar vatios pico en lugar de consumo sostenido.
- Ignorar la altura del disipador y no poder cerrar la tapa.

## Fuentes

- Documentación de los fabricantes de placas, procesadores y memoria.
- Especificaciones de PCI Express y de los formatos de placa.
- Especificación de arranque seguro (UEFI).
