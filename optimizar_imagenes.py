import os
from PIL import Image

BASE_DIR = r'D:\Proyectos VSC\txopo'
MAX_DIMENSION = 1920
QUALITY = 75

# Directorios a excluir
EXCLUDE_DIRS = {
    '.git', 'assets', 'config', 'freebird', 'slider',
    '__pycache__', 'node_modules'
}

def get_image_files():
    images = []
    for root, dirs, files in os.walk(BASE_DIR):
        # Filtrar directorios excluidos
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg')):
                file_path = os.path.join(root, file)
                # Solo procesar si el tamaño es mayor a 300 KB
                if os.path.getsize(file_path) > 300 * 1024:
                    images.append(file_path)
    return images

def optimize_image(file_path):
    try:
        original_size = os.path.getsize(file_path)
        
        # Abrir imagen
        with Image.open(file_path) as img:
            # Mantener el perfil de orientación EXIF si existe
            try:
                if hasattr(img, '_getexif'):
                    exif = img.getexif()
                    if exif:
                        # Auto-orientar basado en EXIF (evita rotaciones incorrectas)
                        from PIL import ImageOps
                        img = ImageOps.exif_transpose(img)
            except Exception:
                pass
                
            width, height = img.size
            new_width, new_height = width, height
            
            # Redimensionar si excede la dimensión máxima
            if width > MAX_DIMENSION or height > MAX_DIMENSION:
                if width > height:
                    new_width = MAX_DIMENSION
                    new_height = int((height * MAX_DIMENSION) / width)
                else:
                    new_height = MAX_DIMENSION
                    new_width = int((width * MAX_DIMENSION) / height)
                
                try:
                    resample_mode = Image.Resampling.LANCZOS
                except AttributeError:
                    resample_mode = Image.LANCZOS
                    
                img = img.resize((new_width, new_height), resample_mode)
            
            # Guardar sobrescribiendo
            if img.mode != 'RGB':
                img = img.convert('RGB')
                
            img.save(file_path, 'JPEG', quality=QUALITY, optimize=True)
            
        new_size = os.path.getsize(file_path)
        saved = original_size - new_size
        return original_size, new_size, saved
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return None

def main():
    images = get_image_files()
    print(f"Encontradas {len(images)} imágenes para optimizar...\n")
    
    total_saved = 0
    count = 0
    
    for img_path in images:
        result = optimize_image(img_path)
        if result:
            count += 1
            orig_size, new_size, saved = result
            total_saved += saved
            
            orig_mb = orig_size / (1024 * 1024)
            new_mb = new_size / (1024 * 1024)
            saved_mb = saved / (1024 * 1024)
            
            file_name = os.path.basename(img_path)
            print(f"[{count}/{len(images)}] {file_name}: {orig_mb:.2f} MB -> {new_mb:.2f} MB (Ahorro: {saved_mb:.2f} MB)")
            
    total_saved_mb = total_saved / (1024 * 1024)
    print(f"\n{'='*60}")
    print(f"Optimización completada.")
    print(f"Imágenes optimizadas: {count}")
    print(f"Ahorro total de espacio: {total_saved_mb:.2f} MB")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
