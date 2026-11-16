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

        for tipo in ("apunte", "guia"):
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

        base = visor.SALIDA / identificador
        if not base.is_dir():
            errores.append(f"{identificador}: no se generó su carpeta")
        for modulo in resultado["modulos"]:
            if not modulo.nodo.url:
                errores.append(f"{identificador}: {modulo.nombre} no tiene página")
                continue
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
    ):
        if not (visor.SALIDA / relativa).exists():
            errores.append(f"falta dist/{relativa}")

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
