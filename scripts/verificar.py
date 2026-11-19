#!/usr/bin/env python3
"""Comprueba el visor construido: conteos, búsqueda, dist y reproducibilidad."""

from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

import visor  # noqa: E402

# Glifos del visor que no salen de las tablas: el de reserva y el de la lupa.
_ICONOS_FIJOS = {"documento", "lupa"}


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFD", texto or "")
    return "".join(c for c in texto if unicodedata.category(c) != "Mn").lower()


def huella_dist() -> str:
    resumen = hashlib.sha256()
    for ruta in sorted(visor.SALIDA.rglob("*")):
        if not ruta.is_file():
            continue
        resumen.update(ruta.relative_to(visor.SALIDA).as_posix().encode())
        resumen.update(b"\0")
        resumen.update(ruta.read_bytes())
    return resumen.hexdigest()


def revisar_iconos() -> list[str]:
    """Cada icono existe, no se repite, se usa y suelta glifo para el árbol."""
    errores: list[str] = []
    claves: dict[str, list[str]] = {}
    for nombre, mapa in (
        ("categoría", visor.ICONOS_CATEGORIA),
        ("módulo", visor.ICONOS_MODULO),
    ):
        vistos: dict[str, str] = {}
        for clave, icono in mapa.items():
            articulo = "la" if nombre == "categoría" else "el"
            claves.setdefault(icono, []).append(f"{articulo} {nombre} «{clave}»")
            if icono in vistos:
                errores.append(
                    f"icono de {nombre} «{icono}» repetido en "
                    f"«{vistos[icono]}» y «{clave}»"
                )
            vistos[icono] = clave
    # Glifos que no salen de las tablas: el de reserva y el de la lupa.
    usados = set(claves) | _ICONOS_FIJOS
    for icono in sorted(usados):
        ruta = visor.SITIO / "sitio" / "iconos" / f"{icono}.svg"
        quien = " y ".join(claves.get(icono, ["el glifo de reserva o la lupa"]))
        if not ruta.is_file():
            errores.append(f"falta sitio/iconos/{icono}.svg para {quien}")
        elif not visor._dibujo(ruta):
            errores.append(
                f"sitio/iconos/{icono}.svg no suelta glifo para el árbol, "
                f"que es lo que usa {quien}"
            )
    for ruta in sorted((visor.SITIO / "sitio" / "iconos").glob("*.svg")):
        if ruta.stem not in usados:
            errores.append(f"icono sin uso: sitio/iconos/{ruta.name}")
    return errores


def buscar(indice: list[dict], consulta: str) -> list[dict]:
    terminos = [t for t in normalizar(consulta).split() if t]
    encontrados = []
    for entrada in indice:
        texto = normalizar(entrada["t"] + " " + entrada["x"])
        if all(termino in texto for termino in terminos):
            encontrados.append(entrada)
    return encontrados


def main() -> int:
    config = visor.cargar_config()
    resumen = visor.construir_todo(config)
    errores: list[str] = []
    if visor.AVISOS_BUILD:
        errores.extend(visor.AVISOS_BUILD)
    errores.extend(revisar_iconos())
    primera_huella = huella_dist()

    for identificador, resultado in resumen.items():
        fuente = resultado["fuente"]
        modulos = resultado["modulos"]
        conteos = {
            "modulos": len(modulos),
            "apuntes": sum(modulo.conteo["apuntes"] for modulo in modulos),
            "guias": sum(modulo.conteo["guias"] for modulo in modulos),
        }
        for clave, esperado in fuente.esperados.items():
            if conteos.get(clave) != esperado:
                errores.append(
                    f"{identificador}: {clave}={conteos.get(clave)}, esperado {esperado}"
                )
        print(
            f"{identificador}: {conteos['modulos']} módulos, "
            f"{conteos['apuntes']} apuntes, {conteos['guias']} guías"
        )

        for md in sorted(fuente.raiz.rglob("*.md")):
            texto = md.read_text(encoding="utf-8")
            ruta_rel = md.relative_to(fuente.raiz)
            if re.search(r"campus\s*mvp", texto, flags=re.I):
                errores.append(f"{identificador}: cita al proveedor del curso en {ruta_rel}")
            if re.search(r"^> \*\*(Curso|Fuente):\*\*", texto, flags=re.M):
                errores.append(f"{identificador}: cabecera de curso en {ruta_rel}")
            if re.search(r"<!--\s*pág\.", texto):
                errores.append(f"{identificador}: marca de página del PDF en {ruta_rel}")

        tipos = (
            ("apunte", "guia")
            if any(modulo.conteo["guias"] for modulo in modulos)
            else ("apunte",)
        )
        for tipo in tipos:
            candidatos = [e for e in resultado["indice"] if e.get("tipo") == tipo]
            if not candidatos:
                errores.append(f"{identificador}: no hay ningún {tipo} en la búsqueda")
                continue
            entrada = candidatos[0]
            palabras = [p for p in entrada["t"].split() if len(p) >= 4]
            consulta = palabras[0] if palabras else entrada["t"]
            if not buscar(resultado["indice"], consulta):
                errores.append(
                    f"{identificador}: la búsqueda no encuentra el {tipo} «{entrada['t']}»"
                )
            else:
                print(f"  búsqueda {tipo}: «{consulta}» → {entrada['t']}")

        if (visor.SALIDA / identificador).exists():
            errores.append(f"{identificador}: la URL conserva el id de la fuente")
        for raiz in fuente.raices:
            if (visor.SALIDA / raiz).exists():
                errores.append(f"{identificador}: la URL conserva la carpeta {raiz}")
        for modulo in resultado["modulos"]:
            if not modulo.nodo.url:
                errores.append(f"{identificador}: {modulo.nombre} no tiene página")
                continue
            if modulo.nodo.url.split("/", 1)[0] != visor.slug_url(modulo.nombre):
                errores.append(
                    f"{identificador}: la URL de {modulo.nombre} no es su nombre"
                )
            pagina = visor.SALIDA / modulo.nodo.url
            if not pagina.exists():
                errores.append(f"{identificador}: falta la página de {modulo.nombre}")
                continue
            html_modulo = pagina.read_text(encoding="utf-8")
            for titulo in re.findall(r"<h1>(.*?)</h1>", html_modulo):
                visible = re.sub(r"<[^>]+>", "", titulo)
                if re.search(r"\b50\d\d\b", visible):
                    errores.append(
                        f"{identificador}: prefijo de curso visible en «{visible}»"
                    )
        for entrada in resultado["indice"]:
            if re.search(r"\b50\d\d\b", entrada["t"]):
                errores.append(
                    f"{identificador}: prefijo de curso en el título «{entrada['t']}»"
                )

    portada = (visor.SALIDA / "index.html").read_text(encoding="utf-8")
    for titulo in re.findall(r'<span class="tarjeta-titulo">(.*?)</span>', portada):
        if re.search(r"\b50\d\d\b", titulo):
            errores.append(f"portada: prefijo de curso visible en «{titulo}»")

    for relativa in (
        "index.html",
        "_sitio/indice.js",
        "_sitio/datos.js",
        "_sitio/estilo.css",
        "_sitio/app.js",
        "_sitio/LICENSE",
        "_identidad/identidad.css",
        "_identidad/marca-tile.svg",
    ):
        if not (visor.SALIDA / relativa).exists():
            errores.append(f"falta dist/{relativa}")

    # La construcción es atómica: no deja restos del intercambio.
    for resto in ("dist.nuevo", "dist.viejo"):
        if (visor.SITIO / resto).exists():
            errores.append(f"quedó {resto}/ tras la construcción")

    # El paquete consumido no se retoca: se comprueban sus huellas.
    paquete = visor.SITIO / "_identidad"
    sumas = subprocess.run(
        ["sha256sum", "-c", "--quiet", "SHA256SUMS"],
        cwd=paquete,
        capture_output=True,
        text=True,
    )
    if sumas.returncode != 0:
        detalle = (sumas.stdout + sumas.stderr).strip().splitlines()
        errores.append(
            "el paquete _identidad/ no coincide con sus huellas: "
            + (detalle[0] if detalle else "sin detalle")
        )

    # Reproducibilidad: el segundo build debe dejar el mismo contenido.
    visor.construir_todo(config)
    if huella_dist() != primera_huella:
        errores.append("el segundo build no es idéntico al primero")

    # `dist/` no se versiona.
    git = shutil.which("git")
    if git and (visor.SITIO / ".git").exists():
        ignorado = subprocess.run(
            [git, "-C", str(visor.SITIO), "check-ignore", "-q", "dist/index.html"],
            capture_output=True,
        )
        if ignorado.returncode != 0:
            errores.append("dist/index.html no está ignorado por git")
        seguidos = subprocess.run(
            [git, "-C", str(visor.SITIO), "ls-files", "dist"],
            capture_output=True,
            text=True,
        )
        if seguidos.stdout.strip():
            errores.append("hay archivos de dist/ versionados")
    else:
        print("git no disponible o repositorio sin inicializar: no se comprueba dist/")

    if errores:
        print("\nFallos:", file=sys.stderr)
        for error in errores:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print("OK: conteos, búsqueda, dist reproducible y dist ignorado")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
