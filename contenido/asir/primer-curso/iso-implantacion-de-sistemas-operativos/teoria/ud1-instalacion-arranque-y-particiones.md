# UD1. Instalación, arranque y esquemas de disco

Instalar un sistema operativo se parece a amueblar una casa vacía: hay que decidir cuántas habitaciones hay, cuáles se comparten y dónde va la puerta de entrada. Elegir mal el esquema de disco o el gestor de arranque se paga meses después, cuando hay que mover una partición con datos dentro.

> **Módulo:** ISO. Implantación de sistemas operativos

## Del botón al sistema

La secuencia siempre es la misma, y saber dónde se rompe ahorra horas:

1. **Firmware** (BIOS o UEFI) comprueba el hardware y busca un medio de arranque según el orden configurado.
2. **Carga el gestor de arranque** del disco —GRUB en Linux, el administrador de arranque de Windows— o el del medio de instalación.
3. **El gestor elige el núcleo o el sistema** y le pasa el control.
4. **El sistema monta la raíz**, arranca los servicios y da acceso.

La diferencia entre BIOS y UEFI no es cosmética: UEFI arranca desde una partición FAT con un fichero `.efi`, admite discos mayores de 2 TiB sin trucos, permite arranque seguro y guarda las entradas de arranque en la memoria del firmware, no solo en el disco.

## Particiones

- **MBR:** tabla clásica, cuatro particiones primarias —o tres más una extendida con lógicas—, límite de 2 TiB. Arranca en BIOS.
- **GPT:** hasta 128 particiones, identificadores GUID, sin límite práctico de tamaño. Es la opción por defecto con UEFI.

En un Linux de servidor, un esquema defendible separa `/` de lo que crece solo:

| Partición | Por qué separada |
|---|---|
| `/` | El sistema; pequeña y estable |
| `/home` | Datos de usuario; se conserva al reinstalar |
| `/var` | Registros y colas; es la que llena el disco |
| `/srv` o `/opt` | Servicios y aplicaciones instaladas aparte |
| `swap` | Memoria de intercambio; con hibernación, igual o mayor que la RAM |
| EFI (`/boot/efi`) | Solo con UEFI; FAT32 y sin cifrar |

Si `/var` comparte partición con `/`, un registro desbocado llena el disco y tumba el sistema entero. Ese es el motivo real de separar, no la elegancia.

Los sistemas de ficheros tampoco son intercambiables: NTFS en Windows, con permisos y registro de transacciones; ext4, XFS y Btrfs en Linux, donde XFS crece bien en servidores y Btrfs añade instantáneas y suma de comprobación.

## Instalación repetible

Instalar un equipo a mano se aprende una vez; instalar veinte exige otra cosa:

- **Imagen del sistema** con una herramienta de clonado: rápida y frágil, porque cada equipo queda idéntico, con el mismo nombre y las mismas claves.
- **Preparación previa** antes de capturar la imagen: en Windows, `sysprep` generaliza el equipo y elimina la identidad; en Linux se limpian claves de host, registros y configuración de red.
- **Instalación por red** con arranque PXE y un servidor de despliegue, que permite elegir imagen por equipo.
- **Configuración declarativa** con una herramienta de gestión (Ansible y similares): se describe el estado final y la herramienta converge, en lugar de repetir pasos.

La guía de instalación que se escribió en el módulo cumplía una función que se olvida: dejar por escrito las decisiones —tamaños, nombres, contraseñas de servicio— para que otro pueda repetirlas. Sin eso, la instalación solo la sabe hacer quien la hizo.

## Licencias y activación

Un despliegue en regla distingue tres cosas: qué licencia tiene el sistema, cuántas instalaciones permite y cómo se activa. Clonar un Windows ya activado sin prepararlo produce equipos que se desactivan solos o, peor, que comparten identificador. En Linux la cuestión es la licencia del software instalado encima, no del núcleo.

## Lo que se comprueba

Que el equipo arranca con el disco interno y no con un USB olvidado; que la partición EFI está montada y el arranque seguro hace lo que se espera; que `/var` tiene espacio propio; que el nombre del equipo, la zona horaria y la red son los correctos; y que la imagen restaurada en otro equipo arranca y no arrastra la identidad del anterior.

## Errores que se repiten

- Instalar en modo BIOS con un disco GPT y luego preguntarse por qué no arranca.
- Comprimir la partición raíz «para dejar sitio» y quedarse sin margen para actualizaciones.
- Capturar la imagen con la máquina encendida y con cuentas ya creadas.
- Documentar la instalación en la cabeza.

## Órdenes que se usan al instalar

```bash
lsblk -f                # discos, particiones y sistemas de ficheros
parted -l               # tabla de particiones y tipo (msdos o gpt)
blkid                   # identificadores y tipos de cada partición
efibootmgr -v           # entradas de arranque de UEFI y su orden
update-grub             # regenera la configuración de GRUB tras un cambio
```

En Windows, `diskpart` con `list disk` y `list partition` responde a las mismas preguntas, y `bcdedit /enum` muestra las entradas del gestor de arranque.

## Fuentes

- Especificación UEFI y documentación de GPT.
- Estándar de jerarquía del sistema de ficheros (FHS).
- Documentación oficial de GRUB 2, `sysprep` y las herramientas de clonado.
