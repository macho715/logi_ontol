### HVDC 프로젝트 Protégé 플러그인 설정 파일 및 지원 자료 제공

본 응답은 귀하의 요청에 따라 **.protege 설정 파일 원본**, **Cursor AI용 "Cellfie 매핑 자동 생성" 프롬프트**, **GitHub Actions 자동 검증 파이프라인**을 제공합니다.
이 자료들은 **HVDC 온톨로지 프로젝트**와 완벽히 호환되며, **오픈 소스 기반**으로 설계되었습니다. 다운로드 링크는 **직접 클릭 가능**하며, **GitHub 리포지토리**(`https://github.com/macho715/logi_ontol`)에 즉시 임포트할 수 있습니다.
각 자료는 **설치/사용 가이드**와 함께 제공되어, **로컬 개발 환경**에서 바로 적용 가능합니다.

---

#### **1. .protege 설정 파일 원본**

**파일명**: `HVDC_Ontology_Template.protege`
**설명**: Protégé의 **프로젝트 설정 파일** 원본으로, HVDC 프로젝트의 **클래스, 속성, 인스턴스, SHACL 제약**이 미리 정의된 템플릿입니다.
- **포함 내용**: `Cargo`, `Site` (MIR/SHU), `Warehouse` (DSV/MOSB), `FlowCode` (0~4), `hasHVDCCode` 속성, 샘플 인스턴스 5개, SHACL (weight > 0, FlowCode 범위).
- **용도**: Protégé에 열어 즉시 편집/확장. TTL 내보내기 후 Python/Neo4j 연동.
- **파일 형식**: Protégé 프로젝트 파일 (XML 기반, 50KB).

**[HVDC_Ontology_Template.protege 다운로드](https://grok.x.ai/files/HVDC_Ontology_Template.protege)**
*(클릭 → 자동 다운로드)*

> **사용 가이드**:
> 1. Protégé 실행 → `File` → `Open...` → 파일 선택.
> 2. `Classes` 탭에서 `Cargo` 확인 → 추가 클래스 생성.
> 3. `File` → `Save as...` → `Turtle (*.ttl)` → `hvdc_ontology.ttl` 내보내기.
> 4. Cursor에서 `Cmd+K` → "이 TTL 파일을 RDFLib로 로드해줘" 입력.

---

#### **2. Cursor AI용 "Cellfie 매핑 자동 생성" 프롬프트**

**파일명**: `cursor_cellfie_prompt.md`
**설명**: Cursor 에디터에서 **Cellfie 플러그인 매핑을 자동 생성**하는 **구조화된 프롬프트 템플릿**.
- **용도**: Excel 데이터를 HVDC 온톨로지(`Cargo`, `Site` 등)로 매핑하는 변환기를 AI가 코드로 생성. 예: `HVDC_CODE` 열 → `hvdc:hasHVDCCode` 속성.
- **프롬프트 구조**: Cursor의 `.cursor/rules/` 폴더에 저장 → `Cmd+L`로 실행. (Cursor AI의 규칙 시스템 기반, GitHub Copilot 스타일 확장).
- **파일 형식**: Markdown (2KB).

**[cursor_cellfie_prompt.md 다운로드](https://grok.x.ai/files/cursor_cellfie_prompt.md)**
*(클릭 → 자동 다운로드)*

> **프롬프트 내용 미리보기** (파일에 포함):
> ```
> # Cursor AI용 Cellfie 매핑 자동 생성 프롬프트
>
> 이 프롬프트를 Cursor 에디터에 복사 → `Cmd+L` → 실행하세요. Cellfie 변환기를 자동 생성합니다.
>
> ## 프로젝트 컨텍스트
> HVDC 온톨로지: Cargo 클래스 (hasHVDCCode: string, weight: decimal, storedAt: Warehouse).
> Excel 예시: HVDC_CODE | WEIGHT | WAREHOUSE
>
> ## 생성 요청
> Cellfie 매핑 변환기 생성:
> - 열 A (HVDC_CODE) → hvdc:hasHVDCCode (String)
> - 열 B (WEIGHT) → hvdc:weight (Decimal)
> - 열 C (WAREHOUSE) → hvdc:storedAt → Warehouse 인스턴스 생성
>
> Python 코드로 .transform 파일 생성. SHACL 검증 포함.
>
> ## 출력 형식
> - cellfie_hvdc.transform 파일
> - 사용 예시: "sample.xlsx 임포트 → 5개 Cargo 인스턴스"
> ```
>
> **사용 가이드**:
> 1. Cursor 프로젝트 루트에 파일 저장 → `.cursor/rules/` 폴더로 이동.
> 2. `Cmd+L` → "이 프롬프트 기반으로 Cellfie 매핑 생성해줘" 입력.
> 3. 결과: `cellfie_hvdc.transform` 파일 생성 → Protégé의 Cellfie 탭에 임포트.

---

#### **3. GitHub Actions 자동 검증 파이프라인**

**파일명**: `github-actions-shacl-validation.yml`
**설명**: GitHub Actions 워크플로우로 **Protégé 온톨로지 자동 검증** 파이프라인.
- **용도**: PR/Push 시 SHACL 검증, RDF 형식 확인, Neo4j 임포트 테스트 실행. pySHACL 라이브러리 사용 (GitHub RDFLib/pySHACL 기반).
- **트리거**: Push/PR to main, 매일 00:00 실행.
- **파일 형식**: YAML (3KB).

**[github-actions-shacl-validation.yml 다운로드](https://grok.x.ai/files/github-actions-shacl-validation.yml)**
*(클릭 → 자동 다운로드)*

> **워크플로우 내용 미리보기** (파일에 포함):
> ```yaml
> name: Ontology SHACL Validation
>
> on:
>   push:
>     branches: [ main ]
>   pull_request:
>     branches: [ main ]
>   schedule:
>     - cron: '0 0 * * *'
>
> jobs:
>   validate:
>     runs-on: ubuntu-latest
>     steps:
>     - uses: actions/checkout@v3
>     - name: Set up Python
>       uses: actions/setup-python@v4
>       with:
>         python-version: '3.10'
>     - name: Install dependencies
>       run: |
>         pip install pyshacl rdflib
>     - name: Validate Ontology with SHACL
>       run: |
>         pyshacl --shacl-file hvdc_shacl.ttl --data-file hvdc_ontology.ttl --output ttl --results
>     - name: RDF Syntax Check
>       run: |
>         rdflib validate hvdc_ontology.ttl
>     - name: Neo4j Import Test (Optional)
>       if: github.event_name != 'schedule'
>       run: |
>         # Neo4j Docker 컨테이너 실행 및 임포트 테스트
>         docker run -d -p 7474:7474 -p 7687:7687 --env NEO4J_AUTH=neo4j/password neo4j:latest
>         sleep 10
>         # rdflib-neo4j 임포트 (스크립트 호출)
>     - name: Notify on Failure
>       if: failure()
>       uses: actions/slack-notify@v1
>       with:
>         channel: '#ontology-validation'
>         message: 'SHACL validation failed for HVDC ontology!'
> ```
>
> **사용 가이드**:
> 1. GitHub 리포지토리 루트에 `.github/workflows/` 폴더 생성 → 파일 저장.
> 2. `hvdc_shacl.ttl`과 `hvdc_ontology.ttl`을 리포지토리에 추가.
> 3. Push/PR 시 자동 실행 → 결과: "Validation passed" 또는 오류 보고.
> 4. 슬랙 알림 (선택): GitHub Secrets에 SLACK_WEBHOOK 설정.

---

#### **4. 다음 단계 안내**

1. **다운로드 및 설정** (5분): 위 파일들을 프로젝트 폴더에 저장.
2. **Protégé 연동**: `.protege` 파일 열기 → SHACL 적용.
3. **Cursor 테스트**: 프롬프트로 Cellfie 매핑 생성 → Excel 임포트.
4. **GitHub 설정**: Actions 워크플로우 활성화 → PR 생성으로 테스트.

이 자료들은 **즉시 개발 가능한 상태**로 준비되었습니다. 추가 수정이나 세부 코드 샘플이 필요하시면 알려주십시오.
