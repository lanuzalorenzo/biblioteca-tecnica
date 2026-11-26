# Introducción práctica a Python orientada a la seguridad

Preparar un script de Python se parece a montar una caja de herramientas para una obra pequeña: puedo llevar el martillo de casa, pero si mezclo llaves de distintos juegos y no sé qué tornillo aprieta cada una, pierdo más tiempo buscando que trabajando. Python es cómodo porque trae muchas piezas, y precisamente por eso conviene ordenarlas antes de usarlas.

Lo uso para automatizar comprobaciones que haría a mano: leer cabeceras, recorrer una lista de hosts propios, comparar configuraciones o transformar una salida. Aquí recojo lo mínimo para escribir ese tipo de script sin romper la instalación del sistema y sin confundir una comprobación con una auditoría.

## La estructura la marca la sangría

En Python los bloques no se delimitan con llaves: los define la indentación. Cuatro espacios al principio de una línea significan que esa instrucción pertenece al bloque anterior. Un espacio de más cambia el significado o provoca un error, así que la alineación no es estilo, es sintaxis.

Por eso, al revisar un script ajeno, miro primero si la sangría es coherente. Una mezcla de tabuladores y espacios suele esconder un bloque que no hace lo que parece. Los editores que muestran los espacios y convierten tabuladores evitan la mayor parte de estos sustos.

## Ejecutar un archivo

Hay dos formas de lanzar un `.py` en Linux:

```bash
python3 comprobar.py            # invoco el intérprete
./comprobar.py                  # lo ejecuto como comando
```

La segunda necesita dos cosas: permiso de ejecución (`chmod +x`) y una primera línea que indique el intérprete, el *shebang*:

```python
#!/usr/bin/env python3
```

Si invoco `python3 archivo.py`, el *shebang* es decorativo. Tampoco sirve de nada en un módulo que solo se importa desde otro programa. Es una pista para el sistema operativo, no una medida de seguridad.

## Un entorno por proyecto

Instalar paquetes con `pip` sobre la instalación del sistema es la vía rápida a un conflicto: dos proyectos necesitan versiones distintas de la misma biblioteca y ninguno de los dos funciona. El entorno virtual resuelve eso. Crea una carpeta con su propio intérprete y sus propios paquetes, y deja intacto lo que administra el sistema operativo.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install requests
```

Muchas distribuciones marcan su Python como «administrado externamente» siguiendo la PEP 668 y rechazan las instalaciones globales con `pip`. No es un obstáculo: es un aviso de que el sitio correcto para una dependencia de proyecto es el entorno virtual.

Antes de instalar, me pregunto si la biblioteca hace falta. Cada paquete añade código que no he escrito, con su propio mantenimiento y sus propias dependencias. Instalo desde el repositorio oficial o desde PyPI, fijo versiones y reviso qué entra en el proyecto.

## Datos, decisiones y repetición

Python usa tipado dinámico: no declaro el tipo, lo lleva el valor. Los tipos que más aparecen en un script de comprobación son:

- **Cadenas** para rutas, direcciones, nombres de cabecera y mensajes.
- **Enteros** para puertos, contadores y tamaños.
- **Listas** para recorrer un conjunto ordenado de elementos.
- **Diccionarios** para asociar claves con valores, la forma natural de leer un JSON.

`if`, `elif` y `else` eligen un camino; `for` recorre una colección. Con esas piezas y una función ya se automatiza casi cualquier comprobación pequeña.

```python
cabeceras = {"server": "nginx", "content-type": "text/html"}
for nombre, valor in cabeceras.items():
    print(f"{nombre}: {valor}")
```

El tipado dinámico no significa que el tipo dé igual: un entero y una cadena no se suman sin más. El error aparece al ejecutar la línea concreta, no al guardar el archivo. Por eso un camino poco usado puede tardar semanas en fallar, y por eso las [pruebas de software](pruebas-de-software.md) son parte del mismo trabajo.

## Funciones y documentación

Una función se declara con `def`, recibe parámetros y puede devolver un valor. Agrupar así el código permite probarlo por separado y reutilizarlo. La *docstring*, escrita entre triples comillas justo debajo de la definición, describe qué hace, qué recibe y qué devuelve. Cuando reviso código ajeno, una docstring desactualizada es tan útil como un cartel que señala la puerta equivocada: me obliga a comprobar el comportamiento real.

## Bibliotecas que aparecen una y otra vez

| Biblioteca o herramienta | Uso habitual |
|---|---|
| `os` | Rutas, permisos y variables de entorno |
| `sys` | Argumentos y detalles del intérprete |
| `socket` | Conexiones TCP y UDP de bajo nivel |
| `requests` | Peticiones HTTP y lectura de respuestas |
| Scapy | Construcción y análisis de paquetes |
| python-nmap | Automatización de descubrimiento con Nmap |
| `cryptography` | Operaciones criptográficas de alto nivel |
| Paramiko | Conexiones SSHv2 |

Ninguna es peligrosa por sí misma. Lo que cambia el juicio es el destino: `socket` contra mi propia máquina es una comprobación; contra una red que no administro es un escaneo. La autorización delimita el uso, no la importación.

## La cadena de suministro

Casi todo lo que instalo viene de código abierto, y esa cadena también es superficie de ataque. Reviso cinco puntos:

1. **Licencia:** una permisiva y una copyleft imponen obligaciones distintas.
2. **Origen:** el repositorio oficial del proyecto o PyPI, no un enlace suelto.
3. **Dependencias:** cada paquete arrastra otros; conviene saber cuáles.
4. **Mantenimiento:** un proyecto abandonado no recibe parches.
5. **Suplantación:** un nombre parecido o una cuenta comprometida puede distribuir código malicioso.

## Una comprobación de cabeceras HTTP

Un ejemplo útil es un script que hace una petición GET y comprueba si la respuesta incluye cinco cabeceras: HSTS, CSP, `X-Frame-Options`, `X-Content-Type-Options` y `Referrer-Policy`. Con la biblioteca estándar basta:

```python
from urllib.error import HTTPError
from urllib.request import urlopen

CABECERAS = (
    "strict-transport-security",
    "content-security-policy",
    "x-frame-options",
    "x-content-type-options",
    "referrer-policy",
)

def revisar(url: str) -> None:
    try:
        with urlopen(url, timeout=10) as respuesta:
            estado = respuesta.status
            cabeceras = respuesta.headers
            final = respuesta.geturl()
    except HTTPError as error:
        estado = error.code
        cabeceras = error.headers
        final = url

    print(f"{url}: {estado}")
    for nombre in CABECERAS:
        valor = cabeceras.get(nombre)
        print(f"  {nombre}: {'presente' if valor else 'ausente'}")

    if final != url:
        print(f"  redirigido a: {final}")
        if url.startswith("https://") and final.startswith("http://"):
            print("  aviso: la petición baja de HTTPS a HTTP")

revisar("https://ejemplo.example")
```

El script muestra el estado y marca cada cabecera como presente o ausente. No valida su contenido, no evalúa la política de la aplicación y no detecta una configuración incorrecta: una CSP presente puede ser inútil si permite `unsafe-inline`. Es un punto de partida, no un veredicto.

Tampoco trae un destino predeterminado, y eso es deliberado. Le paso siempre un sitio propio o autorizado, compruebo si la petición acaba en otro host y aviso si baja de HTTPS a HTTP. El bloque `except` conserva el estado y las cabeceras cuando el servidor responde con error, porque un 403 también informa.

## Antes de lanzarlo

1. Creo el entorno virtual y lo activo antes de instalar nada.
2. Reviso la sangría y ejecuto una primera vez con datos de prueba.
3. Compruebo qué argumentos acepta, qué bibliotecas importa y qué datos envía.
4. Limito el destino a lo propio o autorizado y dejo constancia del alcance.
5. Leo la salida con escepticismo: un resultado verde no cubre lo que el script no mira.

## Glosario

| Término | Definición |
|---|---|
| CSP | Política HTTP que restringe los recursos que puede cargar una página. |
| HSTS | Mecanismo que pide al navegador usar siempre HTTPS en un sitio. |
| PEP 668 | Marca un entorno de Python como administrado externamente. |
| Shebang | Primera línea que indica qué intérprete ejecuta un script. |
| `venv` | Instalación aislada de Python y sus dependencias. |

## Fuentes

- Python Software Foundation. *Documentación oficial de Python 3*.
- PyPA. *PEP 668*, entornos administrados externamente.
- Documentación oficial de Scapy, python-nmap y Paramiko.
