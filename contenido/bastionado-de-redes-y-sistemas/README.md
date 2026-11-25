# Bastionado de redes y sistemas

Bastionar es preparar una instalación para que aguante sola: no basta con echar la llave a la puerta principal si quedan ventanas abiertas, un buzón sin candado y una copia de la llave bajo el felpudo. En una red pasa lo mismo. La seguridad no sale de una herramienta única, sino de revisar cada punto por el que se puede entrar, decidir cuáles deben existir y cerrar el resto.

Este módulo recorre ese trabajo de dentro hacia fuera: primero la red que se va a proteger, después el plan que decide qué merece la pena, luego las identidades que cruzan la puerta y, por último, el perímetro donde se filtra, se detecta y se contiene el tráfico.

## Contenido

| Apunte | Qué responde |
|---|---|
| [Introducción al bastionado](introduccion-al-bastionado.md) | Qué se reduce, en qué orden y por qué la defensa en profundidad no es un producto |
| [Los sistemas de redes](sistemas-de-redes.md) | Qué piezas intervienen en una comunicación y cuáles son superficie de ataque |
| [Ethernet y conmutación](conmutacion-ethernet.md) | Qué riesgos viven en el enlace local y cómo se cierra el puerto |
| [IP y enrutamiento](enrutamiento-ip.md) | Quién decide por dónde sale un paquete y cómo se controla esa decisión |
| [Direccionamiento y subredes](direccionamiento-y-subredes.md) | Cómo se reparte el espacio de direcciones con criterio de separación |
| [VLSM y reparto por sedes](vlsm-y-reparto-multisede.md) | Cómo encajar zonas de tamaños distintos sin quedarse sin direcciones |
| [TCP: conexiones y banderas](tcp-conexiones-y-banderas.md) | Qué cuenta un flujo TCP y qué no prueba ninguna bandera |
| [Análisis de riesgos](analisis-de-riesgos.md) | Cómo se decide qué proteger primero y cuánto esfuerzo dedicarle |
| [Medidas, políticas y estándares](medidas-politicas-y-estandares.md) | Qué es obligatorio, qué es recomendable y qué solo da método |
| [Procedimientos y escalado](procedimientos-y-escalado.md) | Quién responde, a quién avisa y cómo se mide la respuesta |
| [Control de acceso y factores](control-de-acceso-y-factores.md) | Cómo se comprueba una identidad y qué pruebas no valen como doble factor |
| [NAC y protocolos AAA](nac-y-protocolos-aaa.md) | Cómo se decide qué dispositivo entra y con qué credencial se administra |
| [Cuentas privilegiadas](cuentas-privilegiadas.md) | Cómo se evita que una credencial robada abra toda la organización |
| [Gestión de credenciales](gestion-de-credenciales.md) | Cómo se registran, reparten y retiran las claves |
| [PKI y firma electrónica](pki-y-firma-electronica.md) | En quién se confía, qué caduca y qué valor tiene una firma |
| [Segmentación, cortafuegos y DMZ](segmentacion-firewall-y-dmz.md) | Dónde se corta el tráfico y dónde se publica lo que debe ser público |
| [IDS e IPS](ids-e-ips.md) | Qué se vigila, qué se bloquea y por qué un sensor sin ajuste no protege |
| [Prevención de fugas](prevencion-de-fugas.md) | Cómo se impide que la información salga sin constancia |
| [Seguridad en redes inalámbricas](seguridad-wifi.md) | Por qué el aire no tiene puerta y qué cifrado queda en pie |
| [VPN y túneles](vpn-y-tuneles.md) | Qué protege un túnel y qué sigue expuesto dentro de él |

## Relación con otros módulos

La base de conmutación, direccionamiento y enrutamiento se explica en [Redes y conmutación](../redes/README.md); aquí se lee desde la decisión de seguridad, no desde el cálculo.

Los fundamentos de seguridad —activos, propiedades, vocabulario del ataque, criptografía, sistema operativo, copias y alta disponibilidad— están en [Seguridad y alta disponibilidad](../seguridad-y-alta-disponibilidad/README.md). Varios apuntes de este módulo enlazan a sus ficheros concretos para no repetir lo que ya está escrito: el acceso a la red, el control del tráfico, la criptografía y el endurecimiento del sistema operativo se estudian allí. Aquí queda lo propio del bastionado: qué se configura, en qué orden, con qué comprobación y qué errores se repiten.

## Alcance y autorización

Todo lo que se describe se aplica sobre sistemas propios o sobre los que exista autorización escrita. Escanear, capturar tráfico, probar credenciales, interferir en una red inalámbrica o comprobar la respuesta de un IDS son actividades que cambian el estado de un sistema ajeno y pueden afectar a terceros; sin alcance definido y permiso del responsable, no se ejecutan.

Un cambio de configuración se prueba, se documenta y se deja con una vía de vuelta. Desactivar un servicio sin revisar sus dependencias puede interrumpir un proceso legítimo y convertir una medida de seguridad en una incidencia.
