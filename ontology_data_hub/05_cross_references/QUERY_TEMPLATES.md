# SPARQL Query Templates

**Purpose**: Ready-to-use SPARQL queries organized by ontology category
**Last Updated**: 2025-10-31

---

## Warehouse Operations & Flow Code

### Flow Code Distribution

```sparql
PREFIX hvdc: <http://samsung.com/project-logistics#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT
    ?flowCode
    ?description
    (COUNT(?case) AS ?count)
    ((COUNT(?case) * 100.0 / (SELECT (COUNT(?c) AS ?total) WHERE { ?c a hvdc:Case })) AS ?percentage)
WHERE {
  ?case hvdc:hasFlowCode ?flowCode ;
        hvdc:hasFlowDescription ?description .
}
GROUP BY ?flowCode ?description
ORDER BY ?flowCode
```

### AGI/DAS Compliance Check

```sparql
PREFIX hvdc: <http://samsung.com/project-logistics#>

SELECT ?case ?finalLocation ?flowCode ?overrideReason
WHERE {
  ?case hvdc:hasFinalLocation ?finalLocation .
  FILTER(?finalLocation IN ("AGI", "DAS"))
  ?case hvdc:hasFlowCode ?flowCode .
  OPTIONAL {
    ?case hvdc:hasFlowOverrideReason ?overrideReason
  }
}
ORDER BY ?flowCode
```

### Flow 5 Analysis

```sparql
PREFIX hvdc: <http://samsung.com/project-logistics#>

SELECT ?case ?flowCode ?description ?overrideReason ?finalLocation
WHERE {
  ?case hvdc:hasFlowCode "5"^^xsd:string .
  ?case hvdc:hasFlowDescription ?description .
  OPTIONAL { ?case hvdc:hasFlowOverrideReason ?overrideReason }
  OPTIONAL { ?case hvdc:hasFinalLocation ?finalLocation }
}
ORDER BY ?case
LIMIT 100
```

---

## Document OCR & Trust Layer

### OCR Quality Metrics

```sparql
PREFIX ldg: <http://example.com/ldg#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT
    ?doc
    ?meanConf
    ?tableAcc
    ?numericInt
    ?entityMatch
WHERE {
  ?doc ldg:hasMetric ?metric .
  ?metric ldg:hasMeanConf ?meanConf ;
          ldg:hasTableAcc ?tableAcc ;
          ldg:hasNumericIntegrity ?numericInt ;
          ldg:hasEntityMatch ?entityMatch .
  FILTER(?meanConf >= 0.92 && ?tableAcc >= 0.98 && ?entityMatch >= 0.98)
}
ORDER BY DESC(?meanConf)
```

### KPI Gate Violations

```sparql
PREFIX ldg: <http://example.com/ldg#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?doc ?meanConf ?tableAcc ?numericInt ?entityMatch ?violation
WHERE {
  ?doc ldg:hasMetric ?metric .
  ?metric ldg:hasMeanConf ?meanConf ;
          ldg:hasTableAcc ?tableAcc ;
          ldg:hasNumericIntegrity ?numericInt ;
          ldg:hasEntityMatch ?entityMatch .
  BIND(
    IF(?meanConf < 0.92, "MEAN_CONF_BELOW_THRESHOLD",
    IF(?tableAcc < 0.98, "TABLE_ACC_BELOW_THRESHOLD",
    IF(?numericInt != 1.00, "NUMERIC_INTEGRITY_NOT_PERFECT",
    IF(?entityMatch < 0.98, "ENTITY_MATCH_BELOW_THRESHOLD", ""))))
    AS ?violation
  )
  FILTER(?violation != "")
}
```

---

## Invoice & Cost Management

### Cost Guard Analysis

```sparql
PREFIX hvdc: <http://samsung.com/project-logistics#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT
    ?invoice
    ?vendor
    ?totalUSD
    ?deltaPercent
    ?costGuardBand
WHERE {
  ?invoice hvdc:hasVendor ?vendor ;
           hvdc:hasTotalUSD ?totalUSD ;
           hvdc:hasDeltaPercent ?deltaPercent ;
           hvdc:hasCostGuardBand ?costGuardBand .
  FILTER(?deltaPercent > 3.0)
}
ORDER BY DESC(?deltaPercent)
```

### PRISM.KERNEL Audit Trail

```sparql
PREFIX hvdc: <http://samsung.com/project-logistics#>

SELECT ?invoice ?verdict ?deltaPercent ?proofHash
WHERE {
  ?invoice hvdc:hasPrismKernel [
      hvdc:hasVerdict ?verdict ;
      hvdc:hasDeltaPercent ?deltaPercent ;
      hvdc:hasProofHash ?proofHash
    ]
}
ORDER BY ?verdict
```

---

## Network Integration

### Node Coverage

```sparql
PREFIX hvdc: <http://samsung.com/project-logistics#>

SELECT
    (COUNT(DISTINCT ?warehouse) AS ?warehouseCount)
    (COUNT(DISTINCT ?site) AS ?siteCount)
    (COUNT(DISTINCT ?mosb) AS ?mosbCount)
WHERE {
  { ?warehouse a hvdc:Warehouse }
  UNION
  { ?site a hvdc:Site }
  UNION
  { ?mosb a hvdc:OffshoreBase }
}
```

### Vendor Distribution

```sparql
PREFIX hvdc: <http://samsung.com/project-logistics#>

SELECT
    ?vendor
    (COUNT(?case) AS ?caseCount)
    (AVG(?cbm) AS ?avgCBM)
WHERE {
  ?case hvdc:hasVendor ?vendor ;
        hvdc:hasCBM ?cbm .
}
GROUP BY ?vendor
ORDER BY DESC(?caseCount)
```

---

## Complex Cross-Domain Queries

### Flow Code + OCR Quality

```sparql
PREFIX hvdc: <http://samsung.com/project-logistics#>
PREFIX ldg: <http://example.com/ldg#>

SELECT
    ?case
    ?flowCode
    ?meanConf
    ?tableAcc
WHERE {
  ?case hvdc:hasFlowCode ?flowCode ;
        hvdc:hasDocument ?doc .
  ?doc ldg:hasMetric ?metric .
  ?metric ldg:hasMeanConf ?meanConf ;
          ldg:hasTableAcc ?tableAcc .
  FILTER(?meanConf >= 0.92 && ?tableAcc >= 0.98)
}
LIMIT 50
```

### AGI/DAS + Invoice Cost

```sparql
PREFIX hvdc: <http://samsung.com/project-logistics#>

SELECT
    ?case
    ?finalLocation
    ?flowCode
    ?totalUSD
    ?deltaPercent
WHERE {
  ?case hvdc:hasFinalLocation ?finalLocation .
  FILTER(?finalLocation IN ("AGI", "DAS"))
  ?case hvdc:hasFlowCode ?flowCode .
  ?case hvdc:hasInvoice ?invoice .
  ?invoice hvdc:hasTotalUSD ?totalUSD ;
           hvdc:hasDeltaPercent ?deltaPercent .
  FILTER(?deltaPercent > 3.0)
}
ORDER BY DESC(?deltaPercent)
```

---

## Data Quality Queries

### Missing Required Fields

```sparql
PREFIX hvdc: <http://samsung.com/project-logistics#>

SELECT ?case ?field
WHERE {
  VALUES ?field { "hasFlowCode" "hasVendor" "hasHvdcCode" }
  ?case a hvdc:Case .
  FILTER NOT EXISTS {
    ?case hvdc:hasFlowCode [] .
    ?case hvdc:hasVendor [] .
    ?case hvdc:hasHvdcCode [] .
  }
}
```

### Override Tracking

```sparql
PREFIX hvdc: <http://samsung.com/project-logistics#>

SELECT
    (COUNT(?case) AS ?totalWithOverride)
    (COUNT(DISTINCT ?reason) AS ?uniqueReasons)
WHERE {
  ?case hvdc:hasFlowOverrideReason ?reason .
}
```

---

## Statistical Aggregations

### Monthly Flow Distribution

```sparql
PREFIX hvdc: <http://samsung.com/project-logistics#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT
    ?month
    ?flowCode
    (COUNT(?case) AS ?count)
WHERE {
  ?case hvdc:hasFlowCode ?flowCode ;
        hvdc:hasDate ?date .
  BIND(STRBEFORE(STR(?date), "-") AS ?month)
}
GROUP BY ?month ?flowCode
ORDER BY ?month ?flowCode
```

### WH Handling Efficiency

```sparql
PREFIX hvdc: <http://samsung.com/project-logistics#>

SELECT
    ?warehouse
    (COUNT(DISTINCT ?case) AS ?caseCount)
    (AVG(?daysInWH) AS ?avgDays)
WHERE {
  ?case hvdc:hasInboundEvent [
      hvdc:hasLocationAtEvent ?warehouse ;
      hvdc:hasEventDate ?inDate
    ] .
  ?case hvdc:hasOutboundEvent [
      hvdc:hasEventDate ?outDate
    ] .
  BIND((?outDate - ?inDate) AS ?daysInWH)
}
GROUP BY ?warehouse
ORDER BY DESC(?caseCount)
```

---

## Notes

All queries assume standard HVDC namespaces:
- `PREFIX hvdc: <http://samsung.com/project-logistics#>`
- `PREFIX ldg: <http://example.com/ldg#>`
- `PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>`

**See Also**: `USAGE_GUIDE.md`, `FLOW_CODE_LINEAGE.md`

