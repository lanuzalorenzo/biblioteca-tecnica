# Cómputo en Azure

Todo servicio necesita un sitio donde ejecutarse. Azure ofrece un espectro que va de la máquina virtual, donde administras hasta el sistema operativo, al servicio de funciones, donde solo entregas el código. Entre medias hay plataformas que se quedan con una parte del trabajo y cobran por tenerla.

Elegir no es cuestión de moda: es cuestión de cuánto control necesitas, cuánto quieres administrar y cómo llega el tráfico.

## Máquinas virtuales

La **máquina virtual** da control completo: eliges sistema, disco, red y extensiones. A cambio, te quedas con el parcheo, la configuración y la vigilancia del sistema operativo.

Para que no dependa de un solo equipo, se agrupan de dos formas. Los **conjuntos de disponibilidad** reparten las máquinas entre dominios de error y de actualización dentro de un centro de datos. Las **zonas** las reparten entre centros de datos distintos. Y si además hay que escalar, el **conjunto de escalado** crea y destruye instancias según una regla.

## App Service

**App Service** es la plataforma para aplicaciones web y API. Se despliega el código o el contenedor y la plataforma se encarga del sistema operativo, del escalado y del certificado. El plan define la potencia y el coste: se paga por el plan, no por aplicación.

Lo que hay que conocer antes de usarlo:

- **Ranuras de despliegue.** Una ranura de producción y otra de preparación permiten probar y después intercambiar, con la configuración pegada a cada ranura.
- **Escalado.** Manual o automático por reglas, sobre el plan. Las instancias son del plan, así que varias aplicaciones comparten la misma capacidad.
- **Red.** La integración con red virtual resuelve la salida hacia recursos privados; el punto de conexión privado resuelve la entrada. Son dos cosas distintas y se confunden a menudo.
- **Identidad.** Una identidad administrada permite leer un secreto de Key Vault sin guardar credenciales. Es la integración por defecto.

## Funciones

**Azure Functions** ejecuta código por evento: una petición HTTP, un mensaje en una cola, un fichero nuevo, un temporizador. El código se escribe una vez y se enlaza a la fuente con disparadores y enlaces de entrada y salida.

El plan decide el comportamiento. En consumo, la instancia aparece cuando llega el evento y desaparece después, con un arranque en frío que se nota en la primera llamada. En premium, hay instancias preparadas y cabe la red virtual. En dedicado, se paga un plan como el de App Service.

El límite de tiempo es la restricción que más rompe diseños: una tarea larga no cabe en consumo. Para trabajos duraderos existe la orquestación de funciones, que guarda el estado entre pasos, pero un proceso de horas suele pedir otro servicio.

## Contenedores

Un contenedor empaqueta la aplicación con sus dependencias y se ejecuta igual en cualquier sitio. Azure ofrece cuatro formas:

| Opción | Qué resuelve | Cuándo |
|---|---|---|
| Registro de contenedores | Guarda y distribuye imágenes | Siempre que haya contenedores |
| Instancias de contenedor | Un contenedor aislado, sin orquestación | Tareas cortas y pruebas |
| Aplicaciones de contenedor | Contenedores con escalado por eventos, revisiones e ingress | Servicios pequeños y medianos |
| Kubernetes administrado | Orquestación completa | Equipos que ya saben operar Kubernetes |

En Kubernetes, el plano de control lo administra Azure y el trabajo se reparte en grupos de nodos.

## Registro de contenedores

ACR guarda y distribuye las imágenes. La autenticación se hace con identidad administrada desde el servicio que despliega, no con usuario y contraseña. Las tareas de ACR pueden construir la imagen al hacer push y firmarla; el escaneo de vulnerabilidades se activa aparte y conviene que bloquee el despliegue de una imagen con fallos críticos.

## Aplicaciones de contenedor

Container Apps ejecuta contenedores sin que se administre Kubernetes. Cada servicio tiene revisiones, ingress y escalado por eventos; el escalado puede llegar a cero, que es lo que lo hace barato para cargas intermitentes. Es la opción cuando hay varios servicios pequeños, colas o eventos, y no se quiere operar un clúster.

## Kubernetes administrado

AKS entrega el plano de control administrado y deja los nodos bajo control del equipo. Se elige cuando hace falta el ecosistema de Kubernetes: operadores, CRD, mallas de servicio o herramientas que ya se usan. A cambio, hay que actualizar versiones, dimensionar grupos de nodos y operar el ingress.

La identidad de la carga se resuelve con federación de identidad de carga de trabajo, no con secretos montados en el pod. El ingress puede ser el enrutado de aplicaciones de AKS, NGINX o una puerta externa; se elige una y se documenta, porque dos capas con reglas parecidas producen errores difíciles de seguir.

## Cuándo basta App Service

App Service ejecuta un contenedor o código con ranuras, escalado y certificado, sin que haya que tocar Kubernetes. Basta cuando la carga es una aplicación web o una API, el equipo no opera clústeres y el escalado por reglas es suficiente.

Se pasa a Container Apps cuando hay varios servicios con escalado por eventos y a AKS cuando la organización ya tiene una plataforma Kubernetes o necesita sus piezas. El contenedor no obliga a orquestador: muchas aplicaciones viven mejor en una plataforma que en un clúster.

## Planes de App Service

El plan es la unidad de capacidad y de factura. Todas las aplicaciones del plan comparten sus instancias, su CPU y su memoria. Cambiar de plan cambia lo que se puede hacer, no solo la potencia:

| Plan | Ranuras | Escalado automático |
|---|---|---|
| Básico | No | No |
| Estándar | Sí | Sí |
| Premium | Sí | Sí |
| Aislado | Sí | Sí |

La integración con red virtual para la salida empieza en el plan Estándar; la entrada por punto de conexión privado y el entorno aislado añaden piezas que se pagan aparte. Las ranuras de despliegue permiten preparar una versión en una ranura y permutarla con producción. El intercambio no copia archivos: cambia el tráfico de una ranura a otra, y la configuración marcada como fija se queda con la ranura. Antes del intercambio conviene calentar la ranura nueva, porque la primera petición paga el arranque.

## Escalado de App Service

El escalado manual fija un número de instancias. El automático añade reglas sobre una métrica —CPU, memoria, longitud de cola, peticiones— con un mínimo, un máximo y un tiempo de enfriamiento. El enfriamiento evita que la plataforma oscile entre añadir y quitar instancias con cada pico.

La regla se escribe sobre lo que de verdad limita: si el cuello es la base de datos, escalar la web solo mueve el problema. Y se pone un máximo: sin techo, un bucle de peticiones se convierte en factura.

## Disparadores de Functions

Una función se ejecuta por un disparador y puede leer o escribir con enlaces. Los más usados son HTTP, temporizador, cola, blob y evento. El enlace de entrada trae el dato; el de salida lo entrega sin que el código abra la conexión.

El plan cambia el comportamiento. En consumo, la instancia aparece con el evento y desaparece después; el arranque en frío se nota en la primera llamada. En premium hay instancias preparadas, sin ese arranque, y cabe la red virtual. En dedicado se paga un plan como el de App Service.

El tiempo máximo de ejecución es la restricción que más rompe diseños: una tarea larga no cabe en consumo. Para trabajos duraderos, Durable Functions guarda el estado entre pasos; un proceso de horas suele pedir otro servicio.

## Logic Apps

Logic Apps es un flujo visual con conectores: “cuando llega un correo, extrae el adjunto, guárdalo y avisa”. Sirve para integrar servicios sin escribir código y para automatizar tareas administrativas.

Se elige frente a Functions cuando el trabajo es sobre todo orquestación de conectores y cuando quien lo mantiene prefiere editar el flujo, no el código. Se elige Functions cuando hay lógica propia, rendimiento o control fino del runtime. Los dos conviven: un flujo puede llamar a una función para la parte que no encaja en un conector.

## Configuración segura

Los errores de cómputo se repiten en los mismos cinco puntos:

1. Secretos en la configuración de la aplicación en lugar de referencias a Key Vault.
2. Protocolos antiguos habilitados: TLS por debajo de 1.2, FTP o autenticación básica del sitio de despliegue.
3. Punto de conexión público cuando la aplicación solo la consume otro servicio de la misma red.
4. Despliegue desde un equipo en lugar del pipeline, sin rastro de qué versión corre.
5. Sin límite de escalado, de modo que un bucle de peticiones se convierte en factura.

Ninguno de los cinco se detecta mirando la aplicación: se detectan mirando la configuración del recurso.

## Qué revisar

- ¿El plan elegido encaja con la forma del tráfico y con el coste esperado?
- ¿La aplicación se identifica con identidad administrada?
- ¿Los secretos están en Key Vault y no en la configuración?
- ¿La entrada y la salida están resueltas por separado?
- ¿Hay límites de escalado y de tiempo definidos?
- ¿Lo que corre en producción salió de un pipeline?
