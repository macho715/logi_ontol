# ============================================
# LOGI-ONTOL MCP 서버 설치 및 설정
# ============================================
# 실행: PowerShell에서 .\setup_mcp_server.ps1

$ErrorActionPreference = "Stop"

Write-Host "`n"
Write-Host "🚀 LOGI-ONTOL MCP 서버 설치 시작" -ForegroundColor Cyan
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host ""

# ============================================
# 설정
# ============================================
$MCP_DIR = "C:\cursor-mcp\mcp-servers\logi-ontol"
$LOG_FILE = "C:\cursor-mcp\logs\mcp_setup_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"

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
        [string]$Level = "INFO",
        [switch]$NoNewLine
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp][$Level] $Message"
    
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
    
    Add-Content -Path $LOG_FILE -Value $logEntry
}

# ============================================
# STEP 1: Node.js 확인
# ============================================
Write-Log "`n[STEP 1/7] Node.js 확인" "INFO"
Write-Log ("─" * 70) "INFO"

try {
    $nodeVersion = node --version
    Write-Log "✅ Node.js 설치됨: $nodeVersion" "SUCCESS"
    
    # Check if version is >= 18
    $versionNumber = [int]($nodeVersion -replace '[^0-9]','')[0..1] -join ''
    if ($versionNumber -lt 18) {
        Write-Log "⚠️  경고: Node.js 18 이상 권장. 현재: $nodeVersion" "WARNING"
    }
} catch {
    Write-Log "❌ Node.js가 설치되어 있지 않습니다!" "ERROR"
    Write-Log "" "INFO"
    Write-Log "해결 방법:" "WARNING"
    Write-Log "  1. https://nodejs.org 방문" "INFO"
    Write-Log "  2. LTS 버전 다운로드 및 설치" "INFO"
    Write-Log "  3. PowerShell 재시작 후 이 스크립트 다시 실행" "INFO"
    Write-Log "" "INFO"
    Read-Host "Press Enter to exit"
    exit 1
}

try {
    $npmVersion = npm --version
    Write-Log "✅ npm 설치됨: $npmVersion" "SUCCESS"
} catch {
    Write-Log "❌ npm이 설치되어 있지 않습니다!" "ERROR"
    exit 1
}

# ============================================
# STEP 2: Python 확인
# ============================================
Write-Log "`n[STEP 2/7] Python 확인" "INFO"
Write-Log ("─" * 70) "INFO"

try {
    $pythonVersion = python --version
    Write-Log "✅ Python 설치됨: $pythonVersion" "SUCCESS"
} catch {
    Write-Log "⚠️  Python이 설치되어 있지 않습니다" "WARNING"
    Write-Log "   일부 기능(SPARQL 쿼리)이 제한될 수 있습니다" "WARNING"
}

# ============================================
# STEP 3: 디렉토리 생성
# ============================================
Write-Log "`n[STEP 3/7] 디렉토리 구조 생성" "INFO"
Write-Log ("─" * 70) "INFO"

if (!(Test-Path $MCP_DIR)) {
    New-Item -ItemType Directory -Path $MCP_DIR -Force | Out-Null
    Write-Log "✅ MCP 서버 디렉토리 생성: $MCP_DIR" "SUCCESS"
} else {
    Write-Log "✅ MCP 서버 디렉토리 존재: $MCP_DIR" "SUCCESS"
}

# ============================================
# STEP 4: 파일 복사
# ============================================
Write-Log "`n[STEP 4/7] 서버 파일 복사" "INFO"
Write-Log ("─" * 70) "INFO"

# 다운로드한 파일들을 MCP 디렉토리로 복사
$sourceFiles = @(
    @{Source="logi-ontol-server.js"; Dest="logi-ontol-server.js"},
    @{Source="package.json"; Dest="package.json"}
)

foreach ($file in $sourceFiles) {
    $sourcePath = Join-Path $PSScriptRoot $file.Source
    $destPath = Join-Path $MCP_DIR $file.Dest
    
    if (Test-Path $sourcePath) {
        Copy-Item $sourcePath $destPath -Force
        Write-Log "✅ 복사 완료: $($file.Dest)" "SUCCESS"
    } else {
        Write-Log "⚠️  파일 없음: $($file.Source)" "WARNING"
        Write-Log "   수동으로 복사해주세요" "WARNING"
    }
}

# ============================================
# STEP 5: npm 패키지 설치
# ============================================
Write-Log "`n[STEP 5/7] npm 패키지 설치" "INFO"
Write-Log ("─" * 70) "INFO"
Write-Log "설치 중... (1-2분 소요)" "INFO"

Push-Location $MCP_DIR

try {
    npm install --production 2>&1 | Out-Null
    Write-Log "✅ npm 패키지 설치 완료" "SUCCESS"
} catch {
    Write-Log "❌ npm 패키지 설치 실패" "ERROR"
    Write-Log "   오류: $($_.Exception.Message)" "ERROR"
    Write-Log "   수동 설치: cd $MCP_DIR && npm install" "WARNING"
}

Pop-Location

# ============================================
# STEP 6: Claude Desktop 설정 업데이트
# ============================================
Write-Log "`n[STEP 6/7] Claude Desktop 설정 업데이트" "INFO"
Write-Log ("─" * 70) "INFO"

$claudeConfigPath = "$env:APPDATA\Claude\claude_desktop_config.json"

if (Test-Path $claudeConfigPath) {
    Write-Log "✅ Claude Desktop 설정 파일 발견" "SUCCESS"
    
    try {
        $config = Get-Content $claudeConfigPath -Raw | ConvertFrom-Json
        
        # mcpServers 객체가 없으면 생성
        if (-not $config.mcpServers) {
            $config | Add-Member -MemberType NoteProperty -Name "mcpServers" -Value @{}
        }
        
        # logi-ontol 서버 추가
        $logiOntolConfig = @{
            command = "node"
            args = @("$MCP_DIR\logi-ontol-server.js")
            env = @{
                LOGI_ONTOL_PATH = "C:\cursor-mcp\logi_ontol_link"
            }
        }
        
        $config.mcpServers | Add-Member -MemberType NoteProperty -Name "logi-ontol" -Value $logiOntolConfig -Force
        
        # 백업 생성
        $backupPath = "$claudeConfigPath.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
        Copy-Item $claudeConfigPath $backupPath
        Write-Log "✅ 기존 설정 백업: $backupPath" "SUCCESS"
        
        # 새 설정 저장
        $config | ConvertTo-Json -Depth 10 | Set-Content $claudeConfigPath
        Write-Log "✅ Claude Desktop 설정 업데이트 완료" "SUCCESS"
        
    } catch {
        Write-Log "⚠️  설정 파일 업데이트 실패" "WARNING"
        Write-Log "   오류: $($_.Exception.Message)" "WARNING"
        Write-Log "   수동으로 다음 내용을 추가하세요:" "INFO"
        Write-Log "" "INFO"
        
        $manualConfig = @"
{
  "mcpServers": {
    "logi-ontol": {
      "command": "node",
      "args": ["$MCP_DIR\\logi-ontol-server.js"],
      "env": {
        "LOGI_ONTOL_PATH": "C:\\cursor-mcp\\logi_ontol_link"
      }
    }
  }
}
"@
        Write-Log $manualConfig "INFO"
    }
} else {
    Write-Log "⚠️  Claude Desktop 설정 파일 없음" "WARNING"
    Write-Log "   경로: $claudeConfigPath" "WARNING"
    Write-Log "   Claude Desktop이 설치되어 있는지 확인하세요" "WARNING"
}

# ============================================
# STEP 7: 테스트
# ============================================
Write-Log "`n[STEP 7/7] 서버 테스트" "INFO"
Write-Log ("─" * 70) "INFO"

# 심볼릭 링크 확인
if (Test-Path "C:\cursor-mcp\logi_ontol_link") {
    Write-Log "✅ 심볼릭 링크 확인됨" "SUCCESS"
} else {
    Write-Log "❌ 심볼릭 링크 없음!" "ERROR"
    Write-Log "   먼저 setup_logi_symlink.ps1을 실행하세요" "ERROR"
}

# 간단한 서버 시작 테스트 (5초 후 종료)
Write-Log "서버 시작 테스트 중..." "INFO"

$serverProcess = Start-Process -FilePath "node" `
    -ArgumentList "$MCP_DIR\logi-ontol-server.js" `
    -PassThru `
    -NoNewWindow `
    -RedirectStandardError "$MCP_DIR\test_error.log"

Start-Sleep -Seconds 2

if ($serverProcess -and !$serverProcess.HasExited) {
    Write-Log "✅ 서버 시작 성공" "SUCCESS"
    Stop-Process -Id $serverProcess.Id -Force
} else {
    Write-Log "⚠️  서버 시작 확인 불가" "WARNING"
    if (Test-Path "$MCP_DIR\test_error.log") {
        $errorLog = Get-Content "$MCP_DIR\test_error.log" -Raw
        if ($errorLog) {
            Write-Log "에러 로그:" "WARNING"
            Write-Log $errorLog "WARNING"
        }
    }
}

# ============================================
# 완료
# ============================================
Write-Log "`n" -NoNewLine
Write-Log ("=" * 70) "SUCCESS"
Write-Log "🎉 MCP 서버 설치 완료!" "SUCCESS"
Write-Log ("=" * 70) "SUCCESS"
Write-Log "" "INFO"

Write-Log "설치 정보:" "INFO"
Write-Log "  서버 경로: $MCP_DIR" "INFO"
Write-Log "  설정 파일: $claudeConfigPath" "INFO"
Write-Log "" "INFO"

Write-Log "다음 단계:" "INFO"
Write-Log "  1. Claude Desktop 재시작" "INFO"
Write-Log "  2. Claude에서 'list tools' 입력하여 logi-ontol 도구 확인" "INFO"
Write-Log "  3. 테스트: read_ontology tool로 abu_final.ttl 읽기" "INFO"
Write-Log "" "INFO"

Write-Log "사용 가능한 도구:" "INFO"
Write-Log "  • read_ontology - RDF 파일 읽기" "INFO"
Write-Log "  • list_ontologies - 온톨로지 목록" "INFO"
Write-Log "  • query_sparql - SPARQL 쿼리 실행" "INFO"
Write-Log "  • get_statistics - 지식 그래프 통계" "INFO"
Write-Log "  • process_invoice - 인보이스 OCR 처리" "INFO"
Write-Log "  • list_jpt71_files - JPT71 파일 목록" "INFO"
Write-Log "" "INFO"

Write-Log "로그 파일: $LOG_FILE" "INFO"
Write-Log "" "INFO"

# 빠른 테스트 제안
Write-Log "빠른 테스트 명령어 (Claude에서):" "INFO"
Write-Log "  list_ontologies" "INFO"
Write-Log "  list_jpt71_files with file_type='pdf'" "INFO"
Write-Log "" "INFO"

Read-Host "Press Enter to exit"
