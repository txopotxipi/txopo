# -*- coding: utf-8 -*-
"""Genera las miniaturas de las tarjetas destacadas en images/cards/.

Por que: las 6 tarjetas destacadas de la portada usan las FOTOS ORIGINALES
(1920px, 300-460 KB cada una) para pintarlas en una caja de ~373px de ancho.
Entre las 6 bajaban 2.226 KB. Con las miniaturas, una fraccion.

Recorte 800x720: la tarjeta mide ~373px en escritorio (3 columnas) con
min-height: 26rem = 416px. A 800px quedan ~2x para pantallas de alta densidad
y para las 2 columnas de tablet. La caja ya recorta con object-fit: cover, asi
que se recorta aqui igual (centrado) y no se pierde visionado.

El .jpg es el respaldo para navegadores sin WebP, servido via <picture>.
Los originales NO se tocan; nada dentro de las subwebs se modifica.
"""
import os

from PIL import Image, ImageOps

RAIZ = r"D:\Proyectos VSC\txopo"
CARPETA = os.path.join(RAIZ, "images", "cards")
ANCHO, ALTO = 800, 720
CALIDAD_WEBP = 78
CALIDAD_JPG = 80

# (nombre de archivo final, ruta de la foto original)
PARES = [
    ("panticosa", "Panticosa/fotos/1.jpg"),
    ("karlovy-vary", "Karlovy Vary/fotos/1.jpg"),
    ("amboto", "Amboto/fotos/IMG20220125130837-min.jpg"),
    ("semana-santa-2024", "Semana Santa 2024/fotos/01.jpg"),
    ("buitrago", "Buitrago/fotos/20220212_130413-min.jpg"),
    ("cesky-krumlov", "Český Krumlov/fotos/1.jpg"),
]

os.makedirs(CARPETA, exist_ok=True)

total_antes = 0.0
total_webp = 0.0
total_jpg = 0.0

for nombre, origen in PARES:
    ruta = os.path.join(RAIZ, origen)
    if not os.path.exists(ruta):
        print("NO EXISTE (se omite): %s" % ruta)
        continue

    with Image.open(ruta) as im:
        # exif_transpose respeta la orientacion EXIF antes de recortar
        im = ImageOps.exif_transpose(im)
        # Recorte centrado exacto a la proporcion de la tarjeta. centering un
        # pelin hacia arriba (0.45) para no cortar el cielo de los paisajes.
        mini = ImageOps.fit(im, (ANCHO, ALTO), method=Image.LANCZOS,
                            centering=(0.5, 0.45))
        if mini.mode not in ("RGB", "L"):
            mini = mini.convert("RGB")

        ruta_webp = os.path.join(CARPETA, nombre + ".webp")
        ruta_jpg = os.path.join(CARPETA, nombre + ".jpg")
        mini.save(ruta_webp, "WEBP", quality=CALIDAD_WEBP, method=6)
        mini.save(ruta_jpg, "JPEG", quality=CALIDAD_JPG, optimize=True,
                  progressive=True)

    kb_webp = os.path.getsize(ruta_webp) / 1024
    kb_jpg = os.path.getsize(ruta_jpg) / 1024
    total_antes += os.path.getsize(ruta) / 1024
    total_webp += kb_webp
    total_jpg += kb_jpg
    print("%-34s -> %-24s %5.0f KB  (+respaldo jpg %4.0f KB)" % (
        os.path.basename(origen), nombre + ".webp", kb_webp, kb_jpg))

print()
print("Original (las 6 fotos completas): %6.0f KB" % total_antes)
print("Ahora se descarga (WebP):         %6.0f KB   (-%.0f%%)"
      % (total_webp, 100 - 100 * total_webp / total_antes))
