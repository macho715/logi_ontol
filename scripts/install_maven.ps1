#Requires -RunAsAdministrator

<#
.SYNOPSIS
    Install Apache Maven for Windows

.DESCRIPTION
    Downloads and installs Apache Maven 3.9.6, sets up environment variables.

.NOTES
    Version: 1.0
    Date: 2025-10-26
    Requires: Administrator privileges, Internet connection
#>

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Apache Maven Installation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$mavenVersion = "3.9.6"
# Try multiple download URLs (mirrors may change)
$downloadUrls = @(
    "https://archive.apache.org/dist/maven/maven-3/$mavenVersion/binaries/apache-maven-$mavenVersion-bin.zip",
    "https://dlcdn.apache.org/maven/maven-3/$mavenVersion/binaries/apache-maven-$mavenVersion-bin.zip",
    "https://mirrors.tuna.tsinghua.edu.cn/apache/maven/maven-3/$mavenVersion/binaries/apache-maven-$mavenVersion-bin.zip"
)
$installDir = "C:\maven\apache-maven-$mavenVersion"
$tempDir = "$env:TEMP\maven_install"
$zipFile = "$tempDir\apache-maven-$mavenVersion-bin.zip"

# Check if already installed
if (Test-Path "$installDir\bin\mvn.cmd") {
    Write-Host "[INFO] Maven $mavenVersion is already installed at:" -ForegroundColor Yellow
    Write-Host "       $installDir" -ForegroundColor Yellow
    Write-Host ""

    $response = Read-Host "Do you want to reinstall? (y/N)"
    if ($response -ne 'y' -and $response -ne 'Y') {
        Write-Host "[SKIP] Installation skipped" -ForegroundColor Yellow
        exit 0
    }
}

# Check Java installation
Write-Host "[CHECK] Verifying Java installation..." -ForegroundColor Cyan
try {
    $javaVersion = java -version 2>&1 | Select-Object -First 1
    Write-Host "[OK] Java found: $javaVersion" -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Java not found. Please install JDK 11+ first." -ForegroundColor Red
    Write-Host "        Download from: https://adoptium.net" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Create temp directory
Write-Host "[ACTION] Creating temporary directory..." -ForegroundColor Cyan
if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force
}
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

# Download Maven (try multiple URLs)
Write-Host "[ACTION] Downloading Maven $mavenVersion..." -ForegroundColor Cyan
Write-Host "         This may take 2-3 minutes (approx. 9 MB)..." -ForegroundColor Gray
Write-Host ""

$downloadSuccess = $false
$lastError = $null

foreach ($downloadUrl in $downloadUrls) {
    try {
        Write-Host "         Trying: $downloadUrl" -ForegroundColor Gray

        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $downloadUrl -OutFile $zipFile -UseBasicParsing -TimeoutSec 300
        $ProgressPreference = 'Continue'

        Write-Host "[OK] Download complete!" -ForegroundColor Green
        Write-Host "     Size: $([math]::Round((Get-Item $zipFile).Length / 1MB, 2)) MB" -ForegroundColor White
        $downloadSuccess = $true
        break
    }
    catch {
        $lastError = $_.Exception.Message
        Write-Host "         Failed: $lastError" -ForegroundColor Yellow
        continue
    }
}

if (-not $downloadSuccess) {
    Write-Host "[ERROR] Failed to download Maven from all URLs" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please try manual download:" -ForegroundColor Yellow
    Write-Host "  1. Visit: https://maven.apache.org/download.cgi" -ForegroundColor Yellow
    Write-Host "  2. Download: apache-maven-$mavenVersion-bin.zip" -ForegroundColor Yellow
    Write-Host "  3. Extract to: $installDir" -ForegroundColor Yellow
    exit 1
}

# Extract ZIP
Write-Host ""
Write-Host "[ACTION] Extracting Maven..." -ForegroundColor Cyan

try {
    # Extract to C:\maven
    $mavenRoot = "C:\maven"
    if (-not (Test-Path $mavenRoot)) {
        New-Item -ItemType Directory -Path $mavenRoot -Force | Out-Null
    }

    Expand-Archive -Path $zipFile -DestinationPath $mavenRoot -Force

    Write-Host "[OK] Extraction complete!" -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Failed to extract Maven: $_" -ForegroundColor Red
    exit 1
}

# Cleanup temp files
Write-Host ""
Write-Host "[ACTION] Cleaning up temporary files..." -ForegroundColor Cyan
Remove-Item $tempDir -Recurse -Force
Write-Host "[OK] Cleanup complete!" -ForegroundColor Green

# Set environment variables
Write-Host ""
Write-Host "[ACTION] Setting up environment variables..." -ForegroundColor Cyan

try {
    # Set MAVEN_HOME
    [Environment]::SetEnvironmentVariable("MAVEN_HOME", $installDir, "Machine")
    Write-Host "[OK] MAVEN_HOME = $installDir" -ForegroundColor Green

    # Add to PATH
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    $mavenBinPath = "$installDir\bin"

    if ($currentPath -notlike "*$mavenBinPath*") {
        $newPath = $currentPath + ";" + $mavenBinPath
        [Environment]::SetEnvironmentVariable("Path", $newPath, "Machine")
        Write-Host "[OK] Added to PATH: $mavenBinPath" -ForegroundColor Green
    }
    else {
        Write-Host "[INFO] Maven bin is already in PATH" -ForegroundColor Yellow
    }

    # Update current session PATH
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
    $env:MAVEN_HOME = $installDir
}
catch {
    Write-Host "[ERROR] Failed to set environment variables: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please set manually:" -ForegroundColor Yellow
    Write-Host "  1. MAVEN_HOME = $installDir" -ForegroundColor Yellow
    Write-Host "  2. Add to PATH: $installDir\bin" -ForegroundColor Yellow
    exit 1
}

# Verify installation
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Verification" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    $mvnVersion = & "$installDir\bin\mvn.cmd" -version 2>&1 | Select-Object -First 1
    Write-Host "[OK] Maven executable found:" -ForegroundColor Green
    Write-Host "     $mvnVersion" -ForegroundColor White
}
catch {
    Write-Host "[ERROR] Maven verification failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[SUCCESS] Maven $mavenVersion installation complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Installation location: $installDir" -ForegroundColor White
Write-Host "MAVEN_HOME: $installDir" -ForegroundColor White
Write-Host ""
Write-Host "IMPORTANT: Restart PowerShell to use 'mvn' command" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Close and reopen PowerShell (or restart terminal)" -ForegroundColor Yellow
Write-Host "  2. Run: mvn -version" -ForegroundColor Yellow
Write-Host "  3. Run: .\scripts\build_protege_from_source.ps1" -ForegroundColor Yellow
Write-Host ""

exit 0

