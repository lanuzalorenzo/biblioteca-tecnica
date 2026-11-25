# Gestión de cuentas privilegiadas

Si una cuadrilla usa la misma llave del almacén, nadie puede decir quién entró el día que faltó material. Las cuentas de administración sufren el mismo problema: una credencial para diez personas deja un registro que no identifica a nadie y obliga a cambiarlo todo cuando una se marcha. La cuenta privilegiada abre la puerta grande del sistema; su gestión decide si un robo se queda en un incidente o se convierte en una brecha de toda la organización.

El mínimo privilegio y la separación de la cuenta administrativa se explican en [Sistema operativo y aplicaciones](../seguridad-y-alta-disponibilidad/sistema-operativo-y-aplicaciones.md). Este apunte se centra en cómo se ataca esa cuenta y qué configuración reduce el daño cuando cae.

## Por qué es el objetivo

Una cuenta con privilegios puede leer datos, cambiar configuraciones, crear usuarios y desactivar defensas. El atacante no pierde tiempo con la cuenta de un becario: busca la que administra. Dos técnicas conocidas permiten llegar a ella sin descifrar la contraseña:

- **Pass the hash.** Windows acepta el hash NTLM como prueba de identidad, sin necesidad de la contraseña en claro. Quien copia ese hash de la memoria o del registro puede usarlo tal cual.
- **Pass the ticket.** Un ticket Kerberos válido —el TGT que entrega el controlador de dominio— abre los servicios sin volver a pedir credenciales. Si cae la cuenta `krbtgt`, se pueden fabricar tickets para cualquiera: el *golden ticket*.

Robar una credencial no cierra el ataque, lo abre. Se empieza con una cuenta normal, se salta a una administrativa y desde ahí se llega al controlador de dominio.

## Cuatro reglas de partida

1. **Mínimo privilegio.** Cada cuenta tiene lo necesario para su trabajo y durante el tiempo necesario.
2. **Cuentas separadas.** Una para el uso diario y otra para administrar; nunca la misma.
3. **Sin cuentas compartidas.** Si dos personas necesitan el mismo permiso, se crean dos cuentas con el mismo rol.
4. **Administración desde un equipo dedicado.** La cuenta privilegiada no se usa desde el portátil con el que se navega.

La tercera regla es la que resuelve el caso de la cuadrilla: el problema no era el material perdido, sino no poder saber quién lo cogió.

## Propiedades que limitan el daño

En Windows, cada cuenta tiene atributos que reducen el alcance de un compromiso. Bien puestos, convierten una credencial robada en una credencial incómoda:

| Atributo | Uso recomendado |
|---|---|
| Horario de inicio de sesión | Restringirlo en cuentas de servicio y de terceros |
| Equipos donde puede iniciar sesión | Limitar las cuentas administrativas a sus servidores |
| La cuenta expira | Obligatorio en cuentas temporales y de proveedor |
| Cambiar contraseña en el próximo inicio | Al crear la cuenta y al restablecerla |
| La contraseña nunca caduca | Solo en cuentas de servicio con clave gestionada |
| El usuario no puede cambiar la contraseña | Cuentas de servicio, nunca cuentas de persona |
| Almacenar contraseña con cifrado reversible | Desactivado; expone la clave al recuperarla |
| Confiable para delegación | Solo si la aplicación lo exige y con auditoría |

## Grupos y delegación

Los permisos se asignan por grupo. Si se conceden persona a persona, revisar el directorio se vuelve imposible y nadie sabe quién puede qué.

En Active Directory hay dos clases de grupo:

- **De distribución:** solo para listas de correo, sin identificador de seguridad.
- **De seguridad:** con identificador y capacidad de otorgar permisos.

Los grupos que vienen de serie —Administradores del dominio, Operadores de servidores, Administradores de empresa— incluyen derechos predefinidos y protegidos. Saber qué concede cada uno evita dos errores habituales: dar un permiso suelto cuando ya había un grupo que lo cubría e incluir a alguien en un grupo potente por rapidez.

La **administración delegada** reparte tareas concretas sin entregar el control total. Se organiza con unidades organizativas y permisos de distinta granularidad: restablecer contraseñas de un departamento, administrar impresoras de una sede, gestionar copias. La jerarquía se diseña por ubicación, departamento, tipo de recurso o una combinación, y conviene que sea estable.

## La cuenta de administrador local

Todo Windows trae una cuenta de administrador local. Las versiones actuales la entregan desactivada, pero sigue dando problemas en equipos antiguos, en instalaciones donde alguien la activó y cuando la misma clave se repite en toda la red.

Buenas prácticas:

- No usarla para el trabajo diario; sirve para recuperar un equipo en modo seguro.
- Renombrarla reduce los intentos automatizados contra el nombre conocido, aunque no es una defensa real.
- Poner una contraseña distinta en cada equipo, gestionada por **Windows LAPS**, que la rota y la guarda en Active Directory o en Entra ID. Con la misma clave en cien equipos, un solo compromiso los abre todos.

## Separar la administración por niveles

El modelo de niveles de Microsoft divide la administración en tres capas y prohíbe usar una credencial de nivel inferior en una superior:

| Nivel | Qué contiene |
|---|---|
| 0 | Identidad: controladores de dominio, Entra ID, autoridades de certificación |
| 1 | Servidores y aplicaciones |
| 2 | Puestos de trabajo y dispositivos de usuario |

Un administrador de servidores no inicia sesión en un controlador de dominio con su cuenta, ni administra servidores desde un portátil de nivel 2. Esa separación impide que un puesto infectado escale hasta la identidad.

## Bóveda y acceso justo a tiempo

Una solución de gestión de cuentas privilegiadas añade tres controles que la configuración sola no ofrece:

- **Bóveda:** las credenciales se guardan y el administrador las solicita; no las conoce.
- **Acceso justo a tiempo:** el permiso se concede para una tarea y caduca solo.
- **Grabación de sesión:** queda registro de lo que se hizo dentro.

La idea se resume en una frase: la contraseña no se sabe, se pide.

## Qué pasa cuando la gestión falla

- Credenciales robadas y movimiento lateral sin detección.
- Ransomware que se propaga con permisos de administrador.
- Robo de datos personales accesibles desde el activo comprometido.
- Borrados accidentales o deliberados sin responsable identificable.
- Caídas de servicio por cambios de configuración no controlados.

## Qué comprobar

- ¿Hay una cuenta administrativa distinta de la de uso diario?
- ¿Alguien comparte cuenta, o todas son individuales?
- ¿Cada administrador local tiene una contraseña única por equipo?
- ¿La administración se hace desde equipos dedicados y separada por niveles?
- ¿Se registran y se graban las sesiones privilegiadas?

## Fuentes

- Microsoft. *Securing Privileged Access* y documentación de Windows LAPS.
- MITRE ATT&CK: T1550.002 (Pass the Hash) y T1550.003 (Pass the Ticket).
- NIST SP 800-53, controles AC-6 (mínimo privilegio) y AC-5 (separación de funciones).
- INCIBE. Guías de protección de cuentas privilegiadas.
