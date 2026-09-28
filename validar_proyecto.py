# -*- coding: utf-8 -*-
"""Validador del proyecto txopo.

Comprueba lo que se puede comprobar sin navegador:
  - CSS: llaves equilibradas, que las clases usadas en el HTML existan, y que
    los archivos de imagen referenciados existan de verdad.
  - HTML: etiquetas criticas, atributos de accesibilidad, dominio unificado.
No toca las subwebs historicas.
"""
import io
import os
import re
import sys

RAIZ = r"D:\Proyectos VSC\txopo"
CSS = os.path.join(RAIZ, "assets", "css", "design-system.css")
HTML = os.path.join(RAIZ, "index.html")
JS = os.path.join(RAIZ, "assets", "js", "app.js")

fallos = []
avisos = []


def leer(p):
    return io.open(p, encoding="utf-8").read()


css = leer(CSS)
html = leer(HTML)
js = leer(JS)

# ---- 1) CSS: llaves equilibradas -----------------------------------------
sin_comentarios = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
ab, ce = sin_comentarios.count("{"), sin_comentarios.count("}")
if ab != ce:
    fallos.append("CSS: llaves descuadradas (%d '{' contra %d '}')" % (ab, ce))
else:
    print("[OK] CSS: %d bloques con las llaves equilibradas" % ab)

# ---- 2) Las imagenes referenciadas en el CSS existen ----------------------
faltan = []
for ruta in set(re.findall(r"url\(['\"]([^'\"]+)['\"]\)", css)):
    if ruta.startswith(("http:", "https:", "data:")):
        continue
    real = os.path.normpath(os.path.join(os.path.dirname(CSS), ruta))
    if not os.path.exists(real):
        faltan.append(ruta)
if faltan:
    fallos.append("CSS: estas imagenes no existen -> %s" % ", ".join(sorted(faltan)))
else:
    print("[OK] CSS: todas las imagenes referenciadas existen")

# ---- 3) Las clases criticas del HTML tienen regla en el CSS ---------------
CRITICAS = ["honeypot", "skip-link", "preloader", "featured-card", "journey-card",
            "archive-grid", "contact-form", "hero-image-frame", "nav-toggle",
            "site-nav", "scroll-top-btn", "form-feedback", "stat-strip"]
sin_regla = [c for c in CRITICAS if not re.search(r"\.%s[\s,{:.]" % re.escape(c), css)]
if sin_regla:
    fallos.append("CSS: clases usadas en el HTML SIN regla -> %s" % ", ".join(sin_regla))
else:
    print("[OK] CSS: las %d clases criticas tienen regla" % len(CRITICAS))

# ---- 4) Accesibilidad y SEO en el HTML -----------------------------------
comprobaciones = [
    ("viewport", r'<meta name="viewport"', True),
    ("lang en <html>", r'<html lang="es"', True),
    ("enlace saltar al contenido", r'class="skip-link"', True),
    ("canonical a lovestoblog", r'rel="canonical" href="https://txopo\.lovestoblog\.com/"', True),
    ("campo CSRF", r'name="csrf_token"', True),
    ("form apunta a contact.php", r'action="contact\.php"', True),
    ("honeypot con tabindex -1", r'id="website"[^>]*tabindex="-1"', True),
    ("preload del WebP", r'rel="preload"[^>]*hero_urdaibai\.webp', True),
    ("NO queda preload del PNG", r'rel="preload"[^>]*hero_urdaibai\.png', False),
    ("NO queda canonical a pages.dev", r'rel="canonical"[^>]*pages\.dev', False),
    ("NO queda og:url a pages.dev", r'property="og:url"[^>]*pages\.dev', False),
    ("nav-toggle con type=button", r'<button type="button" class="nav-toggle"', True),
    ("nav-toggle con aria-controls", r'class="nav-toggle"[^>]*aria-controls="siteNav"', True),
    ("chips de filtro con aria-pressed", r'class="chip active" data-filter="all" aria-pressed="true"', True),
    ("results-summary con aria-live", r'id="resultsSummary"[^>]*aria-live="polite"', True),
    ("boton submit con id submitBtn", r'id="submitBtn"', True),
    ("fuentes con pesos podados (sin 500)", r'fonts\.googleapis\.com[^"]*Cormorant\+Garamond:wght@400;700&family=Manrope:wght@400;600;700;800', True),
    ("NO quedan pesos de fuente sin usar (500)", r'family=[^"]*wght@[^"]*500', False),
    ("hoja de fuentes sin bloquear el render", r'rel="preload" as="style"[^>]*fonts\.googleapis', True),
    ("noscript de respaldo para fuentes", r'<noscript>[^<]*<link rel="stylesheet"[^>]*fonts\.googleapis', True),
]
for nombre, patron, debe_estar in comprobaciones:
    hay = bool(re.search(patron, html))
    if hay != debe_estar:
        fallos.append("HTML: fallo en '%s'" % nombre)
    else:
        print("[OK] HTML: %s" % nombre)

# ---- 5) Imagenes del HTML con alt ----------------------------------------
sin_alt = [t for t in re.findall(r"<img\b[^>]*>", html) if "alt=" not in t]
if sin_alt:
    fallos.append("HTML: %d <img> sin alt" % len(sin_alt))
else:
    print("[OK] HTML: todas las <img> estaticas llevan alt")

# ---- 6) El JS genera <img> con alt ---------------------------------------
if re.search(r"<img src=[^>]*alt=", js):
    print("[OK] JS: las tarjetas generadas incluyen alt")
else:
    avisos.append("JS: revisar que las <img> generadas lleven alt")

# ---- 7) El honeypot no debe ser visible ----------------------------------
if re.search(r"\.honeypot\s*\{[^}]*position:\s*absolute", css, re.S):
    print("[OK] CSS: el honeypot esta fuera de pantalla")
else:
    fallos.append("CSS: el honeypot NO se esta ocultando -> se ve en la pagina")

# ---- 8) Red de seguridad del preloader -----------------------------------
if "preloaderFailsafe" in css and css.count("preloaderFailsafe") >= 3:
    print("[OK] CSS: el preloader tiene red de seguridad sin depender del JS")
else:
    fallos.append("CSS: falta la red de seguridad del preloader")

# ---- 9) Contraste AA: los valores corregidos siguen en su sitio ----------
if "--accent-text: #127058" in css:
    print("[OK] CSS: token --accent-text presente (texto acento accesible)")
else:
    fallos.append("CSS: falta el token --accent-text (#127058)")
if "--text-soft: #52706a" in css:
    print("[OK] CSS: --text-soft es el valor accesible (#52706a)")
else:
    fallos.append("CSS: --text-soft volvio al valor que no pasa AA (#6a8783)")
if "linear-gradient(135deg, #17795f 0%, var(--accent-deep) 130%)" in css:
    print("[OK] CSS: boton primario con gradiente accesible")
else:
    fallos.append("CSS: el boton primario volvio al gradiente que no pasa AA")
if re.search(r"\.journey-arrow \{[^}]*var\(--accent-text\)", css, re.S):
    print("[OK] CSS: journey-arrow usa --accent-text")
else:
    fallos.append("CSS: journey-arrow no usa --accent-text")

# ---- 10) El JS anuncia los estados clave ---------------------------------
if "setAttribute('aria-label', text)" in js:
    print("[OK] JS: el typewriter fija aria-label con el texto completo")
else:
    fallos.append("JS: el typewriter borra el h1 sin aria-label")
if js.count('aria-pressed'):
    print("[OK] JS: los chips sincronizan aria-pressed")
else:
    fallos.append("JS: los chips no sincronizan aria-pressed")

print()
for a in avisos:
    print("[AVISO] " + a)
if fallos:
    print()
    print("FALLOS:")
    for f in fallos:
        print("  ! " + f)
    sys.exit(1)
print("TODO CORRECTO.")
