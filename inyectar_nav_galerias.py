import os
import re

BASE_DIR = r"D:\Proyectos VSC\txopo"
EXCLUDE_DIRS = {
    '.git', '.github', '.codex-analysis', 'assets', 'config', 'publicar',
    'slider', 'node_modules', '__pycache__', 'eliminar'
}

def inject_gallery_nav():
    updated_count = 0
    skipped_count = 0

    for item in os.listdir(BASE_DIR):
        item_path = os.path.join(BASE_DIR, item)
        if not os.path.isdir(item_path) or item in EXCLUDE_DIRS:
            continue

        index_file = os.path.join(item_path, "index.html")
        if not os.path.isfile(index_file):
            continue

        with open(index_file, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Evitar inyección duplicada
        if "txopo-gallery-nav" in content:
            skipped_count += 1
            continue

        # Obtener título de la página
        title_match = re.search(r"<title>(.*?)</title>", content, re.IGNORECASE)
        if title_match:
            title = title_match.group(1).strip()
            # Limpiar títulos con guiones o pipes
            title = title.split("-")[0].split("|")[0].strip()
        else:
            title = item

        nav_html = f'''<!-- Barra de navegación de retorno Txopo Txipi -->
<header class="txopo-gallery-nav" style="position:sticky;top:0;z-index:9999;width:100%;backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);background:rgba(18,40,36,0.88);border-bottom:1px solid rgba(255,255,255,0.12);padding:0.65rem 1.25rem;display:flex;align-items:center;justify-content:space-between;box-sizing:border-box;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;box-shadow:0 4px 20px rgba(0,0,0,0.25);">
  <a href="../" style="display:inline-flex;align-items:center;gap:0.45rem;color:#ffffff;text-decoration:none;font-weight:700;font-size:0.9rem;padding:0.4rem 0.9rem;border-radius:999px;background:rgba(30,139,113,0.7);transition:background 0.2s ease,transform 0.2s ease;">
    <span style="font-size:1.1rem;line-height:1;">&larr;</span> Volver al inicio
  </a>
  <span style="color:#d8efe6;font-weight:600;font-size:0.92rem;letter-spacing:0.02em;text-overflow:ellipsis;overflow:hidden;white-space:nowrap;max-width:55%;">{title}</span>
</header>
'''

        # Inyectar justo después de <body>
        body_match = re.search(r"<body[^>]*>", content, re.IGNORECASE)
        if body_match:
            insert_pos = body_match.end()
            new_content = content[:insert_pos] + "\n" + nav_html + content[insert_pos:]

            with open(index_file, "w", encoding="utf-8") as f:
                f.write(new_content)
            updated_count += 1
            print(f"✅ Inyectada navegación en: {item}")
        else:
            print(f"⚠️ No se encontró <body> en: {item}")

    print(f"\nResumen: {updated_count} galerías actualizadas, {skipped_count} omitidas (ya tenían navegación).")

if __name__ == "__main__":
    inject_gallery_nav()
