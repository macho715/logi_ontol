# HVDC Full Stack MVP - Quick Start Guide

**소요 시간**: 5분
**난이도**: 초급

---

## 필수 요구사항

### 소프트웨어
- Python 3.13+
- Docker 20+
- Git

### 선택사항
- Neo4j 5.14+ (Docker 사용 시 불필요)
- Node.js 20+ (Frontend 개발 시)

---

## 빠른 시작 (5분)

### Step 1: 프로젝트 클론

```bash
# 프로젝트 디렉토리로 이동
cd c:\logi_ontol\logiontology

# 또는 Git clone (해당하는 경우)
# git clone <repository-url>
# cd logiontology
```

### Step 2: 의존성 설치

```bash
# Python 가상 환경 생성 (권장)
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Mac/Linux

# 개발 의존성 설치
pip install -e ".[dev,api,graph]"
```

### Step 3: Neo4j 시작 (Docker)

```bash
# Neo4j 컨테이너 시작
docker run -d \
  --name hvdc-neo4j \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/hvdc_password \
  neo4j:5.14

# 컨테이너 상태 확인
docker ps | grep hvdc-neo4j
```

**Neo4j Browser**: http://localhost:7474
**Credentials**: neo4j / hvdc_password

### Step 4: 샘플 데이터 준비

Excel 파일 생성 (`data/sample.xlsx`):

| HVDC_CODE | WEIGHT | WAREHOUSE | SITE | PORT | FLOW_CODE |
|-----------|--------|-----------|------|------|-----------|
| HVDC-001  | 25.5   | DSV INDOOR| MIR  | ZAYED| 2         |
| HVDC-002  | 18.3   | MOSB      | DAS  | KHALIFA| 3       |
| HVDC-003  | 42.0   | DSV INDOOR| SHU  | ZAYED| 2         |

### Step 5: 데이터 변환

```bash
# Excel → RDF 변환
logiontology ingest-excel data/sample.xlsx --out output/sample.ttl

# 출력: output/sample.ttl 생성됨
```

### Step 6: Neo4j 로드

```bash
# 환경 변수 설정
set NEO4J_PASSWORD=hvdc_password  # Windows
# export NEO4J_PASSWORD=hvdc_password  # Mac/Linux

# 데이터베이스 설정 (인덱스 + 제약조건)
logiontology setup-neo4j

# RDF → Neo4j 로드
logiontology load-neo4j output/sample.ttl
```

### Step 7: API 서버 시작

```bash
# FastAPI 서버 시작 (개발 모드)
logiontology serve-api --reload

# 출력:
# INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 8: API 테스트

**브라우저에서**:
- API Docs (Swagger): http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**cURL로 테스트**:
```bash
# Health check
curl http://localhost:8000/health

# KPI Dashboard
curl http://localhost:8000/api/kpi/

# Flow 목록
curl http://localhost:8000/api/flows
```

---

## Docker Compose 사용 (전체 스택)

### 한 번에 모든 서비스 시작

```bash
# 프로젝트 루트에서
cd logiontology

# 환경 변수 설정 (선택적)
echo "AI_API_KEY=your_claude_api_key" > .env

# 전체 스택 시작
docker-compose up -d

# 서비스 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f backend
```

### 서비스 접근

- **Neo4j Browser**: http://localhost:7474
- **API Docs**: http://localhost:8000/docs
- **Frontend** (구현 후): http://localhost:3000

### 종료

```bash
# 모든 서비스 중지
docker-compose down

# 데이터까지 삭제
docker-compose down -v
```

---

## 다음 단계

1. **데이터 탐색**
   - Neo4j Browser에서 Cypher 쿼리 실행
   - API Docs에서 엔드포인트 테스트

2. **문서 확인**
   - [API Reference](API_REFERENCE.md) - API 엔드포인트 상세
   - [Troubleshooting](TROUBLESHOOTING.md) - 문제 해결

3. **개발 시작**
   - [README_FULL_STACK.md](../../logiontology/README_FULL_STACK.md) - 전체 가이드
   - [ARCHITECTURE.md](../../logiontology/docs/ARCHITECTURE.md) - 아키텍처

---

## 일반적인 명령어

```bash
# 테스트 실행
pytest tests/ -v

# 코드 포맷팅
black src/ tests/
ruff check src/ tests/

# 타입 체킹
mypy src/

# 배치 처리
logiontology batch-ingest data/ --output-dir output/

# ID 생성
logiontology make-id --prefix HVDC --suffix 001
```

---

## 문제 발생 시

일반적인 문제는 [Troubleshooting Guide](TROUBLESHOOTING.md)를 참고하세요.

**자주 발생하는 문제**:
- Neo4j 연결 실패 → 컨테이너 상태 및 포트 확인
- 모듈 없음 오류 → 가상 환경 활성화 및 의존성 재설치
- 포트 충돌 → 기존 프로세스 종료 또는 다른 포트 사용

---

**축하합니다!** 🎉
HVDC Full Stack MVP를 성공적으로 시작했습니다.

