#Requires -RunAsAdministrator

<#
.SYNOPSIS
    Add GraphViz to System PATH

.DESCRIPTION
    Automatically detects GraphViz installation and adds it to system PATH.

.NOTES
    Version: 1.0
    Date: 2025-10-26
    Requires: Administrator privileges
#>

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GraphViz PATH Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Define possible GraphViz paths
$possiblePaths = @(
    "C:\Program Files\Graphviz\bin",
    "C:\Program Files (x86)\Graphviz\bin",
    "$env:LOCALAPPDATA\Programs\Graphviz\bin"
)

# Find GraphViz installation
$graphvizPath = $null
foreach ($path in $possiblePaths) {
    if (Test-Path "$path\dot.exe") {
        $graphvizPath = $path
        Write-Host "[OK] Found GraphViz at: $path" -ForegroundColor Green
        break
    }
}

if (-not $graphvizPath) {
    Write-Host "[ERROR] GraphViz not found in any standard location." -ForegroundColor Red
    Write-Host ""
    Write-Host "Searched paths:" -ForegroundColor Yellow
    foreach ($path in $possiblePaths) {
        Write-Host "  - $path" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "Please install GraphViz from: https://graphviz.org/download/" -ForegroundColor Yellow
    exit 1
}

# Get current system PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")

# Check if already in PATH
if ($currentPath -like "*$graphvizPath*") {
    Write-Host "[INFO] GraphViz is already in system PATH" -ForegroundColor Yellow
}
else {
    Write-Host "[ACTION] Adding GraphViz to system PATH..." -ForegroundColor Cyan

    # Add to system PATH
    $newPath = $currentPath + ";" + $graphvizPath
    [Environment]::SetEnvironmentVariable("Path", $newPath, "Machine")

    Write-Host "[OK] GraphViz added to system PATH" -ForegroundColor Green
}

# Update current session PATH
$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Verification" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test dot command
try {
    $dotVersion = & "$graphvizPath\dot.exe" -V 2>&1
    Write-Host "[OK] GraphViz dot command works:" -ForegroundColor Green
    Write-Host "     $dotVersion" -ForegroundColor White
    Write-Host ""
    Write-Host "[SUCCESS] GraphViz PATH setup complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Note: You may need to restart PowerShell for the PATH change to take effect globally." -ForegroundColor Yellow
    exit 0
}
catch {
    Write-Host "[ERROR] Failed to execute dot command: $_" -ForegroundColor Red
    exit 1
}

