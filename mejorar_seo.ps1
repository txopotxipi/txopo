# ============================================================
# mejorar_seo.ps1
# Añade meta description y Open Graph tags a las galerías
# con el template estándar (patrón Buitrago/Bilbao/Burgos)
#
# Uso: Ejecutar desde la raíz del proyecto
#   powershell -ExecutionPolicy Bypass -File mejorar_seo.ps1
# ============================================================

$ErrorActionPreference = "Continue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$projectRoot = $PSScriptRoot
if (-not $projectRoot) {
    $projectRoot = Get-Location
}
$domain = "https://txopo.lovestoblog.com"
$modCount = 0
$skipCount = 0
$errorCount = 0

Write-Host "=== Mejorador SEO para galerias Txopo ===" -ForegroundColor Cyan
Write-Host "Directorio: $projectRoot"
Write-Host ""

# Obtener lista de galerias
$galleryDirs = Get-ChildItem -Path $projectRoot -Directory -ErrorAction SilentlyContinue | 
    Where-Object { Test-Path (Join-Path $_.FullName "index.html") }

Write-Host "Galerias encontradas: $($galleryDirs.Count)"
Write-Host ""

foreach ($dir in $galleryDirs) {
    $filePath = Join-Path $dir.FullName "index.html"
    
    try {
        $content = Get-Content -Path $filePath -Raw -Encoding UTF8 -ErrorAction Stop
        
        # Verificar si ya tiene meta description u OG tags
        if ($content -match '<meta\s+name\s*=\s*["\x27]?description') {
            Write-Host "  Omitida: $($dir.Name) - ya tiene meta description" -ForegroundColor Gray
            $skipCount++
            continue
        }
        
        # Verificar si tiene el patron de template estandar
        if ($content -match '<title>([^<]+)</title>') {
            $title = $matches[1].Trim()
            $folderName = $dir.Name
            $encodedFolder = [uri]::EscapeDataString($folderName)
            
            # Buscar la primera imagen en fotos/ para og:image
            $fotosDir = Join-Path $dir.FullName "fotos"
            $ogImage = ""
            if (Test-Path $fotosDir) {
                $firstImage = Get-ChildItem -Path $fotosDir -File -ErrorAction SilentlyContinue | 
                    Where-Object { $_.Extension -match '\.(jpg|jpeg|png|webp|gif)$' -and $_.Name -notlike 'favicon*' -and $_.Name -notlike 'facebook*' -and $_.Name -notlike 'instagram*' -and $_.Name -notlike 'whatsapp*' -and $_.Name -notlike 'gorjeo*' -and $_.Name -notlike 'tik-tok*' -and $_.Name -notlike 'youtube*' -and $_.Name -notlike 'linkedin*' -and $_.Name -notlike 'email*' } |
                    Select-Object -First 1
                if ($firstImage) {
                    $ogImage = "$domain/$encodedFolder/fotos/$($firstImage.Name)"
                }
            }
            
            # Si no hay fotos/, buscar en static/Images/
            if (-not $ogImage) {
                $staticDir = Join-Path $dir.FullName "static\Images"
                if (Test-Path $staticDir) {
                    $firstImage = Get-ChildItem -Path $staticDir -File -ErrorAction SilentlyContinue |
                        Where-Object { $_.Extension -match '\.(jpg|jpeg|png|webp|gif)$' } |
                        Select-Object -First 1
                    if ($firstImage) {
                        $ogImage = "$domain/$encodedFolder/static/Images/$($firstImage.Name)"
                    }
                }
            }
            
            # Construir los meta tags SEO
            $seoBlock = @"

<meta name="description" content="Galeria de fotos de $title. Descubre esta coleccion de imagenes en Txopo.">
<meta property="og:title" content="$title">
<meta property="og:description" content="Galeria de fotos de $title en Txopo. Coleccion de imagenes de viajes y senderismo.">
<meta property="og:type" content="website">
<meta property="og:image" content="$ogImage">
<meta property="og:url" content="$domain/$encodedFolder/">
<meta name="twitter:card" content="summary_large_image">
"@
            
            # Insertar los meta tags SEO justo despues de </title>
            $newContent = $content -replace '(?<=</title>)', $seoBlock
            
            if ($newContent -ne $content) {
                # Usar UTF8 sin BOM si esta disponible (PS 6+), si no usar UTF8 con BOM
                if ($PSVersionTable.PSVersion.Major -ge 6) {
                    $newContent | Out-File -FilePath $filePath -Encoding utf8NoBOM -NoNewline
                } else {
                    $newContent | Out-File -FilePath $filePath -Encoding utf8 -NoNewline
                }
                Write-Host "  OK: $($dir.Name) - SEO anadido" -ForegroundColor Green
                if ($ogImage) {
                    Write-Host "       og:image = $ogImage" -ForegroundColor DarkGray
                } else {
                    Write-Host "       AVISO: no se encontro imagen para og:image" -ForegroundColor Yellow
                }
                $modCount++
            } else {
                Write-Host "  ERROR: $($dir.Name) - no se pudo insertar (formato no reconocido)" -ForegroundColor Red
                $errorCount++
            }
        } else {
            Write-Host "  AVISO: $($dir.Name) - sin tag <title> o formato no estandar" -ForegroundColor Yellow
            $skipCount++
        }
    } catch {
        Write-Host "  ERROR: $($dir.Name) - $_" -ForegroundColor Red
        $errorCount++
    }
}

Write-Host ""
Write-Host "=== Resumen ===" -ForegroundColor Cyan
Write-Host "  Modificadas: $modCount galerias" -ForegroundColor Green
Write-Host "  Omitidas:    $skipCount galerias (ya tenian SEO o formato especial)" -ForegroundColor Gray
Write-Host "  Errores:     $errorCount galerias" -ForegroundColor Red
Write-Host ""
Write-Host "Las galerias modificadas ahora tienen meta description + Open Graph tags." -ForegroundColor Green
