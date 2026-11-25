# Samba, impresión y recursos compartidos

Compartir una carpeta en una red mixta es el problema más viejo del ofimático: hay servidores Linux, puestos Windows y una impresora que nadie sabe dónde está. Samba y CUPS resuelven lo primero; entender los permisos resuelve lo segundo, que es donde se pierden las tardes.


## SMB y Samba

**SMB** es el protocolo de compartición de ficheros e impresoras de Windows. **Samba** lo implementa en Linux, y permite dos papeles distintos:

- **Servidor miembro** de un dominio existente: se une al directorio y usa sus cuentas.
- **Controlador de dominio**, incluyendo el modo de directorio compatible con Active Directory.

Un recurso se declara en `smb.conf` con su ruta, quién puede verlo y quién puede escribir:

```
[proyectos]
   path = /srv/proyectos
   valid users = @devs
   read only = no
   create mask = 0660
   directory mask = 2770
```

Los valores que se discuten siempre: `valid users` limita quién entra; las máscaras fijan los permisos de lo que se cree; y `force group` unifica el grupo para que el trabajo compartido no dependa de quién creó el fichero.

## Los dos permisos que se suman

En un recurso SMB hay dos capas, igual que en Windows: el permiso del recurso compartido y el permiso del sistema de ficheros. Manda el más restrictivo.

Y una tercera capa que se olvida: el **mapeo de usuarios**. Linux y Windows no comparten identificadores, así que hay que decidir cómo se traduce una cuenta. Con `sssd` o `winbind` contra un directorio, la traducción es automática; sin directorio, se mantiene una tabla a mano, y ahí empiezan las diferencias entre equipos.

Un detalle que ahorra horas: en Linux, un directorio compartido necesita **setgid** para que lo creado dentro herede el grupo. Sin él, cada usuario crea ficheros con su grupo principal y nadie más puede escribir aunque el permiso lo diga.

## Impresión

**CUPS** es el sistema de impresión de Linux: gestiona colas, controladores y trabajos, y publica las impresoras por IPP. En Windows, el servicio de cola hace lo propio y publica en el directorio.

Lo que hay que dejar claro en cualquier instalación:

- La impresora se reserva una dirección fija; una IP por DHCP convierte la cola en un error aleatorio.
- Los controladores se despliegan de forma central, no equipo a equipo.
- Hay cuota o registro de trabajos: una impresora sin control imprime lo que no debe y nadie lo sabe.
- La cola se purga y se revisa: un trabajo atascado bloquea a todos los demás.

La parte que se olvida es la de seguridad: una impresora guarda en su disco lo que imprime. Al retirarla, se borra; mientras está en la red, no se deja en una VLAN de usuarios.

## NFS, la alternativa Linux

Entre sistemas Linux, NFS es más directo que SMB: se exporta un directorio en `/etc/exports` con sus clientes y opciones, y se monta en el cliente. No lleva autenticación de usuario propia: confía en la dirección del cliente o en Kerberos, y por eso se limita a redes internas y a hosts concretos.

## Lo que se comprueba

Que un usuario del grupo escribe y otro de fuera no, probado con las dos cuentas; que lo creado por uno puede editarlo el otro; que al reiniciar el servidor el recurso se vuelve a publicar; que la impresora responde tras un cambio de red; y que no queda ningún recurso con acceso anónimo sin querer.

## Errores que se repiten

- Publicar una carpeta con `read only = no` y sin `valid users`.
- Dar permisos en el recurso compartido y olvidar los del sistema de ficheros.
- No mapear usuarios y acabar con ficheros de «nobody».
- Montar NFS en abierto en una red con invitados.

## Órdenes para comprobar un recurso

```bash
testparm                           # valida smb.conf antes de recargar
smbclient -L //servidor -U lorenzo # lista recursos con una cuenta real
mount -t cifs //servidor/proyectos /mnt/p -o user=lorenzo,vers=3.0
showmount -e servidor              # exportaciones NFS visibles
lpstat -t                          # colas de impresión y trabajos
```

La prueba se hace con la cuenta del usuario y desde otro equipo. Lo que diga el servidor sobre sí mismo no demuestra nada.

## Fuentes

- Documentación oficial de Samba, de CUPS y de NFS.
- Especificación del protocolo SMB.
- Páginas de manual de `exports` y `smb.conf`.
