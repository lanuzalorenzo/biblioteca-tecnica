# .NET MAUI para Android

.NET MAUI permite construir un cliente móvil con C# y XAML sobre controles nativos. Para una aplicación como Comicteca, la decisión no está en si el marco puede pintar una lista o abrir una API, sino en si el producto necesita algo que una web instalada no da: lectura sin conexión, almacenamiento local, integración con el sistema y una sesión que sobreviva al cierre del navegador. Cuando esa necesidad existe, MAUI ofrece un camino coherente con el resto de .NET; cuando no, añade un canal de distribución y un ciclo de mantenimiento que hay que poder sostener.

Estas notas describen una base para un cliente Android fino: una biblioteca portable con el dominio y los servicios, un proyecto Android que arranca, pide permisos y muestra XAML, una autenticación nativa con MSAL y PKCE, un APK firmado que se entrega por un canal privado y un reparto de pruebas entre Linux y el dispositivo. El ejemplo de referencia es el cliente Android de [Comicteca](https://github.com/lanuzalorenzo/comicteca).

## Contenido

| Nota | Qué cubre |
|---|---|
| [Qué es y cuándo no usarlo](que-es-y-cuando-no-usarlo.md) | Aportación de MAUI, comparación con TWA, PWA y Blazor Hybrid, y coste de mantener un cliente nativo |
| [Proyecto y ciclo de vida](proyecto-y-ciclo-de-vida.md) | Solución con App.Core portable y app Android fina, arranque, configuración, permisos y ciclo de vida |
| [Seguridad del cliente](seguridad-del-cliente.md) | MSAL con PKCE y navegador del sistema, `SecureStorage`, cierre de sesión, manifiesto, `FLAG_SECURE`, R8 y registros |
| [Firma y distribución](firma-y-distribucion.md) | Almacén de claves fuera de Git, APK firmado, instalación y canal privado sin Google Play |
| [Arquitectura y pruebas](arquitectura-y-pruebas.md) | Qué se prueba en Linux, qué exige emulador o móvil, cobertura y observabilidad del cliente |

## Alcance

- **Una app Android, no una web envoltorio.** La interfaz usa controles nativos; la lógica vive en una biblioteca `net10.0` que no depende de MAUI.
- **Una sesión de usuario real.** Inicio con el navegador del sistema, PKCE, almacenamiento cifrado, cierre de sesión y revocación del lado del servidor.
- **Una entrega controlada.** Firma con una clave custodiada, verificación del APK y distribución privada al propietario.
- **Unas pruebas honestas.** Lo que se ejecuta en Linux se automatiza; lo que depende de Android se prueba en emulador o dispositivo y se declara como tal.

## Límites

- No es un manual de referencia de MAUI ni de Android. Explica las piezas que un cliente de este tipo necesita y remite a la documentación oficial para el detalle.
- No cubre iOS, macOS ni Windows. El proyecto se centra en Android porque es la plataforma del cliente.
- No incluye un APK ni un enlace de descarga. Las notas de firma explican por qué un binario no se publica como artefacto de un repositorio público.
- No hay credenciales, secretos, datos personales ni referencias a repositorios privados. Los ejemplos usan identificadores ficticios y dominios reservados.
- Las versiones citadas son las vigentes al escribir: .NET 10 y las cargas de trabajo de Android que lo acompañan. Antes de aplicar una receta conviene comprobar la matriz de compatibilidad.

## Pendiente

La base cubre el armazón; el módulo se completará con:

- **XAML y MVVM en detalle:** enlaces, comandos, validación, Shell, navegación y ciclo de vida de los ViewModels.
- **`HttpClient` con resiliencia:** tiempos, reintentos, espera, cortocircuito e idempotencia.
- **Observabilidad a fondo:** registro estructurado, informes de fallos, consentimiento, retención y alertas.
- **Rendimiento y tamaño:** arranque en frío, listas, imágenes, memoria y efecto del recorte.
- **El caso práctico de Comicteca:** cuando la app esté terminada y probada, con decisiones y resultados comprobados. El [repositorio del cliente](https://github.com/lanuzalorenzo/comicteca), el [caso de Comicteca](https://lanuzalorenzo.github.io/comicteca.html) y el [portfolio de ciberseguridad](https://lanuzalorenzo.github.io/portfolio.html) reúnen el contexto público.

## Cómo se leen

El orden va de la decisión al artefacto. La primera nota ayuda a descartar MAUI si no compensa; la segunda monta la solución y el ciclo de vida; la tercera protege la sesión y el paquete; la cuarta lo firma y lo entrega; la quinta separa lo que se puede probar en Linux de lo que exige un dispositivo. Cada nota se sostiene sola, pero las cuatro últimas comparten el mismo ejemplo y conviene leerlas en orden.
