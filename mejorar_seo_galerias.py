"""
Script para añadir canonical tags y BreadcrumbList JSON-LD a todas las galerías de Txopo.
Procesa todos los index.html de las galerías y añade las etiquetas SEO faltantes.
"""
import os
import re
import urllib.parse

BASE_DIR = r'D:\Proyectos VSC\txopo'
BASE_URL = 'https://txopo.lovestoblog.com'

# Directorios a excluir (no son galerías)
EXCLUDE_DIRS = {
    '.git', 'assets', 'config', 'fotosnavidad', 'images', 'freebird', 'slider',
    '__pycache__', 'node_modules'
}

def get_gallery_dirs():
    """Obtiene todos los directorios de galerías que tienen index.html"""
    galleries = []
    for entry in os.listdir(BASE_DIR):
        entry_path = os.path.join(BASE_DIR, entry)
        if os.path.isdir(entry_path) and entry not in EXCLUDE_DIRS:
            index_path = os.path.join(entry_path, 'index.html')
            if os.path.exists(index_path):
                galleries.append((entry, index_path))
    return sorted(galleries)

def extract_og_url(content):
    """Extrae og:url del contenido HTML"""
    match = re.search(r'<meta property="og:url" content="([^"]+)"', content)
    if match:
        return match.group(1)
    return None

def extract_gallery_name(content):
    """Extrae el nombre de la galería del og:title"""
    match = re.search(r'<meta property="og:title" content="([^"]+)"', content)
    if match:
        return match.group(1)
    # Fallback: usar <title>
    match = re.search(r'<title>([^<]+)</title>', content, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def has_canonical(content):
    """Verifica si ya tiene canonical tag"""
    return 'rel="canonical"' in content or "rel=canonical" in content

def has_breadcrumb(content):
    """Verifica si ya tiene BreadcrumbList"""
    return 'BreadcrumbList' in content

def url_encode_path(path):
    """Codifica una ruta para URL, preservando slashes"""
    parts = path.split('/')
    encoded_parts = [urllib.parse.quote(part, safe='') for part in parts]
    return '/'.join(encoded_parts)

def add_canonical(content, canonical_url):
    """Añade canonical tag después del cierre del JSON-LD script"""
    # Buscar el cierre del script JSON-LD
    # Hay varios formatos: </script>\n<link, </script><link, </script>\n<script
    ld_close = '</script>'
    
    # Encontrar la posición después del JSON-LD script
    # El JSON-LD es el primer script type="application/ld+json"
    ld_pattern = r'(<script type="application/ld\+json">.*?</script>)'
    match = re.search(ld_pattern, content, re.DOTALL)
    
    if not match:
        return None, 'no_jsonld'
    
    ld_end = match.end()
    canonical_tag = f'\n<link rel="canonical" href="{canonical_url}" />'
    
    # Insertar después del cierre del JSON-LD
    new_content = content[:ld_end] + canonical_tag + content[ld_end:]
    return new_content, 'ok'

def add_breadcrumb(content, gallery_name, gallery_url):
    """Añade BreadcrumbList JSON-LD después del ImageGallery JSON-LD"""
    # Buscar el final del primer JSON-LD (ImageGallery)
    ld_pattern = r'(<script type="application/ld\+json">.*?</script>)'
    match = re.search(ld_pattern, content, re.DOTALL)
    
    if not match:
        return None, 'no_jsonld'
    
    ld_end = match.end()
    
    breadcrumb_jsonld = f'''
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {{
      "@type": "ListItem",
      "position": 1,
      "name": "Txipi Txopo",
      "item": "https://txopo.lovestoblog.com/"
    }},
    {{
      "@type": "ListItem",
      "position": 2,
      "name": "{gallery_name}",
      "item": "{gallery_url}"
    }}
  ]
}}
</script>'''
    
    new_content = content[:ld_end] + breadcrumb_jsonld + content[ld_end:]
    return new_content, 'ok'

def process_gallery(dir_name, index_path):
    """Procesa una galería: añade canonical y breadcrumb si faltan"""
    with open(index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Construir URL
    encoded_dir = url_encode_path(dir_name)
    gallery_url = f"{BASE_URL}/{encoded_dir}/"
    
    # Extraer nombre de galería
    gallery_name = extract_gallery_name(content)
    if not gallery_name:
        gallery_name = dir_name
    
    changes = []
    modified = False
    
    # 1. Añadir canonical
    if not has_canonical(content):
        new_content, status = add_canonical(content, gallery_url)
        if status == 'ok':
            content = new_content
            changes.append('canonical')
            modified = True
        else:
            changes.append(f'canonical_fail:{status}')
    else:
        changes.append('canonical_skip')
    
    # 2. Añadir BreadcrumbList
    if not has_breadcrumb(content):
        new_content, status = add_breadcrumb(content, gallery_name, gallery_url)
        if status == 'ok':
            content = new_content
            changes.append('breadcrumb')
            modified = True
        else:
            changes.append(f'breadcrumb_fail:{status}')
    else:
        changes.append('breadcrumb_skip')
    
    # Guardar si hubo cambios
    if modified:
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    return changes

def main():
    galleries = get_gallery_dirs()
    print(f"Encontradas {len(galleries)} galerías\n")
    
    stats = {
        'canonical_added': 0,
        'canonical_skipped': 0,
        'canonical_failed': 0,
        'breadcrumb_added': 0,
        'breadcrumb_skipped': 0,
        'breadcrumb_failed': 0,
        'errors': []
    }
    
    for dir_name, index_path in galleries:
        try:
            changes = process_gallery(dir_name, index_path)
            
            for change in changes:
                if change == 'canonical':
                    stats['canonical_added'] += 1
                elif change == 'canonical_skip':
                    stats['canonical_skipped'] += 1
                elif change.startswith('canonical_fail'):
                    stats['canonical_failed'] += 1
                    stats['errors'].append(f"{dir_name}: {change}")
                elif change == 'breadcrumb':
                    stats['breadcrumb_added'] += 1
                elif change == 'breadcrumb_skip':
                    stats['breadcrumb_skipped'] += 1
                elif change.startswith('breadcrumb_fail'):
                    stats['breadcrumb_failed'] += 1
                    stats['errors'].append(f"{dir_name}: {change}")
            
            status = '✓' if any(c in ('canonical', 'breadcrumb') for c in changes) else '○'
            print(f"  {status} {dir_name}: {', '.join(changes)}")
            
        except Exception as e:
            stats['errors'].append(f"{dir_name}: {str(e)}")
            print(f"  ✗ {dir_name}: ERROR - {e}")
    
    print(f"\n{'='*60}")
    print(f"RESUMEN:")
    print(f"  Canonical: {stats['canonical_added']} añadidos, {stats['canonical_skipped']} ya existentes, {stats['canonical_failed']} fallos")
    print(f"  Breadcrumb: {stats['breadcrumb_added']} añadidos, {stats['breadcrumb_skipped']} ya existentes, {stats['breadcrumb_failed']} fallos")
    
    if stats['errors']:
        print(f"\n  ERRORES ({len(stats['errors'])}):")
        for err in stats['errors']:
            print(f"    - {err}")
    
    print(f"\n  Total galerías procesadas: {len(galleries)}")

if __name__ == '__main__':
    main()
