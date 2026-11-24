# Identidad en Azure

La identidad es el perímetro real. Cuando todo está en la nube, el cortafuegos deja de separar el dentro del fuera y lo que decide quién entra es una cuenta, un token y una política. Por eso la identidad se diseña antes que la red y se revisa antes que el resto.

## Un directorio, no un servidor

Microsoft Entra ID es el directorio de la suscripción: guarda usuarios, grupos, aplicaciones y las reglas que deciden cómo se autentican. No es un Active Directory alojado, aunque se conecte con uno.

## El permiso se concede una vez

Los permisos se dan a grupos y a identidades de aplicación, no a personas una a una. Con eso, el alta y la baja se resuelven en la pertenencia y no en una lista de excepciones que nadie limpia.

## Por qué importa

Casi todos los incidentes de nube empiezan con una credencial: una cuenta sin MFA, una aplicación con secreto en una variable de entorno, un permiso de administrador permanente que sobraba. La identidad mal hecha no se arregla después con detección.
