#!/usr/bin/env python3
"""Construye el sitio de la biblioteca a partir de los Markdown versionados.

Cada build lee las fuentes configuradas, las convierte a HTML y genera un
sitio en `dist/`. Las fuentes viven en este repositorio, bajo `contenido/`,
y su ruta se declara en `config/fuentes.toml`; no hay rutas del equipo ni
dependencias externas.

Uso:
    python3 scripts/visor.py build
    python3 scripts/visor.py serve [--puerto 8001] [--vigilar] [--abrir]
    python3 scripts/visor.py check
"""

from __future__ import annotations

import contextlib
import hashlib
import html
import json
import posixpath
import re
import shutil
import sys
import threading
import time
import tomllib
import unicodedata
import webbrowser
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote, unquote

SITIO = Path(__file__).resolve().parent.parent
CONFIG = SITIO / "config" / "fuentes.toml"
SALIDA = SITIO / "dist"
FUENTE = SITIO / "sitio"

AUTOR = "Lorenzo Lanuza"
TITULO_SITIO = f"Biblioteca técnica — {AUTOR}"
MARCA_SITIO = "Lorenzo Lanuza"
DESCRIPCION_SITIO = (
    "Biblioteca técnica de Lorenzo Lanuza: apuntes y notas de sistemas, "
    "redes, datos, desarrollo, operaciones y seguridad."
)

ICONOS_CATEGORIA = {
    "Sistemas": "servidor",
    "Redes": "red",
    "Operaciones": "terminal",
    "Datos": "datos",
    "Desarrollo": "codigo",
    "Seguridad": "escudo",
    "Azure": "nube",
    "Empleo": "empleo",
}
ICONOS_MODULO = {
    "fundamentos-de-hardware": "tarjeta",
    "implantacion-de-sistemas-operativos": "monitor",
    "administracion-de-sistemas-operativos": "ajustes",
    "redes": "wifi",
    "servicios-de-red": "nodos",
    "gestion-de-bases-de-datos": "tabla",
    "administracion-de-bases-de-datos": "llave",
    "lenguajes-de-marcas": "etiqueta",
    "implantacion-de-aplicaciones-web": "web",
    "formacion-y-orientacion-laboral": "persona",
    "empresa-e-iniciativa-emprendedora": "idea",
    "angular": "aplicacion",
    "aspnet-core-mvc": "dotnet",
    "git": "git",
    "testing-xunit-moq": "pruebas",
    "contenedores": "docker",
    "fundamentos": "jerarquia",
    "red": "red",
    "identidad": "identidad",
    "computo": "servidor",
    "datos": "datos",
    "bus-de-mensajeria": "mensajes",
    "servicios-orientados-a-eventos": "eventos",
    "monitorizacion": "metricas",
    "seguridad-y-gobierno": "escudo",
    "gestion-de-apis": "codigo",
    "cache-y-entrega": "nube",
    "patrones": "documento",
}

# Se reemplazan por cada fuente durante el build.
RAIZ = SITIO
# El servicio sirve siempre el destino final; el build escribe en `SALIDA`.
DIST = SALIDA
_CERROJO = threading.Lock()
ACTUAL: Fuente | None = None
FUENTES: list[Fuente] = []
GLIFOS_EN_LINEA: dict[str, str] = {}
AVISOS_BUILD: list[str] = []
CATEGORIAS: dict[str, str] = {}
ORDEN_CATEGORIAS: list[str] = []
RECURSOS_URLS: set[str] = set()
# URL de cada recurso copiado, para resolver después su archivo original.
RUTAS_URL: dict[str, Path] = {}
# Módulos ya detectados por fuente: fijan el primer segmento de la URL.
MODULOS_POR_FUENTE: dict[tuple[str, Path], list[Path]] = {}
# Nombre visible de cada módulo convertido a segmento de URL.
SLUGS_MODULOS: dict[tuple[str, Path], dict[Path, str]] = {}
# Página que se está pintando: los enlaces se hacen relativos desde ella.
PAGINA_ACTUAL = ""

# Carpetas que no forman parte del contenido publicado en el sitio.
VETADAS = {".git", ".github", ".opencode", "sitio", "scripts"}
PROFUNDAS = {".git", "dist", "fuentes", "__pycache__", "node_modules"}
VETADOS = {".gitignore", ".opencodeignore", "AGENTS.md"}

# Solo se copian recursos servibles; un .env, una clave o un archivo de
# configuración suelto en la fuente no deben acabar en el servidor local.
RECURSOS_PERMITIDOS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico",
    ".pdf", ".odt", ".ods", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".zip", ".txt", ".csv", ".json", ".yaml", ".yml", ".xml",
    ".sh", ".py", ".java", ".js", ".css", ".html", ".sql",
    ".conf", ".ini", ".service", ".desktop",
}

# El lateral muestra solo categorías y módulos; el contenido vive en la página.
PROFUNDIDAD_LATERAL = 1


@dataclass
class Fuente:
    """Una fuente configurada, ya resuelta a una ruta local."""

    id: str
    etiqueta: str
    titulo: str
    estructura: str
    raiz: Path
    raices: list[str] = field(default_factory=list)
    minimos: dict[str, int] = field(default_factory=dict)
    nombres: dict[str, str] = field(default_factory=dict)


def cargar_config(ruta: Path = CONFIG) -> dict:
    if not ruta.exists():
        raise SystemExit(f"No existe la configuración: {ruta}")
    with ruta.open("rb") as archivo:
        return tomllib.load(archivo)


def resolver_fuentes(config: dict) -> list[Fuente]:
    """Resuelve cada fuente a su carpeta dentro del repositorio."""
    fuentes: list[Fuente] = []
    for item in config.get("fuente", []):
        identificador = item["id"]
        ruta = item.get("ruta")
        if not ruta:
            raise SystemExit(
                f"La fuente {identificador!r} no declara una ruta dentro del repositorio"
            )
        raiz = (SITIO / ruta).resolve()
        if not raiz.is_relative_to(SITIO.resolve()):
            raise SystemExit(f"La fuente {identificador!r} sale del repositorio: {ruta}")
        if not raiz.is_dir():
            raise SystemExit(f"La fuente {identificador!r} no es un directorio: {raiz}")
        if "esperados" in item:
            raise SystemExit(
                f"La fuente {identificador!r} declara 'esperados'; ahora es 'minimos'"
            )
        if not item.get("minimos"):
            raise SystemExit(f"La fuente {identificador!r} no declara 'minimos'")
        fuentes.append(
            Fuente(
                id=identificador,
                etiqueta=item.get("etiqueta", identificador),
                titulo=item.get("titulo", identificador),
                estructura=item.get("estructura", "curso"),
                raiz=raiz,
                raices=item.get("raices", []),
                minimos=item.get("minimos", {}),
                nombres=item.get("nombres", {}),
            )
        )
    if not fuentes:
        raise SystemExit("La configuración no declara ninguna fuente")
    return fuentes

# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------

def ruta_icono(url: str) -> Path | None:
    """Archivo del icono citado por la URL del sitio, si existe."""
    if url.startswith("_sitio/"):
        return FUENTE / url[len("_sitio/"):]
    if (ruta := RUTAS_URL.get(url)) is not None:
        return ruta
    for fuente in FUENTES:
        candidata = fuente.raiz / url
        if candidata.is_file():
            return candidata
    return None


_NS = "{http://www.w3.org/2000/svg}"
_DIBUJABLES = {"path", "circle", "rect", "ellipse", "polygon", "polyline"}
_GEOMETRIA = {
    "d", "cx", "cy", "r", "x", "y", "width", "height", "rx", "ry",
    "points", "transform", "fill-rule", "clip-rule", "stroke-width",
    "stroke-linecap", "stroke-linejoin", "opacity",
}
# Rellenos del tile que solo sirven para recortar: en una tinta pasan a hueco.
_CORTES = {"#07131e", "#0e2a47", "#0b2034", "#1c4a72"}
# Pintura que se hereda del grupo al extraer el glifo para el árbol y los filtros.
_PINTURA = {"fill", "stroke", "stroke-width", "stroke-linecap", "stroke-linejoin"}
# Atributos de trazo: solo cuentan cuando hay trazo.
_TRAZO = {"stroke-width", "stroke-linecap", "stroke-linejoin"}


def _atributo(clave: str, valor: str) -> str:
    """Un color heredado pasa a `currentColor`; el resto, tal cual."""
    if clave in {"fill", "stroke"}:
        return f'{clave}="{"none" if valor == "none" else "currentColor"}"'
    return f'{clave}="{valor}"'


def _pintura(elemento: ET.Element, heredado: dict[str, str]) -> dict[str, str]:
    """Pintura del elemento sobre la que hereda de sus grupos."""
    valores = dict(heredado)
    valores.update(
        {clave: valor for clave, valor in elemento.attrib.items() if clave in _PINTURA}
    )
    return valores


def _etiqueta(elemento: ET.Element) -> str:
    return elemento.tag.removeprefix(_NS)


def _es_corte(elemento: ET.Element) -> bool:
    """Capa del tile que recorta el glifo (fondo o degradado), no dibujo."""
    for clave in ("fill", "stroke"):
        valor = (elemento.get(clave) or "").lower()
        if valor in _CORTES or valor.startswith("url(#"):
            return True
    return False


def _grupo_glifo(raiz: ET.Element) -> ET.Element | None:
    for elemento in raiz.iter():
        if _etiqueta(elemento) == "g" and "scale" in (elemento.get("transform") or ""):
            return elemento
    return None


def _dibujo(ruta: Path) -> str:
    """Glifo de un icono, sin la baldosa ni el borde, en su rejilla de 24.

    Los iconos de la marca dibujan el glifo dentro de un grupo escalado; puede
    llevar subgrupos con su propio transform y capas de recorte. Se conserva
    todo eso, se normaliza el color a `currentColor` y las capas de recorte se
    convierten en huecos con `fill-rule="evenodd"`, para poder pintar el mismo
    dibujo a una tinta por debajo de 32 px. Al descartar los grupos, el dibujo
    hereda su pintura: si no, un glifo a línea pierde el trazo en la versión
    pequeña.
    """
    try:
        raiz = ET.parse(ruta).getroot()
    except (ET.ParseError, OSError):
        return ""
    grupo = _grupo_glifo(raiz)
    if grupo is None:
        return ""
    recortes = any(_es_corte(elemento) for elemento in grupo.iter())

    def serializar(elemento: ET.Element, heredado: dict[str, str]) -> str:
        etiqueta = _etiqueta(elemento)
        if etiqueta not in _DIBUJABLES and etiqueta != "g":
            return ""
        if _es_corte(elemento):
            if etiqueta == "g":
                return "".join(serializar(hijo, heredado) for hijo in elemento)
            return ""
        atributos: list[str] = []
        propio = _pintura(elemento, heredado)
        for clave, valor in elemento.attrib.items():
            if clave in _PINTURA:
                atributos.append(_atributo(clave, valor))
            elif clave in _GEOMETRIA:
                atributos.append(f'{clave}="{valor}"')
        for clave, valor in propio.items():
            if clave in elemento.attrib:
                continue
            # El `svg` que envuelve el glifo ya pinta `currentColor` y no traza:
            # solo se escribe lo que se aparta de esa pintura.
            if clave == "fill" and valor != "none":
                continue
            if clave == "stroke" and valor == "none":
                continue
            if clave in _TRAZO and propio.get("stroke", "none") == "none":
                continue
            atributos.append(_atributo(clave, valor))
        if etiqueta == "path" and recortes and "fill-rule" not in elemento.attrib:
            atributos.append('fill-rule="evenodd"')
        cuerpo = "".join(
            serializar(hijo, propio) for hijo in elemento
        )
        unidos = f' {" ".join(atributos)}' if atributos else ""
        if etiqueta == "g":
            return f"<g{unidos}>{cuerpo}</g>" if cuerpo else ""
        return f"<{etiqueta}{unidos}/>"

    return "".join(serializar(hijo, _pintura(grupo, {})) for hijo in grupo)


def glifo_en_linea(url: str, clase: str) -> str:
    """Glifo a una tinta, sin baldosa, para el árbol y los filtros."""
    dibujo = GLIFOS_EN_LINEA.get(url)
    if dibujo is None:
        ruta = ruta_icono(url)
        dibujo = _dibujo(ruta) if ruta and ruta.exists() else ""
        GLIFOS_EN_LINEA[url] = dibujo
    if not dibujo:
        return ""
    return (
        f'<svg class="{clase}" viewBox="0 0 24 24" aria-hidden="true" '
        f'focusable="false" fill="currentColor" stroke="none">{dibujo}</svg>'
    )


def carpetas_de_modulos(fuente: Fuente) -> list[Path]:
    """Carpetas que son módulo: fijan el primer segmento de su URL.

    Se calculan del sistema de archivos, antes de construir el árbol, porque
    la URL de cada página se decide al crear sus nodos.
    """
    clave = (fuente.id, fuente.raiz)
    if clave in MODULOS_POR_FUENTE:
        return MODULOS_POR_FUENTE[clave]
    if fuente.estructura == "curso":
        carpetas = [
            ruta
            for ruta in fuente.raiz.iterdir()
            if ruta.is_dir() and re.match(r"^\d{4}", ruta.name)
        ]
    elif fuente.estructura == "apuntes":
        carpetas = []
        for ruta in fuente.raiz.rglob("*"):
            if not ruta.is_dir():
                continue
            partes = ruta.relative_to(fuente.raiz).parts
            if any(
                parte.startswith(".") or parte in VETADAS or parte in PROFUNDAS
                for parte in partes
            ):
                continue
            if not (ruta / "README.md").exists():
                continue
            if not any(
                p.suffix == ".md" and p.name != "README.md" for p in ruta.iterdir()
            ):
                continue
            carpetas.append(ruta)
    else:
        carpetas = []
        for nombre in fuente.raices:
            grupo = fuente.raiz / nombre
            if grupo.is_dir():
                carpetas.extend(ruta for ruta in grupo.iterdir() if ruta.is_dir())
    MODULOS_POR_FUENTE[clave] = carpetas
    return carpetas


def slug_url(texto: str) -> str:
    """Segmento de URL legible: sin acentos, minúsculas y guiones."""
    limpio = unicodedata.normalize("NFKD", texto)
    limpio = "".join(c for c in limpio if not unicodedata.combining(c))
    limpio = re.sub(r"[^a-z0-9]+", "-", limpio.lower()).strip("-")
    return limpio or "modulo"


def nombre_de_modulo(fuente: Fuente, carpeta: Path) -> str:
    """Nombre visible del módulo, el mismo que muestran el árbol y las tarjetas."""
    nombre = fuente.nombres.get(carpeta.name, "")
    if nombre:
        return nombre
    nombre = titulo_de(carpeta)
    if fuente.estructura == "apuntes":
        nombre = re.sub(r"^\d+[.\-]\s*", "", nombre)
    return nombre


def slug_de_modulo(carpeta: Path) -> str:
    """Segmento de URL del módulo, derivado de su nombre visible."""
    if not ACTUAL:
        return carpeta.name
    clave = (ACTUAL.id, ACTUAL.raiz)
    if clave not in SLUGS_MODULOS:
        SLUGS_MODULOS[clave] = {
            ruta: slug_url(nombre_de_modulo(ACTUAL, ruta))
            for ruta in carpetas_de_modulos(ACTUAL)
        }
    return SLUGS_MODULOS[clave].get(carpeta, carpeta.name)


def modulo_de_ruta(ruta: Path) -> Path | None:
    """Módulo más cercano que contiene la ruta; fuera de un módulo, `None`."""
    if not ACTUAL:
        return None
    candidatos = [
        carpeta
        for carpeta in carpetas_de_modulos(ACTUAL)
        if ruta == carpeta or ruta.is_relative_to(carpeta)
    ]
    if not candidatos:
        return None
    return max(candidatos, key=lambda carpeta: len(carpeta.parts))


def url_de(ruta: Path) -> str:
    """URL de una página o recurso, con el módulo como primer segmento.

    La fuente y sus carpetas de nivel (`primer-curso`, `azure`) no aparecen:
    son organización del repositorio, no del contenido.
    """
    if ruta == RAIZ:
        return "index.html"
    modulo = modulo_de_ruta(ruta)
    if modulo is not None:
        rel = "" if ruta == modulo else ruta.relative_to(modulo).as_posix()
        nombre = slug_de_modulo(modulo)
        url = f"{nombre}/{rel}" if rel else nombre
    else:
        url = ruta.relative_to(RAIZ).as_posix()
    if ruta.is_dir():
        return f"{url}/index.html" if (ruta / "README.md").exists() else f"{url}/"
    if url.endswith("/README.md"):
        return url[: -len("README.md")] + "index.html"
    if url == "README.md":
        return "index.html"
    if url.endswith(".md"):
        return url[:-3] + ".html"
    return url


def relativo(destino: str, desde: str) -> str:
    """Enlace de `desde` (página) a `destino` (otra página o recurso)."""
    base = posixpath.dirname(desde) or "."
    ruta = posixpath.relpath(destino, base)
    return ruta


def sin_markup(texto: str) -> str:
    texto = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", texto)
    texto = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", texto)
    texto = re.sub(r"<[^>]+>", "", texto)
    texto = texto.replace("**", "").replace("`", "").replace("*", "")
    return texto.strip()


# Siglas y nombres que se conservan al pasar un título a minúscula natural.
SIGLAS = {
    "API": "API", "APIS": "APIs", "HTTP": "HTTP", "HTTPS": "HTTPS", "HTML": "HTML",
    "CSS": "CSS", "JSON": "JSON", "XML": "XML", "SQL": "SQL", "KQL": "KQL",
    "URL": "URL", "URI": "URI", "JWT": "JWT", "MVC": "MVC", "AJAX": "AJAX",
    "CLI": "CLI", "SDK": "SDK", "SSH": "SSH", "PDF": "PDF", "TDD": "TDD",
    "BDD": "BDD", "GUI": "GUI", "VCS": "VCS", "IOC": "IoC", "CI": "CI", "CD": "CD",
    "DI": "DI", "DTO": "DTO", "REST": "REST", "CRUD": "CRUD", "XSS": "XSS",
    "CSRF": "CSRF", "CORS": "CORS", "TLS": "TLS", "WSL": "WSL", "NAT": "NAT",
    "ORM": "ORM", "POO": "POO", "SOLID": "SOLID", "MS": "MS", "HEAD": "HEAD",
    "YAML": "YAML", "CRLF": "CRLF", "REPL": "REPL", "RFC": "RFC", "NET": "NET",
    "DOM": "DOM", "CORE": "Core", "COMPOSE": "Compose", "GO": "Go",
    "KOTLIN": "Kotlin", "ACTIONS": "Actions", "MULTI-STAGE": "multi-stage",
    "MULTI STAGE": "multi-stage", "DOCKER-IN-DOCKER": "Docker-in-Docker",
    "EXCEL": "Excel",
    "ANGULAR": "Angular", "DOCKER": "Docker", "PODMAN": "Podman", "GIT": "Git",
    "AZURE": "Azure", "WINDOWS": "Windows", "LINUX": "Linux",
    "UBUNTU": "Ubuntu", "NGINX": "nginx", "JENKINS": "Jenkins", "KAFKA": "Kafka",
    "KUBERNETES": "Kubernetes", "GITHUB": "GitHub", "GITLAB": "GitLab",
    "NUGET": "NuGet", "SQLITE": "SQLite", "POSTMAN": "Postman", "DEVOPS": "DevOps",
    "VISUAL": "Visual", "STUDIO": "Studio", "CODE": "Code", "DESKTOP": "Desktop",
    "ENGINE": "Engine", "HYPER-V": "Hyper-V", "XUNIT": "xUnit", "MOQ": "Moq",
    "RXJS": "RxJS", "XSSI": "XSSI", "CANACTIVATE": "canActivate",
    "CANACTIVATECHILD": "canActivateChild", "CANDEACTIVATE": "canDeactivate",
    "NGFORM": "ngForm", "NGMODEL": "ngModel", "NGMODELGROUP": "ngModelGroup",
    "NGIF": "ngIf", "NGFOR": "ngFor", "NGSWITCH": "ngSwitch", "NGCLASS": "ngClass",
    "NGSTYLE": "ngStyle", "NG": "ng", "IMPORTS": "imports", "DIGEST": "digest",
    "HTTPCLIENT": "HttpClient", "FORMGROUP": "FormGroup", "FORMBUILDER": "FormBuilder",
    "REACTIVEFORMSMODULE": "ReactiveFormsModule", "HOSTLISTENER": "HostListener",
    "HOSTBINDING": "HostBinding", "TYPESCRIPT": "TypeScript",
    "JAVASCRIPT": "JavaScript",
    "CONTENTRESULT": "ContentResult", "OKRESULT": "OkResult",
    "NOTFOUNDRESULT": "NotFoundResult", "VIEWRESULT": "ViewResult",
    "ACTIONRESULT": "ActionResult", "JSONRESULT": "JsonResult",
    "VIEWDATA": "ViewData", "VIEWBAG": "ViewBag", "TEMPDATA": "TempData",
    "STARTUP.CS": "Startup.cs", "AUTHORIZE": "Authorize",
    "ALLOWANONYMOUS": "AllowAnonymous", "REQUIREHTTPS": "RequireHttps",
    "ANCHORTAGHELPER": "AnchorTagHelper", "FORMTAGHELPER": "FormTagHelper",
    "INPUTTAGHELPER": "InputTagHelper", "PARTIALTAGHELPER": "PartialTagHelper",
    "TAGHELPER": "TagHelper", "TAGHELPERS": "TagHelpers",
    "IVALIDATABLEOBJECT": "IValidatableObject", "REQUIRED": "Required",
    "RANGE": "Range", "REGULAREXPRESSION": "RegularExpression",
    "STRINGLENGTH": "StringLength", "MAXLENGTH": "MaxLength", "MINLENGTH": "MinLength",
    "COMPARE": "Compare", "CREDITCARD": "CreditCard", "EMAILADDRESS": "EmailAddress",
    "FILEEXTENSIONS": "FileExtensions", "PHONE": "Phone",
    "INLINEDATA": "InlineData", "CLASSDATA": "ClassData", "MEMBERDATA": "MemberData",
    "ICLASSFIXTURE": "IClassFixture", "ICOLLECTIONFIXTURE": "ICollectionFixture",
    "GITFLOW": "GitFlow", "MASTER": "master", "TAGS": "tags", "PULL": "pull",
    "PUSH": "push", "ORIGIN": "origin", "BRANCH": "branch", "BRANCHES": "branches",
    "DOCKERHOST": "DOCKER_HOST", "MACVLAN": "macvlan", "MOUNT": "mount",
    "HISTORY": "history", "ROOT": "root", "DOCKERFILE": "Dockerfile",
    "RAID": "RAID", "CPU": "CPU", "RAM": "RAM", "SSD": "SSD", "USB": "USB",
    "VLAN": "VLAN", "SIEM": "SIEM", "DNS": "DNS", "DHCP": "DHCP", "LDAP": "LDAP",
    "NODE.JS": "Node.js", "VS": "vs", "POWERSHELL": "PowerShell",
    "MYSQL": "MySQL", "POSTGRESQL": "PostgreSQL", "TERRAFORM": "Terraform",
    "ANSIBLE": "Ansible", "VAGRANT": "Vagrant", "GRAFANA": "Grafana",
    "PROMETHEUS": "Prometheus", "ELASTICSEARCH": "Elasticsearch",
    "KIBANA": "Kibana", "LOGSTASH": "Logstash", "WIRESHARK": "Wireshark",
}

FRASES = {"HOST LISTENER": "HostListener", "HOST BINDING": "HostBinding",
          "WEB API": "Web API"}

# Palabras cortas que siempre van en minúscula dentro de un título.
MINUSCULAS = {"Y"}


def _minuscula_natural(segmento: str) -> str:
    for viejo, nuevo in FRASES.items():
        segmento = segmento.replace(viejo, nuevo)
    m = re.match(r"^(\d+(?:\.\d+)*\.?)\s+(.*)$", segmento)
    prefijo, resto = (m.group(1) + " ", m.group(2)) if m else ("", segmento)
    salida: list[str] = []
    primera = True
    for palabra in resto.split(" "):
        # Un enlace o un resto de marcado se deja tal cual.
        if "[" in palabra or "]" in palabra:
            salida.append(palabra)
            primera = False
            continue
        nucleo = palabra.strip('.,;:()¿?¡!"“”[]«»$*_`')
        if not nucleo:
            salida.append(palabra)
            continue
        if nucleo in SIGLAS:
            nueva = palabra.replace(nucleo, SIGLAS[nucleo])
        elif not re.fullmatch(r"[A-ZÁÉÍÓÚÜÑ0-9$#.]+", nucleo) or not any(c.isalpha() for c in nucleo):
            nueva = palabra
        elif nucleo in MINUSCULAS:
            nueva = palabra.replace(nucleo, nucleo.lower())
        elif "." in nucleo or any(c.isdigit() for c in nucleo):
            # Nombres de archivo y versiones se quedan como están.
            nueva = palabra
        elif len(nucleo) <= 5 and not any(c in "AEIOUÁÉÍÓÚÜ" for c in nucleo):
            # Siglas sin vocales: DNS, DHCP, FTP, HTTP.
            nueva = palabra
        else:
            nueva = palabra.replace(nucleo, nucleo.lower())
        if primera and nucleo not in SIGLAS:
            pos = next((i for i, c in enumerate(nueva) if c.isalpha()), None)
            if pos is not None:
                nueva = nueva[:pos] + nueva[pos].upper() + nueva[pos + 1:]
        salida.append(nueva)
        if any(c.isalpha() for c in nucleo):
            primera = False
    return prefijo + " ".join(salida)


def titulo_visible(texto: str, fuente_id: str = "") -> str:
    """Pasa a minúscula natural un título escrito en mayúsculas de diapositiva.

    Solo para los apuntes: los otros orígenes ya vienen en su forma final y usan
    siglas propias (DNS, DHCP, RAID) que no conviene tocar. Conserva lo que va
    entre comillas invertidas y los enlaces.
    """
    if not ACTUAL or ACTUAL.estructura != "apuntes":
        return texto
    prosa = "".join(texto.split("`")[0::2])
    letras = [c for c in prosa if c.isalpha()]
    if not letras or sum(c.isupper() for c in letras) / len(letras) < 0.7:
        return texto
    trozos = texto.split("`")
    for i in range(0, len(trozos), 2):
        trozos[i] = _minuscula_natural(trozos[i])
    return "`".join(trozos)


def limpiar_titulo(texto: str) -> str:
    """Quita el prefijo numérico del curso y las referencias «del módulo 50XX»."""
    # El número de módulo es interno: no se muestra en navegación, migas ni título.
    limpio = re.sub(r"^\s*m[oó]dulo\s+\d+\s*[:.\-–—]\s*", "", texto, flags=re.IGNORECASE)
    acronimos = r"(?:ASGBD|LMSGI|GBD|SAD|SRI|ASO|IAW|FOL|EIE|ISO|FH|REDES)"
    limpio = re.sub(r"^\d{4}\.\s*", "", limpio)
    limpio = re.sub(rf"^{acronimos}\s*[.·—:-]\s*", "", limpio, flags=re.IGNORECASE)
    limpio = re.sub(r"\s+del\s+m[oó]dulo\s+50\d\d", "", limpio, flags=re.IGNORECASE)
    limpio = re.sub(r"\s{2,}", " ", limpio).strip(" .·-—:")
    return limpio or texto


def slug(texto: str) -> str:
    limpio = sin_markup(texto).lower()
    limpio = re.sub(r"[^\w\- ]", "", limpio, flags=re.UNICODE)
    return re.sub(r"\s+", "-", limpio).strip("-") or "apartado"


def reescribir_enlace(destino: str, base: Path | None = None) -> str | None:
    """Ajusta un enlace del Markdown al fichero equivalente dentro del sitio.

    `base` es la carpeta del documento: sirve para comprobar qué existe de
    verdad. Un enlace que sale del repositorio o apunta a un archivo vetado
    se desenvuelve: no se publica una ruta del equipo ni una página que no
    existe.
    """
    if not destino or destino.startswith(("http://", "https://", "mailto:", "tel:", "#", "//")):
        return destino
    ruta, almohadilla, ancla = destino.partition("#")
    ruta, interrogacion, consulta = ruta.partition("?")
    if not ruta:
        return destino

    limpia = unquote(ruta)
    origen = (base or RAIZ)
    objetivo = (origen / limpia).resolve()
    dentro = objetivo.is_relative_to(RAIZ.resolve())

    if not dentro or objetivo.name in VETADOS:
        return None

    destino_url = url_de(objetivo)
    if PAGINA_ACTUAL:
        cola = "/" if destino_url.endswith("/") else ""
        relativa = relativo(destino_url.rstrip("/"), PAGINA_ACTUAL) + cola
    else:
        relativa = destino_url

    return (
        quote(relativa, safe="/")
        + ("?" + consulta if interrogacion else "")
        + ("#" + ancla if almohadilla else "")
    )


def sin_vallas(texto: str) -> str:
    """Quita los bloques de código, también los de más de tres backticks."""
    salida: list[str] = []
    valla = ""
    for linea in texto.split("\n"):
        marca = re.match(r"^\s*(`{3,}|~{3,})", linea)
        if marca:
            if not valla:
                valla = marca.group(1)
            elif re.match(rf"^\s*{re.escape(valla[0])}{{{len(valla)},}}\s*$", linea):
                valla = ""
            continue
        if not valla:
            salida.append(linea)
    return "\n".join(salida)


def texto_plano(md: str, limite: int = 12000) -> str:
    """Texto del documento para el índice de búsqueda."""
    md = sin_vallas(md)
    md = re.sub(r"<[^>]+>", " ", md)
    md = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", md)
    md = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", md)
    md = re.sub(r"[#>*_`|]+", " ", md)
    md = re.sub(r"\s+", " ", md)
    return md.strip()[:limite]


# --------------------------------------------------------------------------
# Renderizador de Markdown (subconjunto que usa el repositorio)
# --------------------------------------------------------------------------

RE_MARCADOR = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")
RE_CABECERA = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
RE_TABLA_SEP = re.compile(r"^\|?[\s:|-]+\|[\s:|-]*$")
RE_HTML = re.compile(r"^</?([a-zA-Z][a-zA-Z0-9]*)[^>]*>")
ETIQUETAS = {"img", "br", "hr", "details", "summary", "kbd", "sub", "sup"}


def sin_comentarios(texto: str) -> str:
    """Quita los comentarios HTML; los bloques `interno` no se publican."""
    texto = re.sub(r"<!--\s*interno\s*-->.*?<!--\s*/interno\s*-->", "", texto, flags=re.S)
    salida: list[str] = []
    en_valla = False
    valla = ""
    en_comentario = False
    for linea in texto.split("\n"):
        marca = re.match(r"^\s*(`{3,}|~{3,})", linea)
        if marca:
            cerca = marca.group(1)
            if not en_valla:
                en_valla = True
                valla = cerca
            elif re.match(rf"^\s*{re.escape(valla[0])}{{{len(valla)},}}\s*$", linea):
                en_valla = False
                valla = ""
            salida.append(linea)
            continue
        if en_valla:
            salida.append(linea)
            continue
        if en_comentario:
            if "-->" in linea:
                en_comentario = False
                resto = linea.split("-->", 1)[1]
                if resto.strip():
                    salida.append(resto)
            continue
        if "<!--" in linea:
            antes, _, despues = linea.partition("<!--")
            if "-->" in despues:
                resto = antes + despues.split("-->", 1)[1]
                if resto.strip():
                    salida.append(resto)
            else:
                en_comentario = True
                if antes.strip():
                    salida.append(antes)
            continue
        salida.append(linea)
    return "\n".join(salida)

ALERTAS = {
    "NOTE": ("nota", "Nota"),
    "TIP": ("nota", "Consejo"),
    "IMPORTANT": ("importante", "Importante"),
    "WARNING": ("aviso", "Aviso"),
    "CAUTION": ("aviso", "Cuidado"),
}


class Markdown:
    def __init__(self, base: Path | None = None) -> None:
        self.base = base or RAIZ
        self.toc: list[tuple[int, str, str]] = []
        self.ids: dict[str, int] = {}
        self.h1: str | None = None
        self.fuente_id = ACTUAL.id if ACTUAL else ""

    # -- bloque ------------------------------------------------------------
    def render(self, texto: str) -> str:
        lineas = sin_comentarios(texto.replace("\r\n", "\n")).split("\n")
        salida = self.bloques(lineas)
        self.filtrar_toc()
        return "\n".join(salida)

    def filtrar_toc(self) -> None:
        """Deja fuera del índice las cabeceras que son solo un número.

        Son restos de numeración del origen: la entrada no lleva a ningún título
        legible y ensuciaba «En esta página».
        """
        self.toc = [
            (nivel, ident, texto)
            for nivel, ident, texto in self.toc
            if re.search(r"[^\W\d_]", texto)
        ]

    def bloques(self, lineas: list[str]) -> list[str]:
        salida: list[str] = []
        i = 0
        while i < len(lineas):
            linea = lineas[i]
            if not linea.strip():
                i += 1
                continue

            valla = re.match(r"^(\s*)(`{3,}|~{3,})", linea)
            if valla:
                sangria, cerca = valla.group(1), valla.group(2)
                lenguaje = linea.lstrip()[len(cerca):].strip()
                cierre = re.compile(rf"^\s*{re.escape(cerca[0])}{{{len(cerca)},}}\s*$")
                i += 1
                cuerpo = []
                while i < len(lineas) and not cierre.match(lineas[i]):
                    cuerpo.append(lineas[i][len(sangria):] if lineas[i].startswith(sangria) else lineas[i].lstrip())
                    i += 1
                i += 1
                salida.append(
                    f'<pre class="codigo" data-lenguaje="{html.escape(lenguaje)}">'
                    f"<code>{html.escape(chr(10).join(cuerpo))}</code></pre>"
                )
                continue

            cabecera = RE_CABECERA.match(linea)
            if cabecera:
                nivel = len(cabecera.group(1))
                titulo = cabecera.group(2).strip()
                visible = titulo_visible(titulo, self.fuente_id)
                i += 1
                if nivel == 1 and self.h1 is None:
                    self.h1 = sin_markup(visible)
                    continue
                ident = self.identificador(titulo)
                if nivel >= 2:
                    self.toc.append((nivel, ident, sin_markup(visible)))
                salida.append(
                    f'<h{nivel} id="{ident}">'
                    f'<a class="ancla" href="#{ident}" aria-hidden="true" tabindex="-1">#</a>{self.inline(visible)}</h{nivel}>'
                )
                continue

            if re.fullmatch(r"\s*([-*_])\s*(?:\1\s*){2,}", linea):
                salida.append("<hr>")
                i += 1
                continue

            if linea.startswith(">"):
                i, bloque = self.cita(lineas, i)
                salida.append(bloque)
                continue

            if linea.lstrip().startswith("|") and i + 1 < len(lineas) and RE_TABLA_SEP.match(lineas[i + 1]):
                i, tabla = self.tabla(lineas, i)
                salida.append(tabla)
                continue

            if RE_MARCADOR.match(linea):
                i, lista = self.lista(lineas, i)
                salida.append(lista)
                continue

            etiqueta = RE_HTML.match(linea.strip())
            if etiqueta and etiqueta.group(1).lower() in ETIQUETAS:
                salida.append(linea.strip() if etiqueta.group(1).lower() != "img" else self.imagen_cruda(linea.strip()))
                i += 1
                continue

            parrafo = []
            while i < len(lineas) and lineas[i].strip():
                actual = lineas[i]
                if (
                    RE_CABECERA.match(actual)
                    or RE_MARCADOR.match(actual)
                    or actual.lstrip().startswith(("```", "~~~"))
                    or actual.startswith((">", "|"))
                    or (RE_HTML.match(actual.strip()) and RE_HTML.match(actual.strip()).group(1).lower() in ETIQUETAS)
                    or re.fullmatch(r"\s*([-*_])\s*(?:\1\s*){2,}", actual)
                ):
                    break
                parrafo.append(actual.strip() + ("\x02" if actual.endswith("  ") else ""))
                i += 1
            if not parrafo:
                # Línea suelta que abre un bloque pero no lo completa (por ejemplo
                # una fila de tabla sin separador): se emite como texto.
                parrafo.append(linea.strip())
                i += 1
            salida.append(f"<p>{self.inline(' '.join(parrafo))}</p>")
        return salida

    def identificador(self, titulo: str) -> str:
        base = slug(titulo)
        if base in self.ids:
            self.ids[base] += 1
            return f"{base}-{self.ids[base]}"
        self.ids[base] = 0
        return base

    def cita(self, lineas: list[str], i: int) -> tuple[int, str]:
        cuerpo: list[str] = []
        while i < len(lineas) and lineas[i].startswith(">"):
            cuerpo.append(re.sub(r"^>\s?", "", lineas[i]))
            i += 1
        aviso = ""
        clase = "cita"
        if cuerpo and (m := re.fullmatch(r"\[!(\w+)\]\s*(.*)", cuerpo[0].strip())):
            tipo = m.group(1).upper()
            clase, etiqueta = ALERTAS.get(tipo, ("nota", tipo.title()))
            aviso = f'<p class="aviso-titulo">{etiqueta}</p>'
            cuerpo = cuerpo[1:]
            if m.group(2):
                cuerpo.insert(0, m.group(2))
        lineas_cita = [l for l in cuerpo if l.strip()]
        if lineas_cita and all(re.match(r"^\*\*[^*]+\*\*", l.strip()) for l in lineas_cita):
            # Bloque de metadatos: cada línea en su renglón.
            cuerpo = ["\x02".join(lineas_cita)]
        interior = "\n".join(self.bloques(cuerpo))
        return i, f'<blockquote class="{clase}">{aviso}{interior}</blockquote>'

    def tabla(self, lineas: list[str], i: int) -> tuple[int, str]:
        filas = []
        while i < len(lineas) and lineas[i].lstrip().startswith("|"):
            filas.append(lineas[i].strip())
            i += 1
        celdas = [[c.strip() for c in fila.strip("|").split("|")] for fila in filas]
        alineaciones = []
        for c in celdas[1]:
            if c.startswith(":") and c.endswith(":"):
                alineaciones.append("center")
            elif c.endswith(":"):
                alineaciones.append("right")
            elif c.startswith(":"):
                alineaciones.append("left")
            else:
                alineaciones.append("")
        def clase(n: int) -> str:
            alineada = alineaciones[n] if n < len(alineaciones) else ""
            return ' class="num"' if alineada == "right" else ""

        cabecera = "".join(
            f"<th{clase(n)}>{self.inline(c)}</th>" for n, c in enumerate(celdas[0])
        )
        cuerpo = []
        for fila in celdas[2:]:
            cuerpo.append(
                "<tr>"
                + "".join(f"<td{clase(n)}>{self.inline(c)}</td>" for n, c in enumerate(fila))
                + "</tr>"
            )
        return i, (
            f'<div class="tabla-marco"><table><thead><tr>{cabecera}</tr></thead>'
            f"<tbody>{''.join(cuerpo)}</tbody></table></div>"
        )

    def lista(self, lineas: list[str], i: int) -> tuple[int, str]:
        primero = RE_MARCADOR.match(lineas[i])
        base = len(primero.group(1).expandtabs(2))
        ordenada = primero.group(2)[0].isdigit()
        inicio = int(re.sub(r"\D", "", primero.group(2))) if ordenada else 1

        elementos: list[list[str]] = []
        actual: list[str] | None = None
        while i < len(lineas):
            linea = lineas[i]
            if not linea.strip():
                siguiente = i + 1
                while siguiente < len(lineas) and not lineas[siguiente].strip():
                    siguiente += 1
                if siguiente < len(lineas):
                    m = RE_MARCADOR.match(lineas[siguiente])
                    sangria = len(lineas[siguiente]) - len(lineas[siguiente].lstrip())
                    if m and sangria <= base:
                        i = siguiente
                        continue
                    if sangria > base:
                        actual.append("") if actual is not None else None
                        i += 1
                        continue
                break
            sangria = len(linea) - len(linea.lstrip())
            marcador = RE_MARCADOR.match(linea)
            if marcador and len(marcador.group(1).expandtabs(2)) == base:
                actual = [marcador.group(3)]
                elementos.append(actual)
                i += 1
                continue
            if sangria > base and actual is not None:
                actual.append(linea[base:])
                i += 1
                continue
            break

        etiqueta = "ol" if ordenada else "ul"
        atributos = f' start="{inicio}"' if ordenada and inicio != 1 else ""
        piezas = []
        for elemento in elementos:
            contenido = "\n".join(elemento)
            if re.match(r"^\[[ xX]\]\s", contenido):
                hecho = contenido[1].lower() == "x"
                contenido = contenido[4:]
                interior = self.inline(contenido)
                marca = "hecho" if hecho else "pendiente"
                piezas.append(
                    f'<li class="tarea {marca}"><span class="casilla" aria-hidden="true"></span>{interior}</li>'
                )
                continue
            interior = "\n".join(self.bloques(elemento))
            if interior.startswith("<p>") and interior.endswith("</p>") and interior.count("<p>") == 1:
                interior = interior[3:-4]
            piezas.append(f"<li>{interior}</li>")
        return i, f'<{etiqueta}{atributos} class="lista">{"".join(piezas)}</{etiqueta}>'

    # -- línea -------------------------------------------------------------
    def imagen_cruda(self, etiqueta: str) -> str:
        origen = re.search(r'src="([^"]*)"', etiqueta)
        if origen:
            destino = reescribir_enlace(origen.group(1), self.base)
            if destino is None:
                return ""
            etiqueta = etiqueta.replace(origen.group(1), destino, 1)
        return etiqueta

    def inline(self, texto: str) -> str:
        codigos: list[str] = []
        crudas: list[str] = []

        def guardar_cruda(m: re.Match) -> str:
            crudas.append(self.imagen_cruda(m.group(0)))
            return f"\x05{len(crudas) - 1}\x05"

        texto = re.sub(r"<img\b[^>]*>", guardar_cruda, texto, flags=re.I)

        def guardar_codigo(m: re.Match) -> str:
            codigos.append(f"<code>{html.escape(m.group(1))}</code>")
            return f"\x00{len(codigos) - 1}\x00"

        texto = re.sub(r"<!\[CDATA\[[^\]]*\]\]>|`([^`]+)`", guardar_codigo, texto)
        texto = html.escape(texto, quote=True)

        autoenlaces: list[str] = []

        def guardar_auto(m: re.Match) -> str:
            url = m.group(1)
            autoenlaces.append(f'<a href="{url}">{url}</a>')
            return f"\x01{len(autoenlaces) - 1}\x01"

        texto = re.sub(r"&lt;(https?://[^\s&]+)&gt;", guardar_auto, texto)

        def imagen(m: re.Match) -> str:
            alt = m.group(1)
            # «Figura» no describe nada: mejor sin texto alternativo que con ruido.
            resto = re.sub(
                r"^(figura|imagen|fig)\b\s*\d*\s*[:.\-–—]?\s*",
                "",
                alt.strip(),
                flags=re.IGNORECASE,
            )
            alt = resto
            destino = reescribir_enlace(m.group(2), self.base)
            if destino is None:
                return alt
            return f'<img src="{destino}" alt="{alt}" loading="lazy">'

        texto = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", imagen, texto)

        def enlace(m: re.Match) -> str:
            etiqueta, destino = m.group(1), m.group(2)
            href = reescribir_enlace(destino, self.base)
            if href is None:
                return etiqueta
            externo = ' target="_blank" rel="noopener"' if href.startswith("http") else ""
            return f'<a href="{href}"{externo}>{etiqueta}</a>'

        texto = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", enlace, texto)
        texto = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", texto)
        texto = re.sub(r"(?<![\w*])\*([^*\s][^*]*?)\*(?![\w*])", r"<em>\1</em>", texto)
        texto = re.sub(r"~~([^~]+)~~", r"<del>\1</del>", texto)

        texto = texto.replace("\x02", "<br>")
        for n, bloque in enumerate(codigos):
            texto = texto.replace(f"\x00{n}\x00", bloque)
        for n, bloque in enumerate(autoenlaces):
            texto = texto.replace(f"\x01{n}\x01", bloque)
        for n, bloque in enumerate(crudas):
            texto = texto.replace(f"\x05{n}\x05", bloque)
        return texto


# --------------------------------------------------------------------------
# Inventario de documentos y árbol de navegación
# --------------------------------------------------------------------------

def es_contenido_en(raiz: Path, ruta: Path) -> bool:
    """¿El fichero entra en el sitio? Se vetó por nombre y por carpeta de primer nivel."""
    partes = ruta.relative_to(raiz).parts
    if ruta.name in VETADOS:
        return False
    if partes and partes[0] in VETADAS:
        return False
    return not any(parte in PROFUNDAS for parte in partes[:-1])


def es_contenido(ruta: Path) -> bool:
    return es_contenido_en(RAIZ, ruta)


class Nodo:
    __slots__ = (
        "ruta",
        "titulo",
        "url",
        "hijos",
        "es_carpeta",
        "codigo",
        "fuente_id",
        "clave",
        "icono",
    )

    def __init__(self, ruta: Path, titulo: str, url: str | None, es_carpeta: bool) -> None:
        self.ruta = ruta
        self.titulo = titulo
        self.url = url
        self.hijos: list[Nodo] = []
        self.es_carpeta = es_carpeta
        self.codigo = re.match(r"^(50\d\d)", ruta.name)
        self.codigo = self.codigo.group(1) if self.codigo else ""
        self.fuente_id = ACTUAL.id if ACTUAL else ""
        self.icono = ""
        modulo = modulo_de_ruta(ruta) if ACTUAL else None
        if modulo is not None:
            dentro = (
                "" if ruta == modulo else "/" + ruta.relative_to(modulo).as_posix()
            )
            self.clave = slug_de_modulo(modulo) + dentro
        else:
            try:
                self.clave = ruta.relative_to(RAIZ).as_posix()
            except ValueError:
                self.clave = ruta.name


TITULOS: dict[Path, str] = {}


def titulo_de(ruta: Path) -> str:
    if ruta in TITULOS:
        return TITULOS[ruta]
    titulo = ""
    if ruta.is_file():
        for linea in ruta.read_text(encoding="utf-8").splitlines()[:40]:
            if m := RE_CABECERA.match(linea):
                titulo = sin_markup(titulo_visible(m.group(2), ACTUAL.id if ACTUAL else ""))
                break
    else:
        readme = ruta / "README.md"
        if readme.exists():
            titulo = titulo_de(readme)
    if not titulo:
        titulo = ruta.stem.replace("-", " ").capitalize() if ruta.is_file() else bonito(ruta.name)
    titulo = limpiar_titulo(titulo)
    TITULOS[ruta] = titulo
    return titulo


def bonito(nombre: str) -> str:
    if nombre == "assets":
        return "Recursos gráficos"
    if nombre == "teoria":
        return "Teoría"
    if nombre == "ejercicios":
        return "Ejercicios"
    nombre = re.sub(r"^(ud)(\d+)", lambda m: f"UD{m.group(2)}", nombre, flags=re.I)
    nombre = nombre.replace("-", " ").replace("_", " ")
    return nombre[:1].upper() + nombre[1:]


def orden_indice(carpeta: Path) -> list[str]:
    """Orden de estudio que fija el README de la carpeta, si lo trae."""
    readme = carpeta / "README.md"
    if not readme.exists():
        return []
    orden: list[str] = []
    for destino in re.findall(r"\]\(([^)\s#]+)", readme.read_text(encoding="utf-8")):
        if destino.startswith(("http", "mailto", "#")):
            continue
        limpio = posixpath.normpath(destino.rstrip("/"))
        if limpio not in orden:
            orden.append(limpio)
    return orden


def hijo_ordenado(hijos: list[Nodo], carpeta: Path) -> list[Nodo]:
    orden = orden_indice(carpeta)

    def clave(nodo: Nodo) -> tuple[int, str]:
        rel = posixpath.normpath(nodo.ruta.relative_to(carpeta).as_posix())
        for pos, destino in enumerate(orden):
            if destino in (rel, rel + "/index.html", rel[:-3] + ".html", rel + "/README.md"):
                return pos, ""
            if destino.startswith(rel + "/"):
                return pos, ""
        return len(orden) + 1, nodo.ruta.name

    return sorted(hijos, key=clave)


def arbol(carpeta: Path, profundidad: int = 0) -> Nodo:
    hijos: list[Nodo] = []
    for elemento in sorted(carpeta.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
        if elemento.name in VETADAS or elemento.name in VETADOS or elemento.name in PROFUNDAS or elemento.name.startswith("."):
            continue
        if elemento.is_dir():
            if not any(es_contenido(p) for p in elemento.rglob("*.md")):
                continue
            hijos.append(arbol(elemento, profundidad + 1))
        elif elemento.suffix == ".md" and elemento.name != "README.md":
            hijos.append(Nodo(elemento, titulo_de(elemento), url_de(elemento), False))
    hijos = hijo_ordenado(hijos, carpeta)

    readme = carpeta / "README.md"
    if readme.exists():
        url = url_de(readme)
        titulo = titulo_de(readme)
    else:
        url = None
        titulo = bonito(carpeta.name)
    if profundidad > 0 and carpeta.name.startswith("ud"):
        titulo = titulo if titulo.lower().startswith("ud") else f"{carpeta.name.upper()}. {titulo}"
    return _nodo(carpeta, titulo, url, hijos)


def _nodo(carpeta: Path, titulo: str, url: str | None, hijos: list[Nodo]) -> Nodo:
    nodo = Nodo(carpeta, titulo, url, True)
    nodo.hijos = hijos
    return nodo


def aplanar(nodo: Nodo, salida: list[Nodo]) -> list[Nodo]:
    if nodo.url:
        salida.append(nodo)
    for hijo in nodo.hijos:
        aplanar(hijo, salida)
    return salida


# --------------------------------------------------------------------------
# Construcción de páginas
# --------------------------------------------------------------------------

def leer_plantilla() -> str:
    return (FUENTE / "plantilla.html").read_text(encoding="utf-8")


def migas(camino: list[Nodo], pagina: str, raiz: str) -> str:
    piezas = [f'<a href="{relativo("index.html", pagina)}">Biblioteca técnica</a>']
    for nodo in camino[1:-1]:
        if nodo.url:
            piezas.append(f'<a href="{relativo(nodo.url, pagina)}">{html.escape(nodo.titulo)}</a>')
        else:
            piezas.append(f"<span>{html.escape(nodo.titulo)}</span>")
    if len(camino) > 1:
        piezas.append(f'<span aria-current="page">{html.escape(camino[-1].titulo)}</span>')
    return '<span class="sep">/</span>'.join(piezas)


def etiquetas(ruta: Path) -> list[str]:
    rel = ruta.relative_to(RAIZ).parts
    piezas: list[str] = []
    if len(rel) <= 1:
        return piezas
    clave = ""
    if ACTUAL and ACTUAL.estructura == "curso":
        clave = rel[0]
    elif ACTUAL and ACTUAL.estructura == "apuntes":
        # La categoría sale del módulo: la carpeta más cercana con README.
        carpeta = ruta.parent
        while carpeta != RAIZ and not (carpeta / "README.md").exists():
            carpeta = carpeta.parent
        clave = carpeta.name
    elif ACTUAL and len(rel) > 1:
        clave = rel[1]
    categoria = CATEGORIAS.get(clave) or CATEGORIAS.get(clave.split("-")[0], "")
    if categoria:
        piezas.append(categoria)
    if ACTUAL and ACTUAL.estructura == "apuntes":
        if ruta.name != "README.md":
            piezas.append("Apunte")
        return piezas
    if "teoria" in rel:
        piezas.append("Teoría")
    elif "ejercicios" in rel:
        piezas.append("Ejercicios")
    return piezas


def es_guia_rel(rel: tuple[str, ...]) -> bool:
    """Una guía es el README de una actividad, no el índice de la carpeta."""
    if "ejercicios" not in rel or rel[-1] != "README.md":
        return False
    posicion = rel.index("ejercicios")
    carpetas = rel[posicion + 1 : -1]
    if not carpetas:
        return False
    if any(carpeta in {"soluciones", "recursos", "evidencias"} for carpeta in carpetas):
        return False
    if re.match(r"^ud\d+", carpetas[-1], flags=re.I):
        return False
    return True


def tipo_documento(ruta: Path) -> str:
    """Clasifica una página para el índice de búsqueda."""
    rel = ruta.relative_to(RAIZ).parts
    if ACTUAL and ACTUAL.estructura == "apuntes":
        return "indice" if ruta.name == "README.md" else "apunte"
    if "teoria" in rel and ruta.name != "README.md":
        return "apunte"
    if es_guia_rel(rel):
        return "guia"
    return "indice"


@dataclass
class Modulo:
    nodo: Nodo
    clave: str
    etiqueta: str
    nombre: str
    grupo: str
    conteo: dict[str, int]
    categoria: str = ""
    resumen: str = ""
    icono: str = ""


def codigo_modulo(modulo: Modulo) -> str:
    """Clave estable del módulo: su segmento de URL, sin la fuente."""
    return posixpath.dirname(modulo.nodo.url or "") or modulo.nodo.ruta.name


def resumen_de(ruta: Path) -> str:
    """Primer párrafo útil del README del módulo, para la tarjeta."""
    readme = ruta / "README.md"
    if not readme.exists():
        return ""
    lineas = readme.read_text(encoding="utf-8").splitlines()
    inicio = next(
        (
            indice + 1
            for indice, linea in enumerate(lineas)
            if re.match(r"^##\s+(Alcance|Propósito|Qué es|Que es)", linea, flags=re.I)
        ),
        None,
    )
    if inicio is None:
        inicio = next(
            (indice + 1 for indice, linea in enumerate(lineas) if linea.startswith("# ")),
            0,
        )
    parrafo: list[str] = []
    for linea in lineas[inicio:]:
        limpia = linea.strip()
        if not limpia:
            if parrafo:
                break
            continue
        if limpia.startswith(("#", "|", ">", "-", "*", "```")):
            if parrafo:
                break
            continue
        parrafo.append(limpia)
    texto = sin_markup(" ".join(parrafo))
    if len(texto) > 150:
        texto = texto[:147].rsplit(" ", 1)[0] + "…"
    return texto


def conteo_modulo(ruta: Path) -> dict[str, int]:
    if ACTUAL and ACTUAL.estructura == "apuntes":
        documentos_modulo = [p for p in ruta.rglob("*.md") if es_contenido(p)]
        return {
            "paginas": len(documentos_modulo),
            "teoria": 0,
            "apuntes": sum(1 for p in documentos_modulo if p.name != "README.md"),
            "ejercicios": 0,
            "guias": 0,
        }
    documentos_modulo = [p for p in ruta.rglob("*.md") if es_contenido(p)]
    teoria = 0
    apuntes = 0
    guias = 0
    ejercicios = 0
    for documento in documentos_modulo:
        rel = documento.relative_to(ruta).parts
        if rel and rel[0] == "teoria":
            teoria += 1
            if documento.name != "README.md":
                apuntes += 1
        elif rel and rel[0] == "ejercicios":
            ejercicios += 1
            if es_guia_rel(rel):
                guias += 1
    return {
        "paginas": len(documentos_modulo),
        "teoria": teoria,
        "apuntes": apuntes,
        "ejercicios": ejercicios,
        "guias": guias,
    }


def ordenar_arbol_por_raiz(fuente: Fuente, raiz_arbol: Nodo) -> None:
    """Respeta el orden de módulos que fija el README raíz de ASIR."""
    readme = fuente.raiz / "README.md"
    if not readme.exists() or not fuente.raices:
        return
    orden: list[str] = []
    for destino in re.findall(r"\]\(([^)\s#]+)", readme.read_text(encoding="utf-8")):
        if destino.startswith(("http", "mailto", "#")):
            continue
        limpio = posixpath.normpath(destino.rstrip("/"))
        if limpio not in orden:
            orden.append(limpio)

    def posicion(rel: str) -> int:
        for indice, destino in enumerate(orden):
            if (
                destino == rel
                or destino == rel + "/README.md"
                or destino.startswith(rel + "/")
            ):
                return indice
        return len(orden)

    for grupo in raiz_arbol.hijos:
        if grupo.es_carpeta and grupo.ruta.name in fuente.raices:
            grupo.hijos.sort(
                key=lambda nodo: (
                    posicion(f"{grupo.ruta.name}/{nodo.ruta.name}"),
                    nodo.ruta.name,
                )
            )


def icono_modulo(fuente: Fuente, clave: str) -> str:
    corta = clave.split("-")[0]
    for candidata in (clave, corta):
        ruta = fuente.raiz / "assets" / "iconos" / f"{candidata}.svg"
        if ruta.exists():
            return url_de(ruta)
    glifo = ICONOS_MODULO.get(clave) or ICONOS_MODULO.get(corta, "documento")
    return f"_sitio/iconos/{glifo}.svg"


def _modulos_apuntes(
    fuente: Fuente, raiz_arbol: Nodo, categoria
) -> list[Modulo]:
    """Cada carpeta con README y apuntes es un módulo; admite un nivel de curso."""
    nodos: dict[Path, Nodo] = {}

    def recorrer(nodo: Nodo) -> None:
        nodos[nodo.ruta] = nodo
        for hijo in nodo.hijos:
            recorrer(hijo)

    recorrer(raiz_arbol)
    orden = orden_indice(fuente.raiz)

    def posicion(ruta: Path) -> int:
        rel = ruta.relative_to(fuente.raiz).as_posix()
        for indice, destino in enumerate(orden):
            limpio = posixpath.normpath(destino.rstrip("/"))
            if limpio in (rel, rel + "/README.md") or destino.startswith(rel + "/"):
                return indice
        return len(orden)

    modulos: list[Modulo] = []
    carpetas_vistas: dict[str, Path] = {}
    for ruta, nodo in nodos.items():
        if ruta == fuente.raiz or not nodo.es_carpeta:
            continue
        if not (ruta / "README.md").exists():
            continue
        if not any(
            p.suffix == ".md" and p.name != "README.md" for p in ruta.iterdir()
        ):
            continue
        carpeta = ruta.name
        if carpeta in carpetas_vistas:
            raise SystemExit(
                f"{fuente.id}: dos módulos comparten la carpeta {carpeta!r}: "
                f"{carpetas_vistas[carpeta]} y {ruta}"
            )
        carpetas_vistas[carpeta] = ruta
        nombre = fuente.nombres.get(carpeta)
        if not nombre:
            nombre = re.sub(r"^\d+[.\-]\s*", "", limpiar_titulo(nodo.titulo))
        nodo.titulo = nombre
        icono = icono_modulo(fuente, carpeta)
        nodo.icono = icono
        modulos.append(
            Modulo(
                nodo=nodo,
                clave=ruta.relative_to(fuente.raiz).as_posix(),
                etiqueta="",
                nombre=nombre,
                grupo=fuente.titulo,
                conteo=conteo_modulo(ruta),
                categoria=categoria(carpeta),
                # El README de estos módulos es la introducción al tema; su
                # primer párrafo sirve de resumen en la tarjeta.
                resumen=resumen_de(ruta),
                icono=icono,
            )
        )
    modulos.sort(key=lambda modulo: posicion(modulo.nodo.ruta))
    return modulos


def modulos_de(
    fuente: Fuente, raiz_arbol: Nodo, categorias: dict[str, str]
) -> list[Modulo]:
    """Módulos del temario, sin prefijos de curso en el nombre visible."""
    modulos: list[Modulo] = []

    def categoria(clave: str) -> str:
        return categorias.get(clave) or categorias.get(clave.split("-")[0], "")

    if fuente.estructura == "curso":
        for hijo in raiz_arbol.hijos:
            if hijo.es_carpeta and re.match(r"^\d{4}", hijo.ruta.name):
                clave = hijo.ruta.name
                nombre = fuente.nombres.get(clave) or limpiar_titulo(hijo.titulo)
                hijo.titulo = nombre
                icono = icono_modulo(fuente, clave)
                hijo.icono = icono
                modulos.append(
                    Modulo(
                        nodo=hijo,
                        clave=clave,
                        etiqueta="",
                        nombre=nombre,
                        grupo="Módulos",
                        conteo=conteo_modulo(hijo.ruta),
                        categoria=categoria(clave),
                        resumen=resumen_de(hijo.ruta),
                        icono=icono,
                    )
                )
        return modulos

    if fuente.estructura == "apuntes":
        return _modulos_apuntes(fuente, raiz_arbol, categoria)

    for nombre_grupo in fuente.raices:
        grupo = next((h for h in raiz_arbol.hijos if h.ruta.name == nombre_grupo), None)
        if not grupo:
            continue
        for hijo in grupo.hijos:
            if not hijo.es_carpeta:
                continue
            clave = hijo.ruta.name
            nombre = fuente.nombres.get(clave) or limpiar_titulo(hijo.titulo)
            hijo.titulo = nombre
            icono = icono_modulo(fuente, clave)
            hijo.icono = icono
            modulos.append(
                Modulo(
                    nodo=hijo,
                    clave=clave,
                    etiqueta="",
                    nombre=nombre,
                    grupo=grupo.titulo,
                    conteo=conteo_modulo(hijo.ruta),
                    categoria=categoria(clave),
                    resumen=resumen_de(hijo.ruta),
                    icono=icono,
                )
            )
    return modulos


def render_lateral(nodo: Nodo, pagina: str, actual: str) -> str:
    """Árbol de navegación con `<details>`: se despliega sin JavaScript.

    En una rama, el título es el enlace a su página y el marcador de la
    izquierda despliega; cerrar el grupo no impide navegar.
    """
    def es_actual(candidato: Nodo) -> bool:
        if not candidato.url:
            return False
        if candidato.url == actual:
            return True
        if candidato.es_carpeta and candidato.url.endswith("/index.html"):
            return actual.startswith(candidato.url[: -len("index.html")])
        return False

    contiene_actual = any(es_actual(visitado) for visitado in aplanar(nodo, []))
    etiqueta = html.escape(nodo.titulo)
    marcado = ' aria-current="page"' if es_actual(nodo) else ""
    icono = ""
    if nodo.icono:
        icono = glifo_en_linea(nodo.icono, "icono-lateral")
        if not icono:
            icono = (
                f'<img class="icono-lateral" '
                f'src="{relativo(nodo.icono, pagina)}" alt="">'
            )
    if not nodo.hijos:
        if not nodo.url:
            return f'<li class="hoja"><span class="enlace">{etiqueta}</span></li>'
        return (
            f'<li class="hoja"><a class="enlace"{marcado} '
            f'href="{relativo(nodo.url, pagina)}">{icono}{etiqueta}</a></li>'
        )

    if nodo.url:
        titulo_rama = f'<a class="enlace-rama"{marcado} href="{relativo(nodo.url, pagina)}">{etiqueta}</a>'
    else:
        titulo_rama = f'<span class="enlace-rama">{etiqueta}</span>'
    hijos = "".join(render_lateral(hijo, pagina, actual) for hijo in nodo.hijos)
    abierto = " open" if contiene_actual else ""
    cuenta = ""
    if nodo.clave.startswith("categoria:") or nodo.clave == "recursos":
        cuenta = f'<span class="rama-cuenta">{len(nodo.hijos)}</span>'
    return (
        f'<li class="rama"><details{abierto} data-clave="{html.escape(nodo.clave)}">'
        f'<summary>{icono}{titulo_rama}{cuenta}'
        f'</summary><ul class="hijos">{hijos}</ul></details></li>'
    )


def recortar(nodo: Nodo, nivel: int) -> Nodo:
    """Copia el árbol limitando la profundidad del lateral."""
    copia = _nodo(nodo.ruta, nodo.titulo, nodo.url, [])
    copia.codigo = nodo.codigo
    copia.fuente_id = nodo.fuente_id
    copia.clave = nodo.clave
    copia.icono = nodo.icono
    if nivel < PROFUNDIDAD_LATERAL:
        copia.hijos = [recortar(hijo, nivel + 1) for hijo in nodo.hijos]
    return copia


def bloque_toc(toc: list[tuple[int, str, str]]) -> str:
    """Índice de la página: solo los encabezados de este documento."""
    piezas = "".join(
        f'<li class="nivel-{nivel}"><a href="#{ident}">{html.escape(texto)}</a></li>'
        for nivel, ident, texto in toc
        if nivel == 2
    )
    if not piezas:
        return ""
    return (
        '<nav class="toc" aria-label="En esta página">'
        f'<p class="toc-titulo">En esta página</p><ul>{piezas}</ul></nav>'
    )


def ruta_de(nodo: Nodo) -> Path:
    return nodo.ruta / "README.md" if nodo.es_carpeta else nodo.ruta


def raiz_modulo(ruta: Path) -> Path:
    """Carpeta del módulo: la más cercana hacia arriba con README propio."""
    raiz = ACTUAL.raiz if ACTUAL else SITIO
    carpeta = ruta.parent
    while carpeta != raiz and not (carpeta / "README.md").exists():
        carpeta = carpeta.parent
    return carpeta


def bloque_paso(anterior: Nodo | None, siguiente: Nodo | None, pagina: str) -> str:
    piezas = []
    for nodo, clase, rotulo in ((anterior, "anterior", "Anterior"), (siguiente, "siguiente", "Siguiente")):
        if nodo and nodo.url:
            piezas.append(
                f'<a class="paso-{clase}" href="{relativo(nodo.url, pagina)}">'
                f'<span>{rotulo}</span><strong>{html.escape(nodo.titulo)}</strong></a>'
            )
    if not piezas:
        return ""
    return f'<nav class="pasos" aria-label="Recorrido de estudio">{"".join(piezas)}</nav>'


def tarjeta_modulo(modulo: Modulo, pagina: str) -> str:
    datos = modulo.conteo
    clave_datos = codigo_modulo(modulo)
    icono = (
        f'<img src="{relativo(modulo.icono, pagina)}" alt="" width="32" height="32">'
        if modulo.icono
        else ""
    )
    url = relativo(modulo.nodo.url, pagina) if modulo.nodo.url else ""
    guias = datos["guias"]
    apuntes = datos["apuntes"]
    detalle_apuntes = f"{apuntes} apunte" if apuntes == 1 else f"{apuntes} apuntes"
    if guias:
        detalle_guias = f"{guias} guía" if guias == 1 else f"{guias} guías"
        detalle = f"{detalle_apuntes} · {detalle_guias}"
    elif datos["ejercicios"]:
        detalle = f"{detalle_apuntes} · {datos['ejercicios']} páginas de ejercicios"
    else:
        detalle = detalle_apuntes
    etiqueta = (
        f'<span class="tarjeta-codigo">{html.escape(modulo.etiqueta)}</span>'
        if modulo.etiqueta
        else ""
    )
    categoria_texto = modulo.categoria.strip()
    if categoria_texto.casefold() in {
        modulo.etiqueta.strip().casefold(),
        modulo.nombre.strip().casefold(),
    }:
        categoria_texto = ""
    categoria = (
        f'<span class="tarjeta-categoria">{html.escape(categoria_texto)}</span>'
        if categoria_texto
        else ""
    )
    resumen = (
        f'<span class="tarjeta-resumen">{html.escape(modulo.resumen)}</span>'
        if modulo.resumen
        else ""
    )
    return (
        f'<a class="tarjeta tarjeta-modulo" href="{url}" '
        f'data-modulo="{html.escape(clave_datos)}" '
        f'data-categoria="{html.escape(modulo.categoria)}">'
        f'<span class="tarjeta-cabecera">{icono}{etiqueta}{categoria}</span>'
        f'<span class="tarjeta-titulo">{html.escape(modulo.nombre)}</span>'
        f"{resumen}"
        f'<span class="tarjeta-datos">{detalle}</span>'
        f'<span class="barra"><span class="barra-relleno" data-progreso="{html.escape(clave_datos)}"></span></span>'
        f'<span class="tarjeta-pie"><span data-leidas="{html.escape(clave_datos)}">0 de {datos["paginas"]}</span>'
        f'<span class="porcentaje" data-porcentaje="{html.escape(clave_datos)}">0 %</span></span>'
        "</a>"
    )


def escribir(ruta: Path, contenido: str) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(contenido, encoding="utf-8")


def revisar_enlaces() -> list[str]:
    """Revisa los enlaces del HTML generado; se ejecuta al final del build."""
    avisos: list[str] = []
    for archivo in SALIDA.rglob("*.html"):
        texto = re.sub(r"(?s)<pre.*?</pre>", " ", archivo.read_text(encoding="utf-8"))
        texto = re.sub(r"(?s)<!--.*?-->", " ", texto)
        for destino in re.findall(r'(?:href|src)="([^"]+)"', texto):
            if destino.startswith(("http", "mailto", "data:", "//", "#")):
                continue
            ruta = unquote(destino.split("#")[0].split("?")[0])
            if not ruta:
                continue
            if ruta.startswith("file://"):
                avisos.append(
                    f"{archivo.relative_to(SALIDA)} → enlace file:// no permitido: {ruta}"
                )
                continue
            if not (archivo.parent / ruta).resolve().exists():
                avisos.append(f"{archivo.relative_to(SALIDA)} → {destino}")
    return avisos


def construir_fuente(
    fuente: Fuente,
    modulos: list[Modulo],
    raiz_global: Nodo,
    orden: list[Nodo],
    caminos: dict[str, list[Nodo]],
) -> dict:
    """Genera las páginas de una fuente dentro del árbol común de `dist/`."""
    global RAIZ, ACTUAL
    RAIZ = fuente.raiz
    ACTUAL = fuente
    plantilla = leer_plantilla()
    version = hashlib.sha1(
        (FUENTE / "estilo.css").read_bytes()
        + (FUENTE / "app.js").read_bytes()
        + (SITIO / "_identidad" / "identidad.css").read_bytes()
        + (SITIO / "_identidad" / "menu.js").read_bytes()
    ).hexdigest()[:8]

    copiados = 0
    for origen in RAIZ.rglob("*"):
        if not origen.is_file():
            continue
        if not es_contenido(origen) or origen.suffix == ".md":
            continue
        if origen.suffix.lower() not in RECURSOS_PERMITIDOS or origen.name.startswith("."):
            continue
        url = url_de(origen)
        if (previa := RUTAS_URL.get(url)) is not None and previa != origen:
            raise SystemExit(
                f"Dos recursos comparten la URL {url!r}: {previa} y {origen}"
            )
        RUTAS_URL[url] = origen
        destino = SALIDA / url
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origen, destino)
        copiados += 1

    indice_busqueda: list[dict] = []
    total_fuente = sum(modulo.conteo["paginas"] for modulo in modulos)
    orden_fuente = [
        nodo for nodo in orden if nodo.url and nodo.fuente_id == fuente.id
    ]
    posiciones = {nodo.url: posicion for posicion, nodo in enumerate(orden_fuente)}

    def pagina_de_modulo(pagina: str) -> bool:
        for modulo in modulos:
            if not modulo.nodo.url:
                continue
            base = posixpath.dirname(modulo.nodo.url)
            if pagina == modulo.nodo.url or pagina.startswith(base + "/"):
                return True
        return False

    def pintar(
        pagina: str,
        cuerpo: str,
        titulo_html: str,
        cabecera_html: str,
        lateral: str,
        toc: str,
    ) -> str:
        base = posixpath.dirname(pagina) or "."
        raiz = posixpath.relpath(".", base) if base != "." else "."
        favicon = (
            f'<link rel="icon" href="'
            f'{relativo("_identidad/marca-tile.svg", pagina)}">'
        )
        icono_cabecera = (
            f'<img src="{relativo("_identidad/marca-tile.svg", pagina)}" '
            'alt="" width="40" height="40">'
        )
        reemplazos = {
            "{{TITULO}}": html.escape(titulo_html),
            "{{RAIZ}}": raiz,
            "{{V}}": version,
            "{{LATERAL}}": lateral,
            "{{CABECERA_MIGAS}}": migas(caminos.get(pagina, []), pagina, raiz),
            "{{CABECERA}}": cabecera_html,
            "{{CONTENIDO}}": cuerpo,
            "{{TOC}}": toc,
            "{{PAGINA}}": pagina,
            "{{MARCA}}": MARCA_SITIO,
            "{{DESCRIPCION}}": html.escape(DESCRIPCION_SITIO),
            "{{PIE}}": "",
            "{{CURSOS}}": relativo("index.html", pagina),
            "{{FAVICON}}": favicon,
            "{{ICONO_CABECERA}}": icono_cabecera,
            "{{LUPA}}": glifo_en_linea("_sitio/iconos/lupa.svg", "lupa"),
            "{{NAV_INDICE}}": (
                ' class="is-active" aria-current="page"' if pagina == "index.html" else ""
            ),
            "{{CLASE_CUERPO}}": "" if toc else "sin-toc",
        }
        salida = plantilla
        for clave, valor in reemplazos.items():
            salida = salida.replace(clave, valor)
        return salida

    pagina_count = 0

    def emitir(
        ruta: Path,
        pagina: str,
        titulo_nodo: str,
        anterior: Nodo | None,
        siguiente: Nodo | None,
    ) -> None:
        nonlocal pagina_count
        global PAGINA_ACTUAL
        PAGINA_ACTUAL = pagina
        md = Markdown(ruta.parent)
        texto = ruta.read_text(encoding="utf-8")
        texto = re.sub(
            r"(?mi)^>\s*\*\*módulo.*(?:\n|$)",
            "",
            texto,
        )
        cuerpo = md.render(texto)
        titulo = limpiar_titulo(md.h1 or titulo_nodo)
        camino = caminos.get(pagina, [])
        modulo = next((n for n in reversed(camino) if n.es_carpeta and n.url), None)
        actual = raiz_modulo(ruta)
        if anterior and raiz_modulo(ruta_de(anterior)) != actual:
            anterior = None
        if siguiente and raiz_modulo(ruta_de(siguiente)) != actual:
            siguiente = None

        chips = "".join(f'<span class="chip">{html.escape(c)}</span>' for c in etiquetas(ruta))
        marcar = ""
        if pagina_de_modulo(pagina):
            marcar = (
                f'<button class="boton-leido" data-leido="{pagina}" aria-pressed="false">'
                f'<span class="marca-leido" aria-hidden="true"></span>Marcar como leído</button>'
            )
        cabecera = (
            f'<header class="doc-cabecera"><h1>{html.escape(titulo)}</h1>'
            f'<div class="doc-meta">{chips}{marcar}</div></header>'
        )
        lateral = (
            '<nav class="lateral-nav" aria-label="Contenido"><ul class="nav-raiz">'
            + "".join(
                render_lateral(recortar(hijo, 0), pagina, pagina)
                for hijo in raiz_global.hijos
            )
            + "</ul></nav>"
        )
        escribir(
            SALIDA / pagina,
            pintar(
                pagina,
                f'<article class="documento"><div class="prosa">{cuerpo}</div>'
                f"{bloque_paso(anterior, siguiente, pagina)}</article>",
                f"{titulo} — {AUTOR}",
                cabecera,
                lateral,
                bloque_toc(md.toc),
            ),
        )
        pagina_count += 1
        if pagina not in RECURSOS_URLS:
            indice_busqueda.append(
                {
                    "t": titulo,
                    "u": pagina,
                    "m": "",
                    "x": texto_plano(texto),
                    "tipo": tipo_documento(ruta),
                }
            )

    for nodo in orden_fuente:
        pagina = nodo.url
        ruta = nodo.ruta / "README.md" if nodo.es_carpeta else nodo.ruta
        posicion = posiciones[pagina]
        emitir(
            ruta,
            pagina,
            nodo.titulo,
            orden_fuente[posicion - 1] if posicion > 0 else None,
            orden_fuente[posicion + 1] if posicion + 1 < len(orden_fuente) else None,
        )

    datos = {
        "modulos": [
            {
                "codigo": codigo_modulo(modulo),
                "etiqueta": modulo.etiqueta,
                "titulo": modulo.nombre,
                "grupo": fuente.titulo,
                "url": modulo.nodo.url,
                "paginas": modulo.conteo["paginas"],
                "categoria": modulo.categoria,
                "resumen": modulo.resumen,
            }
            for modulo in modulos
        ],
        "total": total_fuente,
    }
    print(f"[{fuente.id}] Páginas: {pagina_count}", flush=True)
    print(f"[{fuente.id}] Recursos copiados: {copiados}", flush=True)
    return {
        "fuente": fuente,
        "modulos": modulos,
        "datos": datos,
        "indice": indice_busqueda,
        "paginas": pagina_count,
        "total_paginas": total_fuente,
        "copiados": copiados,
    }


def pintar_global(
    plantilla: str, version: str, lateral: str, contenido: str, descripcion: str
) -> str:
    reemplazos = {
        "{{TITULO}}": TITULO_SITIO,
        "{{RAIZ}}": ".",
        "{{V}}": version,
        "{{LATERAL}}": lateral,
        "{{CABECERA_MIGAS}}": "",
        "{{CABECERA}}": "",
        "{{CONTENIDO}}": contenido,
        "{{TOC}}": "",
        "{{PAGINA}}": "index.html",
        "{{MARCA}}": MARCA_SITIO,
        "{{DESCRIPCION}}": html.escape(DESCRIPCION_SITIO),
        "{{PIE}}": "",
        "{{CURSOS}}": "index.html",
        "{{FAVICON}}": '<link rel="icon" href="_identidad/marca-tile.svg">',
        "{{ICONO_CABECERA}}": '<img src="_identidad/marca-tile.svg" alt="" width="40" height="40">',
        "{{LUPA}}": glifo_en_linea("_sitio/iconos/lupa.svg", "lupa"),
        "{{NAV_INDICE}}": ' class="is-active" aria-current="page"',
        "{{CLASE_CUERPO}}": "pagina-portada",
    }
    salida = plantilla
    for clave, valor in reemplazos.items():
        salida = salida.replace(clave, valor)
    return salida


def construir_portada(
    resultados: dict[str, dict],
    raiz_global: Nodo,
) -> None:
    """Portada única: todos los módulos como items, sin separar por cursos."""
    plantilla = leer_plantilla()
    version = hashlib.sha1(
        (FUENTE / "estilo.css").read_bytes()
        + (FUENTE / "app.js").read_bytes()
        + (SITIO / "_identidad" / "identidad.css").read_bytes()
        + (SITIO / "_identidad" / "menu.js").read_bytes()
    ).hexdigest()[:8]
    modulos_global: list[dict] = []
    indice_global: list[dict] = []
    pares_modulos: list[tuple[Fuente, Modulo]] = []
    total = 0
    categorias: set[str] = set()
    for resultado in resultados.values():
        fuente = resultado["fuente"]
        for modulo in resultado["modulos"]:
            pares_modulos.append((fuente, modulo))
            if modulo.categoria:
                categorias.add(modulo.categoria)
        indice_global.extend(resultado["indice"])
        total += resultado["total_paginas"]

    def orden_modulo(par: tuple[Fuente, Modulo]) -> tuple[int, str]:
        categoria = par[1].categoria
        posicion = (
            ORDEN_CATEGORIAS.index(categoria)
            if categoria in ORDEN_CATEGORIAS
            else len(ORDEN_CATEGORIAS)
        )
        return posicion, par[1].nombre.casefold()

    pares_modulos.sort(key=orden_modulo)
    tarjetas: list[str] = []
    for fuente, modulo in pares_modulos:
        modulos_global.append(
            {
                "codigo": codigo_modulo(modulo),
                "etiqueta": modulo.etiqueta,
                "titulo": modulo.nombre,
                "grupo": fuente.titulo,
                "url": modulo.nodo.url,
                "paginas": modulo.conteo["paginas"],
                "categoria": modulo.categoria,
                "resumen": modulo.resumen,
            }
        )
        tarjetas.append(tarjeta_modulo(modulo, "index.html"))

    datos = {
        "modulos": modulos_global,
        "total": total,
    }
    escribir(
        SALIDA / "_sitio" / "datos.js",
        "window.CURSO = " + json.dumps(datos, ensure_ascii=False) + ";\n",
    )
    escribir(
        SALIDA / "_sitio" / "indice.js",
        "window.INDICE = " + json.dumps(indice_global, ensure_ascii=False) + ";\n",
    )
    shutil.copy2(FUENTE / "estilo.css", SALIDA / "_sitio" / "estilo.css")
    shutil.copy2(FUENTE / "app.js", SALIDA / "_sitio" / "app.js")
    shutil.copytree(
        FUENTE / "iconos",
        SALIDA / "_sitio" / "iconos",
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("README.md"),
    )
    shutil.copy2(SITIO / "LICENSE", SALIDA / "_sitio" / "LICENSE")
    (SALIDA / "_identidad").mkdir(parents=True, exist_ok=True)
    for nombre in ("identidad.css", "marca-tile.svg", "menu.js"):
        shutil.copy2(SITIO / "_identidad" / nombre, SALIDA / "_identidad" / nombre)

    filtros = ['<button type="button" data-categoria="todas" aria-pressed="true">Todo</button>']
    for categoria in sorted(
        categorias,
        key=lambda c: (
            ORDEN_CATEGORIAS.index(c) if c in ORDEN_CATEGORIAS else len(ORDEN_CATEGORIAS),
            c,
        ),
    ):
        glifo = ICONOS_CATEGORIA.get(categoria)
        icono_filtro = (
            glifo_en_linea(f"_sitio/iconos/{glifo}.svg", "icono-filtro")
            if glifo
            else ""
        )
        if glifo and not icono_filtro:
            icono_filtro = (
                f'<img class="icono-filtro" src="_sitio/iconos/{glifo}.svg" alt="">'
            )
        filtros.append(
            f'<button type="button" data-categoria="{html.escape(categoria)}" '
            f'aria-pressed="false">{icono_filtro}{html.escape(categoria)}</button>'
        )
    lateral = (
        '<nav class="lateral-nav" aria-label="Contenido"><ul class="nav-raiz">'
        + "".join(
            render_lateral(recortar(hijo, 0), "index.html", "index.html")
            for hijo in raiz_global.hijos
        )
        + "</ul></nav>"
    )
    categorias_hero = [c for c in ORDEN_CATEGORIAS if c in categorias]
    if not categorias_hero:
        categorias_hero = sorted(categorias)
    nodos_hero = []
    for indice, categoria in enumerate(categorias_hero):
        glifo = ICONOS_CATEGORIA.get(categoria, "documento")
        angulo = 360 / max(len(categorias_hero), 1)
        nodos_hero.append(
            f'<span class="hero-node" style="--a:{indice * angulo:.3f}deg" '
            f'title="{html.escape(categoria)}">'
            f'<img src="_sitio/iconos/{glifo}.svg" alt=""></span>'
        )
    contenido = f"""
<header class="portada portada-temario">
  <div class="hero-copy">
    <p class="antetitulo"><span class="status-dot"></span>Contenido IT</p>
    <h1>Biblioteca técnica</h1>
    <p class="hero-role">Apuntes y práctica de sistemas, desarrollo y seguridad.</p>
    <p class="entradilla">Material propio, ordenado por materias, para estudiar y consultar.</p>
    <div class="portada-acciones">
      <button class="boton-principal" data-abrir-busqueda>Buscar en el contenido <kbd>Ctrl</kbd><kbd>K</kbd></button>
      <a class="boton-secundario" data-continuar href="index.html">Seguir donde lo dejé</a>
    </div>
    <div class="portada-progreso">
      <span class="barra barra-ancha"><span class="barra-relleno" data-progreso="total"></span></span>
      <span class="porcentaje" data-porcentaje="total">0 %</span>
    </div>
  </div>
  <div class="hero-art" aria-hidden="true">
    <span class="hero-ring"></span>
    <span class="hero-core"><strong>{len(categorias)}</strong><span>categorías</span></span>
    {''.join(nodos_hero)}
  </div>
</header>
<div class="chips-filtro" data-filtros aria-label="Filtrar por categoría">{''.join(filtros)}</div>
<section class="rejilla rejilla-contenido">{''.join(tarjetas)}</section>
"""
    escribir(
        SALIDA / "index.html",
        pintar_global(
            plantilla,
            version,
            lateral,
            contenido,
            "Biblioteca técnica: módulos de sistemas, redes, datos, desarrollo y seguridad.",
        ),
    )


@contextlib.contextmanager
def _cerrojo_de_proceso():
    """Impide que dos compilaciones se pisen el `dist` provisional.

    El servicio recompila al ver un cambio y alguien puede lanzar `build` a
    mano: sin este cerrojo, la segunda borra el directorio que la primera está
    escribiendo y el sitio queda a medias.
    """
    try:
        import fcntl
        import tempfile
    except ImportError:  # fuera de POSIX no hay cerrojo de fichero
        yield
        return
    clave = hashlib.sha1(str(SITIO).encode("utf-8")).hexdigest()[:12]
    ruta = Path(tempfile.gettempdir()) / f"biblioteca-tecnica-{clave}.lock"
    with open(ruta, "w", encoding="utf-8") as mango:
        fcntl.flock(mango, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(mango, fcntl.LOCK_UN)


def construir_todo(config: dict | None = None) -> dict[str, dict]:
    """Construye en un directorio provisional y lo cambia al final.

    Un fallo a mitad no toca el `dist/` que el servicio está sirviendo: el
    visor sigue en pie con la construcción anterior.
    """
    global SALIDA
    with _CERROJO, _cerrojo_de_proceso():
        definitiva = DIST
        provisional = definitiva.with_name(definitiva.name + ".nuevo")
        respaldo = definitiva.with_name(definitiva.name + ".viejo")
        for ruta in (provisional, respaldo):
            if ruta.exists():
                shutil.rmtree(ruta)
        SALIDA = provisional
        try:
            resultado = _construir(config)
        except BaseException:
            shutil.rmtree(provisional, ignore_errors=True)
            raise
        finally:
            SALIDA = definitiva
        if definitiva.exists():
            definitiva.rename(respaldo)
        try:
            provisional.rename(definitiva)
        except OSError:
            if respaldo.exists():
                respaldo.rename(definitiva)
            raise
        shutil.rmtree(respaldo, ignore_errors=True)
        return resultado


def _construir(config: dict | None = None) -> dict[str, dict]:
    global ACTUAL, RAIZ, AVISOS_BUILD, CATEGORIAS, ORDEN_CATEGORIAS, RECURSOS_URLS
    global FUENTES, GLIFOS_EN_LINEA, RUTAS_URL, MODULOS_POR_FUENTE, PAGINA_ACTUAL
    global SLUGS_MODULOS, TITULOS
    if config is None:
        config = cargar_config()
    fuentes = resolver_fuentes(config)
    FUENTES = fuentes
    CATEGORIAS = config.get("categorias", {})
    ORDEN_CATEGORIAS = config.get("orden_categorias", [])
    if SALIDA.exists():
        shutil.rmtree(SALIDA)
    SALIDA.mkdir(parents=True)
    # Marca de contenido ya construido: las carpetas con guion bajo son
    # contenido, no plantillas, si alguna vez se publica desde rama.
    (SALIDA / ".nojekyll").write_text("", encoding="utf-8")
    GLIFOS_EN_LINEA.clear()
    RUTAS_URL.clear()
    MODULOS_POR_FUENTE.clear()
    SLUGS_MODULOS.clear()
    TITULOS.clear()
    PAGINA_ACTUAL = ""

    raiz_global = Nodo(SITIO, "Biblioteca técnica", "index.html", True)
    raiz_global.fuente_id = ""
    raiz_global.clave = "raiz"
    recursos = Nodo(SITIO, "Recursos", None, True)
    recursos.fuente_id = ""
    recursos.clave = "recursos"
    recursos.icono = "_sitio/iconos/documento.svg"
    categorias_nodos: dict[str, Nodo] = {}
    datos_fuentes: list[tuple[Fuente, list[Modulo]]] = []
    segmentos: dict[str, Path] = {
        "_sitio": SITIO / "_sitio",
        "_identidad": SITIO / "_identidad",
        "assets": SITIO / "assets",
        "index.html": SITIO / "index.html",
    }

    def registrar_segmento(nombre: str, ruta: Path) -> None:
        previa = segmentos.get(nombre)
        if previa is not None and previa != ruta:
            raise SystemExit(
                f"Dos elementos comparten el primer segmento de URL {nombre!r}: "
                f"{previa} y {ruta}"
            )
        segmentos[nombre] = ruta

    for fuente in fuentes:
        ACTUAL = fuente
        RAIZ = fuente.raiz
        # Todo lo que puede ocupar el primer segmento de una URL de esta fuente:
        # carpetas de nivel, restos y recursos sueltos. `assets` es compartido.
        for ruta in fuente.raiz.iterdir():
            if ruta.name.startswith(".") or ruta.name in VETADAS or ruta.name in PROFUNDAS:
                continue
            if ruta.is_dir():
                if ruta.name != "assets":
                    registrar_segmento(ruta.name, ruta)
            elif ruta.name not in VETADOS and ruta.name != "README.md":
                registrar_segmento(url_de(ruta).split("/", 1)[0], ruta)
        for carpeta in carpetas_de_modulos(fuente):
            registrar_segmento(slug_de_modulo(carpeta), carpeta)
    for fuente in fuentes:
        ACTUAL = fuente
        RAIZ = fuente.raiz
        arbol_fuente = arbol(fuente.raiz)
        ordenar_arbol_por_raiz(fuente, arbol_fuente)
        modulos = modulos_de(fuente, arbol_fuente, CATEGORIAS)
        ids_modulos = {id(modulo.nodo) for modulo in modulos}
        for modulo in modulos:
            modulo.nodo.fuente_id = fuente.id
            categoria = modulo.categoria or "Otros"
            if categoria not in categorias_nodos:
                nodo_categoria = Nodo(SITIO, categoria, None, True)
                nodo_categoria.fuente_id = ""
                nodo_categoria.clave = f"categoria:{slug(categoria)}"
                nodo_categoria.icono = (
                    f"_sitio/iconos/{ICONOS_CATEGORIA.get(categoria, 'documento')}.svg"
                )
                categorias_nodos[categoria] = nodo_categoria
            categorias_nodos[categoria].hijos.append(modulo.nodo)
        # Toda la fuente de apuntes son módulos: nada queda como recurso suelto.
        for hijo in arbol_fuente.hijos:
            if id(hijo) in ids_modulos:
                continue
            if hijo.es_carpeta and hijo.ruta.name in fuente.raices:
                continue
            if hijo.ruta.name == "assets":
                continue
            if hijo.url:
                registrar_segmento(hijo.url.split("/", 1)[0], hijo.ruta)
            if fuente.estructura != "apuntes":
                recursos.hijos.append(hijo)
        datos_fuentes.append((fuente, modulos))

    def clave_categoria(nombre: str) -> tuple[int, str]:
        if nombre in ORDEN_CATEGORIAS:
            return ORDEN_CATEGORIAS.index(nombre), nombre
        return len(ORDEN_CATEGORIAS), nombre

    for nombre in sorted(categorias_nodos, key=clave_categoria):
        raiz_global.hijos.append(categorias_nodos[nombre])

    orden = aplanar(raiz_global, [])
    caminos: dict[str, list[Nodo]] = {}

    def recorrer(nodo: Nodo, camino: list[Nodo]) -> None:
        ruta_nodo = camino + [nodo]
        if nodo.url:
            caminos[nodo.url] = ruta_nodo
        for hijo in nodo.hijos:
            recorrer(hijo, ruta_nodo)

    recorrer(raiz_global, [])
    RECURSOS_URLS = {nodo.url for nodo in aplanar(recursos, []) if nodo.url}
    if recursos.hijos:
        orden.extend(aplanar(recursos, []))
        recorrer(recursos, [raiz_global])

    resultados: dict[str, dict] = {}
    for fuente, modulos in datos_fuentes:
        resultados[fuente.id] = construir_fuente(
            fuente, modulos, raiz_global, orden, caminos
        )

    construir_portada(resultados, raiz_global)
    AVISOS_BUILD = revisar_enlaces()
    if AVISOS_BUILD:
        print(f"Enlaces sin destino: {len(AVISOS_BUILD)}", flush=True)
        for aviso in AVISOS_BUILD[:15]:
            print("  " + aviso, flush=True)
    else:
        print("Enlaces internos: todos resuelven", flush=True)
    return resultados


def construir() -> int:
    resumen = construir_todo()
    print(f"Salida: {SALIDA.relative_to(SITIO)}", flush=True)
    print(
        f"Contenido: {sum(len(r['modulos']) for r in resumen.values())} módulos, "
        f"{sum(r['paginas'] for r in resumen.values())} páginas",
        flush=True,
    )
    return len(AVISOS_BUILD)


class Manejador(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST), **kwargs)

    def log_message(self, formato, *args):
        return


def archivos_vigilados(fuentes: list[Fuente]) -> list[Path]:
    rutas = [CONFIG]
    for fuente in fuentes:
        rutas.extend(
            ruta
            for ruta in fuente.raiz.rglob("*.md")
            if es_contenido_en(fuente.raiz, ruta)
        )
    rutas.extend(
        ruta
        for ruta in FUENTE.iterdir()
        if ruta.is_file() and ruta.suffix in {".css", ".js", ".html"}
    )
    rutas.append(SITIO / "_identidad" / "menu.js")
    return rutas


def servir(puerto: int, vigilar: bool, abrir: bool) -> int:
    config = cargar_config()
    construir_todo(config)
    try:
        servidor = ThreadingHTTPServer(("127.0.0.1", puerto), Manejador)
    except OSError as error:
        print(f"No se pudo abrir el puerto {puerto}: {error.strerror}.", flush=True)
        print(
            "Si el visor ya está en marcha, no hace falta otro: "
            f"http://127.0.0.1:{puerto}/",
            flush=True,
        )
        print("Para pararlo: systemctl --user stop biblioteca-tecnica", flush=True)
        return 1

    amable = f"http://127.0.0.1:{puerto}/"
    print(f"Sirviendo en {amable}", flush=True)

    if vigilar:
        def bucle():
            config_actual = config
            fuentes = resolver_fuentes(config_actual)
            sello_config = CONFIG.stat().st_mtime
            sellos: dict[Path, float] = {}
            for ruta in archivos_vigilados(fuentes):
                try:
                    sellos[ruta] = ruta.stat().st_mtime
                except OSError:
                    pass
            while True:
                time.sleep(2)
                cambio = False
                try:
                    sello_actual = CONFIG.stat().st_mtime
                except OSError:
                    sello_actual = sello_config
                if sello_actual != sello_config:
                    sello_config = sello_actual
                    try:
                        config_actual = cargar_config()
                        fuentes = resolver_fuentes(config_actual)
                        sellos = {}
                        cambio = True
                    except SystemExit as error:
                        print(f"No se pudo leer la configuración: {error}", flush=True)
                        continue
                for ruta in archivos_vigilados(fuentes):
                    try:
                        sello = ruta.stat().st_mtime
                    except OSError:
                        continue
                    if sellos.get(ruta) != sello:
                        if sellos:
                            cambio = True
                        sellos[ruta] = sello
                if cambio:
                    print("Cambio detectado, reconstruyendo…", flush=True)
                    try:
                        construir_todo(config_actual)
                    except BaseException as error:  # el servidor sigue en pie
                        print(f"No se pudo reconstruir: {error}", flush=True)

        threading.Thread(target=bucle, daemon=True).start()

    if abrir:
        webbrowser.open(amable)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nParado.", flush=True)
    return 0


def main() -> int:
    argumentos = sys.argv[1:]
    if argumentos and argumentos[0] in ("-h", "--help", "ayuda"):
        print(__doc__)
        return 0
    if argumentos and argumentos[0] == "serve":
        puerto = 8001
        if "--puerto" in argumentos:
            posicion = argumentos.index("--puerto") + 1
            if posicion >= len(argumentos):
                print("Falta el número después de --puerto.", file=sys.stderr)
                return 2
            try:
                puerto = int(argumentos[posicion])
            except ValueError:
                print("--puerto necesita un número.", file=sys.stderr)
                return 2
        return servir(puerto, "--vigilar" in argumentos, "--abrir" in argumentos)
    if argumentos and argumentos[0] in ("build", "check"):
        return 0 if construir() == 0 else 1
    return 0 if construir() == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
