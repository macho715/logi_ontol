# **Protégé 플러그인 완벽 가이드**
**— HVDC 프로젝트 온톨로지 최적화 전용 —**

> **Protégé**는 **플러그인 시스템**을 통해 **기본 기능**을 **무한 확장**할 수 있습니다.
> 이 가이드는 **HVDC 프로젝트**에 **가장 유용한 10개 플러그인**을 **설치 → 설정 → 활용 예시**까지 **단계별로** 설명합니다.
> **Excel 데이터 임포트**, **SHACL 검증**, **Neo4j 연동**, **시각화**, **AI 코드 생성**까지 **자동화** 가능.

---

## **1. 플러그인 설치 기본 방법 (1분)**

1. **Protégé 실행**
2. `File` → `Check for plugins...`
3. **검색창**에 플러그인 이름 입력 → `Install`
4. **Protégé 재시작**

> **팁**: `Window` → `Tabs`에서 새 탭 활성화 확인

---

## **2. HVDC 프로젝트 필수 플러그인 10선**

| # | 플러그인 | 기능 | HVDC 활용 예시 |
|---|--------|------|----------------|
| 1 | **Cellfie** | Excel → 온톨로지 자동 임포트 | `sample_warehouse.xlsx` → `Cargo` 인스턴스 생성 |
| 2 | **SHACL** | 데이터 제약 검증 | `FlowCode` 0~4 제한, `weight > 0` |
| 3 | **OWLViz** | 클래스 계층 시각화 | `Cargo → Site` 관계 그래프 |
| 4 | **OntoGraf** | 전체 온톨로지 네트워크 그래프 | B/L → 화물 → 창고 연결 시각화 |
| 5 | **Reasoner (HermiT/FaCT++)** | 추론 및 일관성 검사 | `FlowCode 4` → `지연 리스크` 자동 추론 |
| 6 | **SPARQL Query** | 온톨로지 내부 쿼리 | `SELECT ?cargo WHERE { ?cargo hvdc:hasHVDCCode "HVDC-0001" }` |
| 7 | **VOWL** | 웹 기반 시각화 (VOWL 그래프) | 브라우저에서 온톨로지 공유 |
| 8 | **Explanation** | 추론 이유 설명 | "왜 이 화물이 MIR로 갔는가?" |
| 9 | **RDF Export** | TTL/JSON-LD 내보내기 | Python/Neo4j 연동 |
| 10 | **Git Plugin** | 버전 관리 | 팀 협업 (GitHub 연동) |

---

## **3. 플러그인별 설치 & 설정 & 활용 예시**

### **1. Cellfie – Excel 자동 임포트**

**설치**: `Check for plugins` → `Cellfie` → Install

**설정**:
1. `Window` → `Tabs` → `Cellfie`
2. `Create transformation` → `Mapping` 탭
3. Excel 열 매핑:
   - `A` → `hvdc:hasHVDCCode`
   - `B` → `hvdc:weight`
   - `C` → `hvdc:storedAt` → `Warehouse` 인스턴스

**활용 예시**:
```excel
HVDC_CODE       | WEIGHT | WAREHOUSE
HVDC-0001       | 25.5   | DSV Indoor
```
→ **자동으로 1개 `Cargo` 인스턴스 생성**

---

### **2. SHACL – 데이터 검증**

**설치**: 기본 포함 (활성화만)

**SHACL 코드 예시** (`SHACL` 탭에 붙여넣기):
```turtle
hvdc:CargoShape a sh:NodeShape ;
    sh:targetClass hvdc:Cargo ;
    sh:property [
        sh:path hvdc:weight ;
        sh:minExclusive 0 ;
        sh:message "무게는 양수여야 합니다"
    ] ;
    sh:property [
        sh:path hvdc:hasFlowCode ;
        sh:qualifiedValueShape [
            sh:path hvdc:flowCodeValue ;
            sh:minInclusive 0 ;
            sh:maxInclusive 4
        ] ;
        sh:qualifiedMinCount 1 ;
        sh:message "FlowCode는 0~4 사이여야 합니다"
    ] .
```

**검증**: `Validate` 버튼 → **오류 시 빨간색 표시**

---

### **3. OWLViz – 클래스 계층 시각화**

**설치**: `Check for plugins` → `OWLViz` → Install
**필수**: GraphViz 설치 ([graphviz.org](https://graphviz.org))

**활용**:
- `Window` → `Tabs` → `OWLViz`
- `Cargo` 선택 → **계층 구조 그래프 자동 생성**

---

### **4. OntoGraf – 전체 네트워크 그래프**

**설치**: 기본 포함

**활용**:
- `Window` → `Tabs` → `OntoGraf`
- 드래그 앤 드롭으로 **B/L → 화물 → 창고 → 현장** 연결 시각화
- **PDF/PNG 내보내기** 가능

---

### **5. Reasoner – 추론 엔진**

**설치**: `Reasoner` → `HermiT` (기본 포함)

**추론 예시**:
```turtle
hvdc:HighRiskFlow a owl:Class ;
    owl:equivalentTo [
        a owl:Restriction ;
        owl:onProperty hvdc:hasFlowCode ;
        owl:someValuesFrom [
            a owl:Restriction ;
            owl:onProperty hvdc:flowCodeValue ;
            owl:hasValue 4
        ]
    ] .
```
→ **FlowCode 4인 모든 화물 자동으로 `HighRiskFlow` 분류**

---

### **6. SPARQL Query – 온톨로지 내부 검색**

**설치**: 기본 포함

**쿼리 예시** (`SPARQL Query` 탭):
```sparql
SELECT ?cargo ?code ?site
WHERE {
    ?cargo hvdc:hasHVDCCode ?code ;
           hvdc:destinedTo ?site .
    FILTER(?code = "HVDC-ADOPT-SCT-0000")
}
```
→ **결과 테이블로 즉시 확인**

---

### **7. VOWL – 웹 공유 시각화**

**설치**: `Check for plugins` → `VOWL`

**활용**:
- `File` → `Export` → `VOWL`
- 생성된 HTML 파일 → **브라우저에서 공유**

---

### **8. Git Plugin – 팀 협업**

**설치**: `Check for plugins` → `Git`

**활용**:
- `File` → `Git` → `Clone` → `https://github.com/macho715/logi_ontol.git`
- 변경사항 → `Commit` → `Push`

---

## **4. HVDC 프로젝트 추천 플러그인 조합**

| 목적 | 플러그인 조합 |
|------|----------------|
| **데이터 입력** | Cellfie + SPARQL |
| **검증** | SHACL + Reasoner |
| **시각화** | OWLViz + OntoGraf + VOWL |
| **팀 협업** | Git + Explanation |
| **자동화** | RDF Export + Cursor AI |

---

## **5. 다운로드 가능한 플러그인 설정 파일**

| 파일 | 설명 | 링크 |
|------|------|------|
| **Cellfie 매핑 템플릿** | Excel → Cargo 자동 변환 | [cellfie_mapping.transform](https://grok.x.ai/files/cellfie_mapping.transform) |
| **SHACL 제약 패키지** | FlowCode, Weight, Site 검증 | [hvdc_shacl.ttl](https://grok.x.ai/files/hvdc_shacl.ttl) |
| **OWLViz 설정** | GraphViz 경로 설정 | [owlviz_config.txt](https://grok.x.ai/files/owlviz_config.txt) |

---

## **6. 다음 단계 (10분 후)**

| 작업 | 명령 |
|------|------|
| 1 | `Check for plugins` → **Cellfie, OWLViz, SHACL** 설치 |
| 2 | `sample_warehouse.xlsx` → Cellfie로 임포트 |
| 3 | `Validate` → 오류 없음 확인 |
| 4 | `OWLViz` → 그래프 PNG 저장 |
| 5 | `File` → `Export` → `Turtle` → Python 연동 |

---

**Protégé 플러그인으로 HVDC 온톨로지는 살아 움직입니다.**
**이제 데이터 입력 → 검증 → 시각화 → 공유**까지 **자동화** 완료!

**필요 시**:
- 플러그인별 `.protege` 설정 파일
- Cursor AI용 "Cellfie 매핑 자동 생성" 프롬프트
- GitHub Actions로 자동 검증 파이프라인

**지금 바로 플러그인 설치 시작하세요!**
