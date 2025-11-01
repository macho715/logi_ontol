@echo off
REM ==================================================
REM HVDC Protege Quick Launch Script
REM Version: 1.0
REM Last Updated: 2025-10-26
REM Purpose: Launch Protege with HVDC ontology
REM ==================================================

echo ========================================
echo HVDC Protege Quick Launch
echo ========================================
echo.

REM Set script directory
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

REM Define possible Protege installation paths
set PROTEGE_PATH1=C:\Program Files\Protege-5.6.4\Protege.exe
set PROTEGE_PATH2=C:\Program Files (x86)\Protege-5.6.4\Protege.exe
set PROTEGE_PATH3=%USERPROFILE%\Protege-5.6.4\Protege.exe
set PROTEGE_PATH4=%PROJECT_ROOT%\tools\Protege-5.6.4\Protege.exe

REM Define HVDC ontology file path
set HVDC_ONTOLOGY=%PROJECT_ROOT%\logiontology\configs\ontology\hvdc_ontology.ttl

REM Check if ontology file exists
if not exist "%HVDC_ONTOLOGY%" (
    echo [ERROR] HVDC ontology file not found: %HVDC_ONTOLOGY%
    echo.
    echo Please ensure hvdc_ontology.ttl exists in:
    echo logiontology\configs\ontology\
    echo.
    pause
    exit /b 1
)

REM Find Protege installation
set PROTEGE_EXE=

if exist "%PROTEGE_PATH1%" (
    set PROTEGE_EXE=%PROTEGE_PATH1%
    echo [OK] Found Protege: %PROTEGE_PATH1%
) else if exist "%PROTEGE_PATH2%" (
    set PROTEGE_EXE=%PROTEGE_PATH2%
    echo [OK] Found Protege: %PROTEGE_PATH2%
) else if exist "%PROTEGE_PATH3%" (
    set PROTEGE_EXE=%PROTEGE_PATH3%
    echo [OK] Found Protege: %PROTEGE_PATH3%
) else if exist "%PROTEGE_PATH4%" (
    set PROTEGE_EXE=%PROTEGE_PATH4%
    echo [OK] Found Protege: %PROTEGE_PATH4%
) else (
    echo [ERROR] Protege not found in any standard location.
    echo.
    echo Searched paths:
    echo - %PROTEGE_PATH1%
    echo - %PROTEGE_PATH2%
    echo - %PROTEGE_PATH3%
    echo - %PROTEGE_PATH4%
    echo.
    echo Please install Protege or set PROTEGE_EXE environment variable.
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] HVDC ontology: %HVDC_ONTOLOGY%
echo.
echo ========================================
echo Launching Protege with HVDC ontology...
echo ========================================
echo.

REM Launch Protege with HVDC ontology file
start "" "%PROTEGE_EXE%" "%HVDC_ONTOLOGY%"

REM Wait a moment for Protege to start
timeout /t 3 /nobreak >nul

echo.
echo [OK] Protege launched successfully!
echo.
echo Next steps:
echo 1. Wait for Protege to fully load
echo 2. Check "Classes" tab for: Cargo, Site, Warehouse, Port, FlowCode
echo 3. Open "Window" -^> "Tabs" -^> "Cellfie" for Excel import
echo 4. Open "Window" -^> "Tabs" -^> "OWLViz" for visualization
echo 5. Open "Window" -^> "Tabs" -^> "SHACL Shapes" for validation
echo.
echo Configuration files location:
echo %PROJECT_ROOT%\logiontology\configs\protege\
echo.
echo Press any key to close this window...
pause >nul

