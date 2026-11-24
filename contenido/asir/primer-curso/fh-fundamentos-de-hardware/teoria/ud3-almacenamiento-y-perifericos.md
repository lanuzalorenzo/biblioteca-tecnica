# UD3. Almacenamiento y periféricos

El disco es la pieza que más se estropea y la que se lleva los datos cuando lo hace. Elegirlo y vigilarlo es la parte del hardware con consecuencias más caras, porque un componente de cincuenta euros puede llevarse años de trabajo.

> **Módulo:** FH. Fundamentos de hardware

## Tipos de unidad

| Tipo | Interfaz | Velocidad | Uso típico |
|---|---|---|---|
| Disco mecánico | SATA | Cientos de operaciones por segundo | Archivo, copia, volumen grande |
| SSD SATA | SATA | Miles | Puesto de trabajo con equipo antiguo |
| SSD NVMe | PCIe | Decenas de miles | Sistema, base de datos, virtualización |

Un disco mecánico sigue teniendo sentido donde importa la capacidad por euro y el acceso no es aleatorio. Un SSD cambia la sensación de un equipo viejo más que cambiar el procesador, y es lo primero que se sustituye en un puesto lento.

De un SSD importan dos datos que no aparecen en el escaparate: **escrituras totales soportadas** y comportamiento cuando se llena. Un disco casi lleno pierde rendimiento y vida útil, porque el controlador necesita espacio libre para reorganizar.

También hay que distinguir la conexión de la forma: `M.2` es un formato de tarjeta y puede llevar SATA o NVMe; no todo M.2 es rápido, y esa confusión se paga al comprar.

## Vigilar el disco

- **Estado del disco:** los discos y SSD modernos informan de su salud. Se consulta periódicamente, no cuando el equipo ya no arranca.
- **Sectores reasignados y errores:** un valor creciente es un aviso; el disco está compensando defectos.
- **Espacio libre:** por debajo del diez por ciento, tanto el sistema como las bases de datos empeoran.
- **Temperatura:** un NVMe sin disipador puede reducir velocidad en carga sostenida.

La vigilancia se automatiza: una comprobación programada que avisa es más fiable que la costumbre de mirar.

## Redundancia, copia y archivo

Aquí conviene no confundir tres conceptos que la unidad de almacenamiento de SAD desarrolla: el **RAID** da continuidad ante el fallo de un disco, la **copia de seguridad** permite volver atrás y el **archivo** conserva lo que ya no se usa. Un equipo puede tener las tres cosas y aun así perder datos si solo tiene la primera.

## Periféricos

Lo que añade un periférico es un controlador, un consumo y una posible incompatibilidad. Los que más problemas dan:

- **Pantallas:** la conexión y la resolución admitida. Dos pantallas a alta resolución pueden superar lo que la salida integrada soporta.
- **Concentradores USB:** reparten ancho de banda; un disco y una cámara en el mismo concentrador compiten.
- **Impresoras:** controlador, cola y dirección fija. Una impresora por dirección dinámica falla un lunes por la mañana.
- **Dispositivos de entrada:** teclados y ratones sin cables añaden dependencia de batería y de receptor.

Un periférico que funciona en un equipo y no en otro casi siempre es alimentación o controlador, no el periférico.

## Sustituir sin perder nada

Cambiar un disco exige un orden: copia verificada de los datos, comprobación de que la copia se puede restaurar, sustitución, instalación y vuelta de los datos. Hacerlo al revés —cambiar primero y buscar la copia después— es cómo se convierte una mejora en una pérdida.

Y un aviso de vida útil: los equipos se retiran con los datos dentro. Un disco que sale del taller se borra de forma segura o se destruye físicamente; formatear no borra.

## Lo que se comprueba

Que el disco elegido es compatible con la placa y la caja; que la salud del disco en uso no tiene avisos; que hay espacio libre suficiente; que las temperaturas están en rango; que los periféricos críticos tienen dirección fija; y que el equipo retirado se ha borrado antes de salir.

## Errores que se repiten

- Comprar un M.2 SATA creyendo que es NVMe.
- Llenar el disco del sistema hasta el último giga.
- Confiar en el RAID como copia de seguridad.
- Cambiar disco sin restaurar antes una copia de prueba.
- Tirar un disco sin borrarlo.

## Fuentes

- Especificaciones de SATA, NVMe y PCI Express.
- Documentación de las herramientas de estado del disco.
- Guías de borrado seguro de medios de almacenamiento.
