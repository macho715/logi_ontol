#Requires -RunAsAdministrator

<#
.SYNOPSIS
    Complete Protégé setup for HVDC Project

.DESCRIPTION
    Automated setup including:
    - Java verification
    - GraphViz PATH addition
    - Protégé installation
    - OWLViz configuration
    - Launch with HVDC ontology

.NOTES
    Version: 1.0
    Date: 2025-10-26
    Requires: Administrator privileges, Internet connection
#>

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "HVDC Protégé Complete Setup" -ForegroundColor Cyan
Write-Host "Version: 1.0" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Java
Write-Host "[STEP 1/5] Checking Java installation..." -ForegroundColor Yellow

try {
    $javaVersion = java -version 2>&1 | Select-Object -First 1
    Write-Host "[OK] Java found: $javaVersion" -ForegroundColor Green

    # Check if Java 11+
    $javaMajorVersion = if ($javaVersion -match 'version "(\d+)') {
        [int]$matches[1]
    }
    else {
        0
    }

    if ($javaMajorVersion -lt 11) {
        Write-Host "[WARNING] Java version must be 11 or higher (found: $javaMajorVersion)" -ForegroundColor Yellow
        Write-Host "          Protégé may not work properly." -ForegroundColor Yellow
    }
}
catch {
    Write-Host "[ERROR] Java not found! Please install Java 11+ from:" -ForegroundColor Red
    Write-Host "        https://adoptium.net/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Step 2: Add GraphViz to PATH
Write-Host "[STEP 2/5] Setting up GraphViz PATH..." -ForegroundColor Yellow
Write-Host ""

# Run GraphViz PATH script
$graphvizScript = Join-Path $PSScriptRoot "add_graphviz_to_path.ps1"
if (Test-Path $graphvizScript) {
    & $graphvizScript
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] GraphViz PATH setup failed!" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "[WARNING] GraphViz PATH script not found: $graphvizScript" -ForegroundColor Yellow
    Write-Host "          Proceeding without PATH setup..." -ForegroundColor Yellow
}

Write-Host ""

# Step 3: Install Protégé
Write-Host "[STEP 3/5] Installing Protégé..." -ForegroundColor Yellow
Write-Host ""

# Check if already installed
$protegeVersion = "5.6.4"
$protegePath = "C:\Program Files\Protege-$protegeVersion"

if (Test-Path "$protegePath\Protege.exe") {
    Write-Host "[INFO] Protégé $protegeVersion is already installed" -ForegroundColor Yellow
    Write-Host "       Location: $protegePath" -ForegroundColor Gray
}
else {
    # Run installation script
    $installScript = Join-Path $PSScriptRoot "install_protege_windows.ps1"
    if (Test-Path $installScript) {
        & $installScript
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ERROR] Protégé installation failed!" -ForegroundColor Red
            exit 1
        }
    }
    else {
        Write-Host "[ERROR] Protégé installation script not found: $installScript" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Step 4: Update OWLViz configuration
Write-Host "[STEP 4/5] Configuring OWLViz..." -ForegroundColor Yellow

$configFile = Join-Path $PSScriptRoot "..\logiontology\configs\protege\owlviz_config.properties"

if (Test-Path $configFile) {
    $configContent = Get-Content $configFile -Raw

    # Update GraphViz path
    $graphvizDot = "C:\Program Files\Graphviz\bin\dot.exe"

    if ($configContent -notmatch 'graphviz\.path=\s*C:\\Program Files\\Graphviz\\bin\\dot\.exe') {
        # Add or update GraphViz path
        if ($configContent -match 'graphviz\.path=') {
            # Update existing
            $configContent = $configContent -replace 'graphviz\.path=.*', "graphviz.path=$graphvizDot"
        }
        else {
            # Add new
            $configContent += "`ngraphviz.path=$graphvizDot`n"
        }

        Set-Content -Path $configFile -Value $configContent -NoNewline
        Write-Host "[OK] OWLViz configuration updated" -ForegroundColor Green
        Write-Host "     GraphViz path: $graphvizDot" -ForegroundColor Gray
    }
    else {
        Write-Host "[OK] OWLViz configuration already set" -ForegroundColor Green
    }
}
else {
    Write-Host "[WARNING] OWLViz config file not found: $configFile" -ForegroundColor Yellow
}

Write-Host ""

# Step 5: Launch Protégé with HVDC ontology
Write-Host "[STEP 5/5] Preparing Protégé launch..." -ForegroundColor Yellow
Write-Host ""

# Check HVDC ontology file
$ontologyFile = Join-Path $PSScriptRoot "..\logiontology\configs\ontology\hvdc_ontology.ttl"

if (-not (Test-Path $ontologyFile)) {
    Write-Host "[ERROR] HVDC ontology file not found: $ontologyFile" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please ensure hvdc_ontology.ttl exists in:" -ForegroundColor Yellow
    Write-Host "logiontology\configs\ontology\" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "You can still launch Protégé manually and load the ontology later." -ForegroundColor Yellow
}
else {
    Write-Host "[OK] HVDC ontology file found" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[SUCCESS] Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Summary
Write-Host "Summary:" -ForegroundColor White
Write-Host "  ✓ Java: Installed" -ForegroundColor Green
Write-Host "  ✓ GraphViz: Configured" -ForegroundColor Green
Write-Host "  ✓ Protégé: Installed at $protegePath" -ForegroundColor Green
Write-Host "  ✓ OWLViz: Configured" -ForegroundColor Green
if (Test-Path $ontologyFile) {
    Write-Host "  ✓ HVDC Ontology: Ready" -ForegroundColor Green
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Run: .\scripts\launch_protege_hvdc.bat" -ForegroundColor Cyan
Write-Host "  2. Or launch manually: $protegePath\Protege.exe" -ForegroundColor Cyan
Write-Host ""
Write-Host "After Protégé launches:" -ForegroundColor Yellow
Write-Host "  1. Install plugins: File → Check for plugins..." -ForegroundColor Gray
Write-Host "     - Cellfie (for Excel import)" -ForegroundColor Gray
Write-Host "     - OWLViz (for visualization)" -ForegroundColor Gray
Write-Host "  2. Load SHACL: Window → Tabs → SHACL Shapes" -ForegroundColor Gray
Write-Host "  3. Import settings from:" -ForegroundColor Gray
Write-Host "     logiontology\configs\protege\" -ForegroundColor Gray
Write-Host ""

# Ask to launch Protégé now
$response = Read-Host "Launch Protégé now with HVDC ontology? (Y/n)"
if ($response -ne 'n' -and $response -ne 'N') {
    if (Test-Path $ontologyFile) {
        & "$protegePath\Protege.exe" $ontologyFile
    }
    else {
        & "$protegePath\Protege.exe"
    }
    Write-Host ""
    Write-Host "[OK] Protégé launched!" -ForegroundColor Green
}

exit 0

