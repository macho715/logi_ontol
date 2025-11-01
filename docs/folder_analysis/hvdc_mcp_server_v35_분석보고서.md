# hvdc_mcp_server_v35/ 분석 보고서

**생성일**: 2025-11-01
**분석 범위**: hvdc_mcp_server_v35/ 전체 폴더
**버전**: v3.5

---

## 1. 개요

### 폴더 경로
```
c:\logi_ontol\hvdc_mcp_server_v35\
```

### 주요 목적
MCP (Model Context Protocol) Server v3.5는 Flow Code v3.5 TTL 데이터에 대한 **SPARQL 쿼리 서버**입니다. FastAPI 기반 REST API를 통해 온톨로지 데이터를 실시간으로 쿼리하고 분석할 수 있습니다.

### 프로젝트 내 역할
- **SPARQL 서버**: TTL 데이터에 대한 쿼리 엔드포인트 제공
- **Flow Code 분석**: v3.5 분류 통계 및 분석
- **도메인 룰 검증**: AGI/DAS 준수 여부 확인
- **GPT 통합**: GPT Custom Actions를 통한 자연어 쿼리 지원
- **CLI 도구**: 명령행 인터페이스 제공

### 중요도
⭐⭐⭐⭐⭐ **최우선** - 데이터 쿼리 및 분석의 핵심 인프라

---

## 2. 통계

### 파일 수
- **총 파일 수**: 약 15개
- **하위 디렉토리 수**: 2개 (mcp_server/, tests/)
- **Python 파일**: 5개 (mcp_server/)
- **테스트 파일**: 3개 (tests/)
- **설정 파일**: 3개 (Docker, requirements)

### 파일 타입별 분류
- **.py**: Python 소스 코드 (9개)
- **.yml**: Docker Compose 설정 (1개)
- **.txt**: 요구사항 파일 (1개)
- **.md**: README (1개)

---

## 3. 주요 파일

### 핵심 소스 코드 (mcp_server/)
1. **mcp_ttl_server.py** - FastAPI 애플리케이션 및 6개 엔드포인트
2. **sparql_engine.py** - SPARQL 쿼리 엔진 및 RDFLib 통합
3. **commands.py** - CLI 명령어 (Click 기반)
4. **config.py** - 설정 관리 (TTL 경로, 환경 변수)

### 테스트 파일 (tests/)
1. **test_sparql_queries.py** - SPARQL 쿼리 테스트
2. **test_mcp_server.py** - 서버 엔드포인트 테스트
3. **test_mcp_integration.py** - 통합 테스트

### 설정 파일
1. **requirements.txt** - Python 의존성 (6개)
2. **docker-compose.yml** - Docker 배포 설정
3. **Dockerfile** - 컨테이너 이미지

### 문서
1. **README.md** - 전체 가이드 (155 라인)

---

## 4. 하위 구조

### mcp_server/ (핵심 모듈)
```
mcp_server/
├── __init__.py              # 패키지 초기화
├── mcp_ttl_server.py        # FastAPI 앱 + 6개 엔드포인트
├── sparql_engine.py         # SPARQL 엔진
├── commands.py              # CLI 명령어 (6개)
└── config.py                # 설정 관리
```

### tests/ (테스트)
```
tests/
├── __init__.py
├── test_sparql_queries.py   # SPARQL 테스트
├── test_mcp_server.py       # API 테스트
└── test_mcp_integration.py  # 통합 테스트
```

### 루트 파일
```
hvdc_mcp_server_v35/
├── docker-compose.yml       # Docker 설정
├── Dockerfile               # 컨테이너 이미지
├── requirements.txt         # 의존성
├── README.md                # 가이드
└── test_load.py             # 로드 테스트
```

---

## 5. 연관성

### 입력 데이터
- **output/hvdc_status_v35.ttl** - Flow Code v3.5 TTL 데이터 (9,904 triples, 755 cases)
- **logiontology/**: Excel → TTL 변환 파이프라인

### 출력/서비스
- **REST API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **GPT Custom Actions**: OpenAPI 스펙

### 의존성
- **FastAPI**: REST API 프레임워크
- **RDFLib**: RDF/TTL 파싱 및 쿼리
- **Click**: CLI 인터페이스
- **pytest**: 테스트 프레임워크
- **httpx**: HTTP 클라이언트

### 다른 폴더와의 관계
```
hvdc_mcp_server_v35/
  ← 입력: logiontology/ (변환 파이프라인)
  ← 데이터: output/hvdc_status_v35.ttl
  → 서비스: GPT Custom Actions, 외부 클라이언트
  ↔ 참조: docs/mcp_integration/
```

---

## 6. 상태 및 권장사항

### 현재 상태
- ✅ **서버 구현**: 완료
- ✅ **6개 엔드포인트**: 모두 작동
- ✅ **CLI 명령어**: 6개 구현
- ✅ **테스트**: 24개 통과
- ✅ **Docker 배포**: 준비됨
- ✅ **GPT 통합**: OpenAPI 스펙 준비

### 핵심 기능
1. **Flow Code 분포 분석** - 0~5 분류 통계
2. **AGI/DAS 준수 검증** - 100% 준수 확인
3. **오버라이드 추적** - 31건 케이스
4. **케이스 조회** - 특정 화물 검색
5. **Flow 5 분석** - 혼합 케이스 분석
6. **Pre Arrival** - Flow 0 상태 추적
7. **범용 SPARQL** - 커스텀 쿼리 지원

### 정리/개선 권장사항

#### 즉시 개선 (High Priority)
1. **성능 최적화**: 대용량 쿼리에 대한 캐싱 추가
2. **에러 핸들링**: 더 상세한 에러 메시지 및 로깅
3. **인증/보안**: JWT 토큰 또는 API 키 추가

#### 중기 개선 (Medium Priority)
1. **대시보드 UI**: React 기반 시각화 추가
2. **추가 엔드포인트**: 더 많은 분석 쿼리 제공
3. **배치 처리**: 여러 쿼리 일괄 실행

#### 장기 개선 (Low Priority)
1. **분산 시스템**: Apache Fuseki 또는 GraphDB 통합
2. **실시간 업데이트**: WebSocket 지원
3. **프로덕션 배포**: CI/CD, Kubernetes 설정

---

## 7. API 엔드포인트

### REST API (6개)
1. **POST /mcp/query** - 범용 SPARQL 쿼리
2. **GET /flow/distribution** - Flow Code 0~5 분포 통계
3. **GET /flow/compliance** - AGI/DAS 준수 검증
4. **GET /flow/overrides** - 오버라이드 케이스 목록
5. **GET /case/{case_id}** - 특정 케이스 상세 정보
6. **GET /flow/5/analysis** - Flow 5 혼합 케이스 분석
7. **GET /flow/0/status** - Pre Arrival 케이스

### CLI 명령어 (6개)
1. **flow_code_distribution_v35** - Flow 분포 통계
2. **agi_das_compliance** - AGI/DAS 검증
3. **override_cases** - 오버라이드 추적
4. **flow_5_analysis** - Flow 5 분석
5. **pre_arrival_status** - Pre Arrival 상태
6. **case_lookup <id>** - 케이스 조회

### 예상 데이터
- **Total Cases**: 755
- **Flow Code Distribution**:
  - Flow 0: 71 cases (9.4%) - Pre Arrival
  - Flow 1: 255 cases (33.8%) - Port → Site
  - Flow 2: 152 cases (20.1%) - Port → WH → Site
  - Flow 3: 131 cases (17.4%) - Port → MOSB → Site
  - Flow 4: 65 cases (8.6%) - Port → WH → MOSB → Site
  - Flow 5: 81 cases (10.7%) - Mixed/Incomplete
- **AGI/DAS Compliance**: 100%
- **Override Cases**: 31건

---

## 8. 기술 스택

### Backend
- **FastAPI** 0.104+ - REST API 프레임워크
- **Uvicorn** 0.24+ - ASGI 서버
- **RDFLib** 7.0+ - RDF/TTL 파싱 및 쿼리
- **Click** 8.1+ - CLI 인터페이스

### Testing
- **pytest** 7.4+ - 테스트 프레임워크
- **httpx** 0.25+ - HTTP 클라이언트

### Deployment
- **Docker** - 컨테이너화
- **Docker Compose** - 다중 컨테이너 오케스트레이션

---

## 9. 사용 가이드

### 로컬 실행
```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 환경 변수 설정 (.env)
TTL_PATH=../output/hvdc_status_v35.ttl

# 3. 서버 시작
uvicorn mcp_server.mcp_ttl_server:app --reload

# 4. Swagger UI 접속
http://localhost:8000/docs
```

### CLI 사용
```bash
# Flow 분포 확인
python -m mcp_server.commands flow_code_distribution_v35

# AGI/DAS 준수 검증
python -m mcp_server.commands agi_das_compliance

# 특정 케이스 조회
python -m mcp_server.commands case_lookup 00045
```

### Docker 배포
```bash
# 빌드 및 실행
docker-compose up

# API 접근
http://localhost:8000
```

### GPT Custom Actions 통합
1. 서버 시작
2. OpenAPI 스펙 다운로드: http://localhost:8000/openapi.json
3. GPT Custom Actions에 import
4. 엔드포인트 연결:
   - get_flow_distribution → /flow/distribution
   - check_compliance → /flow/compliance
   - get_overrides → /flow/overrides
   - case_lookup → /case/{case_id}

---

## 10. 성능 특징

### 현재 성능
- **쿼리 시간**: ~50-100ms (RDFLib in-memory)
- **목표 시간**: <500ms
- **데이터 크기**: 755 cases, 9,904 triples
- **메모리 사용**: RDFLib in-memory 그래프

### 확장성
- **현재**: 단일 서버, in-memory 쿼리
- **권장**: Apache Fuseki 또는 GraphDB (대용량 데이터)
- **캐싱**: 자주 사용되는 쿼리 결과 캐싱 가능

---

**보고서 작성일**: 2025-11-01
**다음 검토 권장일**: 프로덕션 배포 전

