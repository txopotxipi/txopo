import os
import urllib.parse
from datetime import datetime

DOMAIN = "https://txopo.lovestoblog.com"
BASE_DIR = r"D:\Proyectos VSC\txopo"
TODAY = datetime.now().strftime("%Y-%m-%d")

EXCLUDE = {
    '.git', '.github', '.codex-analysis', 'assets', 'config', 'publicar',
    'slider', 'node_modules', '__pycache__', 'eliminar'
}

def generate_sitemap():
    urls = []
    # Portada principal
    urls.append(f"""<url>
  <loc>{DOMAIN}/</loc>
  <lastmod>{TODAY}</lastmod>
  <priority>1.00</priority>
</url>""")

    # Galerías
    for item in sorted(os.listdir(BASE_DIR)):
        item_path = os.path.join(BASE_DIR, item)
        if not os.path.isdir(item_path) or item in EXCLUDE:
            continue
        index_file = os.path.join(item_path, "index.html")
        if not os.path.isfile(index_file):
            continue

        encoded_name = urllib.parse.quote(item)
        urls.append(f"""<url>
  <loc>{DOMAIN}/{encoded_name}/</loc>
  <lastmod>{TODAY}</lastmod>
  <priority>0.80</priority>
</url>""")

    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
{chr(10).join(urls)}
</urlset>
"""

    sitemap_path = os.path.join(BASE_DIR, "sitemap.xml")
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(xml_content)

    print(f"✅ Sitemap generado con éxito en: {sitemap_path}")
    print(f"Total de URLs: {len(urls)} (1 portada + {len(urls) - 1} galerías)")

if __name__ == "__main__":
    generate_sitemap()
