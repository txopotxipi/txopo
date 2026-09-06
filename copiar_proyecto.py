import os

def copiar_proyecto_a_txt(ruta_proyecto, archivo_salida):
    """
    Copia todos los archivos de código de un proyecto a un archivo .txt
    """
    
    # Extensiones de código fuente que se copiarán
    extensiones = ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', 
                   '.h', '.php', '.rb', '.go', '.ts', '.jsx', '.tsx', 
                   '.json', '.xml', '.yaml', '.yml', '.sql', '.sh', '.md',
                   '.txt', '.ini', '.cfg', '.bat', '.ps1']
    
    # Carpetas que se ignoran automáticamente
    ignorar_carpetas = ['node_modules', '.git', '__pycache__', 'venv', 
                        '.venv', 'env', '.env', 'dist', 'build', '.idea', 
                        '.vscode', 'target', 'bin', 'obj', '.pytest_cache',
                        '.mypy_cache', ' migrations', 'uploads', 'static',
                        'media', 'tmp', 'temp', 'logs']
    
    # Archivos específicos que se ignoran
    ignorar_archivos = ['package-lock.json', 'yarn.lock', 'Pipfile.lock',
                        '.DS_Store', 'Thumbs.db', 'README.md']
    
    total_archivos = 0
    ruta_absoluta = os.path.abspath(ruta_proyecto)
    
    with open(archivo_salida, 'w', encoding='utf-8') as salida:
        # Encabezado
        salida.write(f"{'='*80}\n")
        salida.write(f"PROYECTO: {os.path.basename(ruta_absoluta)}\n")
        salida.write(f"RUTA COMPLETA: {ruta_absoluta}\n")
        salida.write(f"FECHA: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        salida.write(f"{'='*80}\n\n")
        
        for raiz, carpetas, archivos in os.walk(ruta_proyecto):
            # Ignorar carpetas no deseadas
            carpetas[:] = [c for c in carpetas if c not in ignorar_carpetas]
            
            for archivo in archivos:
                if archivo in ignorar_archivos:
                    continue
                
                _, ext = os.path.splitext(archivo)
                if ext not in extensiones:
                    continue
                
                ruta_completa = os.path.join(raiz, archivo)
                ruta_relativa = os.path.relpath(ruta_completa, ruta_proyecto)
                
                try:
                    with open(ruta_completa, 'r', encoding='utf-8', errors='ignore') as f:
                        contenido = f.read()
                    
                    # Escribir el archivo en el txt
                    salida.write(f"\n{'='*80}\n")
                    salida.write(f"ARCHIVO: {ruta_relativa}\n")
                    salida.write(f"{'='*80}\n\n")
                    salida.write(contenido)
                    salida.write("\n")
                    
                    total_archivos += 1
                    print(f"✓ {ruta_relativa}")
                    
                except Exception as e:
                    print(f"✗ Error: {ruta_relativa} - {e}")
        
        # Resumen final
        salida.write(f"\n{'='*80}\n")
        salida.write(f"TOTAL DE ARCHIVOS COPIADOS: {total_archivos}\n")
        salida.write(f"{'='*80}\n")
    
    return total_archivos


# ═══════════════════════════════════════════════════════
# PROGRAMA PRINCIPAL - TE PREGUNTA LA RUTA
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("  COPIADOR DE PROYECTO A .TXT")
    print("=" * 60)
    print()
    
    # Preguntar la ruta del proyecto
    ruta = input("📁 Escribe la ruta de tu proyecto (ej: D:\\Junta): ").strip()
    
    # Quitar comillas si el usuario las puso al copiar la ruta
    ruta = ruta.strip('"').strip("'")
    
    # Verificar que la ruta existe
    if not os.path.exists(ruta):
        print(f"\n❌ ERROR: La ruta '{ruta}' no existe.")
        print("Verifica que escribiste bien la ruta.")
        exit()
    
    # Preguntar nombre del archivo de salida (opcional)
    nombre_proyecto = os.path.basename(os.path.normpath(ruta))
    sugerencia = f"{nombre_proyecto}_codigo.txt"
    
    print(f"\n💾 El archivo se guardará como: {sugerencia}")
    cambiar = input("¿Quieres cambiar el nombre? (s/n): ").strip().lower()
    
    if cambiar == 's':
        archivo_salida = input("Escribe el nuevo nombre (con .txt al final): ").strip()
    else:
        archivo_salida = sugerencia
    
    print(f"\n⏳ Copiando archivos...")
    print("-" * 60)
    
    total = copiar_proyecto_a_txt(ruta, archivo_salida)
    
    print("-" * 60)
    print(f"\n✅ ¡LISTO! Se copiaron {total} archivos.")
    print(f"📄 Archivo generado: {os.path.abspath(archivo_salida)}")
    print(f"\n💡 Ahora puedes compartirme el archivo: {archivo_salida}")
    
    # Esperar para que no se cierre la ventana
    input("\nPresiona ENTER para salir...")