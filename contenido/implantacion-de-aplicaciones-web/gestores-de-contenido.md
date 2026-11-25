# Gestores de contenido

Publicar una web a mano significa escribir HTML por cada noticia y tocar el diseño cada vez que cambia un menú. Un gestor de contenido separa lo que se publica de cómo se ve: la redacción escribe en un panel y el sistema compone la página. Es la diferencia entre tener un periódico con imprenta propia y tener que imprimir cada ejemplar a mano.


## Qué compone un CMS

Un gestor de contenido tiene cuatro piezas:

- **Núcleo:** el código que gestiona usuarios, contenidos, plantillas y permisos.
- **Base de datos:** guarda textos, relaciones, usuarios y configuración.
- **Tema:** decide la presentación; se puede cambiar sin tocar el contenido.
- **Extensiones:** añaden funciones —formularios, tienda, analítica, copias—.

Alrededor hay una pila que hay que montar bien: servidor web, intérprete del lenguaje, base de datos y almacenamiento de archivos. En PHP, la combinación clásica es Apache o nginx con PHP-FPM y MySQL o MariaDB; la variante con nginx se suele llamar LEMP frente a LAMP.

## Instalación

El orden importa más que el asistente:

1. **Base de datos y usuario propio** para la aplicación, con permisos solo sobre su base.
2. **Descarga desde la fuente oficial**, no desde una copia empaquetada con extras.
3. **Configuración** con las credenciales fuera del directorio público y permisos de archivo ajustados: escritura solo donde el gestor la necesita.
4. **HTTPS** desde el primer momento, con certificado válido y redirección.
5. **Usuario administrador** con contraseña propia y correo real; nada de `admin`.
6. **Ajustes de correo saliente**, para que el restablecimiento de contraseña funcione.
7. **Copia de seguridad inicial** y comprobación de que se restaura.

El instalador crea tablas y deja el sitio accesible; lo que no hace es decidir la seguridad ni el mantenimiento.

## Contenido, usuarios y roles

El contenido se organiza en entradas, páginas, categorías, etiquetas y medios. La diferencia entre entrada y página no es estética: la entrada se publica en un flujo —con fecha, autor y categoría— y la página es estable —contacto, aviso legal, servicios—.

Los roles limitan lo que cada persona puede hacer: administrador, editor, autor, colaborador, suscriptor. En una empresa pequeña se reparten como mínimo entre quien publica y quien administra. Un editor no necesita instalar plugins; un administrador no debería ser la cuenta del día a día.

## Seguridad

Un CMS es un objetivo frecuente porque es público y porque muchas instalaciones se quedan sin actualizar. Las medidas que más reducen el riesgo:

- **Actualizar núcleo, tema y extensiones**, y retirar lo que no se usa. Una extensión abandonada es una puerta sin mantenimiento.
- **Contraseñas fuertes y segundo factor** para las cuentas con privilegios.
- **Principio de mínimo privilegio** en la base de datos y en el sistema de archivos.
- **Desactivar el editor de archivos** del panel y la instalación de extensiones desde la web si no se necesita.
- **Copias de seguridad probadas**: base de datos y archivos, con restauración verificada.
- **Registro y monitorización** de accesos fallidos y cambios.
- **WAF y limitación de intentos** para frenar ataques automatizados.

Las vulnerabilidades más habituales son las de OWASP: control de acceso roto, inyección, XSS, componentes desactualizados y configuración insegura. Un plugin popular no es sinónimo de seguro; hay que mirar su mantenimiento y sus permisos.

## Rendimiento

Un CMS sin caché consulta la base de datos en cada visita. Las mejoras por orden de impacto:

- **Caché de página** —estática o de objeto— y limpieza al publicar.
- **Imágenes** redimensionadas y en formatos modernos.
- **CDN** para estáticos si el público está repartido.
- **Base de datos** con índices y consultas razonables; revisar extensiones que hacen consultas pesadas.

El rendimiento no se mide «porque va rápido»: se mide con tiempos de respuesta y con la carga que aguanta antes de degradarse.

## Mantenimiento y ciclo de vida

Un CMS se mantiene, no se instala y se olvida. La rutina mínima: actualizar en un entorno de pruebas, comprobar que el sitio sigue igual, aplicar en producción con copia previa, revisar registros y renovar certificados. Las versiones mayores pueden romper el tema o las extensiones; por eso se prueba antes.

La variante **headless** separa el contenido de la presentación y lo sirve por API a una web, una app o una pantalla. Sirve cuando hay varios canales; añade complejidad y no sustituye la gestión de usuarios y permisos.

## Lo que se comprueba

Que la base de datos tiene usuario propio y permisos limitados; que HTTPS está activo; que el administrador no se llama `admin` y tiene segundo factor; que no hay extensiones abandonadas; que la copia se restaura; que el editor de archivos está desactivado; y que el sitio responde con caché y sin errores en el registro.

## Fuentes

- Documentación oficial de WordPress: instalación, roles, seguridad y actualizaciones.
- OWASP Top 10 y OWASP Web Security Testing Guide.
- Documentación de PHP, Apache, nginx, MySQL y MariaDB.
- Orden EDU/392/2010, de 20 de enero (BOE-A-2010-3028).
