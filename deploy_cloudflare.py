import os
import shutil
import json
import re

src_dir = r"d:\Proyectos VSC\txopo"
dst_dir = os.path.join(src_dir, "publicar")

if os.path.exists(dst_dir):
    shutil.rmtree(dst_dir)
os.makedirs(dst_dir)

# Extract used directories from sites-data.js
js_file = os.path.join(src_dir, 'assets', 'js', 'sites-data.js')
used_dirs = set()
with open(js_file, 'r', encoding='utf-8') as f:
    content = f.read()
    # Find all href values
    hrefs = re.findall(r'"href"\s*:\s*"([^"]+)"', content)
    for href in hrefs:
        if not href.startswith('http'):
            folder = href.split('/')[0]
            used_dirs.add(folder)

# Also add known asset directories
used_dirs.update(['assets', 'images', 'confeti', 'fotosnavidad', 'slider'])

# Files to copy in root
root_files = ['index.html', 'favicon.png', 'sitemap.xml', 'robots.txt']
# Adding google verification file
for f in os.listdir(src_dir):
    if f.startswith('google') and f.endswith('.html'):
        root_files.append(f)

# Exclude extensions
exclude_exts = {'.php', '.md', '.bak', '.log', '.ps1', '.py', '.gitignore'}

for item in os.listdir(src_dir):
    s = os.path.join(src_dir, item)
    d = os.path.join(dst_dir, item)
    
    if os.path.isdir(s):
        # Only copy if it's in our used_dirs set
        if item in used_dirs:
            def ignore_func(dir_path, contents):
                ignore = []
                for c in contents:
                    c_path = os.path.join(dir_path, c)
                    if os.path.isfile(c_path):
                        ext = os.path.splitext(c)[1].lower()
                        if ext in exclude_exts:
                            ignore.append(c)
                        elif ext == '.txt' and c != 'robots.txt':
                            ignore.append(c)
                return ignore
            
            shutil.copytree(s, d, ignore=ignore_func)
    else:
        if item in root_files:
            if os.path.exists(s):
                shutil.copy2(s, d)

print(f"✅ ¡Carpeta 'publicar' creada con éxito!")
print(f"Se han incluido las carpetas base y {len(used_dirs)} carpetas de rutas enlazadas.")
print("Archivos sensibles, .php, .md, .txt, scripts y plantillas antiguas han sido excluidos.")
