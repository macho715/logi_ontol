# Lightning 통합 데이터 시각화 보고서

## 📊 통합 통계

- **총 선박 수**: 33개
- **총 담당자 수**: 495명
- **총 위치 수**: 23개
- **총 작업 수**: 697개
- **생성 시간**: 2025-10-22 21:14:38

## 🚢 선박별 작업 타임라인

```mermaid
gantt
    title Lightning 선박별 작업 타임라인
    dateFormat  YYYY-MM-DD
    section 주요 선박
    JOPETWIL    :active, vessel0, 2024-08-01, 2024-12-31
    Jopetwil    :active, vessel1, 2024-08-01, 2024-12-31
    jopetwil    :active, vessel2, 2024-08-01, 2024-12-31
    THURAYA    :active, vessel3, 2024-08-01, 2024-12-31
    Thuraya    :active, vessel4, 2024-08-01, 2024-12-31
    thuraya    :active, vessel5, 2024-08-01, 2024-12-31
    RAZAN    :active, vessel6, 2024-08-01, 2024-12-31
    Razan    :active, vessel7, 2024-08-01, 2024-12-31
    razan    :active, vessel8, 2024-08-01, 2024-12-31
    BUSHRA    :active, vessel9, 2024-08-01, 2024-12-31
```


## 👥 담당자-선박 네트워크

```mermaid
graph TD
    subgraph "Lightning 담당자-선박 네트워크"
        25/1/5_PM_4["25/1/5 PM 4"]
        25/7/8_PM_4["25/7/8 PM 4"]
        25/3/6_AM_7["25/3/6 AM 7"]
        25/3/7_AM_10["25/3/7 AM 10"]
        24/12/6_PM_1["24/12/6 PM 1"]
        25/3/7_AM_7["25/3/7 AM 7"]
        Vessel["Vessel"]
        25/2/6_PM_3["25/2/6 PM 3"]
        25/3/7_AM_7 --> vessel_0["Nasayem"]
        25/3/7_AM_7 --> vessel_1["JOPETWIL"]
        25/3/7_AM_7 --> vessel_2["Jopetwil"]
        25/1/5_PM_4 --> vessel_3["Target"]
        25/1/5_PM_4 --> vessel_4["JPT 62"]
        25/1/5_PM_4 --> vessel_5["Jpt 62"]
        25/3/6_AM_7 --> vessel_6["JPT62"]
        25/3/6_AM_7 --> vessel_7["Jpt62"]
        25/3/6_AM_7 --> vessel_8["JOPETWIL"]
        25/3/7_AM_10 --> vessel_9["TAMARA"]
        25/3/7_AM_10 --> vessel_10["Tamara"]
        25/3/7_AM_10 --> vessel_11["JOPETWIL"]
        24/12/6_PM_1 --> vessel_12["JPT 62"]
        24/12/6_PM_1 --> vessel_13["Jpt 62"]
        24/12/6_PM_1 --> vessel_14["RAZAN"]
        Vessel --> vessel_15["RAZAN"]
        Vessel --> vessel_16["Razan"]
        Vessel --> vessel_17["razan"]
        25/2/6_PM_3 --> vessel_18["RAZAN"]
        25/2/6_PM_3 --> vessel_19["Razan"]
        25/2/6_PM_3 --> vessel_20["razan"]
        25/7/8_PM_4 --> vessel_21["RAZAN"]
        25/7/8_PM_4 --> vessel_22["Razan"]
        25/7/8_PM_4 --> vessel_23["razan"]
    end
```


## 📦 자재 흐름 다이어그램

```mermaid
flowchart LR
    subgraph "Lightning 자재 흐름"
        A[AGI] --> B[DAS]
        B --> C[MOSB]
        C --> D[West Harbor]
        
        E[Container] --> A
        F[CCU] --> B
        G[Basket] --> C
        H[Crane] --> D
        
        A --> I[RORO Operations]
        B --> J[LOLO Operations]
        C --> K[Loading Operations]
        D --> L[Offloading Operations]
    end
```


## 📍 위치별 활동 분포

```mermaid
pie title Lightning 위치별 활동 분포
    "DAS" : 412
    "Das" : 412
    "das" : 412
    "SCT" : 388
    "sct" : 388
    "AGI" : 296
    "agi" : 296
    "MOSB" : 131
```


## ⚙️ 작업 빈도 차트

```mermaid
xychart-beta
    title "Lightning 작업 빈도"
    x-axis ["RORO", "LOLO", "Loading", "Offloading", "Bunkering", "ETA", "ETD", "Sailing", "Underway", "Cast off"]
    y-axis "선박 수" 0 --> 20
    bar [15, 12, 18, 16, 8, 20, 18, 14, 10, 6]
```


## 🔗 주요 관계 분석

### 상위 담당자 (선박 관리 수)
- **25/1/5 PM 4**: 12개 선박 관리
- **25/7/8 PM 4**: 12개 선박 관리
- **25/3/6 AM 7**: 11개 선박 관리
- **25/3/7 AM 10**: 11개 선박 관리
- **24/12/6 PM 1**: 11개 선박 관리
- **25/3/7 AM 7**: 10개 선박 관리
- **Vessel**: 10개 선박 관리
- **25/2/6 PM 3**: 10개 선박 관리
- **25/2/5 AM 7**: 9개 선박 관리
- **25/9/5 PM 4**: 9개 선박 관리

### 상위 선박 (담당자 수)
- **JOPETWIL**: 184명 담당자
- **Jopetwil**: 184명 담당자
- **jopetwil**: 184명 담당자
- **THURAYA**: 129명 담당자
- **Thuraya**: 129명 담당자
- **thuraya**: 129명 담당자
- **RAZAN**: 79명 담당자
- **Razan**: 79명 담당자
- **razan**: 79명 담당자
- **BUSHRA**: 70명 담당자

### 상위 위치 (담당자 수)
- **DAS**: 412명 담당자
- **Das**: 412명 담당자
- **das**: 412명 담당자
- **SCT**: 388명 담당자
- **sct**: 388명 담당자
- **AGI**: 296명 담당자
- **agi**: 296명 담당자
- **MOSB**: 131명 담당자
- **mosb**: 131명 담당자
- **Harbor**: 106명 담당자

## 📋 생성된 파일

- `reports/lightning/visualization_report.md`: 이 보고서
- `reports/lightning/lightning_integrated_stats.json`: 통계 데이터
- `output/lightning_integrated_system.ttl`: Lightning 통합 RDF 그래프

## 🎯 다음 단계

1. Lightning SPARQL 쿼리 예제 작성
2. ABU-Lightning 비교 분석
3. 실시간 대시보드 구축
4. 예측 분석 모델 개발
