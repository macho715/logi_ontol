# PowerShell Archive Script - LogiOntology Project
# Excludes WhatsApp media files (JPT71, ABU/WHATSAPP, HVDC Project Lightning images/videos)

# 제외할 폴더/파일 패턴
$excludeFolders = @(
    "JPT71",
    "ABU\WHATSAPP", 
    "HVDC Project Lightning",
    "__pycache__",
    "htmlcov",
    "lib",
    ".git",
    ".vscode"
)

# 임시 복사 폴더
$tempDir = "C:\temp\logi_ontol_clean_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
$sourceDir = "C:\logi_ontol"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$archiveName = "logi_ontol_archive_$timestamp.zip"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "LogiOntology Project Archive" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Source: $sourceDir" -ForegroundColor Yellow
Write-Host "Temp: $tempDir" -ForegroundColor Yellow
Write-Host "Archive: $archiveName" -ForegroundColor Yellow
Write-Host ""

# 1. 임시 폴더 생성
Write-Host "[1/4] Creating temporary directory..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

# 2. 선택적 복사 (미디어 폴더 제외)
Write-Host "[2/4] Copying files (excluding media folders)..." -ForegroundColor Cyan
$totalFiles = 0
$copiedFiles = 0

Get-ChildItem -Path $sourceDir -Recurse -File | ForEach-Object {
    $totalFiles++
    $relativePath = $_.FullName.Substring($sourceDir.Length + 1)
    $shouldExclude = $false
    
    # 폴더 기준 제외 확인
    foreach ($folder in $excludeFolders) {
        if ($relativePath -like "$folder\*" -or $relativePath -like "$folder") {
            $shouldExclude = $true
            break
        }
    }
    
    # 확장자 필터
    if ($_.Extension -in @('.pyc', '.log', '.tmp', '.bak')) {
        $shouldExclude = $true
    }
    
    # 압축 파일 제외
    if ($_.Name -like "*.zip" -and ($_.Name -like "*archive*" -or $_.Name -like "*logi_ontol*")) {
        $shouldExclude = $true
    }
    
    if (-not $shouldExclude) {
        $destPath = Join-Path $tempDir $relativePath
        $destDir = Split-Path $destPath -Parent
        
        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Force -Path $destDir | Out-Null
        }
        
        try {
            Copy-Item $_.FullName -Destination $destPath -Force
            $copiedFiles++
            if ($copiedFiles % 10 -eq 0) {
                Write-Host "  Processed: $copiedFiles files..." -ForegroundColor Gray
            }
        } catch {
            Write-Host "  [!] Error copying $relativePath" -ForegroundColor Red
        }
    }
}

Write-Host "  Total files scanned: $totalFiles" -ForegroundColor Gray
Write-Host "  Files copied: $copiedFiles" -ForegroundColor Gray
Write-Host ""

# 3. 압축
Write-Host "[3/4] Compressing archive..." -ForegroundColor Cyan
$archivePath = Join-Path $sourceDir $archiveName

try {
    Compress-Archive -Path "$tempDir\*" -DestinationPath $archivePath -CompressionLevel Optimal -Force
    $archiveSize = [math]::Round((Get-Item $archivePath).Length / 1MB, 2)
    Write-Host "  Archive created: $archiveSize MB" -ForegroundColor Green
} catch {
    Write-Host "  [!] Error compressing archive: $_" -ForegroundColor Red
    exit 1
}

# 4. 정리
Write-Host "[4/4] Cleaning up temporary files..." -ForegroundColor Cyan
try {
    Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue
    Write-Host "  Temporary files removed" -ForegroundColor Green
} catch {
    Write-Host "  [!] Warning: Could not remove temp directory" -ForegroundColor Yellow
}

# 5. 결과
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "[SUCCESS] Archive created successfully!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host "Archive: $archivePath" -ForegroundColor Yellow
Write-Host "Size: $archiveSize MB" -ForegroundColor Yellow
Write-Host "Files: $copiedFiles" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Green
