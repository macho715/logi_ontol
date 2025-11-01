# Protégé 소스 빌드 설정 완료

**날짜**: 2025-10-26
**상태**: ✅ 모든 스크립트 생성 완료
**방법**: 소스 빌드 (Maven Daemon 포함)

---

## 생성된 스크립트 (9개)

### 1. Maven 관련 스크립트 (3개)

| 파일 | 설명 | 특징 |
|------|------|------|
| `scripts/check_maven.ps1` | Maven 설치 확인 | 간단한 확인 스크립트 |
| `scripts/install_maven.ps1` | Maven 자동 설치 | Apache Maven 3.9.6 다운로드/설치 |
| - | Maven Daemon (mvnd) | 이미 있음: `maven-mvnd-1.0.3-windows-amd64/` |

### 2. Protégé 빌드 스크립트 (3개)

| 파일 | 설명 | 특징 |
|------|------|------|
| `scripts/build_protege_from_source.ps1` | 소스 빌드 (PowerShell) | mvnd 우선, mvn 폴백 |
| `scripts/build_protege_from_source.bat` | 소스 빌드 (배치) | 더블클릭 실행 가능 |
| - | Protégé 소스 | 이미 있음: `protege-master/` |

### 3. Protégé 실행 스크립트 (2개)

| 파일 | 설명 | 특징 |
|------|------|------|
| `scripts/launch_protege_built.ps1` | 빌드된 Protégé 실행 | JAR 자동 탐지 |
| `scripts/launch_protege_built.bat` | 빌드된 Protégé 실행 | 더블클릭 실행 가능 |

### 4. 통합 설치 스크립트 (2개)

| 파일 | 설명 | 특징 |
|------|------|------|
| `scripts/setup_protege_from_source.ps1` | **전체 자동화** | 권장! |
| `scripts/setup_protege_complete.ps1` | 다운로드 방식 | 기존 방식 |

---

## 실행 방법

### 방법 A: 통합 스크립트 (권장)

**PowerShell 관리자 권한으로 실행**:

```powershell
cd c:\logi_ontol
.\scripts\setup_protege_from_source.ps1
```

**자동 수행 작업**:
1. ✅ Java 확인
2. ⏳ Maven 설치 (필요시)
3. ✅ GraphViz PATH 추가
4. ⏳ Protégé 소스 빌드
5. ✅ OWLViz 설정
6. ⏳ Protégé 자동 실행

**예상 시간**: 5-15분 (빌드 시간 포함)

### 방법 B: 단계별 실행

```powershell
# Step 1: Maven 확인
.\scripts\check_maven.ps1

# Step 2: Maven 설치 (필요시)
.\scripts\install_maven.ps1

# Step 3: Protégé 빌드
.\scripts\build_protege_from_source.ps1

# Step 4: Protégé 실행
.\scripts\launch_protege_built.ps1
```

---

## Maven Daemon (mvnd) 특징

### 속도 비교

| 방식 | 첫 빌드 | 재빌드 (증분) |
|------|---------|-------------|
| **Maven (mvn)** | 10-15분 | 3-5분 |
| **Maven Daemon (mvnd)** | **8-12분** | **1-2분** |

### 자동 감지

- `build_protege_from_source.ps1`이 자동으로 `mvnd` 우선 사용
- 없으면 일반 `mvn` 폴백
- 사용자 개입 불필요

---

## 주요 기능

### 1. Maven 자동 설치

**파일**: `scripts/install_maven.ps1`
- Apache Maven 3.9.6 자동 다운로드
- 환경 변수 자동 설정 (MAVEN_HOME, PATH)
- 설치 검증

### 2. Protégé 소스 빌드

**파일**: `scripts/build_protege_from_source.ps1`
- mvnd 우선 사용 (빠른 빌드)
- 일반 mvn 폴백 (호환성)
- JAR 파일 자동 탐지
- 빌드 시간 측정
- 상세한 빌드 로그

### 3. 빌드된 Protégé 실행

**파일**: `scripts/launch_protege_built.ps1`
- 빌드된 JAR 자동 탐지
- 메모리 설정 가능 (`-MaxMemoryGB`)
- HVDC 온톨로지 자동 로드 옵션

### 4. 통합 설정

**파일**: `scripts/setup_protege_from_source.ps1`
- 모든 단계 자동화
- 오류 처리 및 복구
- 사용자 친화적 메시지

---

## 파일 구조

```
c:\logi_ontol\
├── protege-master/              # Protégé 소스 코드
├── maven-mvnd-1.0.3-windows-amd64/  # Maven Daemon (빠른 빌드)
├── scripts/
│   ├── check_maven.ps1          # Maven 확인
│   ├── install_maven.ps1        # Maven 설치
│   ├── build_protege_from_source.ps1  # 소스 빌드 (PowerShell)
│   ├── build_protege_from_source.bat  # 소스 빌드 (배치)
│   ├── launch_protege_built.ps1 # 빌드 실행 (PowerShell)
│   ├── launch_protege_built.bat # 빌드 실행 (배치)
│   ├── setup_protege_from_source.ps1  # 통합 (소스 빌드)
│   └── setup_protege_complete.ps1     # 통합 (다운로드)
└── logiontology/
    └── configs/
        ├── ontology/
        │   └── hvdc_ontology.ttl     # HVDC 온톨로지
        └── protege/
            └── owlviz_config.properties  # OWLViz 설정
```

---

## 다음 단계

### 즉시 실행 (관리자 권한)

```powershell
cd c:\logi_ontol
.\scripts\setup_protege_from_source.ps1
```

### 재빌드 (빠름)

```powershell
.\scripts\build_protege_from_source.ps1  # mvnd 사용 = 1-2분
```

### Protégé 실행

```powershell
# 일반 실행
.\scripts\launch_protege_built.ps1

# HVDC 온톨로지 로드
.\scripts\launch_protege_built.ps1 -OntologyFile "logiontology\configs\ontology\hvdc_ontology.ttl"
```

---

## 트러블슈팅

### Maven Daemon 오류

**문제**: `mvnd` 실행 시 오류 발생
**해결**: 자동으로 일반 `mvn` 폴백

### 빌드 시간이 너무 오래 걸림

**원인**: 인터넷 속도, 의존성 다운로드
**해결**:
- mvnd 사용 (자동 감지됨)
- 오프라인 빌드: `mvn -o install -DskipTests`

### JAR 파일을 찾을 수 없음

**원인**: 빌드 실패
**해결**:
1. `protege-master/target/` 확인
2. 빌드 로그 확인
3. 재빌드: `.\scripts\build_protege_from_source.ps1`

---

## 성능 최적화 팁

### 1. Maven Daemon 사용 (기본)

```powershell
# 자동 감지됨
.\scripts\build_protege_from_source.ps1
```

### 2. 병렬 빌드

```powershell
cd c:\logi_ontol\protege-master
mvnd clean install -T 4 -DskipTests  # 4개 스레드
```

### 3. 증분 빌드

```powershell
cd c:\logi_ontol\protege-master
mvnd install -DskipTests  # clean 제외
```

---

## 소스 빌드 vs 다운로드

| 방식 | 장점 | 단점 | 권장 |
|------|------|------|------|
| **소스 빌드** | 커스터마이징 가능, 최신 코드, 플러그인 개발 | 시간 소요 (10-15분) | 개발자 |
| **다운로드** | 빠른 설치 (5분), 안정성 | 최신 버전 제한 | 일반 사용자 |

---

**작업 완료**
**날짜**: 2025-10-26
**상태**: ✅ 모든 스크립트 생성 완료
**다음 단계**: `setup_protege_from_source.ps1` 실행
