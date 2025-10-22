# HVDC Project Lightning 데이터 통합

## 프로젝트 개요

**HVDC Project Lightning** 그룹은 ABU 그룹과 유사하지만 더 큰 규모의 물류 조정 그룹입니다:

- **메시지 수**: 20,990개 (ABU 67,499개보다 적지만 상당한 규모)
- **활동기간**: 2022-11-15 ~ 2025년 현재
- **주요 선박**: JPT62/71, Thuraya, Bushra, Razan, Taibah, Wardeh, Jewaher, Marwah
- **주요 담당자**: Khemlal-SCT(1324), Ramaju Das(1272), 정상욱(982), Roy Kim(738), Haitham(644)
- **이미지**: 85개 WhatsApp 이미지 + 1개 스티커

## ABU 시스템과의 차이점

| 항목 | ABU | Lightning |

|------|-----|-----------|

| 메시지 수 | 67,499 | 20,990 |

| 주요 운영 | Abu Dhabi 물류 | 다중 선박 운항 조정 |

| 이미지 수 | 120+ | 85+ |

| 문서화 | Guideline 있음 | Guideline 있음 ✅ |

| 활동기간 | 짧음 | 길음 (2022~) |

## 통합 전략 (ABU 시스템 재사용)

### 1. 기존 스크립트 재활용

ABU 시스템에서 개발한 3개 스크립트를 Lightning에 맞게 수정:

#### A. `scripts/integrate_lightning_images.py` (from ABU images)

```python
# ABU 이미지 통합 스크립트를 Lightning용으로 수정
# - 입력: HVDC Project Lightning/ 폴더
# - 출력: output/lightning_with_images.ttl
# - 이미지 메타데이터: 85개 이미지 + 파일명/크기/날짜
```

#### B. `scripts/build_lightning_cross_references.py` (from ABU cross-ref)

```python
# Lightning WhatsApp 텍스트에서 엔티티 추출:
# - 선박명: JPT62, JPT71, Thuraya, Bushra, Razan, Wardeh 등
# - 담당자: Khemlal, Ramaju Das, 정상욱, Roy Kim, Haitham 등
# - 위치: AGI, DAS, MOSB, MW4, West Harbor 등
# - 작업 타입: RORO, LOLO, Bunkering, Backload, Offloading
# - 자재/장비: Container, CCU, Basket, HCS, Wall Panel, Crane
```

#### C. `scripts/visualize_lightning_integrated.py` (from ABU visualization)

```python
# Lightning 통합 데이터 시각화:
# - Vessel operations timeline (선박별 운항 스케줄)
# - Person-Vessel-Location network (담당자-선박-위치 관계)
# - Cargo flow diagram (자재 흐름도)
# - Operations frequency (작업 빈도 분석)
```

### 2. 네임스페이스 정의

```python
LIGHTNING = Namespace("http://example.org/lightning/")
LIGHTNINGI = Namespace("http://example.org/lightning/instance/")

# 엔티티 타입
LIGHTNING.Vessel
LIGHTNING.Operation
LIGHTNING.Cargo
LIGHTNING.Location
LIGHTNING.Person
LIGHTNING.Message
LIGHTNING.Image
```

### 3. 주요 추출 패턴

```python
EXTRACTION_PATTERNS = {
    'vessels': r'\b(JPT\s*\d+|Thuraya|Bushra|Razan|Taibah|Wardeh|Jewaher|Marwah|Nasayem|Jopetwil|Tamara)\b',
    'locations': r'\b(AGI|DAS|MOSB|MW\d+|West Harbor|Anchorage|Jetty \d+)\b',
    'operations': r'\b(RORO|LOLO|Bunkering|Backload|Offload(?:ing)?|Loading|Cast off|ETA|ETD|ATA|ATD)\b',
    'cargo': r'\b(Container|CCU|Basket|HCS|Wall Panel|Crane|Manlift|Skip|Porta [Cc]abin)\b',
    'times': r'(\d{1,2}:\d{2}|\d{4}hrs|tomorrow|today)',
}
```

### 4. RDF 구조 예시

```turtle
lightningi:Vessel_JPT62 a lightning:Vessel ;
    rdfs:label "JPT62" ;
    lightning:hasOperation lightningi:Op_20240825_RORO ;
    lightning:atLocation lightningi:Loc_AGI .

lightningi:Op_20240825_RORO a lightning:Operation ;
    lightning:operationType "RORO" ;
    lightning:date "2024-08-25"^^xsd:date ;
    lightning:vessel lightningi:Vessel_JPT62 ;
    lightning:location lightningi:Loc_AGI ;
    lightning:responsiblePerson lightningi:Person_Khemlal .

lightningi:Message_20240825_073600 a lightning:Message ;
    lightning:sender lightningi:Person_Haitham ;
    lightning:content "JPT62 at underway to agi eta 15:00hrs" ;
    lightning:timestamp "2024-08-25T07:36:00"^^xsd:dateTime ;
    lightning:mentionsVessel lightningi:Vessel_JPT62 ;
    lightning:mentionsLocation lightningi:Loc_AGI .
```

## 구현 단계

### Phase 1: 이미지 통합 (1-2시간)

1. `scripts/integrate_lightning_images.py` 생성
2. 85개 이미지 메타데이터 추출
3. `output/lightning_with_images.ttl` 생성
4. `reports/lightning/images_integration_report.md` 생성

### Phase 2: 엔티티 추출 및 크로스 레퍼런스 (2-3시간)

1. `scripts/build_lightning_cross_references.py` 생성
2. WhatsApp 텍스트에서 엔티티 추출:

   - 선박: 10-15개
   - 담당자: 20-30명
   - 위치: 5-10개
   - 작업: 500+ 건

3. 관계 매핑: Vessel ↔ Operation ↔ Person ↔ Location
4. `output/lightning_integrated_system.ttl` 생성
5. `reports/lightning/cross_references_report.md` 생성

### Phase 3: 시각화 및 분석 (1-2시간)

1. `scripts/visualize_lightning_integrated.py` 생성
2. Mermaid 다이어그램 생성:

   - Vessel Operations Timeline
   - Person-Vessel Network
   - Cargo Flow Diagram
   - Location Activity Heatmap

3. `reports/lightning/visualization_report.md` 생성
4. `reports/lightning/integrated_stats.json` 생성

### Phase 4: SPARQL 쿼리 및 문서화 (1시간)

1. `logiontology/configs/lightning_sparql_queries.sparql` 생성
2. 주요 쿼리 15개:

   - 선박별 운항 이력
   - 담당자별 작업 부하
   - 위치별 활동 빈도
   - 자재 흐름 추적
   - 지연 분석

3. `reports/lightning/final_integration_report.md` 생성

### Phase 5: ABU-Lightning 비교 분석 (1시간)

1. `scripts/compare_abu_lightning.py` 생성
2. 비교 항목:

   - 메시지 패턴
   - 담당자 역할
   - 작업 타입 분포
   - 효율성 메트릭

3. `reports/final/ABU_LIGHTNING_COMPARISON.md` 생성

## 예상 결과

### RDF 통계

- **총 트리플**: 약 15,000-20,000개 (ABU 23,331개보다 적음)
- **메시지 처리**: 20,990개
- **이미지 통합**: 85개
- **선박 엔티티**: 10-15개
- **담당자 엔티티**: 20-30명
- **작업 엔티티**: 500+ 건

### 문서 생성

- `reports/lightning/` 폴더:
  - `images_integration_report.md`
  - `cross_references_report.md`
  - `visualization_report.md`
  - `integrated_stats.json`
  - `final_integration_report.md`
- `reports/final/ABU_LIGHTNING_COMPARISON.md`

### Git 커밋

```bash
git commit -m "feat: Integrate HVDC Project Lightning data into RDF ontology

- Add Lightning image metadata (85 images)
- Extract vessel, person, location, operation entities
- Build cross-reference mappings
- Generate visualization with Mermaid diagrams
- Create SPARQL query examples
- Compare with ABU system

Statistics:
- Messages processed: 20,990
- RDF triples: ~18,000
- Vessels: 12
- Persons: 28
- Operations: 550+
- Integration rate: 95%+"
```

## 파일 구조

```
logi_ontol/
├── HVDC Project Lightning/        # 원본 데이터 (제공됨)
│   ├── Guideline_HVDC_Project_lightning (1).md
│   ├── ‎[HVDC]⚡️Project lightning⚡️님과의 WhatsApp 대화.txt
│   └── IMG-*.jpg (85개)
├── scripts/
│   ├── integrate_lightning_images.py
│   ├── build_lightning_cross_references.py
│   ├── visualize_lightning_integrated.py
│   └── compare_abu_lightning.py
├── output/
│   ├── lightning_with_images.ttl
│   ├── lightning_integrated_system.ttl
│   └── abu_lightning_comparison_data.json
├── reports/
│   ├── lightning/
│   │   ├── images_integration_report.md
│   │   ├── cross_references_report.md
│   │   ├── visualization_report.md
│   │   ├── integrated_stats.json
│   │   └── final_integration_report.md
│   └── final/
│       └── ABU_LIGHTNING_COMPARISON.md
└── logiontology/configs/
    └── lightning_sparql_queries.sparql
```

## 성공 기준

- ✅ 20,990개 메시지 100% 처리
- ✅ 85개 이미지 메타데이터 통합
- ✅ 선박/담당자/위치/작업 엔티티 추출 완료
- ✅ RDF 통합률 ≥ 95%
- ✅ Mermaid 다이어그램 4개 이상
- ✅ SPARQL 쿼리 15개
- ✅ ABU-Lightning 비교 분석 완료

## 다음 단계 (선택)

1. **실시간 대시보드**: Lightning 운항 현황 대시보드
2. **예측 분석**: 선박 도착 예측, 지연 분석
3. **통합 시스템**: ABU + Lightning 통합 운영 시스템
4. **자동화**: 메시지 자동 분류, 알림 시스템
