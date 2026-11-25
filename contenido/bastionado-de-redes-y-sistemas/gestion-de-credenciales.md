# Gestión de credenciales

En una gestoría de tres personas, todos usan la misma cuenta del programa de facturación y la clave está escrita en un papel pegado al monitor. Funciona hasta el día en que desaparecen asientos y nadie puede decir quién los tocó. Una credencial no es solo una llave: es la prueba de quién hizo qué. Cuando se comparte, esa prueba desaparece.

El tratamiento de contraseñas y privilegios en el sistema operativo se explica en [Sistema operativo y aplicaciones](../seguridad-y-alta-disponibilidad/sistema-operativo-y-aplicaciones.md). Este apunte recorre la vida de una credencial: cómo se descubre, quién la posee, dónde se guarda y cómo se retira.

## Qué es y por qué se comparte

Una credencial es el dato que un sistema acepta como prueba de identidad. Puede ser usuario y contraseña, un certificado, una tarjeta con chip o una llave física.

El acceso ocurre de dos maneras, y cada una abre una superficie distinta:

- **Local.** La credencial se teclea en el propio equipo para configurarlo o mantenerlo.
- **Remoto.** Se llega por consola, escritorio remoto, SSH o interfaz web.

Si a eso se suma que las claves pasan por técnicos distintos y por canales sin cifrar, la exposición crece sin que nadie haya hecho nada conscientemente malo.

## Los cinco fallos que más se ven

| Fallo | Qué ocurre | Por qué importa |
|---|---|---|
| Clave incrustada | Viene fija en el firmware o en el código y no se puede cambiar | Acaba en manuales y en Internet; en entornos industriales es común |
| Clave de fábrica | Se deja la que puso el fabricante | Cualquiera que conozca el modelo puede entrar |
| Demasiadas credenciales | Una por servicio, muchas viajando sin cifrar | Una sola captura de tráfico consigue varias |
| Clave compartida | Se presta al compañero que no recuerda la suya | Se pierde la atribución de las acciones |
| Administración con la cuenta de uso diario | Se hace todo con el usuario administrador | Un error borra lo que no debía y nadie responde |

El patrón se repite: comodidad alta y trazabilidad nula.

## Un ciclo, no una lista

1. **Descubrir e inventariar.** No se protege lo que no se conoce. Hay que saber qué activos piden credenciales; algunas herramientas rastrean la red y localizan equipos con cuentas conocidas.
2. **Asignar por rol.** Cada credencial la conoce quien la necesita para su trabajo y nadie más. Esto no solo protege: permite delegar sin repartir el control total.
3. **Registrar el uso.** El registro debe responder quién, cuándo y desde dónde.
4. **Centralizar con SSO cuando tenga sentido.** Reduce el número de claves, pero concentra el riesgo en la cuenta principal; sin MFA obligatoria, el ahorro se convierte en un punto único de fallo.
5. **Cerrar el ciclo.** Alta, cambio, baja y revisión periódica. La baja el mismo día del cese es la prueba de que el proceso existe de verdad.

## La rotación, con matices

Cambiar las contraseñas cada cierto tiempo parece prudente, aunque incómodo. NIST SP 800-63B rechaza cambiar las claves por calendario si no hay sospecha: esa práctica lleva a retocar un carácter y a elegir claves fáciles de adivinar. En su lugar pide longitud, contraste con listas de contraseñas filtradas y cambio cuando aparezca una duda razonable.

Quedan fuera las cuentas de servicio, que siguen el ciclo de la aplicación, y las credenciales que ya se han visto comprometidas. Conviene conocer las dos posturas y saber por qué se prefiere la segunda.

## Dónde se guardan

Un gestor de contraseñas mantiene las credenciales en una base cifrada que se abre con una contraseña maestra. Se memoriza una y el resto queda bajo llave.

| Función | Para qué sirve |
|---|---|
| Multidispositivo | Misma base en varios sistemas; con nube, sincronizada |
| Online y offline | Funcionar sin conexión o depender del servicio |
| Generador | Crear claves largas y aleatorias |
| Detección de debilidad | Avisar de claves repetidas, cortas o filtradas |
| Verificación en dos pasos | Proteger el acceso a la propia bóveda |
| Integración con el navegador | Rellenar formularios y evitar el copiar y pegar |

La diferencia entre local y nube no es la comodidad, sino el modelo de amenaza. Una base local es un fichero que hay que copiar y proteger; si se pierde, se pierde todo, y una mala sincronización genera conflictos. En un servicio en nube, el proveedor asume la disponibilidad y el riesgo se concentra en la cuenta maestra: comprometerla equivale a comprometer todas.

Para una organización, el siguiente escalón son las bóvedas de credenciales privilegiadas, que registran el uso y permiten prestar una cuenta sin revelar la contraseña. Se tratan en [Cuentas privilegiadas](cuentas-privilegiadas.md).

## Qué comprobar

- ¿Hay inventario de activos con credenciales y un responsable por cada una?
- ¿Queda algún dispositivo con la contraseña de fábrica o incrustada?
- ¿Las cuentas son individuales, incluidas las de servicio?
- ¿El registro permite atribuir una acción a una persona concreta?
- ¿La baja de un empleado desactiva sus accesos el mismo día?
- ¿Las credenciales de servicio se rotan con un procedimiento y no a mano?

Si falla la tercera pregunta, las demás pierden sentido: sin cuentas individuales, la auditoría registra nombres que no identifican a nadie.

## Errores que se repiten

- Guardar la contraseña en el mismo sitio que protege.
- Rotar todas las claves cada 90 días y llamarlo seguridad.
- Compartir una cuenta de servicio entre varias aplicaciones.
- Sincronizar la bóveda por un canal que nadie controla.
- Dar de baja a la persona y olvidar sus credenciales técnicas.

## Fuentes

- NIST. *SP 800-63B, Digital Identity Guidelines*.
- OWASP. *Password Storage Cheat Sheet* y *Authentication Cheat Sheet*.
- INCIBE. Guías de contraseñas y de gestión de identidades.
