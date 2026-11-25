# Publicar la aplicación: servidor, permisos y secreto

Una aplicación que funciona en el equipo de quien la escribió no está terminada: está probada. Publicarla exige decidir qué servidor la sirve, con qué permisos corre, cómo llega el tráfico cifrado y de dónde salen las credenciales. Es la parte que separa un ejercicio de un servicio.


## De ASP a lo que hay hoy

Las prácticas del módulo usaban **ASP clásico**, que ejecutaba scripts en el servidor de Microsoft. Ese modelo está descatalogado y no se usa en instalaciones nuevas; su sucesor es **ASP.NET**, con un modelo de ejecución distinto (compilado, sobre el runtime de .NET).

La idea que se estudiaba —páginas que se generan en el servidor y llegan al navegador ya montadas— sigue vigente en todos los lenguajes de servidor. Lo que cambió es la herramienta y la forma de desplegarla.

Y una consecuencia práctica: una aplicación escrita para ASP clásico no se actualiza cambiando una línea. Se reescribe o se mantiene en un servidor aislado mientras dure. Ese coste se decide al elegir la tecnología, no al retirarla.

## Elegir servidor

| Servidor | Encaja cuando |
|---|---|
| Apache con PHP | Aplicación PHP, configuración por directorio |
| Nginx | Servir estático y hacer de proxy inverso delante de otra aplicación |
| Tomcat | Aplicaciones Java empaquetadas |
| IIS | Ecosistema Microsoft y ASP.NET |

En una arquitectura habitual, Nginx o Apache reciben la petición, terminan TLS y pasan la petición al proceso de la aplicación. Eso permite reiniciar la aplicación sin cortar el servicio y mantener el servidor web como única puerta.

## Permisos: el usuario del servicio

La aplicación **no** corre como administrador. Corre con un usuario propio, con permiso de lectura sobre su código y de escritura solo sobre los directorios que lo necesitan —subidas, caché, registros—.

- Si un atacante consigue ejecutar código, lo ejecuta con los permisos de ese usuario: cuanto menos pueda tocar, menor el daño.
- El directorio de configuración queda fuera del directorio público. Un `config.php` accesible por URL entrega las credenciales de la base de datos.
- Los permisos se revisan después de cada despliegue: un instalador suele dejarlos amplios y nadie los vuelve a mirar.

## Secretos y configuración

Las credenciales no van en el repositorio. Van en variables de entorno o en un gestor de secretos, se inyectan al desplegar y se rotan con un procedimiento.

- Un fichero `.env` que se versionó una vez sigue en el historial: rotar la credencial es obligatorio, no opcional.
- Los entornos (desarrollo, pruebas, producción) tienen configuración distinta y **credenciales distintas**. Compartir la base de datos de producción con el entorno de pruebas es cómo se borran datos reales un viernes.

## Cifrado y cabeceras

- TLS con certificado válido y renovación automatizada. Un certificado caducado tumba el servicio igual que un fallo de disco.
- Redirección de HTTP a HTTPS, y `HSTS` para que el navegador no vuelva a intentar el texto plano.
- Cabeceras que cuestan una línea y evitan clases enteras de problema: política de contenido, tipo de contenido, marco de página, referente.
- La versión del servidor no se anuncia en la cabecera de respuesta: es información gratis para quien busca un fallo conocido.

## Desplegar sin sorpresas

1. Compilar y empaquetar en un entorno limpio.
2. Desplegar en pruebas y ejecutar la comprobación mínima: la aplicación responde, la base conecta, el usuario de servicio tiene los permisos previstos.
3. Desplegar en producción con copia previa del estado anterior y una forma de volver.
4. Comprobar desde fuera, con una petición real, que el cambio está.
5. Anotar qué versión quedó y cuándo.

Los pasos 3 y 4 son los que se saltan cuando hay prisa, y los que convierten una incidencia en una tarde.

## Lo que se comprueba

Que la aplicación corre con usuario propio y sin privilegios de administrador; que la configuración no es accesible por URL; que el tráfico va cifrado y redirige desde HTTP; que las cabeceras de seguridad están; que la versión desplegada es la que se cree; y que existe una forma de volver a la anterior.

## Errores que se repiten

- Permisos de escritura en todo el directorio de la aplicación.
- Credenciales en el repositorio o en una imagen de contenedor.
- Entorno de pruebas apuntando a la base de datos de producción.
- Desplegar por FTP y no saber qué hay en el servidor.
- Mantener una aplicación fuera de soporte porque «funciona».

## Fuentes

- Documentación oficial de Apache, Nginx, Tomcat e IIS.
- Guía de cabeceras de seguridad de OWASP.
- RFC 6797 (HSTS).
