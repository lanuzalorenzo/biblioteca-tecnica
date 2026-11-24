# UD4. Imágenes de software y hardware de CPD

Instalar veinte equipos a mano no es administrar: es repetir el mismo trabajo veinte veces y esperar que salga igual. La imagen de software convierte esa repetición en un procedimiento; el CPD es el sitio donde esos equipos viven y donde una toma mal calculada tumba más que un disco.

> **Módulo:** FH. Fundamentos de hardware

## La imagen de referencia

Una imagen es una copia completa de un sistema instalado y configurado: sistema operativo, controladores, aplicaciones, ajustes y —a veces— el perfil de usuario. Se construye una vez, se prueba y se despliega.

La receta cambia poco entre organizaciones:

1. **Sistema base** desde la fuente oficial, con las actualizaciones del día.
2. **Controladores** del hardware que se va a encontrar.
3. **Aplicaciones y ajustes** comunes, con licencias y activación resueltas.
4. **Limpieza:** sin cuentas personales, sin datos de prueba, sin contraseñas guardadas.
5. **Generalización:** en Windows, `sysprep` quita la identidad del equipo —nombre, SID— para que la imagen se pueda aplicar a varios; en Linux se revisan `machine-id`, claves SSH y red.
6. **Prueba** en un equipo distinto del que se creó.

La imagen envejece: si se despliega seis meses después sin actualizar, cada equipo nace con seis meses de parches pendientes.

## Clonación y despliegue

Herramientas y vías:

- **Clonación local:** Clonezilla o `dd` copian disco a disco o a una imagen. `dd` copia byte a byte, incluido lo vacío; Clonezilla copia solo lo usado y comprime.
- **Despliegue por red:** PXE arranca el equipo desde la red, descarga la imagen y la aplica. Windows Deployment Services o MDT lo hacen en entornos Microsoft; FOG y herramientas libres cubren el mismo caso.
- **Aprovisionamiento declarativo:** Ansible, Puppet o similares instalan y configuran sin imagen, partiendo de un sistema mínimo. Es más flexible para flotas heterogéneas; exige más disciplina.

El **arranque por red** necesita DHCP con la opción de servidor de arranque, TFTP o HTTP para la imagen y un menú que elija el equipo. Si DHCP falla, el despliegue entero se queda esperando.

## Licencias y activación

La imagen no puede saltarse la licencia. Hay que distinguir licencias OEM —atadas al equipo—, licencias por volumen y suscripciones. La activación se resuelve con un servidor de activación, con claves por volumen o con la cuenta de la organización, según el contrato. Una imagen con la clave de otra empresa es un problema legal, no un atajo.

También conviene guardar los instaladores, las claves y la documentación de configuración: el software también se respalda. Una licencia sin su instalador es un papel.

## El CPD

Un centro de proceso de datos pequeño sigue las mismas reglas que uno grande. El detalle de climatización, suministro y extinción está en SAD, UD3; aquí se resume lo que afecta a la instalación del hardware:

- **Rack y espacio:** armario de 19 pulgadas, unidades U contadas y flujo de aire previsto. No se llena un hueco con un equipo que no cabe.
- **Alimentación:** PDU, protección y SAI. Los servidores con dos fuentes van a circuitos distintos; el SAI cubre el corte y el apagado ordenado, no la autonomía indefinida.
- **Refrigeración:** temperatura y humedad controladas, pasillo frío y pasillo caliente si hay varios racks, y sensores que avisan.
- **Cableado:** etiquetado, ordenado, sin curvas cerradas ni cables por el suelo; fibra y cobre separados cuando toca.
- **Acceso y extinción:** puerta cerrada, registro de entradas y sistema de extinción adecuado al equipo eléctrico.
- **Monitorización:** temperatura, humedad, consumo, estado de las baterías y alarmas.

La norma **UNE-EN 50600** y la TIA-942 ordenan estos requisitos por niveles de disponibilidad. Para una pyme no hace falta un CPD de nivel IV; sí saber qué fallo único deja el servicio caído.

## Lo que se comprueba

Que la imagen se ha probado en un equipo distinto y arranca sin datos heredados; que la generalización y la activación están resueltas; que el despliegue por red tiene DHCP, arranque y menú; que las licencias e instaladores están guardados; que el SAI y los circuitos están separados; que la temperatura y la humedad se vigilan; y que el cableado está etiquetado.

## Fuentes

- Documentación de Microsoft: Sysprep, Windows Deployment Services y MDT.
- Documentación de Clonezilla y de PXE.
- UNE-EN 50600, instalaciones de centros de datos; TIA-942.
- Orden EDU/392/2010, de 20 de enero, currículo del ciclo de ASIR (BOE-A-2010-3028), módulo 0371.
