# Java en el servidor: servlets y JSP

Java en el servidor trabaja con otra mentalidad: el código se compila, se empaqueta y se despliega en un contenedor que gestiona las peticiones. Es más ceremonia que un fichero de PHP, y a cambio el sistema arranca con tipos comprobados y un modelo de clases que aguanta un proyecto grande.


## El contenedor

Una aplicación Java web no se ejecuta sola: la ejecuta un **contenedor de servlets** —Tomcat es el más habitual—, que escucha en un puerto, recibe las peticiones HTTP y las traduce en llamadas a objetos.

- El contenedor crea una instancia del servlet la primera vez y la reutiliza: **una instancia atiende muchas peticiones a la vez**.
- Por eso una variable de instancia que guarde datos de un usuario es un fallo de concurrencia, no una comodidad.
- El despliegue es un fichero `.war` con las clases, las páginas, las bibliotecas y un descriptor de configuración.

## Un servlet, paso a paso

```java
public class ListadoEquipos extends HttpServlet {
    @Override
    protected void doGet(HttpServletRequest peticion, HttpServletResponse respuesta)
            throws IOException {
        respuesta.setContentType("text/html;charset=UTF-8");
        try (PrintWriter salida = respuesta.getWriter()) {
            salida.println("<h1>Equipos</h1>");
        }
    }
}
```

Los métodos `doGet` y `doPost` separan leer de modificar: el primero puede repetirse sin efectos, el segundo no. Una acción que cambia datos nunca va en un enlace.

Del objeto de petición se leen los parámetros, las cabeceras y la sesión; en la respuesta se fija el tipo de contenido, la codificación y el código de estado. Codificar en UTF-8 antes de escribir la primera línea evita que las tildes aparezcan como símbolos.

## JSP: la plantilla

Una página JSP es HTML con etiquetas que insertan código. Su ventaja histórica fue escribir la vista sin concatenar cadenas en Java; su riesgo, que invita a meter lógica de negocio dentro de la página.

- **Expresiones y etiquetas estándar** (`JSTL`) para recorrer y decidir, en lugar de código Java suelto.
- **Objetos implícitos:** petición, respuesta, sesión, aplicación.
- **Separación:** el servlet prepara los datos y la página los muestra. Cuando una JSP abre conexiones a base de datos, el proyecto ya tiene un problema de mantenimiento.

La versión del contenedor manda: desde Tomcat 10 las bibliotecas cambiaron de nombre de paquete (`javax` a `jakarta`). Un proyecto antiguo no arranca en un contenedor nuevo sin ese cambio, y es la primera causa de «funcionaba en clase».

## Sesión y seguridad

- La sesión se gestiona por cookie con identificador; el objeto de sesión guarda lo que debe sobrevivir entre peticiones.
- Lo que se guarda en sesión son datos de control —identificador de usuario, permisos—, no objetos enteros que puedan quedar desfasados.
- Las credenciales de base de datos se configuran en el contenedor o en variables de entorno, no en el código.
- Los formularios que modifican estado llevan también su testigo anti falsificación: el problema no es de un lenguaje, es de la web.

## Empaquetar y desplegar

```bash
mvn clean package            # genera target/aplicacion.war
cp target/aplicacion.war /opt/tomcat/webapps/
```

Un despliegue ordenado: compilar, empaquetar, copiar a un entorno de pruebas, verificar y solo entonces al de producción. Copiar ficheros sueltos por FTP a producción es la vía rápida a un servidor que no se puede reconstruir.

## Lo que se comprueba

Que la aplicación arranca en el contenedor con la versión declarada; que los formularios usan `POST` para modificar; que la instancia del servlet no guarda estado de usuario; que la codificación es UTF-8 de extremo a extremo; y que el despliegue se hace con el fichero empaquetado, no con ficheros sueltos.

## Errores que se repiten

- Guardar el usuario en una variable de instancia del servlet.
- Meter consultas a base de datos dentro de la JSP.
- Mezclar `javax` y `jakarta` al actualizar el contenedor.
- Desplegar a mano y no saber qué versión está en producción.

La sesión es cómoda y también una trampa: en un despliegue con varias instancias, el estado tiene que compartirse o quedarse en el cliente. Si no, el usuario cambia de nodo y pierde lo que llevaba.

## Fuentes

- Especificación de servlets de Jakarta EE.
- Documentación oficial de Apache Tomcat y de JSTL.
- Documentación de Maven para el empaquetado.
