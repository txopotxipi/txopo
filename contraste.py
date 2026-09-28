# -*- coding: utf-8 -*-
"""Calcula el contraste WCAG 2.1 de los pares de color usados de verdad en
la portada de txopo.

Umbrales WCAG 2.1 nivel AA:
    texto normal ........ >= 4.5:1
    texto grande ........ >= 3.0:1  (>=24px, o >=18.66px en negrita)
    iconos y UI ......... >= 3.0:1
    logotipos ........... sin requisito (exencion WCAG 1.4.3)

Los fondos con canal alfa se componen primero sobre su fondo real, porque el
contraste se mide sobre el color EFECTIVO que ve el usuario, no sobre el CSS.
"""

# ---------------------------------------------------------------- utilidades


def lin(c):
    """Canal sRGB 0-255 -> luminancia lineal."""
    c = c / 255.0
    if c <= 0.04045:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def lum(rgb):
    """Luminancia relativa WCAG de un color RGB."""
    return (0.2126 * lin(rgb[0])
            + 0.7152 * lin(rgb[1])
            + 0.0722 * lin(rgb[2]))


def contraste(a, b):
    """Ratio de contraste entre dos colores RGB."""
    l1, l2 = sorted([lum(a), lum(b)], reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def hex_rgb(texto):
    texto = texto.strip().lstrip("#")
    return [int(texto[0:2], 16), int(texto[2:4], 16), int(texto[4:6], 16)]


def mezclar(sobre, alpha, encima):
    """Compone 'encima' con opacidad alpha sobre 'sobre' (ambos RGB)."""
    return [sobre[i] * (1 - alpha) + encima[i] * alpha for i in range(3)]


def nombre(color):
    return "#%02x%02x%02x" % tuple(int(round(v)) for v in color)


# ------------------------------------------------------------------ paleta

BG = hex_rgb("f4f0e7")           # --bg
BG_SOFT = hex_rgb("fcfaf5")      # --bg-soft
BLANCO = [255, 255, 255]
TEXT = hex_rgb("153633")         # --text
TEXT_MUTED = hex_rgb("4f6f6b")   # --text-muted
TEXT_SOFT = hex_rgb("52706a")    # --text-soft (ajustado 2026-09-28 por AA)
ACCENT = hex_rgb("1e8b71")       # --accent
ACCENT_TEXT = hex_rgb("127058")  # --accent-text (token nuevo para texto)
ACCENT_DEEP = hex_rgb("0f5d4d")  # --accent-deep
ACCENT_WARM = hex_rgb("ff8a63")  # --accent-warm (cobre)
BOTON_LIGHT = hex_rgb("17795f")        # boton primario: extremo mas claro
CARD_TEXT = hex_rgb("f7fffb")          # texto sobre las tarjetas de foto

# Superficies translucidas compuestas sobre su fondo real
TARJETA = mezclar(BG, 0.7, BLANCO)          # rgba(255,255,255,0.7) sobre --bg
CHIP = mezclar(BG, 0.72, BLANCO)            # rgba(255,255,255,0.72) sobre --bg

# Boton primario: gradiente 135deg de #17795f a --accent-deep al 130%.
# El color visible en el extremo (100% del recorrido) es la interpolacion t=100/130
T_FIN = mezclar(BOTON_LIGHT, 100.0 / 130.0, ACCENT_DEEP)
T_MEDIO = mezclar(BOTON_LIGHT, 0.5, ACCENT_DEEP)

# Tarjeta destacada: foto peor caso (blanca) con el degradado inferior oscuro
# rgba(12,36,34,0.72) ENCIMA: el oscuro cubre el 72% del pixel.
OVERLAY_CARD = mezclar(BLANCO, 0.72, [12, 36, 34])

# Spotlight: foto blanca peor caso -> panel oscuro 0.76 -> texto claro 0.82
SPOT_FONDO = mezclar(BLANCO, 0.76, [18, 43, 40])
SPOT_TEXT = mezclar(SPOT_FONDO, 0.82, [239, 247, 244])

CHIP_ACTIVO_FIN = mezclar(BLANCO, 0.22, ACCENT_WARM)  # extremo claro del chip activo

# ------------------------------------------------------------------ pruebas

PRUEBAS = [
    # (descripcion, color texto, color fondo, umbral)
    ("Texto principal --text sobre --bg", TEXT, BG, 4.5),
    ("Texto principal --text sobre --bg-soft", TEXT, BG_SOFT, 4.5),
    ("--text-muted sobre --bg (chips, notas)", TEXT_MUTED, BG, 4.5),
    ("--text-muted sobre tarjeta blanca 0.7", TEXT_MUTED, TARJETA, 4.5),
    ("--text-soft (nuevo) sobre --bg (resumen, tarjetas)", TEXT_SOFT, BG, 4.5),
    ("--text-soft (nuevo) sobre tarjeta blanca 0.7", TEXT_SOFT, TARJETA, 4.5),
    ("--accent-text sobre --bg (journey-arrow 0.88rem)", ACCENT_TEXT, BG, 4.5),
    ("--accent-text sobre blanco (label 0.75rem)", ACCENT_TEXT, BLANCO, 4.5),
    ("--accent-text sobre --bg-soft", ACCENT_TEXT, BG_SOFT, 4.5),
    ("--accent-deep sobre --bg", ACCENT_DEEP, BG, 4.5),
    ("--accent-deep sobre chip activo (extremo claro)", ACCENT_DEEP, CHIP_ACTIVO_FIN, 4.5),
    ("Boton primario: blanco sobre extremo del gradiente", BLANCO, T_FIN, 4.5),
    ("Boton primario: blanco sobre punto medio", BLANCO, T_MEDIO, 4.5),
    ("Boton primario: blanco sobre extremo claro #17795f", BLANCO, BOTON_LIGHT, 4.5),
    ("Tarjeta foto: texto claro sobre overlay 0.72 (peor caso)", CARD_TEXT, OVERLAY_CARD, 4.5),
    ("Spotlight: texto 0.82 sobre panel 0.76 (peor caso)", SPOT_TEXT, SPOT_FONDO, 4.5),
]

fallidos = 0
for desc, texto, fondo, umbral in PRUEBAS:
    ratio = contraste(texto, fondo)
    estado = "PASA " if ratio >= umbral else "FALLA"
    if ratio < umbral:
        fallidos += 1
    print("[%s] %5.2f:1 (min %s)  %s" % (estado, ratio, umbral, desc))

print()
if fallidos:
    print("%d de %d pares FALLAN el nivel AA." % (fallidos, len(PRUEBAS)))
else:
    print("Todos los pares pasan el nivel AA.")
