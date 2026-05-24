# ============================================================
# SCRIPT DE LIMPIEZA - txopo
# Ejecuta este script para limpiar archivos y git
# 
# INSTRUCCIONES:
# 1. Abre PowerShell en esta carpeta
# 2. Ejecuta: .\limpiar_proyecto.ps1
# ============================================================

$projectPath = "D:\Proyectos VSC\txopo"
Set-Location $projectPath

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  LIMPIADOR DE PROYECTO - txopo" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Este script va a:" -ForegroundColor White
Write-Host "  1. Quitar archivos PHP con credenciales de git (git rm --cached)" -ForegroundColor White
Write-Host "  2. Eliminar archivos duplicados/muertos" -ForegroundColor White
Write-Host "  3. Preguntar si quieres eliminar carpetas freebird/ y slider/" -ForegroundColor White
Write-Host ""
$confirm = Read-Host "Quieres continuar? (s/n)"

if ($confirm -ne "s" -and $confirm -ne "S") {
    Write-Host "Operacion cancelada." -ForegroundColor Yellow
    pause
    exit
}

Write-Host ""
Write-Host "=== PASO 1: Quitar archivos PHP con credenciales de git ===" -ForegroundColor Yellow
git rm --cached db.php 2>$null
git rm --cached csrf_utils.php 2>$null
git rm --cached get_token.php 2>$null
Write-Host "Hecho. Los archivos PHP ya no estan en git (pero siguen en tu disco)." -ForegroundColor Green

Write-Host ""
Write-Host "=== PASO 2: Eliminar archivos muertos/duplicados ===" -ForegroundColor Yellow

$deadFiles = @(
    "Navidad 2023\index_viejo.html",
    "Verbena gallega\index_original.html",
    "Verbena gallega\scripts_original.js",
    "Verbena gallega\styles_original.css",
    "Verbena gallega\submit_original.php",
    "sitemap_viejo.xml",
    "README.md_bueno",
    ".htaccess_WordPress"
)

foreach ($file in $deadFiles) {
    $fullPath = Join-Path $projectPath $file
    if (Test-Path $fullPath) {
        Remove-Item $fullPath -Force
        Write-Host "  Eliminado: $file" -ForegroundColor Green
    } else {
        Write-Host "  No encontrado: $file" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "=== PASO 3: Carpetas freebird/ y slider/ ===" -ForegroundColor Yellow
Write-Host "Estas carpetas contienen plantillas viejas (~3-4 MB) que ya no usas."
$cleanDirs = Read-Host "Quieres eliminarlas tambien? (s/n)"

if ($cleanDirs -eq "s" -or $cleanDirs -eq "S") {
    $dirsToDelete = @("freebird", "slider")
    foreach ($dirName in $dirsToDelete) {
        $dirPath = Join-Path $projectPath $dirName
        if (Test-Path $dirPath) {
            Remove-Item $dirPath -Recurse -Force
            Write-Host "  Eliminado: $dirName/" -ForegroundColor Green
        }
    }
} else {
    Write-Host "  Se conservan freebird/ y slider/." -ForegroundColor Gray
}

Write-Host ""
Write-Host "=== LIMPIEZA COMPLETADA ===" -ForegroundColor Green
Write-Host "Los archivos muertos han sido eliminados."
Write-Host ""
Write-Host "AHORA DEBES HACER:"
Write-Host "  1. git add ."
Write-Host "  2. git commit -m 'Limpieza de archivos muertos y proteccion de credenciales'"
Write-Host "  3. git push"
pause
