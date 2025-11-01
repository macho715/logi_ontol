<#
.SYNOPSIS
    Check if Maven is installed

.DESCRIPTION
    Checks for Maven installation and provides installation instructions if not found.

.NOTES
    Version: 1.0
    Date: 2025-10-26
#>

Write-Host "Checking Maven installation..." -ForegroundColor Cyan

try {
    $mvnVersion = mvn -version 2>&1 | Select-Object -First 1
    Write-Host "[OK] Maven is installed: $mvnVersion" -ForegroundColor Green

    # Check MAVEN_HOME
    $mavenHome = [Environment]::GetEnvironmentVariable("MAVEN_HOME", "Machine")
    if ($mavenHome) {
        Write-Host "[OK] MAVEN_HOME = $mavenHome" -ForegroundColor Green
    }
    else {
        Write-Host "[WARNING] MAVEN_HOME not set" -ForegroundColor Yellow
    }

    exit 0
}
catch {
    Write-Host "[ERROR] Maven not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "To install Maven:" -ForegroundColor Yellow
    Write-Host "  Option 1 (Automated):" -ForegroundColor Cyan
    Write-Host "    Run as Administrator: .\scripts\install_maven.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "  Option 2 (Chocolatey):" -ForegroundColor Cyan
    Write-Host "    choco install maven" -ForegroundColor White
    Write-Host ""
    Write-Host "  Option 3 (Manual):" -ForegroundColor Cyan
    Write-Host "    1. Download from: https://maven.apache.org/download.cgi" -ForegroundColor White
    Write-Host "    2. Extract to: C:\maven" -ForegroundColor White
    Write-Host "    3. Set MAVEN_HOME and add to PATH" -ForegroundColor White
    Write-Host ""

    exit 1
}

