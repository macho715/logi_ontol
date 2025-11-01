# HVDC Full Stack MVP - Troubleshooting Guide

**Version**: 2.0.0
**Last Updated**: 2025-10-26

---

## 일반적인 문제

### 1. Neo4j 연결 실패

**증상**:
```
ConnectionError: Could not connect to Neo4j at bolt://localhost:7687
```

**원인**:
- Neo4j 서버가 실행되지 않음
- 포트가 다른 프로세스에 의해 사용 중
- 잘못된 인증 정보

**해결 방법**:

```bash
# 1. Neo4j 컨테이너 상태 확인
docker ps | grep neo4j

# 출력이 없으면 Neo4j가 실행되지 않은 것
# 다시 시작:
docker start hvdc-neo4j

# 또는 새로 생성:
docker run -d --name hvdc-neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/hvdc_password \
  neo4j:5.14

# 2. 포트 확인
netstat -an | grep 7687  # Windows
lsof -i :7687  # Mac/Linux

# 3. 로그 확인
docker logs hvdc-neo4j

# 4. 재시작
docker restart hvdc-neo4j
```

**환경 변수 확인**:
```bash
# Windows
echo %NEO4J_PASSWORD%

# Mac/Linux
echo $NEO4J_PASSWORD

# 설정되지 않았으면:
set NEO4J_PASSWORD=hvdc_password  # Windows
export NEO4J_PASSWORD=hvdc_password  # Mac/Linux
```

---

### 2. 모듈 없음 오류

**증상**:
```
ModuleNotFoundError: No module named 'fastapi'
ModuleNotFoundError: No module named 'pyshacl'
```

**원인**:
- 가상 환경이 활성화되지 않음
- 의존성이 설치되지 않음

**해결 방법**:

```bash
# 1. 가상 환경 활성화 확인
# 프롬프트에 (.venv) 또는 (logiontology) 표시되어야 함

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate

# 2. 의존성 재설치
pip install -e ".[dev,api,graph]"

# 특정 모듈만:
pip install pyshacl
pip install fastapi uvicorn[standard]
pip install neo4j
```

---

### 3. WeasyPrint 설치 오류 (Windows)

**증상**:
```
OSError: no library called "cairo-2" was found
OSError: no library called "cairo" was found
```

**원인**:
- Windows에서 GTK+ 라이브러리 누락

**해결 방법**:

**옵션 A: GTK+ 설치** (권장)
1. [GTK+ for Windows](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases) 다운로드
2. 설치 실행
3. Python 재시작

**옵션 B: Conda 사용**
```bash
conda install -c conda-forge weasyprint
```

**옵션 C: WSL 사용**
```bash
# Windows Subsystem for Linux에서 개발
wsl
pip install weasyprint
```

---

### 4. API 서버 포트 충돌

**증상**:
```
OSError: [Errno 48] Address already in use
OSError: [Errno 10048] Only one usage of each socket address is normally permitted
```

**원인**:
- 8000 포트가 이미 사용 중

**해결 방법**:

```bash
# 옵션 A: 다른 포트 사용
logiontology serve-api --port 8001

# 옵션 B: 기존 프로세스 종료 (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# 옵션 C: 기존 프로세스 종료 (Mac/Linux)
lsof -ti:8000 | xargs kill -9
```

---

### 5. SHACL 검증 실패

**증상**:
```
SHACLValidationError: Validation failed
  - sh:minCount constraint violation
  - sh:datatype constraint violation
```

**원인**:
- Excel 데이터가 온톨로지 제약을 위반

**해결 방법**:

```bash
# 1. SHACL 검증 비활성화 (임시)
logiontology ingest-excel data/sample.xlsx --skip-validation

# 2. 데이터 수정
# - Flow Code: 0-4 범위 확인
# - Weight: 양수 확인
# - 필수 컬럼: HVDC_CODE, WEIGHT, SITE 존재 확인

# 3. 검증 다시 실행
logiontology ingest-excel data/sample.xlsx
```

**일반적인 제약 조건**:
- `flowCodeValue`: 0-4 범위
- `weight`: 양수 (> 0)
- `hasHVDCCode`: 필수
- `destinedTo`: 필수 (Site)

---

### 6. Docker Compose 실패

**증상**:
```
ERROR: Service 'backend' failed to build
ERROR: for neo4j  Cannot start service neo4j
```

**원인**:
- Docker 데몬이 실행되지 않음
- 이미지 빌드 실패
- 포트 충돌

**해결 방법**:

```bash
# 1. Docker 상태 확인
docker info

# 2. 로그 확인
docker-compose logs backend
docker-compose logs neo4j

# 3. 포트 충돌 해결
# docker-compose.yml 수정:
# backend:
#   ports:
#     - "8001:8000"  # 호스트 포트 변경

# 4. 이미지 재빌드
docker-compose build --no-cache

# 5. 전체 재시작
docker-compose down -v
docker-compose up -d
```

---

### 7. Excel 파일 읽기 오류

**증상**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'data/sample.xlsx'
ValueError: Excel file must contain required columns
```

**원인**:
- 파일 경로 오류
- 필수 컬럼 누락

**해결 방법**:

```bash
# 1. 파일 존재 확인
ls data/sample.xlsx  # Mac/Linux
dir data\sample.xlsx  # Windows

# 2. 절대 경로 사용
logiontology ingest-excel c:\logi_ontol\data\sample.xlsx

# 3. 필수 컬럼 확인
# HVDC_CODE, WEIGHT, SITE는 필수
# WAREHOUSE, PORT, FLOW_CODE는 선택적
```

**최소 Excel 형식**:
| HVDC_CODE | WEIGHT | SITE |
|-----------|--------|------|
| HVDC-001  | 25.5   | MIR  |

---

### 8. Neo4j 인덱스 생성 실패

**증상**:
```
Neo.ClientError.Schema.EquivalentSchemaRuleAlreadyExists
```

**원인**:
- 인덱스가 이미 존재

**해결 방법**:

```bash
# 옵션 A: 인덱스 삭제 후 재생성
# Neo4j Browser (http://localhost:7474)에서:
DROP INDEX flow_code_idx IF EXISTS;
DROP INDEX hvdc_code_idx IF EXISTS;

# 다시 설정:
logiontology setup-neo4j

# 옵션 B: 기존 인덱스 사용
# 이미 존재하면 setup-neo4j는 스킵됨 (정상)
```

---

### 9. API 응답이 비어있음

**증상**:
```json
{
  "total": 0,
  "flows": []
}
```

**원인**:
- Neo4j에 데이터가 없음
- API가 Neo4j와 연결되지 않음 (v2.0.0 stub 구현)

**해결 방법**:

```bash
# 1. Neo4j 데이터 확인
# Neo4j Browser에서:
MATCH (c:Cargo) RETURN COUNT(c)

# 0이면 데이터 로드:
logiontology load-neo4j output/sample.ttl

# 2. v2.0.0 제한사항
# 현재 버전은 stub 구현 (빈 데이터 반환)
# Phase 2A에서 실제 Neo4j 쿼리 연결 예정
```

---

### 10. 테스트 실패

**증상**:
```
FAILED tests/unit/test_flow_code.py::test_calculate_flow_code
AssertionError: assert 1 == 2
```

**원인**:
- 코드 변경으로 인한 기대값 불일치
- 환경 차이

**해결 방법**:

```bash
# 1. 상세 로그로 실행
pytest tests/unit/test_flow_code.py -v -s

# 2. 특정 테스트만 실행
pytest tests/unit/test_flow_code.py::test_calculate_flow_code -v

# 3. 캐시 삭제
pytest --cache-clear

# 4. 가상 환경 재생성
deactivate
rm -rf .venv
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev,api,graph]"
```

---

## 플랫폼별 주의사항

### Windows

1. **경로 구분자**:
   - Python: `/` 또는 `\\` (이스케이프)
   - Windows: `\`

2. **환경 변수**:
   ```cmd
   set VAR=value  # CMD
   $env:VAR="value"  # PowerShell
   ```

3. **Docker Desktop**:
   - Hyper-V 또는 WSL 2 필요
   - 가상화 활성화 확인

### Mac (Apple Silicon)

1. **Docker 이미지**:
   - ARM64 이미지 사용 (자동)
   - 호환성 문제 시 `--platform linux/amd64` 추가

2. **Python 설치**:
   ```bash
   # Homebrew 권장
   brew install python@3.13
   ```

### Linux

1. **Docker 권한**:
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```

2. **시스템 의존성** (WeasyPrint):
   ```bash
   sudo apt-get install libcairo2-dev libpango1.0-dev
   ```

---

## 성능 문제

### API 응답 느림 (>5초)

**원인**:
- 대량 데이터
- 비효율적 쿼리

**해결 방법**:

```bash
# 1. 쿼리 최적화 (Neo4j)
# Neo4j Browser에서 실행 계획 확인:
EXPLAIN MATCH (c:Cargo) RETURN c

# 2. 인덱스 확인
SHOW INDEXES

# 3. Pagination 사용
curl "http://localhost:8000/api/flows?limit=10&offset=0"

# 4. Redis 캐싱 (Phase 3)
# 추후 구현 예정
```

### Excel 변환 느림 (>30초)

**원인**:
- 대용량 파일 (>1000행)

**해결 방법**:

```bash
# 1. 파일 분할
# 500행씩 분할 처리

# 2. 배치 처리 사용
logiontology batch-ingest data/ --output-dir output/

# 3. SHACL 검증 비활성화 (임시)
# 변환 후 별도로 검증
```

---

## 로깅 및 디버깅

### 로그 레벨 설정

```bash
# 환경 변수로 설정
set LOG_LEVEL=DEBUG  # Windows
export LOG_LEVEL=DEBUG  # Mac/Linux

# API 서버 실행
logiontology serve-api --reload
```

### Python 디버깅

```python
# 코드에 breakpoint 추가
import pdb; pdb.set_trace()

# 또는
breakpoint()  # Python 3.7+
```

### Docker 로그

```bash
# 컨테이너 로그 확인
docker logs hvdc-neo4j
docker-compose logs -f backend

# 로그 파일 저장
docker logs hvdc-neo4j > neo4j.log 2>&1
```

---

## 자주 묻는 질문 (FAQ)

### Q1: v2.0.0에서 API가 빈 데이터를 반환하는 이유는?

**A**: 현재 버전은 Backend Core만 완료되었으며, API 엔드포인트는 stub 구현입니다. Phase 2A에서 실제 Neo4j 쿼리 연결이 구현될 예정입니다.

### Q2: Flow Code가 자동으로 계산되나요?

**A**: 네, Excel 파일에 FLOW_CODE 컬럼이 없으면 자동으로 계산됩니다. 계산 로직은 `wh_handling`, `offshore_flag` 기반입니다.

### Q3: Neo4j 데이터를 초기화하려면?

**A**:
```bash
# 옵션 A: 컨테이너 재생성
docker-compose down -v
docker-compose up -d

# 옵션 B: Cypher로 삭제
# Neo4j Browser에서:
MATCH (n) DETACH DELETE n
```

### Q4: 여러 Excel 파일을 한 번에 처리하려면?

**A**:
```bash
logiontology batch-ingest data/ --output-dir output/ --pattern "*.xlsx"
```

### Q5: 온톨로지를 수정하려면?

**A**: `logiontology/configs/ontology/hvdc_ontology.ttl` 파일을 텍스트 에디터로 수정 후, 데이터를 다시 로드합니다.

---

## 추가 지원

### 문서
- [Quick Start Guide](QUICK_START.md) - 빠른 시작
- [API Reference](API_REFERENCE.md) - API 상세
- [README_FULL_STACK.md](../../logiontology/README_FULL_STACK.md) - 전체 가이드

### 커뮤니티
- GitHub Issues: 버그 리포트 및 기능 요청
- 프로젝트 관리자: 기술 지원 문의

---

**마지막 업데이트**: 2025-10-26
**버전**: 2.0.0

