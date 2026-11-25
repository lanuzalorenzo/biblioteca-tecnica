# PHP: formularios, sesiones y acceso a datos

Una página que solo muestra texto es un folleto. En cuanto recibe datos, guarda algo y recuerda quién eres, se convierte en una aplicación, y con ella llegan los tres problemas clásicos: validar lo que llega, escapar lo que sale y proteger lo que se guarda.


## Cómo se ejecuta

El servidor web recibe la petición, se la pasa al intérprete de PHP, el intérprete ejecuta el fichero, genera HTML y lo devuelve. El navegador no ve el código: ve el resultado. Eso implica que **todo lo que se calcula en el servidor es invisible para el usuario, y por eso mismo todo lo que llega del usuario es sospechoso**.

- Un fichero `.php` con `<?php ... ?>` mezcla lógica y presentación. Se permite en lo pequeño y se paga en lo grande.
- La configuración se lee de variables de entorno o de un fichero fuera del directorio público.
- Los errores se registran en el servidor y **no** se muestran al usuario: un mensaje de error con la ruta del fichero es un mapa para quien busca.

## Validar la entrada

Regla única: **no se confía en nada que venga del cliente**. Ni el formulario, ni la cookie, ni la cabecera, ni el campo oculto.

```php
$nombre = filter_input(INPUT_POST, 'nombre', FILTER_UNSAFE_RAW);
if (!is_string($nombre) || trim($nombre) === '') {
    $errores[] = 'El nombre es obligatorio';
}

$email = filter_input(INPUT_POST, 'email', FILTER_VALIDATE_EMAIL);
if ($email === false) {
    $errores[] = 'El correo no es válido';
}
```

La validación se hace en el servidor siempre, aunque también se haga en el navegador para comodidad. La del navegador es una ayuda; la del servidor es la que protege.

## Escapar la salida

Todo lo que se imprime y viene de fuera se escapa para el contexto donde se imprime. En HTML, `htmlspecialchars` con `ENT_QUOTES` y UTF-8; en un atributo, lo mismo; dentro de JavaScript o de una hoja de estilos, otra función distinta.

Sin eso, un comentario con `<script>` se ejecuta en el navegador de quien lo lee: es la ejecución de código en el navegador ajeno, y sigue siendo la vulnerabilidad más común de las aplicaciones web.

## Sesiones y formularios

- La sesión se inicia con `session_start()` y se identifica por una cookie. Esa cookie se marca `HttpOnly` y `Secure`, y el identificador se regenera al iniciar sesión para evitar la fijación.
- Los formularios que cambian algo llevan **testigo anti falsificación** (CSRF): un valor aleatorio guardado en la sesión y comprobado al recibir. Sin él, otra web puede enviar el formulario con tus credenciales.
- Un campo oculto con el precio no es un dato del sistema: se lee de la base de datos al procesar.

## Acceso a datos

La consulta se prepara y se le pasan los valores aparte. Es la diferencia entre un dato y una orden:

```php
$stmt = $pdo->prepare('SELECT id, nombre FROM equipos WHERE estado = :estado');
$stmt->execute([':estado' => $estado]);
foreach ($stmt as $fila) { /* ... */ }
```

Concatenar el valor en la consulta es cómo se construye una inyección de SQL, aunque el valor venga de un desplegable. La conexión se abre con un usuario limitado, sin permisos de administración, y con los errores desactivados en pantalla.

## La aplicación de incidencias del módulo

El proyecto de 2016 —inventario de equipos, incidencias y usuarios, en PHP y MariaDB— tenía la estructura correcta: separación entre la capa que accede a datos, la que gestiona incidencias y la administración, y un fichero de conexión común. Lo que hoy no se reutiliza es la pila: PHP 5.6 lleva años sin soporte, y el volcado de la base incluía una contraseña en claro que no debe copiarse a ningún sitio.

La lección que sí se conserva: una aplicación pequeña se ordena desde el primer día en carpetas por responsabilidad. Cuando todo está en un fichero, la primera funcionalidad nueva rompe dos que ya funcionaban.

## Lo que se comprueba

Que la entrada se valida en el servidor; que todo lo que se imprime está escapado; que las consultas van preparadas; que los formularios que cambian estado llevan testigo; que la configuración y las credenciales están fuera del directorio público; y que los errores se registran y no se muestran.

## Errores que se repiten

- Concatenar variables en la consulta.
- Guardar contraseñas con hash débil o, peor, en claro.
- Subir ficheros sin comprobar tipo, tamaño y nombre, y dejarlos en un directorio ejecutable.
- Mostrar errores en producción «para depurar».

## Fuentes

- Manual oficial de PHP (versión soportada).
- Guía de prevención de la vulnerabilidad de inyección SQL y de la ejecución de código en el navegador (OWASP).
- Documentación de PDO.
