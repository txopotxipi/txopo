@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ================================================
echo    GENERADOR DE SITEMAP PARA TXOPO (batch puro)
echo ================================================
echo.

set "DOMAIN=https://txopo.lovestoblog.com"

REM Obtener fecha en formato yyyy-MM-dd via wmic
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value 2^>nul') do set "DT=%%I"
set "TODAY=%DT:~0,4%-%DT:~4,2%-%DT:~6,2%"
if "%TODAY%"=="--" set "TODAY=2026-05-21"

set "COUNT=0"

echo Buscando galerias con index.html...
echo.

REM Escribir el sitemap directamente
(
echo ^<?xml version="1.0" encoding="UTF-8"?^>
echo ^<urlset
echo       xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
echo       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
echo       xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
echo             http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd"^>
echo.
echo ^<url^>
echo   ^<loc^>%DOMAIN%/^</loc^>
echo   ^<lastmod^>%TODAY%^</lastmod^>
echo   ^<priority^>1.00^</priority^>
echo ^</url^>

for /d %%D in (*) do (
    if exist "%%D\index.html" (
        set /a COUNT+=1
        set "FNAME=%%D"
        REM Codificar SOLO espacios (lo demas va en UTF-8 nativo, valido en XML)
        set "FNAME=!FNAME: =%%20!"
        echo   [!COUNT!] %%D
        echo.
        echo ^<url^>^<loc^>%DOMAIN%/!FNAME!/^</loc^>^<lastmod^>%TODAY%^</lastmod^>^<priority^>0.80^</priority^>^</url^>
    )
)

echo.
echo ^</urlset^>
) > "sitemap.xml"

echo.
echo ================================================
echo ✅ Sitemap generado: sitemap.xml
echo    URLs: 1 raiz + %COUNT% galerias
echo    Fecha: %TODAY%
echo ================================================
echo.
echo NOTA: Las URLs usan UTF-8 nativo (valido en XML).
echo Si necesitas encoding %%XX, ejecuta generar_sitemap.bat
echo que usa PowerShell para mejor encoding.
echo ================================================
