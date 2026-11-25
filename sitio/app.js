/* Interacción del sitio: progreso, búsqueda, navegación y filtros.
   Sin dependencias. Todo el estado vive en localStorage del navegador. */

(() => {
  const cuerpo = document.body;
  const raiz = cuerpo.dataset.raiz || ".";
  const pagina = cuerpo.dataset.pagina || "index.html";
  // La versión del estado invalida claves guardadas con URL de esquemas antiguos.
  const VERSION_ESTADO = "v2";
  const CLAVE_LEIDAS = `temario.${VERSION_ESTADO}.leidas`;
  const CLAVE_ABIERTOS = `temario.${VERSION_ESTADO}.abiertos`;
  const CLAVE_ULTIMA = `temario.${VERSION_ESTADO}.ultima`;

  const $ = (selector, contexto = document) => contexto.querySelector(selector);
  const $$ = (selector, contexto = document) => [...contexto.querySelectorAll(selector)];

  /* ---------------------------------------------------------------- estado */

  const leer = (clave, porDefecto) => {
    try {
      const valor = localStorage.getItem(clave);
      return valor ? JSON.parse(valor) : porDefecto;
    } catch (e) {
      return porDefecto;
    }
  };

  const guardar = (clave, valor) => {
    try {
      localStorage.setItem(clave, JSON.stringify(valor));
    } catch (e) {}
  };

  const leidas = () => leer(CLAVE_LEIDAS, {});
  const estaLeida = (url) => Boolean(leidas()[url]);

  const moduloDeEntrada = (url) => {
    const modulos = window.CURSO?.modulos || [];
    return modulos.find((m) => {
      if (!m.url) return false;
      const base = m.url.replace(/\/?index\.html$/, "/");
      return url === m.url || (base !== "/" && url.startsWith(base));
    });
  };

  const moduloDe = (url) => moduloDeEntrada(url)?.codigo || "";

  /* -------------------------------------------------------------- progreso */

  function pintarProgreso() {
    const marcas = leidas();
    const totales = window.CURSO?.total || 0;
    // Solo cuentan las páginas de módulo: son las que suma el total del temario.
    const totalLeidas = Object.keys(marcas).filter((url) => moduloDe(url)).length;
    const porcentaje = (parte, todo) => (todo ? Math.round((parte / todo) * 100) : 0);

    $$("[data-progreso]").forEach((barra) => {
      const clave = barra.dataset.progreso;
      let parte = 0;
      let todo = 0;
      if (clave === "total") {
        parte = totalLeidas;
        todo = totales;
      } else {
        const modulo = (window.CURSO?.modulos || []).find((m) => m.codigo === clave);
        todo = modulo?.paginas || 0;
        parte = Object.keys(marcas).filter((url) => moduloDe(url) === clave).length;
      }
      barra.style.transform = `scaleX(${porcentaje(parte, todo) / 100})`;
    });

    $$("[data-porcentaje]").forEach((nodo) => {
      const clave = nodo.dataset.porcentaje;
      const modulo = (window.CURSO?.modulos || []).find((m) => m.codigo === clave);
      const todo = clave === "total" ? totales : modulo?.paginas || 0;
      const parte =
        clave === "total"
          ? totalLeidas
          : Object.keys(marcas).filter((url) => moduloDe(url) === clave).length;
      nodo.textContent = `${porcentaje(parte, todo)} %`;
    });

    $$("[data-leidas]").forEach((nodo) => {
      const clave = nodo.dataset.leidas;
      const modulo = (window.CURSO?.modulos || []).find((m) => m.codigo === clave);
      const todo = clave === "total" ? totales : modulo?.paginas || 0;
      const parte =
        clave === "total"
          ? totalLeidas
          : Object.keys(marcas).filter((url) => moduloDe(url) === clave).length;
      nodo.textContent =
        clave === "total" ? `${parte} de ${todo} páginas leídas` : `${parte} de ${todo}`;
    });

    const mini = $("[data-leidas-mini]");
    if (mini) mini.textContent = `${porcentaje(totalLeidas, totales)} %`;
  }

  function marcarLeido() {
    const boton = $("[data-leido]");
    if (!boton) return;
    const url = boton.dataset.leido;
    const aplicar = () => {
      const marcas = leidas();
      const activo = Boolean(marcas[url]);
      boton.setAttribute("aria-pressed", String(activo));
      boton.lastChild.textContent = activo ? "Leído" : "Marcar como leído";
      pintarProgreso();
    };
    aplicar();
    boton.addEventListener("click", () => {
      const marcas = leidas();
      if (marcas[url]) delete marcas[url];
      else marcas[url] = Date.now();
      guardar(CLAVE_LEIDAS, marcas);
      aplicar();
    });
  }

  /* ------------------------------------------------------------ navegación */

  function navegacion() {
    const lateral = $("#lateral");
    const botonTemario = $("[data-abrir-temario]");
    const abiertos = leer(CLAVE_ABIERTOS, {});
    const detalles = $$(".lateral details");

    detalles.forEach((detalle) => {
      const clave =
        detalle.dataset.clave || detalle.querySelector("summary")?.textContent?.trim() || "";
      const dentro = Boolean(detalle.querySelector('[aria-current="page"]'));
      if (!dentro && clave && Object.prototype.hasOwnProperty.call(abiertos, clave)) {
        detalle.open = abiertos[clave];
      }
      detalle.addEventListener("toggle", () => {
        if (!clave) return;
        abiertos[clave] = detalle.open;
        guardar(CLAVE_ABIERTOS, abiertos);
      });
    });

    const botonExpandir = $("[data-arbol-expandir]");
    const botonComprimir = $("[data-arbol-comprimir]");
    if (botonExpandir && botonComprimir && detalles.length) {
      botonExpandir.addEventListener("click", () => {
        detalles.forEach((detalle) => {
          detalle.open = true;
        });
      });
      botonComprimir.addEventListener("click", () => {
        detalles.forEach((detalle) => {
          detalle.open = false;
        });
      });
    }

    if (botonTemario && lateral) {
      // El temario es un cajón aparte: se abre desde el menú principal, que
      // se cierra antes para no dejar dos paneles superpuestos.
      const plegarMenu = (devolverFoco) => {
        lateral.classList.remove("abierto");
        document.body.classList.remove("menu-abierto");
        botonTemario.setAttribute("aria-expanded", "false");
        if (devolverFoco) {
          const toggle = $(".menu-toggle");
          const visible = toggle && getComputedStyle(toggle).display !== "none";
          (visible ? toggle : botonTemario).focus();
        }
      };
      botonTemario.addEventListener("click", () => {
        const menuPrincipal = $(".menu-toggle");
        if (menuPrincipal?.getAttribute("aria-expanded") === "true") menuPrincipal.click();
        const abierto = !lateral.classList.contains("abierto");
        lateral.classList.toggle("abierto", abierto);
        document.body.classList.toggle("menu-abierto", abierto);
        botonTemario.setAttribute("aria-expanded", String(abierto));
        if (abierto) lateral.querySelector("a, summary, button")?.focus();
      });
      // El menú principal queda por debajo del overlay del cajón: si se abre,
      // el cajón se cierra para que el primer clic no se pierda.
      const menuPrincipal = $(".menu-toggle");
      menuPrincipal?.addEventListener("click", () => {
        if (menuPrincipal.getAttribute("aria-expanded") === "true") plegarMenu();
      });
      document.addEventListener("click", (evento) => {
        if (!lateral.classList.contains("abierto")) return;
        if (lateral.contains(evento.target) || botonTemario.contains(evento.target)) return;
        plegarMenu();
      });
      document.addEventListener("keydown", (evento) => {
        if (evento.key === "Escape" && lateral.classList.contains("abierto")) {
          plegarMenu(true);
        }
      });
      window.addEventListener("resize", () => {
        if (window.innerWidth > 940 && lateral.classList.contains("abierto")) plegarMenu();
      });
    }

    const continuar = $("[data-continuar]");
    if (continuar) {
      const ultima = leer(CLAVE_ULTIMA, "");
      if (ultima) {
        continuar.href = `${raiz}/${ultima}`;
      } else {
        continuar.hidden = true;
      }
    }

    if (pagina !== "index.html") guardar(CLAVE_ULTIMA, pagina);
  }

  /* -------------------------------------------------------------- lectura */

  function lectura() {
    const barra = $(".barra-lectura span");
    if (barra) {
      const actualizar = () => {
        const doc = document.scrollingElement || document.documentElement;
        const alto = doc.scrollHeight - doc.clientHeight;
        const avance = alto > 0 ? Math.min(1, doc.scrollTop / alto) : 0;
        barra.style.transform = `scaleX(${avance})`;
      };
      actualizar();
      window.addEventListener("scroll", actualizar, { passive: true });
      window.addEventListener("resize", actualizar);
    }

    const enlaces = $$(".toc a");
    const altoCabecera =
      parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--header-h")) || 78;
    if (enlaces.length && "IntersectionObserver" in window) {
      const mapa = new Map();
      enlaces.forEach((enlace) => {
        const destino = document.getElementById(decodeURIComponent(enlace.hash.slice(1)));
        if (destino) mapa.set(destino, enlace);
      });
      const observador = new IntersectionObserver(
        (entradas) => {
          entradas.forEach((entrada) => {
            if (!entrada.isIntersecting) return;
            enlaces.forEach((e) => e.parentElement.classList.remove("activo"));
            const enlace = mapa.get(entrada.target);
            if (enlace) enlace.parentElement.classList.add("activo");
          });
        },
        {
          rootMargin: `-${altoCabecera + 8}px 0px -75% 0px`,
          threshold: 0,
        }
      );
      mapa.forEach((_, destino) => observador.observe(destino));
    }

    const aviso = document.createElement("p");
    aviso.className = "aviso-copia";
    document.body.appendChild(aviso);
    $$(".ancla").forEach((ancla) => {
      ancla.addEventListener("click", async (evento) => {
        evento.preventDefault();
        const url = new URL(window.location.href);
        url.hash = ancla.hash.slice(1);
        history.replaceState(null, "", url);
        try {
          await navigator.clipboard.writeText(url.toString());
          aviso.textContent = "Enlace copiado";
        } catch (e) {
          aviso.textContent = url.hash;
        }
        aviso.classList.add("visible");
        setTimeout(() => aviso.classList.remove("visible"), 1400);
      });
    });
  }

  /* -------------------------------------------------------------- búsqueda */

  const normalizar = (texto) =>
    (texto || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase();

  const escapar = (texto) =>
    texto.replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

  function rutaLegible(url) {
    const partes = url
      .replace(/\/?index\.html$/, "")
      .replace(/\.html$/, "")
      .split("/")
      .filter(Boolean);
    const modulo = moduloDeEntrada(url);
    const trozos = [];
    if (modulo) trozos.push(modulo.etiqueta || modulo.titulo || modulo.codigo);
    else if (partes.length) {
      const primera = partes[0];
      trozos.push(primera.charAt(0).toUpperCase() + primera.slice(1));
    }
    if (partes.includes("teoria")) trozos.push("Teoría");
    else if (partes.includes("ejercicios")) trozos.push("Ejercicios");
    return trozos.join(" · ") || "General";
  }

  function cargarIndice() {
    if (window.INDICE) return Promise.resolve(window.INDICE);
    return new Promise((resolver) => {
      const etiqueta = document.createElement("script");
      etiqueta.src = `${raiz}/_sitio/indice.js`;
      etiqueta.onload = () => resolver(window.INDICE || []);
      etiqueta.onerror = () => resolver([]);
      document.head.appendChild(etiqueta);
    });
  }

  function búsqueda() {
    const paleta = $("#paleta");
    if (!paleta) return;
    const campo = $("#paleta-campo");
    const lista = $("#paleta-resultados");
    const vacio = $("#paleta-vacio");
    let indice = null;
    let elegido = -1;

    const abrir = async () => {
      // El buscador no debe quedar detrás de un menú móvil abierto.
      const menuPrincipal = $(".menu-toggle");
      if (menuPrincipal?.getAttribute("aria-expanded") === "true") menuPrincipal.click();
      const temario = $("[data-abrir-temario]");
      if (temario?.getAttribute("aria-expanded") === "true") temario.click();
      paleta.showModal();
      campo.value = "";
      campo.focus();
      if (!indice) {
        vacio.hidden = false;
        vacio.textContent = "Cargando el índice…";
        indice = await cargarIndice();
        vacio.textContent = "";
      }
      // Al terminar de cargar se busca lo que ya se haya escrito.
      buscar(campo.value);
    };

    const cerrar = () => paleta.close();

    function buscar(consulta) {
      const terminos = normalizar(consulta).split(/\s+/).filter(Boolean);
      lista.innerHTML = "";
      elegido = -1;
      if (!indice) return;
      if (!indice.length) {
        vacio.hidden = false;
        vacio.textContent = "No hay índice de búsqueda en este sitio.";
        return;
      }
      if (!terminos.length) {
        vacio.hidden = false;
        const totalModulos = window.CURSO?.modulos?.length || 0;
        vacio.textContent = `Escribe para buscar en los ${totalModulos} módulos. Los resultados enlazan al documento exacto.`;
        return;
      }

      const resultados = [];
      for (const entrada of indice) {
        const titulo = normalizar(entrada.t);
        const texto = normalizar(entrada.x);
        let puntuacion = 0;
        let valido = true;
        for (const termino of terminos) {
          const enTitulo = titulo.includes(termino);
          const enTexto = texto.includes(termino);
          if (!enTitulo && !enTexto) {
            valido = false;
            break;
          }
          puntuacion += enTitulo ? 12 : 0;
          puntuacion += titulo.startsWith(termino) ? 6 : 0;
          if (enTexto) puntuacion += 1;
        }
        if (valido) resultados.push({ entrada, puntuacion });
      }

      resultados.sort((a, b) => b.puntuacion - a.puntuacion || a.entrada.t.localeCompare(b.entrada.t));
      const recorte = resultados.slice(0, 40);

      if (!recorte.length) {
        vacio.hidden = false;
        vacio.textContent = `Sin resultados para «${consulta}». Prueba con una palabra suelta.`;
        return;
      }
      vacio.hidden = true;

      recorte.forEach(({ entrada }) => {
        const original = entrada.x;
        const textoNormalizado = normalizar(original);
        // El fragmento no repite el título: empieza después de él si coincide.
        const comienzo = textoNormalizado.startsWith(normalizar(entrada.t)) ? entrada.t.length : 0;
        const posicionTexto = Math.max(comienzo, textoNormalizado.indexOf(terminos[0]));
        let fragmento = original.slice(Math.max(0, posicionTexto - 55), posicionTexto + 95);
        if (posicionTexto > 55) fragmento = "…" + fragmento;
        if (posicionTexto >= 0 && original.length > posicionTexto + 95) fragmento += "…";
        const marcado = escapar(fragmento).replace(
          new RegExp(`(${terminos.map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|")})`, "gi"),
          "<mark>$1</mark>"
        );
        const item = document.createElement("li");
        item.innerHTML = `<a href="${raiz}/${entrada.u}">
          <span class="ruta">${escapar(rutaLegible(entrada.u))}</span>
          <span class="titulo">${escapar(entrada.t)}</span>
          <span class="fragmento">${posicionTexto >= 0 ? marcado : ""}</span>
        </a>`;
        lista.appendChild(item);
      });
    }

    function mover(paso) {
      const enlaces = $$("a", lista);
      if (!enlaces.length) return;
      elegido = (elegido + paso + enlaces.length) % enlaces.length;
      enlaces.forEach((a) => a.classList.remove("elegido"));
      enlaces[elegido].classList.add("elegido");
      enlaces[elegido].scrollIntoView({ block: "nearest" });
    }

    $$("[data-abrir-busqueda]").forEach((boton) => boton.addEventListener("click", abrir));
    campo.addEventListener("input", () => buscar(campo.value));
    paleta.addEventListener("click", (evento) => {
      if (evento.target === paleta) cerrar();
    });
    campo.addEventListener("keydown", (evento) => {
      if (evento.key === "ArrowDown") {
        evento.preventDefault();
        mover(1);
      } else if (evento.key === "ArrowUp") {
        evento.preventDefault();
        mover(-1);
      } else if (evento.key === "Enter") {
        const enlace = $$("a", lista)[elegido] || $$("a", lista)[0];
        if (enlace) window.location.href = enlace.href;
      }
    });

    document.addEventListener("keydown", (evento) => {
      const escribiendo = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName);
      if ((evento.ctrlKey || evento.metaKey) && evento.key.toLowerCase() === "k") {
        evento.preventDefault();
        if (paleta.open) cerrar();
        else abrir();
      } else if (evento.key === "/" && !escribiendo && !paleta.open) {
        evento.preventDefault();
        abrir();
      } else if (evento.key === "Escape" && paleta.open) {
        cerrar();
      }
    });
  }

  /* --------------------------------------------------------------- filtros */

  function filtros() {
    const contenedor = $("[data-filtros]");
    if (!contenedor) return;
    const tarjetas = $$(".rejilla-contenido .tarjeta");
    contenedor.querySelectorAll("button").forEach((boton) => {
      boton.addEventListener("click", () => {
        const categoria = boton.dataset.categoria || "todas";
        contenedor.querySelectorAll("button").forEach((otro) => {
          otro.setAttribute("aria-pressed", String(otro === boton));
        });
        tarjetas.forEach((tarjeta) => {
          tarjeta.hidden = categoria !== "todas" && tarjeta.dataset.categoria !== categoria;
        });
      });
    });
  }

  /* ---------------------------------------------------------------- inicio */

  document.addEventListener("DOMContentLoaded", () => {
    pintarProgreso();
    marcarLeido();
    navegacion();
    lectura();
    búsqueda();
    filtros();
  });

  if (document.readyState !== "loading") {
    pintarProgreso();
  }
})();
