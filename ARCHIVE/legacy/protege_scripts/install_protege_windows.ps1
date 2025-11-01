#Requires -RunAsAdministrator

<#
.SYNOPSIS
    Install Protégé 5.6.4 for Windows

.DESCRIPTION
    Downloads and installs Protégé 5.6.4 from GitHub releases.

.NOTES
    Version: 1.0
    Date: 2025-10-26
    Requires: Administrator privileges, Internet connection
#>

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Protégé 5.6.4 Installation" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$protegeVersion = "5.6.4"
# Try alternative URLs - GitHub releases may vary
$downloadUrls = @(
    "https://github.com/protegeproject/protege/releases/download/v$protegeVersion/Protege-$protegeVersion-win.zip",
    "https://github.com/protegeproject/protege-distribution/releases/download/v$protegeVersion/Protege-$protegeVersion-win.zip",
    "https://github.com/protegeproject/protege/releases/latest/download/Protege-5.6.4-win.zip"
)
$installDir = "C:\Program Files\Protege-$protegeVersion"
$tempDir = "$env:TEMP\protege_install"
$zipFile = "$tempDir\Protege-$protegeVersion-win.zip"

# Check if already installed
if (Test-Path "$installDir\Protege.exe") {
    Write-Host "[INFO] Protégé $protegeVersion is already installed at:" -ForegroundColor Yellow
    Write-Host "       $installDir" -ForegroundColor Yellow
    Write-Host ""

    $response = Read-Host "Do you want to reinstall? (y/N)"
    if ($response -ne 'y' -and $response -ne 'Y') {
        Write-Host "[SKIP] Installation skipped" -ForegroundColor Yellow
        exit 0
    }
}

# Create temp directory
Write-Host "[ACTION] Creating temporary directory..." -ForegroundColor Cyan
if (Test-Path $tempDir) {
    Remove-Item $tempDir -Recurse -Force
}
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

# Download Protégé (try multiple URLs)
Write-Host "[ACTION] Downloading Protégé $protegeVersion..." -ForegroundColor Cyan
Write-Host "         This may take 5-10 minutes (approx. 150 MB)..." -ForegroundColor Gray
Write-Host ""

$downloadSuccess = $false
$lastError = $null

foreach ($downloadUrl in $downloadUrls) {
    try {
        Write-Host "         Trying: $downloadUrl" -ForegroundColor Gray

        # Use faster download method with progress
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
    Write-Host "[ERROR] Failed to download Protégé from all URLs" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please try manual download:" -ForegroundColor Yellow
    Write-Host "  1. Visit: https://protege.stanford.edu" -ForegroundColor Yellow
    Write-Host "  2. Download: Protégé Desktop (Windows)" -ForegroundColor Yellow
    Write-Host "  3. Extract to: $installDir" -ForegroundColor Yellow
    exit 1
}

# Extract ZIP
Write-Host ""
Write-Host "[ACTION] Extracting Protégé..." -ForegroundColor Cyan

try {
    # Extract to temp location first
    $extractTemp = "$tempDir\extracted"
    Expand-Archive -Path $zipFile -DestinationPath $extractTemp -Force

    # Find the Protege folder (it's usually Protege-X.X.X inside the zip)
    $protegeFolder = Get-ChildItem -Path $extractTemp -Directory | Where-Object { $_.Name -like "Protege*" } | Select-Object -First 1

    if (-not $protegeFolder) {
        throw "Protege folder not found in extracted files"
    }

    # Move to final location
    if (Test-Path $installDir) {
        Remove-Item $installDir -Recurse -Force
    }

    Move-Item -Path $protegeFolder.FullName -Destination $installDir -Force

    Write-Host "[OK] Extraction complete!" -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Failed to extract Protégé: $_" -ForegroundColor Red
    exit 1
}

# Cleanup temp files
Write-Host ""
Write-Host "[ACTION] Cleaning up temporary files..." -ForegroundColor Cyan
Remove-Item $tempDir -Recurse -Force
Write-Host "[OK] Cleanup complete!" -ForegroundColor Green

# Verify installation
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Verification" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (Test-Path "$installDir\Protege.exe") {
    Write-Host "[OK] Protégé executable found at:" -ForegroundColor Green
    Write-Host "     $installDir\Protege.exe" -ForegroundColor White

    # Get file version
    $fileVersion = (Get-Item "$installDir\Protege.exe").VersionInfo.FileVersion
    if ($fileVersion) {
        Write-Host "     Version: $fileVersion" -ForegroundColor White
    }
}
else {
    Write-Host "[ERROR] Protégé executable not found!" -ForegroundColor Red
    exit 1
}

# Create desktop shortcut (optional)
Write-Host ""
$response = Read-Host "Create desktop shortcut? (Y/n)"
if ($response -ne 'n' -and $response -ne 'N') {
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\Protégé.lnk")
    $Shortcut.TargetPath = "$installDir\Protege.exe"
    $Shortcut.WorkingDirectory = $installDir
    $Shortcut.Description = "Protégé Ontology Editor $protegeVersion"
    $Shortcut.Save()
    Write-Host "[OK] Desktop shortcut created!" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[SUCCESS] Protégé $protegeVersion installation complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Installation location: $installDir" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Run: .\scripts\launch_protege_hvdc.bat" -ForegroundColor Yellow
Write-Host "  2. Or launch manually: $installDir\Protege.exe" -ForegroundColor Yellow
Write-Host ""

exit 0

