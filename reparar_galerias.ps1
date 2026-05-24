# ============================================================
# SCRIPT DE REPARACION DE GALERIAS - txopo
# Corrige backslashes, anyade loading=lazy y unifica favicon
#
# INSTRUCCIONES:
# 1. Abre PowerShell en esta carpeta
# 2. Ejecuta: .\reparar_galerias.ps1
# ============================================================

$projectPath = "D:\Proyectos VSC\txopo"
Set-Location $projectPath

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  REPARADOR DE GALERIAS - txopo" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Este script va a:" -ForegroundColor White
Write-Host "  1. Corregir barras invertidas (\) en rutas de imagenes" -ForegroundColor White
Write-Host "  2. Anyadir loading=lazy a todas las imagenes" -ForegroundColor White
Write-Host "  3. Unificar favicon a ../favicon.png" -ForegroundColor White
Write-Host "  4. Anyadir tracking Google Analytics + Clarity donde falte" -ForegroundColor White
Write-Host ""
$confirm = Read-Host "Quieres continuar? (s/n)"

if ($confirm -ne "s" -and $confirm -ne "S") {
    Write-Host "Operacion cancelada." -ForegroundColor Yellow
    pause
    exit
}

# Tracking code template
$ga4Code = @'
<script async src="https://www.googletagmanager.com/gtag/js?id=G-19SLJ1H579"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}gtag("js",new Date());gtag("config","G-19SLJ1H579");</script>
'@

$clarityCode = @'
<script type="text/javascript">
(function(c,l,a,r,i,t,y){c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);})(window,document,"clarity","script","jk6xa82oti");
</script>
'@

# Get all gallery index.html files (skip freebird, slider, assets, root)
$galleryDirs = Get-ChildItem -Directory | Where-Object { 
    $_.Name -notin @('freebird','slider','assets','.git','images','publicar') -and 
    (Test-Path (Join-Path $_.FullName 'index.html'))
}

$fixedBackslash = 0
$fixedFavicon = 0
$addedLazyLoading = 0
$addedTracking = 0

foreach ($dir in $galleryDirs) {
    $htmlFile = Join-Path $dir.FullName 'index.html'
    $content = Get-Content $htmlFile -Raw -Encoding UTF8
    $originalContent = $content
    $changes = @()
    
    # ---- FIX 1: Replace backslashes with forward slashes in image paths ---- 
    if ($content -match 'fotos\\') {
        $content = $content -replace 'fotos\\', 'fotos/'
        $fixedBackslash++
        $changes += "backslashes"
    }
    
    # ---- FIX 2: Add loading="lazy" to img tags that don't have it ----
    # IMPORTANTE: un solo reemplazo para evitar doble loading="lazy"
    if ($content -match '<img ' -and $content -notmatch 'loading=') {
        # Captura <img atributos> o <img atributos/>
        $content = $content -replace '(<img\s)([^>]*?)(\s*/?>)', '$1$2 loading="lazy"$3'
        $addedLazyLoading++
        $changes += "lazy loading"
    }
    
    # ---- FIX 3: Fix favicon to use ../favicon.png ----
    if ($content -match 'fotos/favicon\.png') {
        $content = $content -replace 'href=["\x27]?fotos/favicon\.png["\x27]?', 'href="../favicon.png"'
        $fixedFavicon++
        $changes += "favicon"
    }
    
    # ---- FIX 4: Add GA4 + Clarity tracking if missing ----
    if ($content -notmatch 'googletagmanager') {
        # Add GA4 after <head> or after <meta charset
        if ($content -match '(<meta charset[^>]*>)') {
            $content = $content -replace '(<meta charset[^>]*>)', "`$1`n$ga4Code"
        } elseif ($content -match '(<head[^>]*>)') {
            $content = $content -replace '(<head[^>]*>)', "`$1`n$ga4Code"
        }
        $addedTracking++
        $changes += "GA4 tracking"
    }
    
    if ($content -notmatch 'clarity\.ms') {
        if ($content -match '(</head>)') {
            $content = $content -replace '(</head>)', "$clarityCode`n`$1"
        }
    }
    
    # Write changes back if modified
    if ($content -ne $originalContent) {
        # Compatible con PowerShell 5.1 y 7+
        [System.IO.File]::WriteAllText($htmlFile, $content, [System.Text.UTF8Encoding]::new($false))
        $changeList = $changes -join ", "
        Write-Host "  [OK] $($dir.Name): $changeList" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "=== RESUMEN ===" -ForegroundColor Yellow
Write-Host "  Backslashes corregidos: $fixedBackslash galerias" -ForegroundColor Green
Write-Host "  Lazy loading anyadido: $addedLazyLoading galerias" -ForegroundColor Green
Write-Host "  Favicon unificado: $fixedFavicon galerias" -ForegroundColor Green
Write-Host "  Tracking anyadido: $addedTracking galerias" -ForegroundColor Green
Write-Host ""
Write-Host "=== REPARACION COMPLETADA ===" -ForegroundColor Green
Write-Host "Revisa los cambios y haz commit cuando estes satisfecho."
pause
