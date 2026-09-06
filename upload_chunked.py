import os
import subprocess

def run_cmd(cmd):
    print(f"Ejecutando: {cmd}")
    subprocess.run(cmd, shell=True)

print("Iniciando repositorio desde cero...")

# Inicializar git
run_cmd('git init')
run_cmd('git config --global credential.https://github.com.username txopotxipi')
run_cmd('git config --global user.name "txopotxipi"')
run_cmd('git config http.postBuffer 1048576000')
run_cmd('git config core.autocrlf false')

# Archivos base
base_items = ['index.html', 'assets', 'config', '*.php', '*.md', '*.py', '.gitignore', 'sitemap.xml', 'favicon.png', 'plandemejora.txt', '*.txt']
for item in base_items:
    subprocess.run(f"git add {item}", shell=True)

run_cmd('git commit -m "Archivos base del proyecto"')
run_cmd('git branch -M main')
run_cmd('git remote add origin https://github.com/txopotxipi/txipitxopo.git')
run_cmd('git push -u origin main -f')

# Iterar sobre el resto de carpetas
ignored_folders = ['.git', '.vscode', '.softaculous', '.chrome-headless', '.wrangler', 'publicar', 'assets', 'config']

carpetas = [d for d in os.listdir('.') if os.path.isdir(d) and d not in ignored_folders and not d.startswith('.')]

for idx, entry in enumerate(carpetas, 1):
    print(f"\n[{idx}/{len(carpetas)}] Procesando carpeta: {entry}")
    run_cmd(f'git add "{entry}"')
    
    status = subprocess.run('git status --porcelain', shell=True, capture_output=True, text=True)
    if status.stdout.strip():
        run_cmd(f'git commit -m "Añadida galeria: {entry}"')
        run_cmd('git push origin main')
    else:
        print(f"Nada nuevo en {entry}")

print("\n¡SUBIDA COMPLETADA AL 100%!")
