<#
.SYNOPSIS
    Build Protégé from source code

.DESCRIPTION
    Builds Protégé using Maven from the protege-master source directory.

.NOTES
    Version: 1.0
    Date: 2025-10-26
    Requires: JDK 11+, Maven 3.6+
#>

param(
    [switch]$SkipTests = $true,
    [switch]$Clean = $true,
    [string]$SourceDir = "c:\logi_ontol\protege-master"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Protégé Source Build" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if source directory exists
if (-not (Test-Path $SourceDir)) {
    Write-Host "[ERROR] Source directory not found: $SourceDir" -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] Source directory: $SourceDir" -ForegroundColor White
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

# Check Maven (use standard mvn - skip mvnd due to Java 25 compatibility)
Write-Host "[CHECK] Verifying Maven installation..." -ForegroundColor Cyan

$mavenCmd = $null

# Skip mvnd due to Java 25 compatibility issues
Write-Host "[INFO] Skipping mvnd (Java 25 compatibility issue)" -ForegroundColor Yellow
Write-Host "[INFO] Using standard Maven (mvn)" -ForegroundColor Cyan

# Use regular mvn
try {
    $mvnVersion = mvn -version 2>&1 | Select-Object -First 1
    Write-Host "[OK] $mvnVersion" -ForegroundColor Green
    $mavenCmd = "mvn"
}
catch {
    Write-Host "[ERROR] Maven not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Maven first:" -ForegroundColor Yellow
    Write-Host "  .\scripts\install_maven.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "After installation, restart PowerShell and run:" -ForegroundColor Yellow
    Write-Host "  mvn -version" -ForegroundColor White
    exit 1
}

Write-Host ""

# Navigate to source directory
Set-Location $SourceDir

# Build command (use mvnd if available)
$buildCmd = $mavenCmd
if ($Clean) {
    $buildCmd += " clean"
}
$buildCmd += " install"
if ($SkipTests) {
    $buildCmd += " -DskipTests"
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Building Protégé" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[ACTION] Build command: $buildCmd" -ForegroundColor Cyan
Write-Host "[INFO] This may take 5-10 minutes..." -ForegroundColor Yellow
Write-Host ""

$startTime = Get-Date

try {
    # Execute Maven build
    Invoke-Expression $buildCmd

    if ($LASTEXITCODE -eq 0) {
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalMinutes

        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "[SUCCESS] Build completed!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Build time: $([math]::Round($duration, 2)) minutes" -ForegroundColor White
        Write-Host ""

        # Find built JAR files
        Write-Host "[INFO] Searching for built JAR files..." -ForegroundColor Cyan
        $jarFiles = Get-ChildItem -Path $SourceDir -Recurse -Filter "protege*.jar" -ErrorAction SilentlyContinue | Where-Object { $_.DirectoryName -like "*target*" -and $_.Name -notlike "*-sources.jar" -and $_.Name -notlike "*-javadoc.jar" }

        if ($jarFiles) {
            Write-Host ""
            Write-Host "Built JAR files:" -ForegroundColor Green
            foreach ($jar in $jarFiles) {
                $size = [math]::Round($jar.Length / 1MB, 2)
                Write-Host "  - $($jar.FullName)" -ForegroundColor White
                Write-Host "    Size: $size MB" -ForegroundColor Gray
            }

            # Find the main Protégé JAR (usually the largest)
            $mainJar = $jarFiles | Sort-Object Length -Descending | Select-Object -First 1

            Write-Host ""
            Write-Host "Main executable JAR:" -ForegroundColor Yellow
            Write-Host "  $($mainJar.FullName)" -ForegroundColor White
            Write-Host ""
            Write-Host "To run Protégé:" -ForegroundColor Yellow
            Write-Host "  java -Xmx4G -jar `"$($mainJar.FullName)`"" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "Or use the launch script:" -ForegroundColor Yellow
            Write-Host "  .\scripts\launch_protege_built.ps1" -ForegroundColor Cyan
            Write-Host ""
        }
        else {
            Write-Host "[WARNING] No JAR files found in target directories" -ForegroundColor Yellow
        }

        exit 0
    }
    else {
        throw "Maven build failed with exit code: $LASTEXITCODE"
    }
}
catch {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "[ERROR] Build failed!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Check internet connection (Maven downloads dependencies)" -ForegroundColor White
    Write-Host "  2. Verify Java version: java -version (requires JDK 11+)" -ForegroundColor White
    Write-Host "  3. Verify Maven version: mvn -version (requires 3.6+)" -ForegroundColor White
    Write-Host "  4. Check build logs above for specific errors" -ForegroundColor White
    Write-Host ""

    exit 1
}

