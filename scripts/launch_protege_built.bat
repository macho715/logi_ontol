@echo off
:: Launch Built Protege (Quick Launch)
:: Double-click to run built Protege

echo ========================================
echo Launch Protege (Built from Source)
echo ========================================
echo.

cd /d "%~dp0.."
powershell.exe -ExecutionPolicy Bypass -File ".\scripts\launch_protege_built.ps1"

echo.
pause

