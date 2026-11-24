# UD4. Despliegue, clonado y virtualización

Poner un sistema en un equipo es un rato; ponerlo en treinta sin que cada uno salga distinto es un procedimiento. La diferencia entre las dos cosas es la misma que entre cocinar para uno y montar un servicio de comidas: hace falta una receta que otra persona pueda ejecutar igual.

> **Módulo:** ISO. Implantación de sistemas operativos

## Del equipo dorado a la plantilla

Un despliegue ordenado se apoya en una **imagen de referencia** —el «equipo dorado»—: sistema actualizado, software autorizado, configuración fijada y sin datos de nadie. De ahí salen las copias.

- **Clonado con imagen:** se captura el disco entero y se restaura en otro equipo. Rápido, y peligroso si se olvida la preparación previa.
- **Plantilla en un hipervisor:** la máquina virtual se convierte en molde; cada instancia arranca de una copia. Es el camino habitual en servidores.
- **Instalación por red con PXE:** el equipo arranca desde la red, recibe la imagen y aplica su configuración. Permite atender varios a la vez y elegir variante por equipo.

En todos los casos hay dos operaciones previas innegociables: eliminar la identidad —en Windows con `sysprep`, que generaliza y limpia; en Linux, claves de host SSH, identificadores de máquina, registros e histórico— y dejar fuera cualquier credencial que la imagen pudiera arrastrar.

## Virtualización

Virtualizar es ejecutar varios sistemas sobre uno con un hipervisor. Importa por tres razones prácticas:

- **Laboratorio:** un equipo puede tener servidor, cliente y fallo reproducible sin comprar hardware.
- **Consolidación:** lo que ocupaba tres servidores cabe en uno, con menos consumo y más copia.
- **Plantillas y reversión:** una instantánea antes de tocar permite volver en segundos.

Dos modelos: **hipervisor de tipo 1**, que corre sobre el hardware (ESXi, Hyper-V, Proxmox, KVM como base del sistema), y **tipo 2**, que corre sobre un sistema operativo de escritorio (VirtualBox y similares). En producción manda el tipo 1; en el aula, el tipo 2 es suficiente y más cómodo.

Y una advertencia que se aprende con un susto: una instantánea no es una copia de seguridad. Vive en el mismo almacenamiento, con las mismas credenciales, y si el volumen se daña, se van las dos.

## Configuración declarativa

Los guiones clásicos dicen **qué hacer** paso a paso; las herramientas de gestión de configuración describen **cómo debe quedar** el equipo y convergen hacia ello. La diferencia se nota al ejecutarlas dos veces: el guion repite y puede romper; la herramienta comprueba y solo cambia lo que no está.

Ese principio —idempotencia— es el que permite administrar veinte servidores con la misma definición y detectar el que se ha desviado. Es el mismo criterio que la línea base de un sistema: se define una vez, se aplica y se comprueba.

## Inventario y ciclo de vida

Un despliegue no acaba al instalar. Hay que saber qué equipos existen, con qué sistema y versión, cuándo se actualizaron y cuándo se retiran.

- **Inventario:** nombre, función, ubicación, sistema, versión, responsable y etiqueta física que coincida con el registro. Un inventario que no se puede comprobar en el rack no se mantiene.
- **Ciclo de vida:** fecha de fin de soporte del sistema y de las aplicaciones. Un servidor fuera de soporte es un riesgo conocido y medible, no una sorpresa.
- **Baja:** retirar el equipo incluye borrar los datos de forma que no se puedan recuperar, no solo apagarlo.

## El arranque por red

PXE usa dos servicios que ya existen en la red: DHCP, que además de la dirección indica dónde está el servidor de arranque, y TFTP, que entrega la primera imagen. De ahí sale un menú de instalación o un entorno que aplica la imagen completa.

Ese mismo mecanismo es una puerta: un servidor PXE no autorizado en la red puede arrancar equipos con una imagen propia. Por eso se controla a nivel de puerto y de VLAN, no solo en el servidor.

## Lo que se comprueba

Que una imagen capturada se restaura en un equipo distinto y arranca; que no lleva cuentas ni claves heredadas; que el equipo resultante tiene su nombre, su red y su identidad de dominio; y que el inventario refleja lo desplegado el mismo día.

## Errores que se repiten

- Clonar con la máquina encendida y con la identidad sin limpiar.
- Reutilizar la misma contraseña de administrador local en toda la flota.
- Guardar las imágenes donde el usuario al que se las restaura tiene acceso.
- Dar por hecho que la plantilla está actualizada cuando se creó hace un año.

## Órdenes que se usan al desplegar

```powershell
C:\Windows\System32\Sysprep\sysprep.exe /generalize /oobe /shutdown
Get-VM | Select-Object Name,State          # inventario del hipervisor
```

```bash
ansible all -m ping                        # comprobar alcance antes de aplicar
ansible-playbook sitio.yml --check         # ver qué cambiaría, sin cambiar
virsh snapshot-create-as servidor antes   # instantánea previa a un cambio
```

La copia de la imagen se verifica restaurándola en un equipo distinto; mientras eso no ocurra, solo se sabe que el fichero existe.

Una imagen tiene un límite que conviene decir en voz alta: solo sirve mientras los equipos sean iguales. En cuanto hay tres modelos de portátil con controladores distintos, o dos versiones de sistema, la imagen única deja de ser una ventaja y se convierte en un problema de inventario. Ahí es donde entra el despliegue por red con perfiles, o la configuración declarativa que se aplica después de instalar una base común.

## Fuentes

- Documentación oficial de `sysprep`, WDS/MDT, Clonezilla y los hipervisores citados.
- Documentación de Ansible y de las herramientas de gestión de configuración.
- Catálogos de fin de soporte de los fabricantes de sistemas operativos.
