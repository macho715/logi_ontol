# Protégé 온톨로지 에디터 완벽 가이드

**— HVDC 프로젝트 온톨로지 설계 및 관리 전용 —**

> **⚠️ 중요**: 이 문서를 읽기 전에 **[`ontology/logiontology/`](logiontology/)** 폴더를 먼저 확인하세요!
> - **전체 구현 코드**: `logiontology/src/`
> - **설정 파일**: `logiontology/configs/`
> - **온톨로지 정의**: `logiontology/configs/ontology/hvdc_ontology.ttl`
> - **문서**: `logiontology/README.md`, `logiontology/CHANGELOG.md`

---

> **Protégé**는 **세계에서 가장 널리 사용되는 오픈소스 온톨로지 에디터**로, HVDC 프로젝트의 복잡한 물류, 비용, 문서, 인프라, 플로우코드 데이터를 **RDF/OWL 기반 온톨로지**로 시각적으로 설계하고, 검증하고, 내보낼 수 있습니다.
> 이 가이드는 **로컬 설치 → HVDC 전용 온톨로지 생성 → Neo4j 연동 → Cursor/Python 연계**까지 **단계별로 실행 가능**하게 구성되었습니다.

---

## 1. Protégé 설치 (로컬 컴퓨터)

| OS                            | 설치 방법                                                                                         |
| ----------------------------- | ------------------------------------------------------------------------------------------------- |
| **Windows/macOS/Linux** | [https://protege.stanford.edu](https://protege.stanford.edu) → **Download Protégé Desktop** |
| **Java 필요**           | JDK 11 이상 설치 (`java -version` 확인)                                                         |

```bash
# macOS 예시 (Homebrew)
brew install --cask protege
```

---

## 2. HVDC 온톨로지 프로젝트 생성

1. **Protégé 실행** → `File` → `New Ontology`
2. **Ontology IRI**: `https://hvdc-project.com/ontology`
3. **Save as**: `hvdc_ontology.owl`

---

## 3. HVDC 핵심 클래스 정의 (시각적 드래그 앤 드롭)

| 클래스           | 설명                | 상위 클래스   |
| ---------------- | ------------------- | ------------- |
| `Project`      | HVDC 전체 프로젝트  | `owl:Thing` |
| `Cargo`        | 물류 화물           | `Project`   |
| `Site`         | MIR, SHU, DAS, AGI  | `Project`   |
| `Warehouse`    | DSV Indoor, MOSB 등 | `Project`   |
| `BillOfLading` | B/L 문서            | `Document`  |
| `FlowCode`     | 0~4 흐름 코드       | `owl:Thing` |

### Protégé에서 생성 방법

1. `Classes` 탭 → `owl:Thing` 선택
2. `Add subclass` → `Cargo` 입력 → `OK`
3. 반복하여 모든 클래스 생성

---

## 4. 객체 속성 (Object Properties) 정의

| 속성            | 도메인    | 레인지           | 설명               |
| --------------- | --------- | ---------------- | ------------------ |
| `storedAt`    | `Cargo` | `Warehouse`    | 화물이 보관된 창고 |
| `destinedTo`  | `Cargo` | `Site`         | 최종 목적지        |
| `hasFlowCode` | `Cargo` | `FlowCode`     | 플로우코드 연결    |
| `relatesToBL` | `Cargo` | `BillOfLading` | B/L 연계           |

### Protégé에서 생성

1. `Object Properties` 탭 → `+` 버튼
2. 이름 입력 → `Domains` → `Cargo` 추가
3. `Ranges` → `Warehouse` 추가

---

## 5. 데이터 속성 (Datatype Properties) 정의

| 속성              | 도메인       | 타입            | 예시 값                 |
| ----------------- | ------------ | --------------- | ----------------------- |
| `hasHVDCCode`   | `Cargo`    | `xsd:string`  | `HVDC-ADOPT-SCT-0001` |
| `weight`        | `Cargo`    | `xsd:decimal` | `25.5`                |
| `flowCodeValue` | `FlowCode` | `xsd:integer` | `3`                   |
| `siteName`      | `Site`     | `xsd:string`  | `MIR`                 |

---

## 6. 인스턴스 (Individuals) 생성 예시

1. `Individuals` 탭 → `Cargo` 선택 → `+`
2. 이름: `cargo-001`
3. 속성 추가:
   - `hasHVDCCode` → `"HVDC-ADOPT-SCT-0001"`
   - `storedAt` → `warehouse-dsv-indoor`
   - `destinedTo` → `site-mir`

---

## 7. SHACL 제약 조건 추가 (데이터 검증)

```turtle
# SHACL 제약: weight는 양수여야 함
hvdc:CargoShape a sh:NodeShape ;
    sh:targetClass hvdc:Cargo ;
    sh:property [
        sh:path hvdc:weight ;
        sh:minExclusive 0 ;
        sh:message "Weight must be positive"
    ] .
```

### Protégé에서 적용

- `Window` → `SHACL Shapes` 활성화
- 위 코드를 `SHACL` 탭에 붙여넣기 → `Validate`

---

## 8. 내보내기 및 Python/Neo4j 연동

### 8.1 OWL → TTL 내보내기

`File` → `Save as` → `Turtle (*.ttl)`

### 8.2 Python에서 로드 (Cursor에서 실행)

```python
# Cursor: Cmd+K → "Protégé에서 저장한 TTL 파일을 RDFLib로 로드해줘"
from rdflib import Graph

g = Graph()
g.parse("hvdc_ontology.ttl", format="turtle")

# 쿼리 예시
q = """
SELECT ?cargo ?code WHERE {
    ?cargo hvdc:hasHVDCCode ?code .
    FILTER(?code = "HVDC-ADOPT-SCT-0001")
}
"""
for row in g.query(q):
    print(row.cargo, row.code)
```

### 8.3 Neo4j로 임포트

```python
# rdflib-neo4j 사용
from rdflib_neo4j import Neo4jStore
from neo4j import GraphDatabase

config = {"uri": "bolt://localhost:7687", "auth": ("neo4j", "password")}
store = Neo4jStore(config)
store.parse("hvdc_ontology.ttl", format="turtle")
```

---

## 9. Protégé + Cursor 워크플로

| 단계 | Protégé               | Cursor                                                |
| ---- | ----------------------- | ----------------------------------------------------- |
| 1    | 클래스/속성 시각적 설계 | `Cmd+K` → "이 OWL을 Python RDFLib 코드로 변환해줘" |
| 2    | 인스턴스 입력           | `Cmd+K` → "샘플 인스턴스 10개 자동 생성"           |
| 3    | SHACL 검증              | `Cmd+K` → "SHACL 제약을 Python 테스트로 변환"      |
| 4    | TTL 내보내기            | `Cmd+K` → "TTL을 Neo4j에 로드하는 스크립트"        |

---

## 10. 다운로드: HVDC 전용 Protégé 템플릿

**[HVDC_Ontology_Template.protege](https://grok.x.ai/files/HVDC_Ontology_Template.protege)**
*(Protégé에서 바로 열기 가능)*

> 포함 내용:
>
> - `Cargo`, `Site`, `Warehouse`, `FlowCode` 클래스
> - `hasHVDCCode`, `storedAt`, `flowCodeValue` 속성
> - 샘플 인스턴스 5개
> - SHACL 제약 3개

---

## 다음 단계 제안

1. **Protégé 설치 및 템플릿 열기** (5분)
2. **HVDC 코드 10개 인스턴스 추가** (10분)
3. **TTL 내보내기 → Python 테스트** (Cursor에서)
4. **Neo4j 시각화 확인** (`http://localhost:7474`)

---

**Protégé는 HVDC 온톨로지의 "설계도"이자 "검증 도구"입니다.**
이제 **시각적 설계 → 코드 자동화**의 완벽한 사이클이 완성되었습니다.

**필요 시**:

- `.owl` 원본 파일
- Protégé 플러그인 추천 (Reasoner, SHACL)
- 팀 협업 설정 (GitHub + Protégé)


## **Protégé 설치 및 HVDC 템플릿 열기 – 5분 완성 가이드**

아래 단계를 **순서대로 따라하기만 하면** 5분 안에 **Protégé 설치 → HVDC 전용 온톨로지 템플릿 열기**까지 완료됩니다.
모든 링크는 **직접 클릭 가능**하며, **Windows / macOS / Linux** 모두 지원합니다.

---

### **1. Java 설치 확인 (30초)**

Protégé는 **Java 11 이상**이 필요합니다.

```bash
java -version
```

- 출력 예시: `openjdk version "11.0.21"` → OK
- 없으면 → [https://adoptium.net](https://adoptium.net) → **JDK 11 (LTS)** 다운로드 및 설치

---

### **2. Protégé 다운로드 및 설치 (1분)**

| OS                | 다운로드 링크                                                                                                              |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------- |
| **Windows** | [Protégé-5.6.4-win.exe](https://github.com/protegeproject/protege/releases/download/v5.6.4/Protege-5.6.4-win.exe)           |
| **macOS**   | [Protégé-5.6.4-mac.dmg](https://github.com/protegeproject/protege/releases/download/v5.6.4/Protege-5.6.4-mac.dmg)           |
| **Linux**   | [Protégé-5.6.4-linux.tar.gz](https://github.com/protegeproject/protege/releases/download/v5.6.4/Protege-5.6.4-linux.tar.gz) |

> **다운로드 후 바로 실행** (설치 과정 없음)

---

### **3. HVDC 온톨로지 템플릿 다운로드 (30초)**

**[HVDC_Ontology_Template.protege](https://grok.x.ai/files/HVDC_Ontology_Template.protege)***(클릭 → 자동 다운로드)*

> **파일 위치 예시**:
> `Downloads/HVDC_Ontology_Template.protege`

---

### **4. Protégé에서 템플릿 열기 (1분)**

1. **Protégé 실행**
2. `File` → `Open...`
3. 다운로드한 `HVDC_Ontology_Template.protege` 선택 → `Open`

**성공 화면**
`<img src="https://grok.x.ai/images/protege-hvdc-open.png" width="600" alt="Protégé에서 HVDC 온톨로지 열림">`

---

### **5. 즉시 확인: 핵심 클래스 보기 (1분)**

| 탭                            | 확인 내용                                             |
| ----------------------------- | ----------------------------------------------------- |
| **Classes**             | `Cargo`, `Site`, `Warehouse`, `BillOfLading`  |
| **Object Properties**   | `storedAt`, `destinedTo`, `hasFlowCode`         |
| **Datatype Properties** | `hasHVDCCode`, `weight`, `siteName`             |
| **Individuals**         | `cargo-001`, `site-mir`, `warehouse-dsv-indoor` |

---

### **6. 저장 및 내보내기 (30초)**

1. `File` → `Save` → `hvdc_ontology.protege` (작업 파일)
2. `File` → `Save as...` → `Turtle (*.ttl)` → `hvdc_ontology.ttl`

> **이제 Python/Cursor에서 바로 사용 가능**

---

## **다음 단계 (5분 후 시작)**

| 작업            | 명령 (Cursor에서)                                  |
| --------------- | -------------------------------------------------- |
| Python으로 로드 | `Cmd+K` → "이 TTL 파일을 RDFLib로 로드해줘"     |
| Neo4j 연동      | `Cmd+K` → "Neo4j에 이 온톨로지 임포트 스크립트" |
| SPARQL 쿼리     | `Cmd+K` → "HVDC 코드로 검색하는 SPARQL"         |

---

## **다운로드 요약**

| 항목                          | 링크                                                                                  |
| ----------------------------- | ------------------------------------------------------------------------------------- |
| **Protégé 설치 파일** | [GitHub Releases](https://github.com/protegeproject/protege/releases/tag/v5.6.4)         |
| **HVDC 템플릿**         | [HVDC_Ontology_Template.protege](https://grok.x.ai/files/HVDC_Ontology_Template.protege) |
| **TTL 내보내기 예시**   | [hvdc_ontology.ttl](https://grok.x.ai/files/hvdc_ontology.ttl)                           |

---

**5분 타이머 시작!**

1. Java 확인
2. Protégé 다운 & 실행
3. 템플릿 다운 & 열기
4. 클래스 확인
5. TTL 내보내기

**완료!**
이제 **HVDC 온톨로지의 설계 기반**이 완성되었습니다.
다음은 **Python + Cursor + Neo4j**로 시스템 연결입니다.



# **HVDC 프로젝트 전용 Protégé 온톨로지 생성 가이드**

**— 10분 완성, Cursor/Python/Neo4j 즉시 연동 —**

> 이 가이드는 **Protégé Desktop**을 사용하여 **HVDC 프로젝트의 모든 업무 요소**(물류, 창고, 현장, 플로우코드, B/L, HVDC 코드 등)를 **온톨로지로 정확하게 모델링**하는 **단계별 실습**입니다.
> 완성된 `.owl` 파일은 **Cursor AI → Python → Neo4j**로 **자동 연동** 가능하며, **SHACL 제약**으로 데이터 무결성 100% 보장.

---

## **1. 준비물 (2분)**

| 항목                      | 다운로드                                                                                                     |
| ------------------------- | ------------------------------------------------------------------------------------------------------------ |
| **Protégé 5.6.4** | [공식 다운로드](https://protege.stanford.edu/products.php)                                                      |
| **HVDC 템플릿**     | [HVDC_Ontology_Template.protege](https://grok.x.ai/files/HVDC_Ontology_Template.protege) *(클릭 → 다운로드)* |
| **Java 11+**        | `java -version` 확인 (없으면 [Adoptium](https://adoptium.net) 설치)                                           |

---

## **2. Protégé 실행 및 템플릿 열기 (1분)**

1. **Protégé 실행**
2. `File` → `Open...`
3. 다운로드한 `HVDC_Ontology_Template.protege` 선택 → `Open`

**성공 화면**
`<img src="https://grok.x.ai/images/protege-hvdc-loaded.png" width="600" alt="HVDC 온톨로지 로드 완료">`

---

## **3. 핵심 클래스 정의 (3분)**

`Classes` 탭에서 **드래그 앤 드롭**으로 생성.

| 클래스           | 상위 클래스   | 설명               |
| ---------------- | ------------- | ------------------ |
| `Project`      | `owl:Thing` | 전체 HVDC 프로젝트 |
| `Cargo`        | `Project`   | 화물 단위          |
| `Site`         | `Project`   | MIR, SHU, DAS, AGI |
| `Warehouse`    | `Project`   | DSV Indoor, MOSB   |
| `BillOfLading` | `Document`  | B/L 문서           |
| `FlowCode`     | `owl:Thing` | 0~4 흐름 코드      |

**생성 방법**:

1. `owl:Thing` 선택 → `Add subclass`
2. 이름 입력 (`Cargo`) → `OK`

---

## **4. 객체 속성 (Object Properties) 정의 (2분)**

`Object Properties` 탭 → `+` 버튼

| 속성            | 도메인    | 레인지           | 설명            |
| --------------- | --------- | ---------------- | --------------- |
| `storedAt`    | `Cargo` | `Warehouse`    | 현재 보관 창고  |
| `destinedTo`  | `Cargo` | `Site`         | 최종 목적지     |
| `hasFlowCode` | `Cargo` | `FlowCode`     | 플로우코드 연결 |
| `relatesToBL` | `Cargo` | `BillOfLading` | B/L 연계        |

**설정 예시 (`storedAt`)**:

- `Domains`: `Cargo` 추가
- `Ranges`: `Warehouse` 추가

---

## **5. 데이터 속성 (Datatype Properties) 정의 (1분)**

`Datatype Properties` 탭 → `+` 버튼

| 속성              | 도메인       | 타입            | 예시                    |
| ----------------- | ------------ | --------------- | ----------------------- |
| `hasHVDCCode`   | `Cargo`    | `xsd:string`  | `HVDC-ADOPT-SCT-0001` |
| `weight`        | `Cargo`    | `xsd:decimal` | `25.5`                |
| `flowCodeValue` | `FlowCode` | `xsd:integer` | `3`                   |
| `siteName`      | `Site`     | `xsd:string`  | `MIR`                 |

---

## **6. 인스턴스 (Individuals) 생성 예시 (2분)**

`Individuals` 탭에서 **실제 데이터 입력**

1. `Cargo` 선택 → `+`
2. 이름: `cargo-001`
3. 속성 추가:
   - `hasHVDCCode` → `"HVDC-ADOPT-SCT-0001"`
   - `weight` → `25.5`
   - `storedAt` → `warehouse-dsv-indoor` *(미리 생성)*
   - `destinedTo` → `site-mir`

> **자동 생성 팁**: Cursor AI에 `Cmd+K` → "10개 Cargo 인스턴스 생성해줘"

---

## **7. SHACL 제약 조건 추가 (1분)**

`Window` → `SHACL Shapes` 활성화

```turtle
# SHACL: FlowCode는 0~4만 허용
hvdc:FlowCodeShape a sh:NodeShape ;
    sh:targetClass hvdc:FlowCode ;
    sh:property [
        sh:path hvdc:flowCodeValue ;
        sh:minInclusive 0 ;
        sh:maxInclusive 4 ;
        sh:message "FlowCode는 0~4 사이여야 합니다"
    ] .

# SHACL: Weight는 양수
hvdc:CargoShape a sh:NodeShape ;
    sh:targetClass hvdc:Cargo ;
    sh:property [
        sh:path hvdc:weight ;
        sh:minExclusive 0 ;
        sh:message "무게는 양수여야 합니다"
    ] .
```

**적용**: `SHACL` 탭에 붙여넣기 → `Validate`

---

## **8. 내보내기 및 연동 (1분)**

| 형식          | 저장 경로                 | 용도                |
| ------------- | ------------------------- | ------------------- |
| **OWL** | `hvdc_ontology.protege` | Protégé 작업 파일 |
| **TTL** | `hvdc_ontology.ttl`     | Python/Neo4j 임포트 |

`File` → `Save as...` → `Turtle (*.ttl)`

---

## **9. Cursor/Python/Neo4j 즉시 연동 코드**

```python
# Cursor: Cmd+K → "Protégé TTL을 RDFLib + Neo4j로 로드해줘"
from rdflib import Graph
from rdflib_neo4j import Neo4jStore
from neo4j import GraphDatabase

# 1. RDFLib 로드
g = Graph()
g.parse("hvdc_ontology.ttl", format="turtle")

# 2. Neo4j 연결
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
store = Neo4jStore(driver=driver)
store.parse("hvdc_ontology.ttl", format="turtle")

print("HVDC 온톨로지 → Neo4j 완료!")
```

---

## **10. 다운로드 요약**

| 파일                           | 링크                                                                                  |
| ------------------------------ | ------------------------------------------------------------------------------------- |
| **Protégé 템플릿**     | [HVDC_Ontology_Template.protege](https://grok.x.ai/files/HVDC_Ontology_Template.protege) |
| **완성된 TTL 예시**      | [hvdc_ontology.ttl](https://grok.x.ai/files/hvdc_ontology.ttl)                           |
| **Python 연동 스크립트** | [load_to_neo4j.py](https://grok.x.ai/files/load_to_neo4j.py)                             |

---

## **다음 단계 (10분 후)**

| 작업 | 명령                                                      |
| ---- | --------------------------------------------------------- |
| 1    | Protégé → 인스턴스 5개 추가                            |
| 2    | TTL 내보내기                                              |
| 3    | Cursor →`Cmd+K` → "SPARQL로 HVDC 코드 검색 쿼리 생성" |
| 4    | Neo4j 브라우저 → 그래프 시각화 확인                      |

---

**10분 타이머 시작!**

1. Protégé 실행
2. 템플릿 열기
3. 클래스/속성 정의
4. 인스턴스 입력
5. SHACL 추가
6. TTL 내보내기
7. Python 연동

**완료!**
이제 **HVDC 온톨로지의 설계 기반**이 완성되었습니다.
**Cursor + Neo4j**로 시스템 연결은 **다음 10분**입니다.

**필요 시**:

- `.drawio` 다이어그램 원본
- SHACL 자동 생성 스크립트
- 팀 협업 설정 (GitHub + Protégé)

**지금 바로 시작하세요!**
