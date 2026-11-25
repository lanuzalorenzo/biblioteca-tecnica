# Control de acceso y factores de autenticación

En una farmacia, el dependiente usa la cuenta del dueño para el programa de recetas porque «es más rápido». El registro acaba diciendo que el dueño atendió a un cliente que estaba a veinte kilómetros. Compartir la contraseña no es un atajo: es renunciar a saber quién hizo qué. Controlar el acceso exige responder quién dice ser, cómo lo demuestra y qué puede hacer; si una de las tres respuestas falta, la puerta está abierta.

Los conceptos de identidad, factores y registro se presentan en [Conceptos de seguridad](../seguridad-y-alta-disponibilidad/conceptos-de-seguridad.md), y la configuración de privilegios en el sistema en [Sistema operativo y aplicaciones](../seguridad-y-alta-disponibilidad/sistema-operativo-y-aplicaciones.md). Aquí se revisa el control desde la perspectiva de quien audita un sistema concreto.

## Identificar, demostrar y decidir

| Paso | Pregunta que responde | Error típico |
|---|---|---|
| Identificación | ¿Quién dice ser? | Confundir el nombre de usuario con una prueba |
| Autenticación | ¿Puede demostrarlo? | Dar por hecho que la contraseña sola basta |
| Autorización | ¿Qué le está permitido hacer? | Asignar permisos al grupo «todos» |

Cada paso se apoya en el anterior, pero no se deduce de él. Una cuenta puede demostrar su identidad y aun así tener permisos que no le tocan: el sistema sabe quién entró y se equivoca al decidir qué puede tocar.

A esos tres pasos se suma el **registro** de lo que hace cada uno. Sin él, un acceso indebido se descubre tarde o no se descubre, y no hay forma de atribuir una acción a una persona.

## Físico, lógico y mixto

| Clase | Qué protege | Ejemplos |
|---|---|---|
| Físico | Espacios y equipos | Puerta con llave, caja fuerte, sala con lector |
| Lógico | Servicios, datos y aplicaciones | Usuario y contraseña, certificado, permiso de carpeta |
| Mixto | Combina los dos | Puerta con teclado, torno con tarjeta |

Una medida de un plano no cubre el otro. Una clave perfecta no evita el robo del portátil, y una sala con lector no impide que un becario borre la base desde su puesto.

## Los tres tipos de prueba

| Factor | Qué es | Ejemplos | Debilidad principal |
|---|---|---|---|
| Algo que sé | Información memorizada | Contraseña, PIN, frase de paso | Se adivina, se reutiliza o se filtra |
| Algo que soy | Rasgo físico o conductual | Huella, iris, voz, rostro | No se puede cambiar si se compromete |
| Algo que tengo | Objeto o dispositivo | Token, tarjeta con certificado, móvil, llave FIDO2 | Se pierde, se presta o se copia |

Conviene no mezclar categorías: identificación, autenticación y autorización son etapas del proceso, no factores. Y los principios de mínimo privilegio, necesidad de conocer y separación de funciones son criterios de diseño, no pruebas de identidad.

## Por qué una contraseña no basta

Hay tres vías conocidas por las que una contraseña sola falla:

- **Phishing.** El usuario la escribe en una página que imita la legítima.
- **Reutilización.** La misma clave en el correo, la tienda y el trabajo; una brecha en cualquiera de ellos abre las demás.
- **Filtraciones.** Hay listas públicas con millones de credenciales y servicios que permiten comprobar si una cuenta aparece en ellas.

A eso se añaden la fuerza bruta y el *password spraying*, que prueba una clave común contra muchas cuentas para no activar bloqueos. En todos los casos la conclusión es la misma: la contraseña, por sí sola, no demuestra identidad con garantías.

## Dos pasos no siempre son dos factores

El **doble factor** suma una prueba más al entrar. El **multifactor** permite más de dos y puede pedir cosas distintas según la operación.

Una contraseña seguida de una pregunta secreta son dos pruebas, pero del mismo tipo: algo que sé. Quien descubre una suele descubrir la otra. El doble factor bien hecho combina categorías distintas, como contraseña más código del móvil o contraseña más llave física.

La banca muestra la granularidad: entrar en la web pide usuario y contraseña; consultar el saldo, un código; ordenar una transferencia, una firma adicional.

Dos variantes que conviene situar:

- **MFA adaptativo.** Decide si pide la segunda prueba según ubicación, dispositivo, hora o red. Entrar desde el despacho habitual no pide nada; desde otro país, sí. El riesgo es que el contexto se pueda imitar.
- **SSO (inicio de sesión único).** Una autenticación da acceso a varios servicios mediante un proveedor de identidad. Centraliza la revocación y mejora la comodidad, pero concentra el riesgo: si roban la sesión, el atacante entra en todo lo que cuelga de ella. La cookie de esa sesión vale tanto como la contraseña.

## Ataques y defensas por factor

| Factor | Ataque | Defensa |
|---|---|---|
| Algo que sé | Phishing, reutilización, *spraying* | Gestor de contraseñas, comprobación en filtraciones, MFA |
| Código por SMS | *SIM swapping*, interceptación | Código temporal (TOTP), notificación con número, llave FIDO2 |
| Notificación push | *MFA fatigue*: marear con avisos hasta que se acepta | Comparación de números, límite de envíos, bloqueo tras varios rechazos |
| Biometría | Ataque de presentación (foto, máscara, grabación) | Detección de vitalidad, segundo factor, umbrales de falsa aceptación y falsa denegación |
| Token o certificado | Robo, clonación, mal uso | Almacenamiento protegido por hardware, PIN, revocación |

La biometría arrastra un problema que la tecnología no resuelve: una clave comprometida se reemplaza; una huella comprometida, no. De ahí que sirva para desbloquear el teléfono y no para sostener sola un sistema crítico.

Las llaves FIDO2 y las *passkeys* van contra esa corriente: el navegador solo usa la clave con el dominio auténtico, así que una página falsa no recibe nada.

## Revisión de un sistema

1. ¿Se distinguen identificación, autenticación y autorización, o hay una cuenta compartida que lo hace todo?
2. ¿La MFA es obligatoria para administradores y acceso remoto, o solo para el usuario normal?
3. ¿Se combinan factores de tipos distintos o se disfraza de doble factor una segunda contraseña?
4. ¿Hay registro de accesos con fecha, usuario y resultado?
5. ¿Se desactiva la cuenta el día del cese y se revisan los permisos temporales?

Si falla la primera o la última, lo demás pierde valor: no hay control fiable sobre cuentas que no se pueden atribuir o que siguen activas después de su dueño.

## Errores que se repiten

- Llamar doble factor a dos contraseñas.
- Exigir MFA al usuario y dejarla opcional para el administrador.
- Mantener una cuenta de turno compartida «porque solo la usa el equipo de noche».
- Confiar en el SMS como segunda prueba de un sistema crítico.
- Guardar el registro y no revisarlo nunca.

## Fuentes

- NIST. *SP 800-63B, Digital Identity Guidelines*, y *SP 800-53*, familia AU.
- PCI Security Standards Council. *PCI DSS v4.0*, requisito 8.4.2.
- CISA. *More than a Password*.
- INCIBE. Guía de técnicas biométricas.
