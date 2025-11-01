# Protégé 자동 설치 스크립트 생성 완료

**날짜**: 2025-10-26
**상태**: ✅ 스크립트 생성 완료
**대기**: 사용자 실행 필요

---

## 생성된 스크립트 (3개)

### 1. GraphViz PATH 추가 스크립트

**파일**: `scripts/add_graphviz_to_path.ps1`
**라인 수**: ~70 lines
**요구사항**: 관리자 권한

**기능**:
- GraphViz 설치 경로 자동 탐지
  - `C:\Program Files\Graphviz\bin`
  - `C:\Program Files (x86)\Graphviz\bin`
  - `%LOCALAPPDATA%\Programs\Graphviz\bin`
- 시스템 PATH에 자동 추가
- 현재 세션 PATH 즉시 업데이트
- `dot -V` 명령으로 설치 검증

### 2. Protégé 자동 설치 스크립트

**파일**: `scripts/install_protege_windows.ps1`
**라인 수**: ~150 lines
**요구사항**: 관리자 권한, 인터넷 연결

**기능**:
- Protégé 5.6.4 다운로드 (GitHub releases, ~150 MB)
- `C:\Program Files\Protege-5.6.4\` 자동 압축 해제
- 설치 검증
- 데스크톱 바로가기 생성 (옵션)
- 이미 설치된 경우 재설치 선택 가능

### 3. 통합 설치 스크립트 (권장)

**파일**: `scripts/setup_protege_complete.ps1`
**라인 수**: ~150 lines
**요구사항**: 관리자 권한, 인터넷 연결

**기능**:
1. ✅ Java 확인 (이미 설치됨 - Java 25)
2. ✅ GraphViz PATH 추가
3. ⏳ Protégé 설치
4. ✅ OWLViz 설정 업데이트
5. ⏳ Protégé 자동 실행 (HVDC ontology 로드)

**통합 흐름**:
```powershell
setup_protege_complete.ps1
  ├─ check_java()
  ├─ add_graphviz_to_path.ps1
  ├─ install_protege_windows.ps1
  ├─ update_owlviz_config()
  └─ launch_protege(hvdc_ontology.ttl)
```

---

## 실행 방법

### Option A: 통합 스크립트 실행 (권장)

**PowerShell 관리자 권한으로 실행**:

```powershell
# 1. Windows PowerShell을 관리자 권한으로 실행
#    (시작 메뉴 → PowerShell → 우클릭 → 관리자 권한으로 실행)

# 2. 프로젝트 디렉토리로 이동
cd c:\logi_ontol

# 3. 통합 설치 스크립트 실행
.\scripts\setup_protege_complete.ps1
```

**예상 실행 시간**: 5-10분 (인터넷 속도에 따라)

**스크립트 실행 중**:
- ✅ Java 확인 (즉시 완료)
- ✅ GraphViz PATH 추가 (즉시 완료)
- ⏳ Protégé 다운로드 (5-10분, ~150 MB)
- ⏳ Protégé 압축 해제 (30초)
- ✅ OWLViz 설정 업데이트 (즉시 완료)
- ⏳ Protégé 자동 실행 (선택)

### Option B: 단계별 실행

```powershell
# Step 1: GraphViz PATH 추가 (관리자 권한 필요)
.\scripts\add_graphviz_to_path.ps1

# Step 2: Protégé 설치 (관리자 권한 필요)
.\scripts\install_protege_windows.ps1

# Step 3: Protégé 실행 (일반 권한 OK)
.\scripts\launch_protege_hvdc.bat
```

---

## 예상 출력

### setup_protege_complete.ps1 실행 시

```
========================================
HVDC Protégé Complete Setup
Version: 1.0
========================================

[STEP 1/5] Checking Java installation...
[OK] Java found: openjdk version "25" 2025-09-16 LTS

[STEP 2/5] Setting up GraphViz PATH...
========================================
GraphViz PATH Setup
========================================

[OK] Found GraphViz at: C:\Program Files\Graphviz\bin
[ACTION] Adding GraphViz to system PATH...
[OK] GraphViz added to system PATH

========================================
Verification
========================================

[OK] GraphViz dot command works:
     dot - graphviz version X.X.X

[STEP 3/5] Installing Protégé...
[ACTION] Downloading Protégé 5.6.4...
         URL: https://github.com/protegeproject/protege-distribution/releases/download/v5.6.4/Protege-5.6.4-win.zip
         This may take 5-10 minutes (approx. 150 MB)...

[OK] Download complete!
     Size: 150.XX MB

[ACTION] Extracting Protégé...
[OK] Extraction complete!
[ACTION] Cleaning up temporary files...
[OK] Cleanup complete!

========================================
Verification
========================================

[OK] Protégé executable found at:
     C:\Program Files\Protege-5.6.4\Protege.exe
     Version: 5.6.4

Create desktop shortcut? (Y/n): Y
[OK] Desktop shortcut created!

[STEP 4/5] Configuring OWLViz...
[OK] OWLViz configuration updated
     GraphViz path: C:\Program Files\Graphviz\bin\dot.exe

[STEP 5/5] Preparing Protégé launch...
[OK] HVDC ontology file found

========================================
[SUCCESS] Setup Complete!
========================================

Summary:
  ✓ Java: Installed
  ✓ GraphViz: Configured
  ✓ Protégé: Installed at C:\Program Files\Protege-5.6.4
  ✓ OWLViz: Configured
  ✓ HVDC Ontology: Ready

Next steps:
  1. Run: .\scripts\launch_protege_hvdc.bat
  2. Or launch manually: C:\Program Files\Protege-5.6.4\Protege.exe

After Protégé launches:
  1. Install plugins: File → Check for plugins...
     - Cellfie (for Excel import)
     - OWLViz (for visualization)
  2. Load SHACL: Window → Tabs → SHACL Shapes
  3. Import settings from:
     logiontology\configs\protege\

Launch Protégé now with HVDC ontology? (Y/n): Y
[OK] Protégé launched!
```

---

## 설치 후 작업 (사용자가 수행)

### 1. Protégé 플러그인 설치 (5분)

Protégé가 실행되면:

1. **Cellfie 플러그인 설치**
   - `File` → `Check for plugins...`
   - 검색: "Cellfie"
   - Install → Protégé 재시작

2. **OWLViz 플러그인 설치**
   - `File` → `Check for plugins...`
   - 검색: "OWLViz"
   - Install → Protégé 재시작

3. **SHACL Shapes 활성화** (기본 포함)
   - `Window` → `Tabs` → `SHACL Shapes`
   - 탭이 보이면 활성화됨

### 2. HVDC 설정 파일 적용 (5분)

**Cellfie 매핑**:
1. `Window` → `Tabs` → `Cellfie`
2. `File` → `Load Transformation`
3. 선택: `logiontology\configs\protege\cellfie_hvdc_mapping.transform`

**SHACL 제약조건**:
1. `Window` → `Tabs` → `SHACL Shapes`
2. `File` → `Load...`
3. 선택: `logiontology\configs\protege\hvdc_shacl_constraints.ttl`

**OWLViz 설정** (자동):
자동 적용됨 (`owlviz_config.properties`)

### 3. HVDC 데이터 테스트 (10분)

**샘플 Excel 준비**:
- 파일: `data/sample_hvdc.xlsx`
- 컬럼: HVDC_CODE, WEIGHT, WAREHOUSE, SITE, PORT

**Cellfie로 임포트**:
1. `File` → `New Ontology` 또는 HVDC ontology 열기
2. Cellfie 탭 열기
3. Excel 파일 선택
4. 변환 실행
5. 결과 확인: Cargo 인스턴스 10개 생성

**SHACL 검증**:
1. SHACL Shapes 탭 열기
2. `Validate` 버튼 클릭
3. 검증 결과 확인 (✅ Pass 또는 오류 메시지)

**OWLViz 시각화**:
1. OWLViz 탭 열기
2. Classes 탭에서 `Cargo` 선택
3. 계층 구조 그래프 확인
4. Export → PNG/SVG 저장

---

## 파일 위치 요약

| 파일 | 경로 | 상태 |
|------|------|------|
| **통합 설치 스크립트** | `scripts/setup_protege_complete.ps1` | ✅ 생성 완료 |
| GraphViz PATH 스크립트 | `scripts/add_graphviz_to_path.ps1` | ✅ 생성 완료 |
| Protégé 설치 스크립트 | `scripts/install_protege_windows.ps1` | ✅ 생성 완료 |
| 빠른 시작 배치 파일 | `scripts/launch_protege_hvdc.bat` | ✅ 생성 완료 (이전) |
| Protégé 설치 위치 | `C:\Program Files\Protege-5.6.4\` | ⏳ 설치 대기 |
| HVDC 온톨로지 | `logiontology/configs/ontology/hvdc_ontology.ttl` | ✅ 기존 파일 |
| Cellfie 매핑 | `logiontology/configs/protege/cellfie_hvdc_mapping.transform` | ✅ 기존 파일 |
| SHACL 제약 | `logiontology/configs/protege/hvdc_shacl_constraints.ttl` | ✅ 기존 파일 |
| OWLViz 설정 | `logiontology/configs/protege/owlviz_config.properties` | ✅ 기존 파일 (경로 포함) |

---

## 다음 단계 (사용자)

### 즉시 실행 (관리자 권한)

```powershell
cd c:\logi_ontol
.\scripts\setup_protege_complete.ps1
```

**작업 시간**: 5-10분

### 플러그인 설치 (Protégé에서)

- Cellfie (Excel → 온톨로지)
- OWLViz (시각화)
- SHACL (검증)

### 데이터 테스트

- Excel 파일 준비
- Cellfie로 임포트
- SHACL 검증
- OWLViz 시각화

---

## 주의사항

- **관리자 권한 필수**: PATH 수정을 위해
- **인터넷 연결 필요**: Protégé 다운로드 (약 150 MB)
- **예상 시간**: 5-10분 (인터넷 속도에 따라)
- **디스크 공간**: 약 200 MB 필요

---

## 트러블슈팅

### 스크립트가 실행되지 않는 경우

**문제**: PowerShell 실행 정책 오류

**해결**:
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### GraphViz PATH 추가 실패

**문제**: 관리자 권한 없음

**해결**:
- PowerShell을 관리자 권한으로 실행
- 또는 수동으로 환경 변수 편집

### Protégé 다운로드 실패

**문제**: 인터넷 연결 문제

**해결**:
- 방화벽 확인
- 프록시 설정 확인
- 수동 다운로드: https://github.com/protegeproject/protege/releases/tag/v5.6.4

---

**작업 완료**
**날짜**: 2025-10-26
**상태**: ✅ 스크립트 생성 완료
**다음 단계**: 사용자가 `setup_protege_complete.ps1` 실행

