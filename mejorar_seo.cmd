@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ================================================
echo    MEJORADOR SEO PARA GALERIAS DE TXOPO
echo    ^(batch + PowerShell hibrido^)
echo ================================================
echo.
echo Intentando ejecutar con PowerShell...

REM Intentar multiples metodos para invocar PowerShell
REM Metodo 1: PowerShell directo (mas comun)
where powershell.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo [Metodo 1] Ejecutando con powershell.exe...
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0mejorar_seo.ps1"
    if %errorlevel% equ 0 goto :done
    echo Metodo 1 fallo, intentando metodo 2...
)

REM Metodo 2: Usando ruta completa comun
if exist "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe" (
    echo [Metodo 2] Ejecutando con ruta completa...
    C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0mejorar_seo.ps1"
    if %errorlevel% equ 0 goto :done
    echo Metodo 2 fallo, intentando metodo 3...
)

REM Metodo 3: Usando pwsh (PowerShell Core)
where pwsh.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo [Metodo 3] Ejecutando con pwsh.exe...
    pwsh.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0mejorar_seo.ps1"
    if %errorlevel% equ 0 goto :done
    echo Metodo 3 fallo.
)

echo.
echo ================================================
echo ERROR: No se pudo ejecutar PowerShell.
echo.
echo Soluciones:
echo   1. Abre Windows Terminal o CMD como administrador
echo   2. Ve a la carpeta del proyecto
echo   3. Ejecuta: powershell -ExecutionPolicy Bypass -File mejorar_seo.ps1
echo.
echo O usa el metodo mas simple:
echo   - Haz doble clic en: mejorar_seo.bat ^(wrapper simple^)
echo ================================================
goto :eof

:done
echo.
echo ================================================
echo ✅ Script SEO ejecutado correctamente
echo ================================================
goto :eof
