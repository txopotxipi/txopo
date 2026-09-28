# -*- coding: utf-8 -*-
"""
Genera versiones WebP de las imagenes del hero.

El hero rota tres fondos (hero_urdaibai.png, pic02.jpg y banner.jpg) que juntos
pesan unos 1,1 MB, y el PNG solo ya son 749 KB: es lo primero que descarga
cualquier visitante, asi que marca el LCP de la pagina.

Este script NO borra los originales: crea los .webp al lado y el CSS los usa
con image-set(), de modo que los navegadores antiguos siguen recibiendo el
PNG/JPG de siempre.

Uso:
    C:\\Python314\\python.exe optimizar_webp.py
"""
import os
import sys

from PIL import Image, ImageOps

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images")

# Imagenes del hero, por orden de peso. Se les pone tope de 1920 px de ancho.
OBJETIVOS = ["hero_urdaibai.png", "pic02.jpg", "banner.jpg"]

MAX_WIDTH = 1920
QUALITY = 82


def convertir(nombre):
    origen = os.path.join(IMAGES_DIR, nombre)
    if not os.path.isfile(origen):
        print("  [saltado] %s no existe" % nombre)
        return None

    destino = os.path.splitext(origen)[0] + ".webp"
    peso_original = os.path.getsize(origen)

    with Image.open(origen) as img:
        # Respeta la orientacion EXIF antes de nada
        try:
            img = ImageOps.exif_transpose(img)
        except Exception:
            pass

        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")

        if img.width > MAX_WIDTH:
            alto = round(img.height * MAX_WIDTH / img.width)
            img = img.resize((MAX_WIDTH, alto), Image.Resampling.LANCZOS)
            redimensionada = True
        else:
            redimensionada = False

        img.save(destino, "WEBP", quality=QUALITY, method=6)

    peso_webp = os.path.getsize(destino)
    ahorro = 100.0 * (1 - peso_webp / peso_original)

    print("  %-24s %7.0f KB -> %6.0f KB  (-%.0f%%)%s" % (
        nombre, peso_original / 1024, peso_webp / 1024, ahorro,
        "  [redimensionada a %dpx]" % MAX_WIDTH if redimensionada else ""))

    return peso_original, peso_webp


def main():
    print("Convirtiendo las imagenes del hero a WebP...")
    print("-" * 66)

    total_antes = total_despues = 0
    for nombre in OBJETIVOS:
        resultado = convertir(nombre)
        if resultado:
            total_antes += resultado[0]
            total_despues += resultado[1]

    print("-" * 66)
    if total_antes:
        print("  TOTAL  %7.0f KB -> %6.0f KB  (-%.0f%%)" % (
            total_antes / 1024, total_despues / 1024,
            100.0 * (1 - total_despues / total_antes)))
    print("Listo. Los originales siguen intactos como respaldo.")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()
