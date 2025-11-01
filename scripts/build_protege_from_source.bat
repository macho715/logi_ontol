@echo off
:: Build Protege from Source (Quick Launch)
:: Double-click to build Protege

echo ========================================
echo Protege Source Build
echo ========================================
echo.

cd /d "%~dp0.."
powershell.exe -ExecutionPolicy Bypass -File ".\scripts\build_protege_from_source.ps1"

echo.
pause

