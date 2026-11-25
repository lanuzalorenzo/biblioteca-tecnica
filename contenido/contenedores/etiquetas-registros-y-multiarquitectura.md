# Etiquetas, registros y multiarquitectura

Una imagen se comparte a través de un registro, no enviando un fichero. Para publicarla hay que nombrarla con el registro, la organización y la versión; para consumirla hay que decidir si se acepta una etiqueta móvil o se fija un identificador inmutable. Esa decisión separa un despliegue reproducible de uno que cambia solo.

## Anatomía de un nombre

```
registro/organización/imagen:etiqueta
```

Las tres primeras partes son opcionales con valores por defecto: si no hay registro se asume `docker.io`; si no hay organización se asume `library` en Docker Hub; si no hay etiqueta se asume `latest`.

| Nombre | Registro | Organización | Imagen |
|---|---|---|---|
| `nginx` | Docker Hub | `library` | `nginx:latest` |
| `postgres:16` | Docker Hub | `library` | `postgres:16` |
| `miempresa/api:2.3` | Docker Hub | `miempresa` | `api:2.3` |
| `ghcr.io/miempresa/api:2.3` | `ghcr.io` | `miempresa` | `api:2.3` |
| `mcr.microsoft.com/dotnet/aspnet:10.0` | `mcr.microsoft.com` | `dotnet` | `aspnet:10.0` |

Docker Hub es el registro por defecto, pero no el único: GitHub Container Registry, Quay, el registro de Microsoft, Azure Container Registry, Amazon ECR, Google Artifact Registry o un Harbor propio. Todos hablan el mismo protocolo OCI.

## Publicar y descargar

```bash
docker login
docker tag miapp:1.0 usuario/miapp:1.0
docker push usuario/miapp:1.0
docker pull usuario/miapp:1.0
```

`login` guarda la credencial en la configuración del cliente; conviene usar un token de acceso, no la contraseña de la cuenta. `tag` no crea una imagen: añade otro nombre al mismo identificador. `push` sube solo las capas que el registro no tiene. Para un registro distinto de Docker Hub se indica el servidor:

```bash
docker login ghcr.io
docker tag miapp:1.0 ghcr.io/miempresa/miapp:1.0
docker push ghcr.io/miempresa/miapp:1.0
```

Una organización permite que varias personas publiquen bajo el mismo prefijo y compartan la gestión de los repositorios. El nombre de la imagen debe llevar ese prefijo; no se puede publicar en una organización ajena.

## Etiquetas móviles y digests

Una etiqueta es un puntero y se puede mover. `latest` es la más evidente, pero cualquier etiqueta puede ser flotante según lo que haga quien publica:

- `latest` apunta a la última versión publicada.
- `2` apunta a la última 2.x.
- `2.4` apunta a la última 2.4.x.
- `2.4.1` apunta a una versión concreta y no debería moverse.

Si el proyecto publica una 2.4.2, `2`, `2.4` y `latest` pueden pasar a apuntar a ella; `2.4.1` se queda donde estaba. En producción se fija una versión completa o, mejor, un digest:

```bash
docker pull nginx@sha256:<digest>
docker images --digests
```

El **digest** es el hash del manifiesto y lo asigna el registro; identifica la imagen de forma global. El **ID** de la imagen es el hash de su configuración y es local: la misma imagen descargada en dos máquinas puede mostrar IDs distintos, pero el digest coincide. Una imagen construida y nunca publicada tiene ID y no tiene digest. Fijar el digest garantiza que se ejecuta exactamente lo que se probó.

`docker run` o `compose up` no actualizan una etiqueta que ya existe en local; `docker pull` sí consulta el digest del registro y actualiza la etiqueta. Para asegurar la comprobación se usa `docker pull nginx:latest` o `--pull=always` al ejecutar. Esa es la trampa de las etiquetas móviles: el fichero de despliegue dice lo mismo, pero la imagen es otra.

## Copiar entre registros

El camino directo usa las herramientas de siempre: autenticarse en ambos, descargar, etiquetar con el nombre de destino y subir. Para volúmenes grandes o automatización, `skopeo copy` copia de registro a registro sin pasar por el almacenamiento local:

```bash
skopeo copy docker://origen/imagen:1.0 docker://destino/imagen:1.0
```

## Nombres cortos en Podman

Podman muestra siempre el nombre completo (`docker.io/library/nginx`) y traduce los nombres cortos con un fichero de alias y un registro por defecto. Por eso `podman run hello-world` puede ejecutar una imagen distinta de `docker run hello-world`. En scripts conviene usar el nombre completo para no depender de esa configuración.

## Capas, IDs y espacio

Una imagen es una lista ordenada de capas. Cada capa es inmutable y se identifica por el hash de su contenido, así que dos imágenes que comparten una base comparten esas capas en disco. `docker history` muestra el comando que creó cada capa y su tamaño; las capas de solo configuración ocupan cero.

```bash
docker history miapp:1.0
docker image inspect miapp:1.0
docker save miapp:1.0 -o miapp.tar
docker load -i miapp.tar
```

`save` exporta la imagen con sus capas y metadatos; `load` la reconstruye. El tar contiene un `manifest.json` y un directorio de blobs: ahí se ve que las capas son ficheros independientes que se reutilizan entre imágenes. No se debe confundir con `export`, que aplana el sistema de archivos de un contenedor y pierde la historia.

Las imágenes colgantes son las que perdieron su etiqueta al reconstruir sobre un nombre ya usado y no tienen contenedores. Ocupan disco y no aportan nada:

```bash
docker image prune
docker image prune -a
docker system df
docker system prune
```

`system df` separa imágenes, contenedores, volúmenes y caché de construcción, y marca lo recuperable. `system prune` borra imágenes colgantes, contenedores parados y redes sin usar; `-a` amplía a todas las imágenes sin contenedores y `--volumes` incluye volúmenes sin usar, con riesgo de pérdida de datos.

## Multiarquitectura

Una imagen pertenece a una plataforma: `linux/amd64`, `linux/arm64`, `linux/arm/v7`, `windows/amd64`. No se puede ejecutar un binario ARM en un host AMD64 sin emulación. Para evitar que el usuario tenga que elegir, existe la **imagen multiarquitectura**: un manifiesto que apunta a una imagen distinta por plataforma bajo el mismo nombre y etiqueta. El motor elige la que corresponde al host.

```bash
docker manifest inspect nginx
docker buildx build --platform linux/amd64,linux/arm64 -t usuario/api:1.0 --push .
```

`buildx` es la extensión de BuildKit que construye para varias plataformas. Para producir varias variantes en una sola orden hace falta un *builder* con el driver `docker-container`; el builder por defecto está pensado para la plataforma del host. Para emular otras arquitecturas se apoya en QEMU, lo que permite compilar, aunque más lento.

Un *builder* es un entorno de BuildKit, no un demonio de Docker. Se listan y se seleccionan con:

```bash
docker buildx ls
docker buildx create --name multi --driver docker-container --bootstrap
docker buildx use multi
```

`docker buildx use` cambia el constructor; `docker context use` cambia el motor. Son dos ejes distintos y se confunden con facilidad. Al construir varias plataformas, `--push` publica el manifiesto directamente en el registro; sin él, el resultado se queda en la caché del builder y no aparece en `docker images`.

Ejecutar una imagen de otra arquitectura en Docker Desktop funciona con emulación y un aviso; en Docker Engine falla salvo que el sistema tenga `binfmt_misc` y QEMU configurados. En producción, la plataforma del clúster decide qué variante debe existir.

## Confianza en la imagen

Publicar no es sinónimo de confiar. Antes de usar una imagen de terceros conviene revisar si es oficial o verificada, qué base utiliza, cuándo se actualizó y qué vulnerabilidades arrastra. Herramientas como Trivy o Grype analizan capas y paquetes; cosign firma y verifica imágenes. La firma no sustituye al análisis, pero permite comprobar que lo que se despliega es lo que se publicó.
