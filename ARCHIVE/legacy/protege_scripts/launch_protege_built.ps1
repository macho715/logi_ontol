<#
.SYNOPSIS
    Launch built Protégé from source

.DESCRIPTION
    Finds and launches the Protégé JAR built from source code.

.PARAMETER OntologyFile
    Optional ontology file to load on startup

.NOTES
    Version: 1.0
    Date: 2025-10-26
    Requires: Built Protégé JAR file
#>

param(
    [string]$OntologyFile = "",
    [string]$SourceDir = "c:\logi_ontol\protege-master",
    [int]$MaxMemoryGB = 4
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Launch Protégé (Built from Source)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Java
Write-Host "[CHECK] Verifying Java installation..." -ForegroundColor Cyan
try {
    $javaVersion = java -version 2>&1 | Select-Object -First 1
    Write-Host "[OK] $javaVersion" -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Java not found. Please install JDK 11+ first." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Find built JAR file
Write-Host "[ACTION] Searching for built Protégé JAR..." -ForegroundColor Cyan

if (-not (Test-Path $SourceDir)) {
    Write-Host "[ERROR] Source directory not found: $SourceDir" -ForegroundColor Red
    exit 1
}

$jarFiles = Get-ChildItem -Path $SourceDir -Recurse -Filter "protege*.jar" -ErrorAction SilentlyContinue | Where-Object {
    $_.DirectoryName -like "*target*" -and
    $_.Name -notlike "*-sources.jar" -and
    $_.Name -notlike "*-javadoc.jar" -and
    $_.Name -notlike "*tests.jar"
}

if (-not $jarFiles) {
    Write-Host "[ERROR] No built Protégé JAR found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please build Protégé first:" -ForegroundColor Yellow
    Write-Host "  .\scripts\build_protege_from_source.ps1" -ForegroundColor White
    Write-Host ""
    exit 1
}

# Find the main JAR (usually the largest)
$mainJar = $jarFiles | Sort-Object Length -Descending | Select-Object -First 1

Write-Host "[OK] Found JAR: $($mainJar.Name)" -ForegroundColor Green
Write-Host "     Location: $($mainJar.DirectoryName)" -ForegroundColor Gray
Write-Host "     Size: $([math]::Round($mainJar.Length / 1MB, 2)) MB" -ForegroundColor Gray
Write-Host ""

# Prepare launch command
$javaCmd = "java -Xmx${MaxMemoryGB}G"

# Add ontology file if specified
if ($OntologyFile -and (Test-Path $OntologyFile)) {
    Write-Host "[INFO] Loading ontology: $OntologyFile" -ForegroundColor Cyan
    $javaCmd += " -jar `"$($mainJar.FullName)`" `"$OntologyFile`""
}
else {
    $javaCmd += " -jar `"$($mainJar.FullName)`""
}

Write-Host "[ACTION] Launching Protégé..." -ForegroundColor Cyan
Write-Host "         Command: $javaCmd" -ForegroundColor Gray
Write-Host "         Max Memory: ${MaxMemoryGB}GB" -ForegroundColor Gray
Write-Host ""

try {
    Invoke-Expression $javaCmd
}
catch {
    Write-Host "[ERROR] Failed to launch Protégé: $_" -ForegroundColor Red
    exit 1
}

