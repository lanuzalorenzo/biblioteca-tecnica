# Sistema operativo y aplicaciones

Si el CPD es la cerradura de la calle, el sistema operativo es lo que se cierra por dentro: la puerta del piso, el armario con llave y la lista de quién tiene copia. Un equipo con el sistema mal configurado deja sin efecto la sala blindada donde está.


## Antes de arrancar: firmware

El primer control está por debajo del sistema operativo. Si alguien puede cambiar el orden de arranque, entra con un LiveCD y lee el disco sin tocar la contraseña de Windows.

- **Contraseña de UEFI** para impedir cambios de configuración; en muchos equipos, además, contraseña de arranque.
- **Arranque seguro** (*Secure Boot*): solo se ejecuta software firmado por una autoridad reconocida por el firmware. Bloquea los gestores de arranque manipulados.
- **Orden de arranque fijado** en el disco interno, con el arranque por USB y por red desactivado salvo cuando se necesite.
- **Detección de apertura de la caja:** el firmware deja constancia y avisa en el siguiente arranque.
- **TPM 2.0:** chip que guarda claves y mide lo que se ejecuta durante el arranque. Es lo que permite que el disco se descifre solo cuando la cadena es la esperada.

## Cifrado del disco

Si el equipo se pierde o lo roban, el cifrado es la única medida que sigue protegiendo los datos. Sin él, extraer el disco y montarlo en otro equipo es cuestión de minutos.

- **Linux:** LUKS2 sobre la partición raíz, con Argon2id como derivación de clave.
- **Windows:** BitLocker con TPM, y PIN si el equipo sale a la calle. La clave de recuperación se guarda en un repositorio de custodia —AD, Entra ID— nunca junto al equipo.

El cifrado protege el dato en reposo, no el sistema en marcha: con la sesión abierta, el disco está descifrado.

## Autenticación

- **Contraseña:** sigue siendo el factor principal y la causa principal de incidentes. El criterio actual —NIST SP 800-63B— pide longitud mínima de 8 caracteres, comprobación contra listas de contraseñas filtradas y **nada de caducidad forzada ni reglas de composición**. Rotar cada 90 días produce contraseñas peores y más predecibles. Se cambia cuando hay indicio de compromiso.
- **Tarjeta o token:** el material de 2015 distinguía bien dos tipos. En una tarjeta de **almacenamiento**, el equipo lee la clave y la usa; en una de **procesamiento**, la clave nunca sale del chip y es el chip quien firma el desafío. La segunda es la que aguanta un ataque sobre el lector.
- **Biometría:** cómoda, no secreta y no revocable. Se mide con dos tasas: falsos positivos (acepta a quien no es) y falsos negativos (rechaza a quien sí es). Se usa como comodidad o como segundo factor, no como llave única.
- **Multifactor:** combinar factores de tipos distintos. Contraseña más código en el móvil es MFA; contraseña más pregunta secreta, no.

## Autorización y privilegios

- **Mínimo privilegio:** cada cuenta tiene lo que necesita para su trabajo y nada más.
- **Cuenta de administración separada** de la de uso diario, y elevación puntual: UAC en Windows, `sudo` en Linux. Desactivar UAC «porque molesta» es regalar la mitad de la protección.
- **Grupos, no permisos por usuario.** Se administra la pertenencia y se audita.
- **Cuentas de servicio** con contraseña gestionada, sin inicio de sesión interactivo y con permisos acotados.
- **Cuotas de disco** por usuario: evitan que el llenado del disco tumbe un servicio y que un usuario deje sin espacio al resto.

## Aplicaciones

- Instalar solo lo necesario y siempre desde una cuenta de administración.
- **Desactivar el autoarranque** de medios extraíbles y de instaladores descargados: es la vía de entrada de buena parte del malware doméstico.
- **Actualizar** sistema y aplicaciones; las vulnerabilidades explotadas el año pasado estaban parcheadas y sin aplicar.
- **Listas de permitidos** (*AppLocker*, WDAC) para lo que corre en puestos críticos: si no está en la lista, no se ejecuta. Es más eficaz que cualquier antivirus firmado.
- **EDR** en lugar del antivirus clásico: no solo detecta firmas, registra comportamiento y permite responder.
- **Firma de código** y verificación del origen de lo que se instala.

## Registro y auditoría

Lo que no se registra no se puede investigar ni demostrar. Como mínimo:

- Inicios de sesión correctos y fallidos, y elevaciones de privilegio.
- Altas, bajas y cambios de cuentas y de grupos.
- Arranque y parada de servicios, y cambios de configuración.
- Errores del sistema y de las aplicaciones críticas.

Tres condiciones hacen útil un registro: **hora fiable** (servicio de tiempo sincronizado), **retención definida** y **envío a un sistema central** al que el atacante no llegue con las credenciales del equipo comprometido. En un equipo aislado, el atacante borra sus huellas con privilegios de administrador.

## Línea base y comprobación

Endurecer un sistema es aplicar una configuración conocida y poder demostrar que sigue puesta. Se parte de una guía pública —CIS Benchmarks, DISA STIG— y se adapta: no todos los controles aplican a un servidor de base de datos ni a un puesto de aula. Después se comprueba de forma automática y periódica, porque lo que no se mide vuelve a su estado por defecto en la siguiente instalación.

## Errores que se siguen viendo

Cuenta de administrador local compartida para todo y con la misma contraseña en cien equipos; actualizaciones desatendidas durante meses; antivirus instalado pero sin actualizar firmas; registro activado sin nadie que lo lea; y la idea de que un equipo de aula no necesita protección porque «no tiene datos», cuando lo que guarda son credenciales de la red.

## Lo que ha cambiado desde 2015

BIOS pasó a UEFI con arranque seguro; el antivirus de firmas se ha quedado corto frente al EDR; la caducidad periódica de contraseñas se ha retirado de las recomendaciones; Windows 7 y Windows Server 2008 —los del material original— llevan fuera de soporte desde enero de 2020. La idea de fondo no ha cambiado: menos superficie, menos privilegio, registro y actualización.

## Fuentes

- NIST SP 800-63B, guía de autenticación digital.
- CIS Benchmarks y DISA STIG, guías de configuración segura por plataforma.
- Especificación UEFI y documentación de BitLocker y LUKS2.
- ISO/IEC 27001:2022, controles tecnológicos (anexo A, tema tecnológico).
