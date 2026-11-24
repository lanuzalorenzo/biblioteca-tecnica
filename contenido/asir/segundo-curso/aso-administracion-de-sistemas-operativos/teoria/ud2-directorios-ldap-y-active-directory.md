# UD2. Directorios: LDAP y Active Directory

Una red con veinte equipos y veinte listas de usuarios es imposible de mantener: alguien se va y hay que borrarlo en veinte sitios. Un directorio centraliza esa lista y la convierte en la única fuente: se da de alta una vez y el acceso se propaga. Es la diferencia entre una agenda de papel y una base de datos.

> **Módulo:** ASO. Administración de sistemas operativos

## Qué es un directorio

Un servicio de directorio guarda objetos —personas, equipos, grupos, impresoras— y los organiza en un árbol. Está pensado para **leer mucho y escribir poco**, y para responder rápido a búsquedas.

**LDAP** es el protocolo de acceso, no el directorio en sí. Sus piezas:

- **Entrada:** cada objeto, identificado por un **DN** (nombre distinguido), que se lee de lo particular a lo general: `uid=lorenzo,ou=personas,dc=empresa,dc=test`.
- **Atributos:** los datos de la entrada, cada uno con su tipo y sus reglas.
- **Esquema:** define qué atributos puede tener cada clase de objeto. Un directorio no admite cualquier campo: el esquema manda.
- **Operaciones:** buscar, añadir, modificar y borrar, más el **bind**, que es cómo se autentica quien consulta.
- **Puertos:** 389 para LDAP y 636 para LDAPS, con TLS. Un directorio sin cifrar expone credenciales en cada autenticación.

**OpenLDAP** es la implementación libre de referencia: potente y exigente. Su configuración moderna vive en el propio directorio (`cn=config`), no solo en ficheros, lo que sorprende a quien viene de editar `/etc`.

## Active Directory

Active Directory es el directorio de Microsoft, y añade a LDAP un modelo de dominio con autenticación propia:

- **Dominio, árbol y bosque:** el dominio agrupa objetos con políticas comunes; los dominios se agrupan en árboles y estos en bosques, que comparten esquema y catálogo.
- **Controladores de dominio:** replican el directorio entre sí. Los roles de operaciones maestras (FSMO) son tareas que solo puede hacer uno a la vez, y repartirlas importa cuando un controlador falla.
- **Kerberos** para autenticar, con tickets en lugar de contraseñas en cada petición. Depende del reloj: más de cinco minutos de desfase y la autenticación falla.
- **DNS** no es un servicio más: es la pieza que permite a los clientes encontrar el controlador. Un DNS mal configurado rompe el dominio entero.
- **Unidades organizativas y directivas:** las OU agrupan objetos para aplicar GPO. El orden de aplicación —sitio, dominio, OU, con la última política ganando— explica por qué una configuración no surte efecto.

## Unir un cliente

El cliente necesita: dirección del servidor DNS del dominio, conectividad con los puertos del directorio y del Kerberos (88, 389, 445), hora sincronizada y credenciales con permiso para unir equipos. Se une con la herramienta del sistema o con `realm join` en Linux, y se comprueba reiniciando sesión con una cuenta de dominio.

Los usuarios de dominio no se crean en el equipo: se crean en el directorio. Si algo falla al iniciar sesión, el orden de comprobación es DNS, hora, conectividad y permisos, en ese orden.

## Lo que se gana con un directorio

Además de la lista única, tres cosas que no se ven: **inicio de sesión único**, porque la misma credencial vale para el equipo, la carpeta y el correo; **política central**, porque la contraseña y el bloqueo se deciden en un sitio; y **registro**, porque cada autenticación queda en el controlador y no repartida por veinte equipos. Las tres dependen de lo mismo: que el directorio esté disponible. Sin él, nadie entra, y por eso se replica.

## La consulta también es superficie

Un directorio se consulta con filtros, y un filtro construido con texto que llega del usuario permite leer más de lo que se pretendía: es la inyección LDAP, la prima pobre de la inyección SQL. Se evita validando la entrada y limitando qué puede leer una cuenta anónima. Como mínimo, la consulta anónima se restringe y el tráfico va por TLS.

## Lo que se comprueba

Que el cliente resuelve el nombre del dominio por el DNS correcto; que la hora coincide; que la unión aparece en el directorio; que una cuenta deshabilitada no puede entrar; que una GPO llega al equipo que debe y no a otro; y que hay al menos dos controladores, o una copia de seguridad que permita reconstruir el que cae.

## Errores que se repiten

- Instalar el directorio sin planificar el esquema de nombres: cambiarlo después es un proyecto, no una edición.
- Un solo controlador de dominio, sin réplica y sin copia.
- Usar el administrador del dominio como cuenta diaria.
- Desactivar TLS porque «no funciona» la consulta.
- Aplicar directivas a la raíz del dominio para «que llegue a todos».

## Órdenes para consultar y unir

```bash
ldapsearch -x -H ldap://servidor -b "dc=empresa,dc=test" "(uid=lorenzo)"
ldapwhoami -x -H ldaps://servidor -D "cn=admin,dc=empresa,dc=test" -W
slapcat                            # volcado del directorio para copia
kinit lorenzo                      # obtener un ticket Kerberos
realm join --user=administrador empresa.test   # unir un cliente Linux
```

```powershell
dsquery user -name "lorenzo*"      # buscar en el directorio desde Windows
gpresult /r /scope:computer        # directivas aplicadas al equipo
```

El esquema es la parte que más se subestima. Añadir un atributo propio exige declararlo, asignarle una sintaxis única y documentarlo, porque dos atributos con el mismo nombre y distinta sintaxis rompen el directorio. En Active Directory se amplía con una extensión de esquema, que es una operación irreversible y por eso se hace una vez y con copia previa.

## Fuentes

- RFC 4511 (LDAP) y RFC 4120 (Kerberos).
- Documentación oficial de Active Directory y de OpenLDAP.
- Guías de configuración segura para controladores de dominio.
