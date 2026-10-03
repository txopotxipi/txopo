@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo    MEJORADOR SEO PARA GALERIAS DE TXOPO
echo ============================================
echo.
echo [DEBUG] Directorio actual: %CD%
echo [DEBUG] Buscando mejorar_seo.ps1...

if not exist "%~dp0mejorar_seo.ps1" (
    echo [ERROR] No se encuentra mejorar_seo.ps1
    echo [AYUDA] Asegurate de que el archivo esta en la misma carpeta.
    goto :fin
)

echo [DEBUG] Buscando PowerShell...

REM Intentar PowerShell
where powershell.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] PowerShell encontrado. Ejecutando script SEO...
    echo.
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0mejorar_seo.ps1"
    set "EXITCODE=%errorlevel%"
    echo.
    echo [INFO] Script termino con codigo: %EXITCODE%
    goto :fin
)

REM Intentar pwsh (PowerShell Core)
where pwsh.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] PowerShell Core encontrado. Ejecutando script SEO...
    echo.
    pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0mejorar_seo.ps1"
    set "EXITCODE=%errorlevel%"
    echo.
    echo [INFO] Script termino con codigo: %EXITCODE%
    goto :fin
)

echo.
echo [ERROR] PowerShell no encontrado en el sistema.
echo.
echo [AYUDA] Abre Windows Terminal o PowerShell manualmente:
echo   1. Win+X -^> Terminal/PowerShell
echo   2. Navega a: %CD%
echo   3. Ejecuta: powershell -ExecutionPolicy Bypass -File mejorar_seo.ps1

:fin
echo.
echo ============================================
echo Pulsa cualquier tecla para cerrar...
pause >nul
