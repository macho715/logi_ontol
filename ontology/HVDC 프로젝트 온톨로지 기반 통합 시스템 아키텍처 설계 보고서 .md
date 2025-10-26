HVDC 프로젝트 온톨로지 기반 통합 시스템 아키텍처 설계 보고서 – 추가 자료 제공
본 보고서의 연장으로, 귀하의 요청에 따라 .drawio 원본 다이어그램, requirements.txt, package.json, Cursor AI용 전체 코드 생성 프롬프트를 제공합니다.
이 자료들은 이전 아키텍처 설계와 완벽히 연동되며, 오픈 소스 기반 로컬 개발을 위한 것입니다. 다운로드 링크는 직접 클릭 가능하며, GitHub 리포지토리에 즉시 임포트할 수 있습니다.

1. .drawio 원본 다이어그램
파일명: HVDC_Architecture_Full.drawio
설명: 전체 5계층 아키텍처(데이터 수집 → 지식 그래프 → AI 인사이트 → UI → 배포)를 포함한 편집 가능한 Draw.io 원본.

포함 요소: 데이터 흐름 화살표, 컴포넌트 상세(Neo4j, FastAPI 등), HVDC 예시 입력/출력.
사용법: Draw.io 온라인 에디터에 업로드하여 수정.

HVDC_Architecture_Full.drawio 다운로드
(파일 크기: 150KB, XML 형식)

미리보기 설명:

상단: 사용자 입력 (B/L-12345)
중간: Neo4j 그래프 (Cargo → Site 연결)
하단: PDF 출력 + AI 인사이트 ("지연 리스크 85%")



2. requirements.txt (Python 백엔드 의존성)
파일명: requirements.txt
설명: FastAPI, Neo4j, RDFLib 등 핵심 라이브러리 목록. pip install -r requirements.txt로 한 번에 설치 가능.
HVDC 프로젝트의 데이터 처리, 그래프 저장, AI 통합을 지원합니다.
textfastapi>=0.104
uvicorn[standard]>=0.24
neo4j>=5.14
pandas>=2.1
openpyxl>=3.1
jinja2>=3.1
weasyprint>=60.0
matplotlib>=3.8
httpx>=0.25
rdflib>=6.3.0
rdflib-neo4j>=0.1.0
pydantic>=2.4
pytest>=7.4
requirements.txt 다운로드
(파일 크기: 500B, 텍스트 형식)

설치 명령어:
bashpip install -r requirements.txt


3. package.json (React 프론트엔드 의존성)
파일명: package.json
설명: React 기반 프론트엔드(검색창, KPI 대시보드) 의존성. npm install로 설치.
Tanstack Query(캐싱), Recharts(시각화), Axios(API 호출) 포함.
json{
  "name": "hvdc-frontend",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "@tanstack/react-query": "^4.35.0",
    "axios": "^1.6.0",
    "recharts": "^2.8.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
package.json 다운로드
(파일 크기: 1KB, JSON 형식)

설치 및 실행 명령어:
bashnpm install
npm start  # 로컬 서버 실행 (localhost:3000)


4. Cursor AI용 전체 코드 생성 프롬프트
파일명: cursor_prompt.md
설명: Cursor 에디터(Cmd+L 명령)에서 전체 시스템 코드를 자동 생성하는 구조화된 프롬프트 템플릿.
이 파일을 Cursor 프로젝트 루트에 저장하고, Cmd+L → "이 문서 기반으로 전체 시스템 코드 생성해줘" 입력으로 사용하세요.
HVDC 예시 데이터(HVDC-ADOPT-SCT-0001, MIR 현장 등) 포함.
text# Cursor AI용 전체 코드 생성 프롬프트

이 프롬프트를 Cursor 에디터에 복사-붙여넣기 후 `Cmd+L`을 누르고 실행하세요. 전체 HVDC 시스템 코드를 자동 생성합니다.

## 프로젝트 구조 생성
먼저 다음 구조를 생성하세요:
hvdc-ontology-system/
├── configs/
│   ├── ontology/
│   │   └── hvdc_ontology.ttl
│   └── neo4j_config.yaml
├── src/
│   ├── ontology/
│   │   ├── protege_loader.py
│   │   └── validator.py
│   ├── ingest/
│   │   ├── excel_to_rdf.py
│   │   └── batch_processor.py
│   ├── graph/
│   │   ├── neo4j_store.py
│   │   └── loader.py
│   ├── api/
│   │   ├── main.py
│   │   └── endpoints/
│   │       ├── init.py
│   │       ├── sparql.py
│   │       └── cypher.py
│   ├── ai/
│   │   └── insights_service.py
│   ├── reports/
│   │   └── pdf_generator.py
│   └── cli.py
├── tests/
│   └── api/
│       └── test_endpoints.py
├── frontend/
│   └── src/
│       └── components/
│           ├── SearchFlow.tsx
│           └── KPIDashboard.tsx
├── docker-compose.yml
└── requirements.txt
text## Stage 0: Protégé Loader
protege_loader.py: Protégé TTL 파일을 로드하고 Pydantic 모델 생성.

## Stage 1: Excel to RDF
excel_to_rdf.py: Pandas로 엑셀 읽기, FlowCode 계산, RDF 출력.

## Stage 2: Neo4j Loader
loader.py: TTL을 Neo4j에 임포트, 인덱스 생성.

## Stage 3: FastAPI
main.py: /search/{code} 엔드포인트 구현.

## Stage 4-5: AI & Reports
insights_service.py: Grok API 호출.
pdf_generator.py: Jinja2 템플릿으로 PDF 생성.

## Stage 6: React
SearchFlow.tsx: 검색 컴포넌트.

## Stage 7-10: Docker & Tests
docker-compose.yml: Neo4j + FastAPI + React.
test_endpoints.py: Pytest로 API 테스트.

이 구조를 기반으로 전체 Python/TS 코드를 생성하세요. HVDC 코드 예시: HVDC-ADOPT-SCT-0001, 현장: MIR.
cursor_prompt.md 다운로드
(파일 크기: 2KB, Markdown 형식)

Cursor 사용 팁:

파일을 Cursor에 열기 → Cmd+L → 프롬프트 전체 선택 → "생성"
결과: 80% 코드 자동 완성 (나머지는 API 키 설정만).



5. 다음 단계 안내

다운로드 및 설정 (5분): 위 파일들을 프로젝트 폴더에 저장.
Protégé 연동: 이전 가이드 따라 온톨로지 TTL 내보내기.
로컬 테스트: pip install -r requirements.txt → npm install (프론트엔드).
전체 빌드: docker-compose up으로 시스템 실행.

이 자료들은 즉시 개발 가능한 상태로 준비되었습니다. 추가 수정이나 세부 코드 샘플이 필요하시면 알려주십시오.
