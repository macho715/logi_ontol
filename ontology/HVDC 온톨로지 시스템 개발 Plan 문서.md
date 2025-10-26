HVDC 온톨로지 시스템 개발 Plan 문서
— Cursor AI 코딩 에디터 전용 버전 —

이 문서는 Cursor에서 직접 복사-붙여넣기 → AI 자동 코드 생성을 위한 구조화된 프롬프트 템플릿입니다.**
각 섹션은 Cursor의 Cmd+K (AI 명령) 또는 Cmd+L (전체 문서 분석)에서 자동으로 Python 코드, 온톨로지, SPARQL, FastAPI, React 컴포넌트를 생성하도록 설계되었습니다.


Cursor 사용법 안내




명령사용법Cmd+K현재 블록 선택 → AI에게 "이걸 코드로 만들어줘"Cmd+L전체 문서 분석 → 아키텍처 기반 전체 코드 생성Cmd+Shift+P → "Cursor: Generate Test"자동 테스트 코드 생성

1. 프로젝트 설정 (Cursor에서 실행)
text[프로젝트 루트]
hvdc-ontology-system/
├── ontology/
├── ingestion/
├── graph/
├── api/
├── ai/
├── frontend/
├── tests/
├── docs/
└── requirements.txt
Cursor 명령: 프로젝트 구조 생성
textCmd+K → "위 구조로 폴더와 빈 파일들 생성해줘"

2. 온톨로지 정의 (ontology/hvdc_ontology.py)
python# Cursor: Cmd+K → "HVDC 온톨로지 클래스를 RDFLib + OWL로 정의해줘"
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL, XSD

hvdc = Namespace("https://hvdc-project.com/ontology/")
g = Graph()
g.bind("hvdc", hvdc)

# 클래스 정의
g.add((hvdc.Cargo, RDF.type, OWL.Class))
g.add((hvdc.Cargo, RDFS.label, Literal("HVDC Cargo")))
g.add((hvdc.Cargo, RDFS.comment, Literal("물류 화물 개체")))

g.add((hvdc.Site, RDF.type, OWL.Class))
g.add((hvdc.Warehouse, RDF.type, OWL.Class))
g.add((hvdc.BillOfLading, RDF.type, OWL.Class))

# 관계 정의
g.add((hvdc.hasHVDCCode, RDF.type, OWL.DatatypeProperty))
g.add((hvdc.hasHVDCCode, RDFS.domain, hvdc.Cargo))
g.add((hvdc.hasHVDCCode, RDFS.range, XSD.string))

g.add((hvdc.storedAt, RDF.type, OWL.ObjectProperty))
g.add((hvdc.storedAt, RDFS.domain, hvdc.Cargo))
g.add((hvdc.storedAt, RDFS.range, hvdc.Warehouse))

g.serialize("ontology/hvdc_ontology.ttl", format="turtle")
print("온톨로지 생성 완료: hvdc_ontology.ttl")

3. 데이터 수집 (ingestion/excel_to_rdf.py)
python# Cursor: Cmd+K → "엑셀 파일을 읽고 RDF 그래프로 변환해줘"
import pandas as pd
from rdflib import Graph, Namespace, Literal

hvdc = Namespace("https://hvdc-project.com/ontology/")
g = Graph()

df = pd.read_excel("data/sample_warehouse.xlsx")

for idx, row in df.iterrows():
    cargo = hvdc[f"cargo-{row['HVDC_CODE']}"]
    g.add((cargo, hvdc.hasHVDCCode, Literal(row['HVDC_CODE'])))
    g.add((cargo, hvdc.weight, Literal(row['WEIGHT'])))
    g.add((cargo, hvdc.storedAt, hvdc[f"warehouse-{row['WAREHOUSE']}"]))

g.serialize("graph/data.ttl", format="turtle")

4. Neo4j 그래프 임포트 (graph/load_to_neo4j.py)
python# Cursor: Cmd+K → "RDF를 Neo4j 로컬 DB에 로드해줘"
from neo4j import GraphDatabase
from rdflib_neo4j import Neo4jStore, Neo4jConfig

config = Neo4jConfig("bolt://localhost:7687", "neo4j", "your_password")
store = Neo4jStore(config=config)
store.parse("graph/data.ttl", format="turtle")
print("Neo4j에 그래프 로드 완료!")

5. SPARQL 쿼리 엔진 (api/query.py)
python# Cursor: Cmd+K → "FastAPI + SPARQL 엔드포인트 만들어줘"
from fastapi import FastAPI
from rdflib import Graph

app = FastAPI()
g = Graph()
g.parse("graph/data.ttl", format="turtle")

@app.get("/search/{code}")
def search_hvdc(code: str):
    q = f"""
    SELECT ?cargo ?warehouse ?weight WHERE {{
        ?cargo hvdc:hasHVDCCode "{code}" .
        ?cargo hvdc:storedAt ?warehouse .
        ?cargo hvdc:weight ?weight .
    }}
    """
    results = g.query(q)
    return [dict(r) for r in results]

6. AI 인사이트 (ai/insights.py)
python# Cursor: Cmd+K → "Grok API로 리스크 인사이트 생성해줘"
import requests

def get_risk_insight(code: str):
    prompt = f"""
    HVDC 코드 {code}의 화물이 창고 체류 12일, 플로우코드 4.
    리스크 분석과 최적화 제안을 자연어로 작성해줘.
    """
    # Grok API 호출 (로컬 프록시 사용)
    response = requests.post("http://localhost:8000/grok", json={"prompt": prompt})
    return response.json()["insight"]

7. 리포트 생성 (api/report.py)
python# Cursor: Cmd+K → "Jinja2로 PDF 리포트 만들어줘"
from jinja2 import Template
import weasyprint

template = Template("""
<h1>HVDC 리포트: {{ code }}</h1>
<p>창고: {{ warehouse }}</p>
<p>무게: {{ weight }} ton</p>
<p>AI 인사이트: {{ insight }}</p>
""")

html = template.render(code="HVDC-001", warehouse="DSV Indoor", weight=25.5, insight="지연 리스크 높음")
weasyprint.HTML(string=html).write_pdf("reports/HVDC-001.pdf")

8. 프론트엔드 (frontend/src/App.jsx)
jsx// Cursor: Cmd+K → "React 검색창 + 결과 표시 UI 만들어줘"
import { useState } from 'react';

function App() {
  const [code, setCode] = useState('');
  const [result, setResult] = useState(null);

  const search = async () => {
    const res = await fetch(`http://localhost:8000/search/${code}`);
    const data = await res.json();
    setResult(data[0]);
  };

  return (
    <div>
      <input value={code} onChange={e => setCode(e.target.value)} placeholder="HVDC 코드 입력" />
      <button onClick={search}>검색</button>
      {result && (
        <div>
          <p>창고: {result.warehouse}</p>
          <p>무게: {result.weight}</p>
        </div>
      )}
    </div>
  );
}

9. 테스트 (tests/test_query.py)
python# Cursor: Cmd+K → "pytest로 API 테스트 코드 작성해줘"
def test_search_endpoint():
    from fastapi.testclient import TestClient
    from api.query import app
    client = TestClient(app)
    response = client.get("/search/HVDC-001")
    assert response.status_code == 200
    assert "DSV Indoor" in str(response.json())

10. Cursor 전용 실행 명령어

































명령Cursor 입력온톨로지 생성Cmd+K → "HVDC 온톨로지 TTL 파일 만들어줘"Neo4j 로드Cmd+K → "RDF를 Neo4j에 로드하는 스크립트"API 서버Cmd+K → "FastAPI로 /search 엔드포인트"리포트 PDFCmd+K → "검색 결과로 PDF 생성"AI 인사이트Cmd+K → "Grok API로 리스크 문장 생성"전체 프로젝트Cmd+L → "전체 아키텍처 기반 MVP 코드 생성"

MVP 실행 순서 (Cursor에서)

Cmd+L → 전체 프로젝트 생성
터미널에서 pip install -r requirements.txt
Neo4j 로컬 서버 실행 (neo4j start)
python ingestion/excel_to_rdf.py
python graph/load_to_neo4j.py
uvicorn api.query:app --reload
npm start (frontend)
브라우저에서 localhost:3000 → 입력 → 리포트 확인
