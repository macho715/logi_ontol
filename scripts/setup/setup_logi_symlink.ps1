# ============================================
# LOGI_ONTOL → CURSOR-MCP 심볼릭 링크 생성
# ============================================
# 실행: 관리자 PowerShell에서 .\setup_logi_symlink.ps1

$ErrorActionPreference = "Stop"

Write-Host "`n" -NoNewline
Write-Host "🔧 LOGI_ONTOL 심볼릭 링크 자동 설정" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host ""

# ============================================
# 설정
# ============================================
$SOURCE_DIR = "C:\logi_ontol"
$TARGET_LINK = "C:\cursor-mcp\logi_ontol_link"
$LOG_FILE = "C:\cursor-mcp\logs\symlink_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

# 로그 디렉토리 생성
$logDir = Split-Path $LOG_FILE -Parent
if (!(Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

# ============================================
# 로그 함수
# ============================================
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO",  # INFO, SUCCESS, WARNING, ERROR
        [switch]$NoNewLine
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp][$Level] $Message"
    
    # 콘솔 출력
    $color = switch ($Level) {
        "SUCCESS" { "Green" }
        "WARNING" { "Yellow" }
        "ERROR"   { "Red" }
        default   { "White" }
    }
    
    if ($NoNewLine) {
        Write-Host $Message -ForegroundColor $color -NoNewline
    } else {
        Write-Host $Message -ForegroundColor $color
    }
    
    # 파일 로그
    Add-Content -Path $LOG_FILE -Value $logEntry
}

# ============================================
# STEP 1: 권한 확인
# ============================================
Write-Log "`n[STEP 1/6] 권한 확인" "INFO"
Write-Log ("─" * 70) "INFO"

$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if ($isAdmin) {
    Write-Log "✅ 관리자 권한으로 실행 중" "SUCCESS"
} else {
    Write-Log "❌ 관리자 권한이 필요합니다!" "ERROR"
    Write-Log "" "INFO"
    Write-Log "해결 방법:" "WARNING"
    Write-Log "  1. PowerShell 종료" "INFO"
    Write-Log "  2. PowerShell 아이콘을 오른쪽 클릭" "INFO"
    Write-Log "  3. '관리자 권한으로 실행' 선택" "INFO"
    Write-Log "  4. 이 스크립트 다시 실행" "INFO"
    Write-Log "" "INFO"
    Read-Host "Press Enter to exit"
    exit 1
}

# ============================================
# STEP 2: Source 디렉토리 확인
# ============================================
Write-Log "`n[STEP 2/6] Source 디렉토리 확인" "INFO"
Write-Log ("─" * 70) "INFO"
Write-Log "경로: $SOURCE_DIR" "INFO"

if (Test-Path $SOURCE_DIR) {
    Write-Log "✅ Source 디렉토리 존재" "SUCCESS"
    
    # 디렉토리 통계
    $dirCount = (Get-ChildItem $SOURCE_DIR -Directory -ErrorAction SilentlyContinue).Count
    $fileCount = (Get-ChildItem $SOURCE_DIR -File -ErrorAction SilentlyContinue).Count
    
    Write-Log "   📁 하위 디렉토리: $dirCount 개" "INFO"
    Write-Log "   📄 파일: $fileCount 개" "INFO"
    
    # 주요 디렉토리 확인
    $criticalDirs = @("logiontology", "JPT71", "HVDC Project Lightning", "output", "scripts")
    $missingDirs = @()
    
    foreach ($dir in $criticalDirs) {
        $dirPath = Join-Path $SOURCE_DIR $dir
        if (Test-Path $dirPath) {
            Write-Log "   ✅ $dir" "SUCCESS"
        } else {
            Write-Log "   ⚠️  $dir (누락)" "WARNING"
            $missingDirs += $dir
        }
    }
    
    if ($missingDirs.Count -gt 0) {
        Write-Log "`n⚠️  경고: 일부 주요 디렉토리가 누락되었지만 계속 진행합니다" "WARNING"
    }
} else {
    Write-Log "❌ Source 디렉토리를 찾을 수 없습니다!" "ERROR"
    Write-Log "   경로: $SOURCE_DIR" "ERROR"
    Read-Host "Press Enter to exit"
    exit 1
}

# ============================================
# STEP 3: Target 경로 확인
# ============================================
Write-Log "`n[STEP 3/6] Target 경로 확인" "INFO"
Write-Log ("─" * 70) "INFO"

$targetParent = Split-Path $TARGET_LINK -Parent

if (!(Test-Path $targetParent)) {
    Write-Log "⚠️  상위 디렉토리 없음. 생성 중..." "WARNING"
    New-Item -ItemType Directory -Path $targetParent -Force | Out-Null
    Write-Log "✅ 상위 디렉토리 생성 완료" "SUCCESS"
} else {
    Write-Log "✅ 상위 디렉토리 존재: $targetParent" "SUCCESS"
}

# 기존 링크/디렉토리 확인
if (Test-Path $TARGET_LINK) {
    $existingItem = Get-Item $TARGET_LINK
    
    if ($existingItem.LinkType -eq "SymbolicLink") {
        Write-Log "⚠️  심볼릭 링크가 이미 존재합니다" "WARNING"
        Write-Log "   Target: $($existingItem.Target)" "INFO"
        
        $response = Read-Host "`n기존 링크를 삭제하고 다시 생성하시겠습니까? (Y/N)"
        if ($response -eq "Y" -or $response -eq "y") {
            Remove-Item $TARGET_LINK -Force
            Write-Log "✅ 기존 링크 삭제 완료" "SUCCESS"
        } else {
            Write-Log "작업 취소됨" "WARNING"
            exit 0
        }
    } else {
        Write-Log "❌ Target 경로에 일반 디렉토리/파일이 존재합니다" "ERROR"
        Write-Log "   수동으로 삭제 후 다시 실행하세요: $TARGET_LINK" "ERROR"
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# ============================================
# STEP 4: 심볼릭 링크 생성
# ============================================
Write-Log "`n[STEP 4/6] 심볼릭 링크 생성" "INFO"
Write-Log ("─" * 70) "INFO"
Write-Log "Source: $SOURCE_DIR" "INFO"
Write-Log "Target: $TARGET_LINK" "INFO"
Write-Log "" "INFO"

try {
    $link = New-Item -ItemType SymbolicLink -Path $TARGET_LINK -Target $SOURCE_DIR -ErrorAction Stop
    Write-Log "✅ 심볼릭 링크 생성 성공!" "SUCCESS"
    Write-Log "   LinkType: $($link.LinkType)" "INFO"
    Write-Log "   Target: $($link.Target)" "INFO"
} catch {
    Write-Log "❌ 심볼릭 링크 생성 실패!" "ERROR"
    Write-Log "   오류: $($_.Exception.Message)" "ERROR"
    Write-Log "" "INFO"
    Write-Log "대안: Junction 생성을 시도합니다..." "WARNING"
    
    try {
        cmd /c mklink /J "$TARGET_LINK" "$SOURCE_DIR" 2>&1 | Out-Null
        Write-Log "✅ Junction 생성 성공!" "SUCCESS"
    } catch {
        Write-Log "❌ Junction 생성도 실패했습니다" "ERROR"
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# ============================================
# STEP 5: 검증
# ============================================
Write-Log "`n[STEP 5/6] 생성된 링크 검증" "INFO"
Write-Log ("─" * 70) "INFO"

if (Test-Path $TARGET_LINK) {
    $linkItem = Get-Item $TARGET_LINK
    Write-Log "✅ 링크 접근 가능" "SUCCESS"
    
    # 하위 디렉토리 접근 테스트
    $testDirs = @("logiontology", "output", "scripts")
    $allTestsPassed = $true
    
    foreach ($testDir in $testDirs) {
        $testPath = Join-Path $TARGET_LINK $testDir
        if (Test-Path $testPath) {
            Write-Log "   ✅ $testDir 접근 가능" "SUCCESS"
        } else {
            Write-Log "   ❌ $testDir 접근 불가" "ERROR"
            $allTestsPassed = $false
        }
    }
    
    if ($allTestsPassed) {
        Write-Log "`n✅ 모든 검증 통과!" "SUCCESS"
    } else {
        Write-Log "`n⚠️  일부 검증 실패" "WARNING"
    }
} else {
    Write-Log "❌ 링크를 찾을 수 없습니다" "ERROR"
    exit 1
}

# ============================================
# STEP 6: 인덱스 생성
# ============================================
Write-Log "`n[STEP 6/6] 인덱스 파일 생성" "INFO"
Write-Log ("─" * 70) "INFO"

$indexFile = "C:\cursor-mcp\logi_ontol_index.json"

$index = @{
    created = Get-Date -Format "o"
    source_path = $SOURCE_DIR
    link_path = $TARGET_LINK
    link_type = (Get-Item $TARGET_LINK).LinkType
    directories = @()
    file_count = 0
    total_size_mb = 0
}

# 주요 디렉토리 스캔
$mainDirs = Get-ChildItem $SOURCE_DIR -Directory -ErrorAction SilentlyContinue

foreach ($dir in $mainDirs) {
    $fileCount = (Get-ChildItem $dir.FullName -File -Recurse -ErrorAction SilentlyContinue).Count
    $index.directories += @{
        name = $dir.Name
        path = $dir.FullName
        file_count = $fileCount
    }
    $index.file_count += $fileCount
}

# JSON 저장
$index | ConvertTo-Json -Depth 10 | Out-File $indexFile -Encoding UTF8
Write-Log "✅ 인덱스 파일 생성: $indexFile" "SUCCESS"

# ============================================
# 완료
# ============================================
Write-Log "`n" -NoNewLine
Write-Log ("=" * 70) "SUCCESS"
Write-Log "🎉 설정 완료!" "SUCCESS"
Write-Log ("=" * 70) "SUCCESS"
Write-Log "" "INFO"
Write-Log "심볼릭 링크 정보:" "INFO"
Write-Log "  Source: $SOURCE_DIR" "INFO"
Write-Log "  Link:   $TARGET_LINK" "INFO"
Write-Log "  Type:   $((Get-Item $TARGET_LINK).LinkType)" "INFO"
Write-Log "" "INFO"
Write-Log "다음 단계:" "INFO"
Write-Log "  1. MCP 서버 설정 스크립트 실행" "INFO"
Write-Log "  2. Claude에서 /logi-master 명령어 테스트" "INFO"
Write-Log "" "INFO"
Write-Log "로그 파일: $LOG_FILE" "INFO"
Write-Log "" "INFO"

Read-Host "Press Enter to exit"
