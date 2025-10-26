# HVDC Flow Code System Guide v1.0

## Overview

The **Flow Code System** provides a unified classification framework for HVDC logistics operations, enabling real-time tracking, bottleneck detection, and KPI monitoring across the entire supply chain network.

## Flow Code Definitions

| Code | Name | Description | Path Example |
|------|------|-------------|--------------|
| **0** | Pre-Arrival | Documents only, no physical cargo movement | Invoice/PL/BL pending customs clearance |
| **1** | Direct Delivery | Port → Site (no intermediate stops) | Khalifa Port → AGI (offshore direct) |
| **2** | WH Once | Port → Warehouse → Site | Zayed Port → DSV → MIR |
| **3** | WH + MOSB | Port → WH → MOSB → Site | Khalifa → DSV → MOSB → DAS |
| **4** | WH Double + MOSB | Port → WH → WH → MOSB → Site | Complex multi-hop flows |

## Calculation Formula

The Flow Code is calculated using the following business rule:

```python
if is_pre_arrival:
    flow_code = 0
else:
    flow_code = min(1 + wh_hops + (1 if offshore else 0), 4)
```

### Parameters

- **`wh_hops`**: Number of warehouse handling steps (0, 1, 2, ...)
- **`offshore`**: Boolean flag indicating MOSB involvement (True/False)
- **`is_pre_arrival`**: Boolean flag for documents-only state (True/False)

### Examples

```python
# Pre-Arrival
calculate_flow_code(wh_hops=0, offshore=False, pre_arrival=True)  → 0

# Direct Delivery (Port → Site)
calculate_flow_code(wh_hops=0, offshore=False, pre_arrival=False) → 1

# WH Once (Port → WH → Site)
calculate_flow_code(wh_hops=1, offshore=False, pre_arrival=False) → 2

# WH + MOSB (Port → WH → MOSB → Site)
calculate_flow_code(wh_hops=1, offshore=True, pre_arrival=False)  → 3

# WH Double + MOSB (Port → WH → WH → MOSB → Site)
calculate_flow_code(wh_hops=2, offshore=True, pre_arrival=False)  → 4

# Clipping: (1 + 5 + 1 = 7) → clipped to 4
calculate_flow_code(wh_hops=5, offshore=True, pre_arrival=False)  → 4
```

## Transport Modes

### Container Flow

**Attributes:**
- `gate_appt_win_min` (0-1440): Gate appointment window in minutes
- `cy_in_out_lag_hr` (≥0): Container yard in/out lag in hours
- `unload_rate_tph` (>0): Unload rate in tons per hour

**Use Cases:**
- Standard container shipments via Khalifa Port or Jebel Ali Port
- Gate appointment scheduling and CY optimization
- Container dwell time tracking

### Bulk Flow

**Attributes:**
- `unload_rate_tph` (>0): Unload rate in tons per hour
- `spillage_risk_pct` (0-100): Spillage risk percentage

**Use Cases:**
- Heavy/bulk cargo via Zayed Port
- Spillage risk monitoring for bulk materials
- Unload rate optimization

### Land Transport Flow

**Attributes:**
- `convoy_period_min` (≥0): Convoy escort period in minutes
- `dot_permit_lead_days` (≥0): DOT permit acquisition lead time in days

**Use Cases:**
- Truck/convoy transport to onshore sites (MIR, SHU)
- DOT permit tracking and compliance
- Convoy scheduling optimization

### LCT/Barge Flow

**Attributes:**
- `ramp_cycle_min` (>0): Ramp loading/unloading cycle in minutes
- `stowage_util_pct` (0-100): Stowage space utilization percentage
- `lolo_slots` (≥0): Number of Lift-On/Lift-Off slots
- `voyage_time_hours` (>0): Voyage time from MOSB to offshore site in hours

**Use Cases:**
- Offshore transport to AGI/DAS via MOSB
- LCT ramp cycle optimization
- LOLO operations scheduling
- Voyage time prediction

## Key Performance Indicators (KPIs)

### 1. Direct Delivery Rate

**Definition:** Percentage of shipments with FlowCode=1 (direct delivery)

**Calculation:**
```
Direct Delivery Rate = (Count of FlowCode=1) / (Total Flows) × 100%
```

**Target:** **Maximize** (reduces handling costs and dwell time)

**SPARQL Query:**
```sparql
PREFIX hvdc-flow: <https://hvdc.example.org/flow#>

SELECT
  (100.0 * SUM(IF(?code = 1, 1, 0)) / COUNT(?flow) AS ?directRate)
WHERE {
  ?flow hvdc-flow:hasFlowCode ?code .
}
```

### 2. MOSB Pass Rate

**Definition:** Percentage of flows passing through MOSB offshore hub

**Calculation:**
```
MOSB Pass Rate = (Count of offshore_flag=True) / (Total Flows) × 100%
```

**Target:** **Monitor** (indicates offshore site dependencies)

**SPARQL Query:**
```sparql
PREFIX hvdc-flow: <https://hvdc.example.org/flow#>

SELECT
  (100.0 * SUM(IF(?offshore, 1, 0)) / COUNT(?flow) AS ?mosbPassRate)
WHERE {
  ?flow hvdc-flow:hasOffshoreFlag ?offshore .
}
```

### 3. Average WH Hops

**Definition:** Average number of warehouse handling steps per shipment

**Calculation:**
```
Avg WH Hops = SUM(wh_handling) / (Total Flows)
```

**Target:** **Minimize** (reduces dwell time and costs)

**SPARQL Query:**
```sparql
PREFIX hvdc-flow: <https://hvdc.example.org/flow#>

SELECT (AVG(?whHops) AS ?avgWHHops)
WHERE {
  ?flow hvdc-flow:hasWHHandling ?whHops .
}
```

### 4. Port Dwell Days

**Definition:** Average days between port arrival and departure

**Target:** **≤ 3 days** (industry benchmark)

**Note:** Requires integration with port/customs timestamp data.

## Site/WH/Port Code Normalization

### HVDC Sites (from ontology/HVDC.MD v3.0)

| Code | Full Name | Type |
|------|-----------|------|
| **AGI** | Al Ghallan Island | Offshore Site |
| **DAS** | Das Island | Offshore Site |
| **MIR** | Mirfa Site | Onshore Site |
| **SHU** | Shuweihat Site | Onshore Site |

### Warehouses

| Code | Full Name | Type |
|------|-----------|------|
| **DSV** | DSV Indoor Warehouse | Indoor WH |
| **MOSB** | Mussafah Offshore Supply Base | Central Hub |

### Ports

| Code | Full Name | UNLOCODE |
|------|-----------|----------|
| **ZAYED_PORT** | Zayed Port | AEZYD |
| **KHALIFA_PORT** | Khalifa Port | AEKHL |
| **JEBEL_ALI_PORT** | Jebel Ali Port | AEJEA |

## SHACL Validation Rules

### Rule 1: FlowCode Range [0, 4]

```turtle
sh:property [
  sh:path hvdc-flow:hasFlowCode ;
  sh:minInclusive 0 ;
  sh:maxInclusive 4 ;
  sh:datatype xsd:integer ;
] .
```

### Rule 2: FlowCode Consistency

**Logic:** FlowCode must equal `min(1 + wh_hops + offshore, 4)` for non-PreArrival flows

```sparql
# SPARQL constraint
BIND(1 + ?wh + (IF(?offshore, 1, 0)) AS ?expected)
BIND(IF(?expected > 4, 4, ?expected) AS ?clipped)
FILTER(?code != ?clipped)
```

### Rule 3: PreArrival Constraint

**Logic:** `isPreArrival=true` **→** `FlowCode=0`

```sparql
# SPARQL constraint
SELECT $this WHERE {
  $this hvdc-flow:isPreArrival true ;
        hvdc-flow:hasFlowCode ?code .
  FILTER(?code != 0)
}
```

## Usage Examples

### Python API

```python
from src.core.flow_models import ContainerFlow, LCTFlow, FlowCode
from src.analytics.kpi_calculator import FlowKPICalculator
from src.mapping.flow_rdf_mapper import FlowRDFMapper

# Create flows
flows = [
    ContainerFlow(
        flow_id="CT001",
        flow_code=FlowCode.DIRECT,
        wh_handling=0,
        offshore_flag=False,
        gate_appt_win_min=120,
        unload_rate_tph=30.0
    ),
    LCTFlow(
        flow_id="LCT001",
        flow_code=FlowCode.WH_MOSB,
        wh_handling=1,
        offshore_flag=True,
        ramp_cycle_min=45,
        voyage_time_hours=10.5
    )
]

# Calculate KPIs
calc = FlowKPICalculator()
kpis = calc.calculate(flows)

print(f"Total Flows: {kpis.total_flows}")
print(f"Direct Delivery Rate: {kpis.direct_delivery_rate:.2f}%")
print(f"MOSB Pass Rate: {kpis.mosb_pass_rate:.2f}%")
print(f"Avg WH Hops: {kpis.avg_wh_hops:.2f}")

# Generate RDF
mapper = FlowRDFMapper.from_flows(flows)
mapper.serialize("output/flows.ttl")
```

### CLI Commands

```bash
# Generate Flow KPI Dashboard
logiontology flow-kpi-dashboard --data output/flows.ttl --out dashboard.json

# Inject mode-specific attributes
logiontology inject-flow-attributes --mode container --attrs '{"gate_appt_win_min": 120}'
```

## Integration Points

### ERP/WMS Integration

- **Site/WH Codes:** Normalize via `SiteNormalizer` class
- **Transport Events:** Map to `TransportEvent` → calculate FlowCode
- **Dwell Time:** Port/WH timestamps → KPI calculation

### ATLP/eDAS Integration

- **Customs Clearance:** Document approval event → PreArrival → Code 1/2 transition
- **eDAS Approval:** Trigger flow code recalculation

### Marine (LCT) Integration

- **Voyage Schedule:** `MarineTransport{vesselType=LCT, route, voyageTime}`
- **HSE Compliance:** Pre-voyage HSE checks and MOSB gate pass verification

## Roadmap

### Phase 1: Core Implementation (✅ Completed)
- [x] Flow Code ontology (flow_code.ttl)
- [x] SHACL validation rules
- [x] Python models and KPI calculator
- [x] Unit tests and validation tests

### Phase 2: Integration (In Progress)
- [ ] ERP/WMS connector
- [ ] ATLP/eDAS event listener
- [ ] Site normalizer integration
- [ ] Real-time KPI dashboard

### Phase 3: Advanced Features (Planned)
- [ ] Predictive dwell time model
- [ ] LCT voyage optimizer
- [ ] HSE/Permit package integration
- [ ] Cost optimization recommendations

## Performance Targets

| KPI | Target | Current |
|-----|--------|---------|
| **ETA MAPE** | ≤ 12.00% | TBD |
| **Flow Verification** | ≥ 99.90% | TBD |
| **MOSB Pass Rate** | Monitor | TBD |
| **Direct Delivery Rate** | Maximize | TBD |

## References

- **Ontology:** `ontology/HVDC.MD` v3.0
- **Infrastructure Nodes:** `ontology/core/1_CORE-02-hvdc-infra-nodes.md` v3.0
- **SHACL Shapes:** `configs/shapes/FlowCode.shape.ttl`
- **SPARQL Queries:** `configs/sparql/flow_kpi_queries.sparql`

## Support

For questions or issues, please refer to:
- Technical documentation: `logiontology/docs/`
- Test examples: `logiontology/tests/unit/test_flow_code.py`
- Integration examples: `logiontology/src/integration/`

