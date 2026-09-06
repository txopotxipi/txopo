@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo    GENERADOR DE SITEMAP PARA TXOPO
echo ============================================
echo.
echo [DEBUG] Directorio actual: %CD%
echo [DEBUG] Buscando PowerShell...

REM Intentar PowerShell primero (mejor encoding UTF-8)
where powershell.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] PowerShell encontrado. Ejecutando script...
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0generar_sitemap.ps1"
    if %errorlevel% equ 0 goto :fin
    echo.
    echo [ERROR] PowerShell fallo con codigo: %errorlevel%
    echo [INFO] Probando fallback con batch puro...
    echo.
)

REM Fallback: batch puro (encoding limitado pero funcional)
if exist "%~dp0generar_sitemap.cmd" (
    echo [INFO] Usando generador batch puro...
    echo.
    call "%~dp0generar_sitemap.cmd"
    goto :fin
)

echo [ERROR] No se encontro generar_sitemap.cmd ni PowerShell.
echo [AYUDA] Abre CMD en esta carpeta y ejecuta: generar_sitemap.cmd

:fin
echo.
echo ============================================
echo Pulsa cualquier tecla para cerrar...
pause >nul
