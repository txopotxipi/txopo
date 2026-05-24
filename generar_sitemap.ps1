# ============================================================
# generar_sitemap.ps1
# Genera automáticamente sitemap.xml escaneando todas las
# carpetas del proyecto que contienen un index.html
#
# Uso: Ejecutar desde la raíz del proyecto
#   powershell -ExecutionPolicy Bypass -File generar_sitemap.ps1
# ============================================================

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Configuración
$domain = "https://txopo.lovestoblog.com"
$today = Get-Date -Format "yyyy-MM-dd"
$projectRoot = $PSScriptRoot

Write-Host "=== Generador de Sitemap para Txopo ===" -ForegroundColor Cyan
Write-Host ""

# Buscar todas las carpetas que contienen index.html (excluyendo la raíz)
$galleryDirs = Get-ChildItem -Path $projectRoot -Directory | 
    Where-Object { Test-Path (Join-Path $_.FullName "index.html") } |
    Sort-Object Name

Write-Host "Galerías encontradas: $($galleryDirs.Count)" -ForegroundColor Green

# Función para codificar URLs
function Encode-UrlPath {
    param([string]$path)
    # Codificar caracteres especiales para URLs
    $encoded = [uri]::EscapeDataString($path)
    # Restaurar caracteres que no necesitan codificación en path
    $encoded = $encoded -replace '%20', '%20'  # mantener espacios
    $encoded = $encoded -replace '%2F', '/'    # no codificar barras
    return $encoded
}

# Generar el XML
$sitemap = @"
<?xml version="1.0" encoding="UTF-8"?>
<urlset
      xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
            http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">

<url>
  <loc>$domain/</loc>
  <lastmod>$today</lastmod>
  <priority>1.00</priority>
</url>
"@

foreach ($dir in $galleryDirs) {
    $encodedName = [uri]::EscapeDataString($dir.Name)
    # Arreglar codificación de caracteres Unicode para que coincida con el formato esperado
    # [uri]::EscapeDataString usa %20 para espacios (correcto para sitemap)
    
    $sitemap += @"

<url><loc>$domain/$encodedName/</loc><lastmod>$today</lastmod><priority>0.80</priority></url>
"@
}

$sitemap += @"

</urlset>
"@

# Guardar el archivo
$outputPath = Join-Path $projectRoot "sitemap.xml"
$sitemap | Out-File -FilePath $outputPath -Encoding utf8

Write-Host ""
Write-Host "✅ Sitemap generado correctamente:" -ForegroundColor Green
Write-Host "   Archivo: $outputPath" -ForegroundColor White
Write-Host "   URLs: $($galleryDirs.Count + 1) (1 raíz + $($galleryDirs.Count) galerías)" -ForegroundColor White
Write-Host "   Fecha: $today" -ForegroundColor White
Write-Host ""
Write-Host "📋 Galerías incluidas:" -ForegroundColor Cyan
foreach ($dir in $galleryDirs) {
    Write-Host "   - $($dir.Name)" -ForegroundColor Gray
}
