#!/usr/bin/env python3
"""Construye el visor local del temario a partir de los Markdown de los cursos.

No guarda contenido propio: cada build lee las fuentes configuradas, las
convierte a HTML y genera un sitio en `dist/`. La raíz de cada fuente se
resuelve por etiqueta con `privatenotes/scripts/repos.py`; no hay rutas de
repos en el código.

Uso:
    python3 scripts/visor.py build
    python3 scripts/visor.py serve [--puerto 8001] [--vigilar] [--abrir]
    python3 scripts/visor.py check
"""

from __future__ import annotations

import hashlib
import html
import json
import posixpath
import re
import shutil
import subprocess
import sys
import threading
import time
import tomllib
import webbrowser
from dataclasses import dataclass, field
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

SITIO = Path(__file__).resolve().parent.parent
CONFIG = SITIO / "config" / "fuentes.toml"
SALIDA = SITIO / "dist"
FUENTE = SITIO / "sitio"

AUTOR = "Lorenzo Lanuza"
TITULO_SITIO = f"Formación · {AUTOR}"
MARCA_SITIO = 'Lorenzo <em>Lanuza</em>'
DESCRIPCION_SITIO = (
    "Formación de Lorenzo Lanuza: módulos de sistemas, redes, datos, "
    "desarrollo y seguridad."
)

ICONOS_CATEGORIA = {
    "Sistemas": "servidor",
    "Redes": "redes",
    "Datos": "datos",
    "Desarrollo": "codigo",
    "Hardware": "hardware",
    "Empleo": "empleo",
    "Incidentes": "alerta",
    "Bastionado": "escudo",
    "Producción": "paquete",
    "Forense": "lupa",
    "Ofensiva": "terminal",
    "Normativa": "balanza",
}
ICONOS_MODULO = {
    "iso": "monitor",
    "redes": "redes",
    "gbd": "datos",
    "lmsgi": "codigo",
    "fh": "hardware",
    "fol": "empleo",
    "sri": "servidor",
    "aso": "terminal",
    "asgbd": "datos",
    "iaw": "web",
}

# Se reemplazan por cada fuente durante el build.
RAIZ = SITIO
DESTINO = SALIDA
ACTUAL: Fuente | None = None
AVISOS_BUILD: list[str] = []
CATEGORIAS: dict[str, str] = {}
ORDEN_CATEGORIAS: list[str] = []

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
    esperados: dict[str, int] = field(default_factory=dict)


def leer_env(ruta: Path) -> dict[str, str]:
    """Lee un archivo KEY=valor como `workspace/rutas.env`."""
    datos: dict[str, str] = {}
    if not ruta.exists():
        raise SystemExit(f"No existe el registro de rutas: {ruta}")
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#") or "=" not in linea:
            continue
        clave, valor = linea.split("=", 1)
        datos[clave.strip()] = valor.strip().strip("'\"")
    return datos


def cargar_config(ruta: Path = CONFIG) -> dict:
    if not ruta.exists():
        raise SystemExit(f"No existe la configuración: {ruta}")
    with ruta.open("rb") as archivo:
        return tomllib.load(archivo)


def resolver_fuentes(config: dict) -> list[Fuente]:
    """Resuelve cada etiqueta a su raíz con `repos.py`; no adivina rutas."""
    registro = config.get("registro", {})
    if not registro.get("rutas_env"):
        raise SystemExit("config/fuentes.toml no declara registro.rutas_env")
    env_ruta = Path(registro["rutas_env"]).expanduser()
    env = leer_env(env_ruta)
    privatenotes = env.get("PRIVATENOTES")
    if not privatenotes:
        raise SystemExit("rutas.env no declara PRIVATENOTES")
    repos_py = Path(privatenotes) / "scripts" / "repos.py"
    if not repos_py.exists():
        raise SystemExit(f"No existe la puerta del registro: {repos_py}")

    fuentes: list[Fuente] = []
    for item in config.get("fuente", []):
        etiqueta = item["etiqueta"]
        proceso = subprocess.run(
            [sys.executable, str(repos_py), "campo", etiqueta, "ruta"],
            capture_output=True,
            text=True,
        )
        if proceso.returncode != 0 or not proceso.stdout.strip():
            raise SystemExit(
                f"No se pudo resolver la fuente {etiqueta!r}: {proceso.stderr.strip()}"
            )
        raiz = Path(proceso.stdout.strip())
        if not raiz.is_dir():
            raise SystemExit(f"La fuente {etiqueta!r} no es un directorio: {raiz}")
        fuentes.append(
            Fuente(
                id=item["id"],
                etiqueta=etiqueta,
                titulo=item.get("titulo", item["id"]),
                estructura=item.get("estructura", "curso"),
                raiz=raiz,
                raices=item.get("raices", []),
                esperados=item.get("esperados", {}),
            )
        )
    if not fuentes:
        raise SystemExit("La configuración no declara ninguna fuente")
    return fuentes


# --------------------------------------------------------------------------
# Utilidades
# --------------------------------------------------------------------------

def url_de(ruta: Path) -> str:
    """Ruta del Markdown a su página, con el prefijo de la fuente."""
    rel = ruta.relative_to(RAIZ).as_posix()
    if rel == "README.md":
        # La portada del curso es el panel; el índice del repositorio va aparte.
        rel = "indice-curso.html"
    elif rel.endswith("/README.md"):
        rel = rel[: -len("README.md")] + "index.html"
    else:
        rel = rel[:-3] + ".html"
    prefijo = f"{ACTUAL.id}/" if ACTUAL else ""
    return prefijo + rel


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


def limpiar_titulo(texto: str) -> str:
    """Quita el prefijo numérico del curso y las referencias «del módulo 50XX»."""
    limpio = re.sub(r"^\d{4}\.\s*", "", texto)
    limpio = re.sub(r"^[A-ZÁÉÍÓÚÜ]{2,}\.\s*", "", limpio)
    limpio = re.sub(r"\s+del\s+m[oó]dulo\s+50\d\d", "", limpio, flags=re.IGNORECASE)
    limpio = re.sub(r"\b50\d\d\b", "", limpio)
    acronimos = r"(?:ASGBD|LMSGI|GBD|SAD|SRI|ASO|IAW|FOL|ISO|FH)"
    limpio = re.sub(rf"\s+(?:de|del)\s+{acronimos}\s*$", "", limpio, flags=re.IGNORECASE)
    limpio = re.sub(rf"^{acronimos}\s*[.·—:-]\s*", "", limpio, flags=re.IGNORECASE)
    limpio = re.sub(r"\s{2,}", " ", limpio).strip(" .·-—:")
    return limpio or texto


def slug(texto: str) -> str:
    limpio = sin_markup(texto).lower()
    limpio = re.sub(r"[^\w\- ]", "", limpio, flags=re.UNICODE)
    return re.sub(r"\s+", "-", limpio).strip("-") or "apartado"


def reescribir_enlace(destino: str, base: Path | None = None) -> str:
    """Ajusta un enlace del Markdown al fichero equivalente dentro del sitio.

    `base` es la carpeta del documento: sirve para comprobar qué existe de
    verdad. Los enlaces que salen del repositorio (puentes al portfolio) se
    resuelven como `file://` para que abran el fichero local real.
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
        return "file://" + str(objetivo)

    if limpia.endswith(".md"):
        if objetivo.is_file():
            nombre = limpia[: -len("README.md")] + "index.html" if limpia.endswith("README.md") else limpia[:-3] + ".html"
            ruta = nombre
        else:
            ruta = limpia
    elif objetivo.is_dir():
        ruta = limpia.rstrip("/") + "/index.html" if (objetivo / "README.md").exists() else limpia.rstrip("/") + "/"
    elif not posixpath.splitext(limpia)[1]:
        ruta = limpia + "/"

    return ruta + ("?" + consulta if interrogacion else "") + ("#" + ancla if almohadilla else "")


def texto_plano(md: str, limite: int = 12000) -> str:
    """Texto del documento para el índice de búsqueda."""
    md = re.sub(r"```.*?```", " ", md, flags=re.S)
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
    en_comentario = False
    for linea in texto.split("\n"):
        if linea.lstrip().startswith(("```", "~~~")):
            en_valla = not en_valla
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

    # -- bloque ------------------------------------------------------------
    def render(self, texto: str) -> str:
        lineas = sin_comentarios(texto.replace("\r\n", "\n")).split("\n")
        return "\n".join(self.bloques(lineas))

    def bloques(self, lineas: list[str]) -> list[str]:
        salida: list[str] = []
        i = 0
        while i < len(lineas):
            linea = lineas[i]
            if not linea.strip():
                i += 1
                continue

            valla = re.match(r"^(\s*)(```|~~~)", linea)
            if valla:
                sangria, cerca = valla.group(1), valla.group(2)
                lenguaje = linea.lstrip()[3:].strip()
                i += 1
                cuerpo = []
                while i < len(lineas) and not lineas[i].lstrip().startswith(cerca):
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
                i += 1
                if nivel == 1 and self.h1 is None:
                    self.h1 = sin_markup(titulo)
                    continue
                ident = self.identificador(titulo)
                if nivel >= 2:
                    self.toc.append((nivel, ident, sin_markup(titulo)))
                salida.append(
                    f'<h{nivel} id="{ident}">'
                    f'<a class="ancla" href="#{ident}" aria-hidden="true">#</a>{self.inline(titulo)}</h{nivel}>'
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
            etiqueta = etiqueta.replace(origen.group(1), reescribir_enlace(origen.group(1), self.base), 1)
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
            return f'<img src="{reescribir_enlace(m.group(2), self.base)}" alt="{alt}" loading="lazy">'

        texto = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)\)", imagen, texto)

        def enlace(m: re.Match) -> str:
            etiqueta, destino = m.group(1), m.group(2)
            href = reescribir_enlace(destino, self.base)
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
        try:
            self.clave = (
                f"{ACTUAL.id}/{ruta.relative_to(RAIZ).as_posix()}"
                if ACTUAL
                else str(ruta)
            )
        except ValueError:
            self.clave = f"{ACTUAL.id}/{ruta.name}" if ACTUAL else str(ruta)


TITULOS: dict[Path, str] = {}


def titulo_de(ruta: Path) -> str:
    if ruta in TITULOS:
        return TITULOS[ruta]
    titulo = ""
    if ruta.is_file():
        for linea in ruta.read_text(encoding="utf-8").splitlines()[:40]:
            if m := RE_CABECERA.match(linea):
                titulo = sin_markup(m.group(2))
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
    piezas = [f'<a href="{relativo("index.html", pagina)}">Formación</a>']
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
    elif ACTUAL and len(rel) > 1:
        clave = rel[1]
    categoria = CATEGORIAS.get(clave) or CATEGORIAS.get(clave.split("-")[0], "")
    if categoria:
        piezas.append(categoria)
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
    ruta = fuente.raiz / "assets" / "iconos" / f"{clave}.svg"
    if ruta.exists():
        return f"{fuente.id}/assets/iconos/{clave}.svg"
    glifo = ICONOS_MODULO.get(clave.split("-")[0], "documento")
    return f"_sitio/iconos/{glifo}.svg"


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
                nombre = limpiar_titulo(hijo.titulo)
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

    for nombre_grupo in fuente.raices:
        grupo = next((h for h in raiz_arbol.hijos if h.ruta.name == nombre_grupo), None)
        if not grupo:
            continue
        for hijo in grupo.hijos:
            if not hijo.es_carpeta:
                continue
            clave = hijo.ruta.name
            nombre = limpiar_titulo(hijo.titulo)
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
        icono = (
            f'<img class="icono-lateral" src="{relativo(nodo.icono, pagina)}" alt="">'
        )
    if not nodo.hijos:
        if not nodo.url:
            return f'<li class="hoja"><span class="enlace">{etiqueta}</span></li>'
        return (
            f'<li class="hoja"><a class="enlace"{marcado} '
            f'href="{relativo(nodo.url, pagina)}">{etiqueta}</a></li>'
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
    if not toc:
        return ""
    piezas = "".join(
        f'<li class="nivel-{nivel}"><a href="#{ident}">{html.escape(texto)}</a></li>'
        for nivel, ident, texto in toc
        if nivel <= 3
    )
    if not piezas:
        return ""
    return f'<nav class="toc" aria-label="En esta página"><p class="toc-titulo">En esta página</p><ul>{piezas}</ul></nav>'


def bloque_paso(anterior: Nodo | None, siguiente: Nodo | None, pagina: str) -> str:
    piezas = []
    for nodo, clase, rotulo in ((anterior, "anterior", "Anterior"), (siguiente, "siguiente", "Siguiente")):
        if nodo and nodo.url:
            piezas.append(
                f'<a class="paso-{clase}" href="{relativo(nodo.url, pagina)}">'
                f'<span>{rotulo}</span><strong>{html.escape(nodo.titulo)}</strong></a>'
            )
    return f'<nav class="pasos" aria-label="Recorrido de estudio">{"".join(piezas)}</nav>'


def tarjeta_modulo(modulo: Modulo, fuente: Fuente, pagina: str) -> str:
    datos = modulo.conteo
    clave_datos = f"{fuente.id}:{modulo.clave}"
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
    else:
        detalle = f"{detalle_apuntes} · {datos['ejercicios']} páginas de ejercicios"
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
                objetivo = Path(ruta[len("file://") :])
                if objetivo.exists():
                    continue
                avisos.append(
                    f"{archivo.relative_to(SALIDA)} → fuera del repo, no existe: {ruta}"
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
        (FUENTE / "estilo.css").read_bytes() + (FUENTE / "app.js").read_bytes()
    ).hexdigest()[:8]

    copiados = 0
    for origen in RAIZ.rglob("*"):
        if not origen.is_file():
            continue
        if not es_contenido(origen) or origen.suffix == ".md":
            continue
        if origen.suffix.lower() not in RECURSOS_PERMITIDOS or origen.name.startswith("."):
            continue
        destino = SALIDA / fuente.id / origen.relative_to(RAIZ)
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origen, destino)
        copiados += 1

    indice_busqueda: list[dict] = []
    total_fuente = sum(modulo.conteo["paginas"] for modulo in modulos)
    orden_fuente = [
        nodo for nodo in orden if nodo.url and nodo.url.startswith(f"{fuente.id}/")
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

    def pie(pagina: str) -> str:
        enlaces: list[str] = []
        if (RAIZ / "entregas.md").exists():
            enlaces.append(
                f'<a href="{relativo(f"{fuente.id}/entregas.html", pagina)}">Entregas</a>'
            )
        if (RAIZ / "campusvdi.md").exists():
            enlaces.append(
                f'<a href="{relativo(f"{fuente.id}/campusvdi.html", pagina)}">Laboratorio</a>'
            )
        return "".join(enlaces)

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
            f'{relativo("_sitio/marca-tile.svg", pagina)}">'
        )
        icono_cabecera = (
            f'<img src="{relativo("_sitio/marca.svg", pagina)}" '
            'alt="" width="28" height="28">'
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
            "{{PIE}}": pie(pagina),
            "{{CURSOS}}": relativo("index.html", pagina),
            "{{FAVICON}}": favicon,
            "{{ICONO_CABECERA}}": icono_cabecera,
            "{{CLASE_CUERPO}}": "",
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
        md = Markdown(ruta.parent)
        texto = ruta.read_text(encoding="utf-8")
        texto = re.sub(
            r"(?mi)^>\s*\*\*módulo.*(?:\n|$)",
            "",
            texto,
        )
        cuerpo = md.render(texto)
        titulo = limpiar_titulo(md.h1 or titulo_nodo)

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
                f"{titulo} · {TITULO_SITIO}",
                cabecera,
                lateral,
                bloque_toc(md.toc),
            ),
        )
        pagina_count += 1
        indice_busqueda.append(
            {
                "t": titulo,
                "u": pagina,
                "m": "",
                "x": texto_plano(texto),
                "tipo": tipo_documento(ruta),
                "fuente": fuente.id,
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
                "codigo": f"{fuente.id}:{modulo.clave}",
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
        "{{FAVICON}}": '<link rel="icon" href="_sitio/marca-tile.svg">',
        "{{ICONO_CABECERA}}": '<img src="_sitio/marca.svg" alt="" width="28" height="28">',
        "{{CLASE_CUERPO}}": "pagina-portada",
    }
    salida = plantilla
    for clave, valor in reemplazos.items():
        salida = salida.replace(clave, valor)
    return salida


def construir_portada(
    resultados: dict[str, dict],
    raiz_global: Nodo,
    recursos: Nodo,
) -> None:
    """Portada única: todos los módulos como items, sin separar por cursos."""
    plantilla = leer_plantilla()
    version = hashlib.sha1(
        (FUENTE / "estilo.css").read_bytes() + (FUENTE / "app.js").read_bytes()
    ).hexdigest()[:8]
    modulos_global: list[dict] = []
    indice_global: list[dict] = []
    pares_modulos: list[tuple[Fuente, Modulo]] = []
    total = 0
    fuentes_meta: list[dict] = []
    categorias: set[str] = set()
    for resultado in resultados.values():
        fuente = resultado["fuente"]
        fuentes_meta.append({"id": fuente.id, "titulo": fuente.titulo})
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
                "codigo": f"{fuente.id}:{modulo.clave}",
                "etiqueta": modulo.etiqueta,
                "titulo": modulo.nombre,
                "grupo": fuente.titulo,
                "url": modulo.nodo.url,
                "paginas": modulo.conteo["paginas"],
                "categoria": modulo.categoria,
                "resumen": modulo.resumen,
            }
        )
        tarjetas.append(tarjeta_modulo(modulo, fuente, "index.html"))

    datos = {
        "modulos": modulos_global,
        "total": total,
        "fuentes": fuentes_meta,
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
    for nombre in ("marca.svg", "marca-tile.svg"):
        shutil.copy2(FUENTE / nombre, SALIDA / "_sitio" / nombre)
    shutil.copytree(FUENTE / "iconos", SALIDA / "_sitio" / "iconos", dirs_exist_ok=True)
    shutil.copy2(SITIO / "LICENSE", SALIDA / "_sitio" / "LICENSE")

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
            f'<img src="_sitio/iconos/{glifo}.svg" alt="" width="16" height="16">'
            if glifo
            else ""
        )
        filtros.append(
            f'<button type="button" data-categoria="{html.escape(categoria)}" '
            f'aria-pressed="false">{icono_filtro}{html.escape(categoria)}</button>'
        )
    enlaces_recursos = "".join(
        f'<a class="enlace-suelto" href="{relativo(nodo.url, "index.html")}">'
        f"{html.escape(nodo.titulo)}</a>"
        for nodo in recursos.hijos
        if nodo.url
    )
    recursos_html = (
        '<section class="panel panel-recursos"><h2>Recursos</h2>'
        f'<div class="suelto">{enlaces_recursos}</div></section>'
        if enlaces_recursos
        else ""
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
            f'<span class="hero-node" style="--a:{indice * angulo:.3f}deg">'
            f'<img src="_sitio/iconos/{glifo}.svg" alt=""></span>'
        )
    contenido = f"""
<header class="portada portada-temario">
  <div class="hero-copy">
    <p class="antetitulo"><span class="status-dot"></span>Contenido IT</p>
    <h1>Formación</h1>
    <p class="hero-role">Apuntes, guías y práctica de <span>sistemas, redes y seguridad</span>.</p>
    <p class="entradilla">Lo que he ido estudiando y documentando: {len(modulos_global)} módulos de sistemas, redes, datos, desarrollo y seguridad.</p>
    <div class="portada-acciones">
      <button class="boton-principal" data-abrir-busqueda>Buscar en el contenido <kbd>Ctrl</kbd><kbd>K</kbd></button>
      <a class="boton-secundario" data-continuar href="index.html">Seguir donde lo dejé</a>
    </div>
    <div class="portada-progreso">
      <span class="barra barra-ancha"><span class="barra-relleno" data-progreso="total"></span></span>
      <span class="porcentaje" data-porcentaje="total">0 %</span>
      <span class="nota-progreso" data-leidas="total">0 de {total} páginas leídas</span>
    </div>
  </div>
  <div class="hero-art" aria-hidden="true">
    <span class="hero-ring"></span>
    <span class="hero-core"><strong>{len(modulos_global)}</strong><span>módulos</span></span>
    {''.join(nodos_hero)}
  </div>
</header>
<section class="metrics" aria-label="Resumen del contenido">
  <div class="metric"><strong>{len(modulos_global)}</strong><span>módulos</span></div>
  <div class="metric"><strong>{len(categorias)}</strong><span>categorías</span></div>
  <div class="metric"><strong>{total}</strong><span>páginas</span></div>
</section>
<div class="chips-filtro" data-filtros aria-label="Filtrar por categoría">{''.join(filtros)}</div>
<section class="rejilla rejilla-contenido">{''.join(tarjetas)}</section>
{recursos_html}
"""
    escribir(
        SALIDA / "index.html",
        pintar_global(
            plantilla,
            version,
            lateral,
            contenido,
            "Visor local del contenido: módulos de sistemas, redes, datos, desarrollo y seguridad.",
        ),
    )


def construir_todo(config: dict | None = None) -> dict[str, dict]:
    global ACTUAL, RAIZ, AVISOS_BUILD, CATEGORIAS, ORDEN_CATEGORIAS
    if config is None:
        config = cargar_config()
    fuentes = resolver_fuentes(config)
    CATEGORIAS = config.get("categorias", {})
    ORDEN_CATEGORIAS = config.get("orden_categorias", [])
    if SALIDA.exists():
        shutil.rmtree(SALIDA)
    SALIDA.mkdir(parents=True)

    raiz_global = Nodo(SITIO, "Formación", "index.html", True)
    raiz_global.fuente_id = ""
    raiz_global.clave = "raiz"
    recursos = Nodo(SITIO, "Recursos", None, True)
    recursos.fuente_id = ""
    recursos.clave = "recursos"
    recursos.icono = "_sitio/iconos/documento.svg"
    categorias_nodos: dict[str, Nodo] = {}
    datos_fuentes: list[tuple[Fuente, list[Modulo]]] = []
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
        for hijo in arbol_fuente.hijos:
            if id(hijo) in ids_modulos:
                continue
            if hijo.es_carpeta and hijo.ruta.name in fuente.raices:
                continue
            if hijo.ruta.name == "assets":
                continue
            recursos.hijos.append(hijo)
        datos_fuentes.append((fuente, modulos))

    def clave_categoria(nombre: str) -> tuple[int, str]:
        if nombre in ORDEN_CATEGORIAS:
            return ORDEN_CATEGORIAS.index(nombre), nombre
        return len(ORDEN_CATEGORIAS), nombre

    for nombre in sorted(categorias_nodos, key=clave_categoria):
        raiz_global.hijos.append(categorias_nodos[nombre])
    if recursos.hijos:
        raiz_global.hijos.append(recursos)

    orden = aplanar(raiz_global, [])
    caminos: dict[str, list[Nodo]] = {}

    def recorrer(nodo: Nodo, camino: list[Nodo]) -> None:
        ruta_nodo = camino + [nodo]
        if nodo.url:
            caminos[nodo.url] = ruta_nodo
        for hijo in nodo.hijos:
            recorrer(hijo, ruta_nodo)

    recorrer(raiz_global, [])

    resultados: dict[str, dict] = {}
    for fuente, modulos in datos_fuentes:
        resultados[fuente.id] = construir_fuente(
            fuente, modulos, raiz_global, orden, caminos
        )

    construir_portada(resultados, raiz_global, recursos)
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
        super().__init__(*args, directory=str(SALIDA), **kwargs)

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
        print("Para pararlo: systemctl --user stop visor-temario", flush=True)
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
                    except Exception as error:  # el servidor sigue en pie
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
