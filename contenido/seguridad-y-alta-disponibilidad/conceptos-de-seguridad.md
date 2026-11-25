# Conceptos de seguridad

La seguridad informática se ocupa de que la información siga siendo la que es, esté disponible cuando se necesita y solo la lea quien debe. Es el mismo problema que resuelve una casa: cerradura para que no entre cualquiera, alarma para enterarse de que algo pasa, caja fuerte para lo que importa y seguro para cuando la cerradura falla. Ninguna de las cuatro cosas basta por separado, y ninguna se elige sin saber qué se guarda dentro.


## Qué se protege

Un **activo** es cualquier cosa que, si se pierde o se altera, duele. En un sistema informático los hay de cinco clases:

- **Personas:** quien administra, quien usa y quien mantiene. Es el activo más olvidado y el más atacado por ingeniería social.
- **Equipos:** servidores, puestos de trabajo, dispositivos de red y de almacenamiento. Se protegen contra robo, sabotaje y fallo.
- **Aplicaciones:** el software instalado y su configuración. Solo debe estar lo necesario y lo instala quien administra.
- **Datos:** la información de negocio y la de las personas. Sin ellos la organización no funciona, y su pérdida no siempre se puede reparar.
- **Comunicaciones:** el canal por el que viajan los datos. Si el canal es abierto, el resto de protecciones se saltan por la mitad.

Un inventario de activos con su dueño y su criticidad es el punto de partida de todo lo demás. Sin él se protege lo que se ve, no lo que importa.

## Las cuatro clasificaciones que se usan para hablar

Las medidas se ordenan con cuatro etiquetas que forman dos pares. Sirven para entenderse, pero conviene saber que no son una norma: ISO/IEC 27001 clasifica los controles en organizativos, de personas, físicos y tecnológicos, y en preventivos, detectivos y correctivos.

- **Seguridad física / lógica.** Física es la que actúa sobre el continente —edificio, sala, cerradura, cable—; lógica, sobre el contenido: cuentas, permisos, cifrado, software.
- **Seguridad activa / pasiva.** Activa es lo que impide o detecta el ataque mientras ocurre: cortafuegos, antivirus, autenticación, monitorización. Pasiva es lo que permite seguir o volver: copias, redundancia, SAI, un centro de respaldo. La pasiva no evita el golpe, reduce el daño.

## Confidencialidad, integridad, disponibilidad y no repudio

Son las propiedades que se quieren conservar; cada control existe para sostener al menos una.

| Propiedad | Qué garantiza | Se rompe cuando |
|---|---|---|
| Confidencialidad | Solo accede quien está autorizado | Alguien lee datos que no le tocan |
| Integridad | El dato es el que se escribió, sin cambios | Se altera un registro, un binario o un log |
| Disponibilidad | El servicio responde en su horario | Cae el servidor, la red o el suministro |
| No repudio | Nadie puede negar haber participado | Se discute quién firmó o quién envió qué |

La no repudio solo se sostiene con pruebas verificables: una firma digital, un registro con hora fiable y un control de acceso que impida usar la cuenta de otro. Sin eso, es una promesa.

## Autenticación, autorización y registro

Se confunden con facilidad y son tres pasos distintos:

1. **Autenticación:** comprobar que alguien es quien dice ser. Se hace con uno o varios **factores**: algo que sabes (contraseña), algo que tienes (tarjeta, token) y algo que eres (huella, cara).
2. **Autorización:** decidir qué puede hacer esa identidad ya autenticada. Va después, nunca antes.
3. **Registro y auditoría** (en RADIUS y en la literatura, *accounting*): dejar constancia de qué se hizo, quién y cuándo. Es lo que permite reconstruir un incidente y lo que sostiene el no repudio.

Dos factores del mismo tipo no son doble factor: contraseña más pregunta secreta sigue siendo «algo que sabes». La biometría tiene además un problema propio —no se puede cambiar si se filtra—, por eso se usa como comodidad o como complemento, no como única llave.

## Vocabulario del ataque

- **Vulnerabilidad:** defecto o debilidad que se puede aprovechar. Puede ser de diseño, de configuración o de código.
- **Amenaza:** quien o qué puede explotarla.
- **Riesgo:** probabilidad de que la amenaza use la vulnerabilidad multiplicada por el daño. Es la cifra que decide dónde se gasta el esfuerzo.
- **Exploit:** el procedimiento o programa concreto que aprovecha la vulnerabilidad.

Una vulnerabilidad **conocida y parcheada** se resuelve aplicando el parche; si aún no hay parche, se aplica una medida temporal o se retira el servicio. La **no conocida** —la de día cero— solo se contiene con defensa en profundidad: menos superficie, menos privilegio y detección.

## Malware por comportamiento

La lista clásica (virus, gusanos, troyanos) sigue siendo válida, pero se entiende mejor por lo que hace cada familia:

- **Virus:** se pega a un fichero y se ejecuta con él.
- **Gusano:** se propaga solo por la red, sin que nadie lo abra.
- **Troyano:** entra disfrazado y abre una puerta trasera.
- **Ransomware:** cifra los datos y cobra por la clave. Hoy suele robar antes y amenazar con publicar.
- **Rootkit:** se esconde en el sistema para no ser detectado.
- **Spyware y keylogger:** roban información, a menudo credenciales.
- **Fileless:** vive en memoria y en herramientas legítimas del sistema, así que no deja fichero que escanear.

## Cómo se ataca

La clasificación clásica de la recomendación X.800 sigue siendo la más útil porque ordena el ataque por su efecto, no por su herramienta:

- **Interrupción:** se corta el servicio. Es un ataque a la disponibilidad.
- **Interceptación:** se lee la comunicación sin modificarla. Ataque a la confidencialidad, pasivo y difícil de detectar.
- **Modificación:** se altera lo que viaja o lo que está guardado.
- **Fabricación:** se inventa un mensaje o una identidad, como en el spoofing.

Sobre esa base, las técnicas concretas que se estudiaron: ingeniería social y phishing —el ataque que no necesita vulnerabilidad técnica—, fuerza bruta y pulverización de contraseñas, keyloggers, suplantación de identidad o de máquina (*spoofing*), escucha del tráfico (*sniffing*) y denegación de servicio, con una máquina o con una red de máquinas alquiladas.

## Quién ataca

La clasificación por motivación —hacker, cracker, *script kiddie*, programador de malware, analista de tráfico, ciberterrorista— sirve para explicar el oficio, no para decidir defensas. En la práctica lo que cambia la respuesta es el **recurso** del atacante y su **objetivo**: un oportunista que busca cualquier puerta abierta se contiene con lo básico bien hecho; un atacante dirigido necesita detección y segmentación, porque entrará.

## Marco legal: lo que ha cambiado desde 2015

El apunte original se apoyaba en la **LOPD 15/1999** y sus tres niveles de protección. Esa ley está derogada y los niveles ya no existen:

- **RGPD** (Reglamento UE 2016/679), aplicable desde mayo de 2018, sustituye el modelo de niveles por el de principios, base jurídica y evaluación de impacto.
- **LOPDGDD** (LO 3/2018) adapta el RGPD al ordenamiento español y deroga la LOPD de 1999.
- **ENS** (Real Decreto 311/2022) fija el esquema de seguridad para el sector público y sus proveedores; sustituyó al de 2010.
- **LSSI** (Ley 34/2002) y el **texto refundido de la Ley de Propiedad Intelectual** siguen vigentes y se citaban bien.
- **eIDAS** (Reglamento UE 910/2014) regula la firma electrónica y la identificación; su reforma de 2024 añade la cartera europea de identidad digital.

La consecuencia práctica para quien administra: el cumplimiento ya no se demuestra con una auditoría cada dos años, sino con registro de actividades de tratamiento, medidas de seguridad proporcionadas al riesgo y notificación de brechas en 72 horas.

## Buenas prácticas que siguen valiendo

Inventariar activos y revisar copias; probar la restauración, no solo la copia; instalar solo lo necesario y revisar la configuración por defecto; actualizar con criterio y sin retrasos; separar la cuenta de administración de la de uso diario; registrar y revisar los eventos; formar a las personas, que es el control más barato y el que más falla.

## Fuentes

- ISO/IEC 27000: vocabulario de gestión de la seguridad de la información.
- ITU-T X.800 (ISO 7498-2): arquitectura de seguridad y clasificación de amenazas.
- Reglamento (UE) 2016/679 (RGPD) y Ley Orgánica 3/2018 (LOPDGDD).
- Real Decreto 311/2022, Esquema Nacional de Seguridad.
- Reglamento (UE) 910/2014 (eIDAS), modificado por el Reglamento (UE) 2024/1183.
