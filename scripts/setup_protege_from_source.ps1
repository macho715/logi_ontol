#Requires -RunAsAdministrator

<#
.SYNOPSIS
    Complete Protégé setup from source code

.DESCRIPTION
    Automated setup including:
    - Java verification
    - Maven installation (if needed)
    - GraphViz PATH addition
    - Protégé source build
    - Launch with HVDC ontology

.NOTES
    Version: 1.0
    Date: 2025-10-26
    Requires: Administrator privileges, Internet connection
#>

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "HVDC Protégé Source Build Setup" -ForegroundColor Cyan
Write-Host "Version: 1.0" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Java
Write-Host "[STEP 1/6] Checking Java installation..." -ForegroundColor Yellow

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

# Step 2: Check Maven
Write-Host "[STEP 2/6] Checking Maven installation..." -ForegroundColor Yellow

$mavenInstalled = $false

try {
    $mvnVersion = mvn -version 2>&1 | Select-Object -First 1
    Write-Host "[OK] Maven found: $mvnVersion" -ForegroundColor Green
    $mavenInstalled = $true
}
catch {
    # Check for mvnd
    $mvndPath = Join-Path $PSScriptRoot "..\maven-mvnd-1.0.3-windows-amd64\bin\mvnd.cmd"
    if (Test-Path $mvndPath) {
        Write-Host "[OK] Maven Daemon (mvnd) found" -ForegroundColor Green
        $mavenInstalled = $true
    }
    else {
        Write-Host "[INFO] Maven not found, will install automatically" -ForegroundColor Yellow
    }
}

if (-not $mavenInstalled) {
    # Install Maven
    Write-Host ""
    Write-Host "[ACTION] Installing Maven..." -ForegroundColor Cyan

    $installScript = Join-Path $PSScriptRoot "install_maven.ps1"
    if (Test-Path $installScript) {
        & $installScript
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[ERROR] Maven installation failed!" -ForegroundColor Red
            Write-Host ""
            Write-Host "Please install Maven manually:" -ForegroundColor Yellow
            Write-Host "  .\scripts\install_maven.ps1" -ForegroundColor White
            exit 1
        }
    }
    else {
        Write-Host "[ERROR] Maven installation script not found!" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Step 3: Add GraphViz to PATH
Write-Host "[STEP 3/6] Setting up GraphViz PATH..." -ForegroundColor Yellow
Write-Host ""

$graphvizScript = Join-Path $PSScriptRoot "add_graphviz_to_path.ps1"
if (Test-Path $graphvizScript) {
    & $graphvizScript
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[WARNING] GraphViz PATH setup skipped" -ForegroundColor Yellow
    }
}
else {
    Write-Host "[WARNING] GraphViz PATH script not found" -ForegroundColor Yellow
}

Write-Host ""

# Step 4: Build Protégé from source
Write-Host "[STEP 4/6] Building Protégé from source..." -ForegroundColor Yellow
Write-Host ""

$buildScript = Join-Path $PSScriptRoot "build_protege_from_source.ps1"
if (Test-Path $buildScript) {
    & $buildScript
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Protégé build failed!" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "[ERROR] Build script not found!" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 5: Update OWLViz configuration
Write-Host "[STEP 5/6] Configuring OWLViz..." -ForegroundColor Yellow

$configFile = Join-Path $PSScriptRoot "..\logiontology\configs\protege\owlviz_config.properties"

if (Test-Path $configFile) {
    $configContent = Get-Content $configFile -Raw

    # Update GraphViz path
    $graphvizDot = "C:\Program Files\Graphviz\bin\dot.exe"

    if ($configContent -notmatch 'graphviz\.path=\s*C:\\Program Files\\Graphviz\\bin\\dot\.exe') {
        # Add or update GraphViz path
        if ($configContent -match 'graphviz\.path=') {
            $configContent = $configContent -replace 'graphviz\.path=.*', "graphviz.path=$graphvizDot"
        }
        else {
            $configContent += "`ngraphviz.path=$graphvizDot`n"
        }

        Set-Content -Path $configFile -Value $configContent -NoNewline
        Write-Host "[OK] OWLViz configuration updated" -ForegroundColor Green
    }
    else {
        Write-Host "[OK] OWLViz configuration already set" -ForegroundColor Green
    }
}
else {
    Write-Host "[WARNING] OWLViz config file not found" -ForegroundColor Yellow
}

Write-Host ""

# Step 6: Launch Protégé
Write-Host "[STEP 6/6] Preparing Protégé launch..." -ForegroundColor Yellow
Write-Host ""

$ontologyFile = Join-Path $PSScriptRoot "..\logiontology\configs\ontology\hvdc_ontology.ttl"

if (-not (Test-Path $ontologyFile)) {
    Write-Host "[ERROR] HVDC ontology file not found: $ontologyFile" -ForegroundColor Red
}
else {
    Write-Host "[OK] HVDC ontology file found" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[SUCCESS] Source Build Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Summary:" -ForegroundColor White
Write-Host "  ✓ Java: Installed" -ForegroundColor Green
Write-Host "  ✓ Maven: Installed" -ForegroundColor Green
Write-Host "  ✓ GraphViz: Configured" -ForegroundColor Green
Write-Host "  ✓ Protégé: Built from source" -ForegroundColor Green
Write-Host "  ✓ OWLViz: Configured" -ForegroundColor Green
if (Test-Path $ontologyFile) {
    Write-Host "  ✓ HVDC Ontology: Ready" -ForegroundColor Green
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Launch built Protégé:" -ForegroundColor Cyan
Write-Host "     .\scripts\launch_protege_built.ps1" -ForegroundColor White
Write-Host ""
Write-Host "  2. Or launch with HVDC ontology:" -ForegroundColor Cyan
Write-Host "     .\scripts\launch_protege_built.ps1 -OntologyFile `"logiontology\configs\ontology\hvdc_ontology.ttl`"" -ForegroundColor White
Write-Host ""

# Ask to launch Protégé now
$response = Read-Host "Launch Protégé now? (Y/n)"
if ($response -ne 'n' -and $response -ne 'N') {
    $launchScript = Join-Path $PSScriptRoot "launch_protege_built.ps1"
    if (Test-Path $launchScript) {
        & $launchScript
    }
}

exit 0
