# Administración de sistemas Windows

Administrar Windows es saber qué puede hacer cada cuenta, qué servicios escuchan y qué queda registrado. El sistema viene con casi todo encendido y con permisos generosos; el trabajo del administrador es apagar lo que sobra, acotar lo que queda y poder demostrar qué pasó.


## Cuentas, grupos y permisos

Tres piezas y una regla:

- **Cuenta local:** vive en ese equipo. **Cuenta de dominio:** vive en el directorio y sirve en toda la red (se desarrolla en ASO).
- **Grupos:** se administra la pertenencia; el permiso se concede al grupo. Los integrados que importan son Administradores, Usuarios, Usuarios avanzados y Usuarios de escritorio remoto.
- **Permisos NTFS:** se aplican al recurso con independencia de cómo se llegue a él. Son acumulativos por grupo, la denegación explícita gana y los permisos se heredan del contenedor salvo que se corten.

Al compartir una carpeta hay **dos capas**: el permiso de recurso compartido, que solo aplica por red, y el NTFS, que aplica siempre. Vale el más restrictivo de los dos. Por eso «he dado control total al recurso compartido y no entra nadie» casi siempre es un problema de NTFS, no de red.

**UAC** no es un adorno: la cuenta de administrador funciona con un token limitado y pide elevación explícita. Desactivarlo convierte cualquier ejecución accidental en una instalación con privilegios.

## Directivas y configuración

- **Directiva de grupo local** en un equipo suelto; **de dominio** en una red con Active Directory, aplicada por sitio, dominio y unidad organizativa, con el orden que decide qué gana.
- Con ella se fijan política de contraseñas, bloqueo de cuentas, escritorio, unidades de red, permisos de servicios y registro de auditoría.
- **Registro de Windows:** base de datos de configuración. Se toca con la interfaz siempre que se pueda; cada cambio manual es una dependencia oculta.

La configuración del sistema tiene que quedar en algo repetible: una plantilla, una directiva o un guion. Un servidor configurado a mano es un servidor que no se puede reconstruir.

## Servicios y tareas

- **Servicios:** procesos que corren en segundo plano con su cuenta de inicio. La cuenta `LocalSystem` tiene privilegios amplios; un servicio que no los necesita debe correr con una cuenta de servicio acotada.
- **Tareas programadas:** ejecutan trabajos con hora y condiciones. Sustituyen a los guiones lanzados a mano, y quedan registrados.
- **Administración remota:** escritorio remoto para soporte, WinRM y PowerShell para automatizar. Cada vía abierta es superficie: se habilita lo que se usa y se cierra el resto.

## Registro y diagnosis

El **Visor de eventos** agrupa registros de sistema, seguridad y aplicaciones. Tres cosas hay que revisar con regularidad: inicios de sesión fallidos, cambios en cuentas y grupos, y errores de servicios críticos.

Sin auditoría activada no hay eventos que leer: la política de auditoría se configura antes del incidente, no después. Y la hora del equipo tiene que venir de una fuente común, porque un registro sin hora fiable no sirve como prueba.

## PowerShell

La consola moderna no devuelve texto, devuelve objetos: se puede filtrar, ordenar y volcar a otro comando sin recortar cadenas. Los nombres siguen el patrón verbo-sustantivo (`Get-Service`, `New-LocalUser`, `Set-ItemProperty`), y casi todo lo que se hace por interfaz tiene su equivalente.

Su valor en administración es la repetición: un inventario de servicios, una lista de equipos con disco bajo o una comprobación de permisos se escriben una vez y se ejecutan cuando haga falta. Lo que se hace por clics no se audita ni se repite igual.

## Lo que se comprueba

Que la cuenta de administrador no es la de uso diario; que la política de contraseñas y bloqueo está aplicada y se puede demostrar; que solo están en marcha los servicios necesarios; que las carpetas compartidas tienen la combinación de recurso y NTFS que se pretende —probando con un usuario del grupo, no leyendo la pestaña—; y que la auditoría de inicios de sesión genera eventos.

## Errores que se repiten

- Dar control total al recurso compartido y dejar NTFS en solo lectura.
- Usar la cuenta de administrador para el correo y la navegación.
- Desactivar UAC o el cortafuegos «para que funcione» la aplicación.
- Instalar servicios con `LocalSystem` por comodidad.
- No rotar la contraseña del administrador local común a todos los equipos.

## Órdenes que se usan a diario

```powershell
Get-LocalUser                                   # cuentas locales y su estado
New-LocalUser -Name operador -Password (Read-Host -AsSecureString)   # cuenta con clave
Get-Acl C:\datos | Format-List                 # permisos NTFS de una carpeta
icacls C:\datos /grant "devs:(OI)(CI)M"        # conceder con herencia a subcarpetas
gpupdate /force ; gpresult /r                   # aplicar y ver qué directiva llega
auditpol /get /category:*                       # qué se está auditando
```

`Get-Service` y `Get-WinEvent` sustituyen a la consola para inventariar servicios y leer eventos de forma repetible.

De PowerShell conviene quedarse además con `Start-Transcript`, que guarda en un fichero todo lo que se ejecuta y lo que devuelve. En un cambio delicado, ese registro es la diferencia entre explicar qué se hizo y suponerlo.

## Fuentes

- Documentación oficial de Windows Server, NTFS y directivas de grupo.
- Documentación de PowerShell.
- Guías de configuración segura (CIS Benchmarks, DISA STIG) para Windows.
