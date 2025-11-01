# MCP + Flow Code v3.5 Integration

**Date**: 2025-01-25
**Version**: 3.5
**Status**: Production Ready

---

## Architecture Overview

The integration connects Excel data through TTL conversion to a queryable MCP SPARQL server for GPT and CLI access.

```
Excel (input)
    ↓
Conversion Script (excel_to_ttl_with_events.py)
    ↓
TTL File (hvdc_status_v35.ttl with hvdc: namespace)
    ↓
SPARQL Engine (RDFLib Graph)
    ↓
FastAPI Endpoints + CLI Commands
    ↓
GPT/CLI/API Clients
```

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  HVDC STATUS(20250815) (1).xlsx                                 │
│  755 rows × 80 columns                                          │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────────────────┐
│  Flow Code v3.5 Calculator                                      │
│  - Normalize column names                                       │
│  - Calculate Flow Code 0-5                                      │
│  - Apply AGI/DAS domain rules                                   │
│  - Extract Final_Location                                       │
│  - Generate event triples                                       │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────────────────┐
│  hvdc_status_v35.ttl (9,845 lines)                              │
│  Namespace: hvdc: <http://samsung.com/project-logistics#>      │
│  - 755 Case instances                                           │
│  - 818 StockEvent instances                                     │
│  - Flow Code properties (v3.5)                                  │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────────────────┐
│  MCP Server v3.5 (hvdc_mcp_server_v35/)                         │
│  - SPARQLEngine (RDFLib)                                        │
│  - FastAPI endpoints                                            │
│  - CLI commands (Click)                                         │
└────────────────┬────────────────────────────────────────────────┘
                 │
          ┌──────┴──────┐
          ↓             ↓
┌──────────────┐  ┌──────────────┐
│  API Clients │  │  CLI Users   │
│  (GPT, curl) │  │  (terminal)  │
└──────────────┘  └──────────────┘
```

---

## Namespace Migration

### Old Namespace (from .groovy file)
```sparql
PREFIX mcp: <http://example.com/mcp#>
```

**Properties**:
- `mcp:case_id`
- `mcp:flow_code`
- `mcp:vendor`
- `mcp:inbound_event`
- `mcp:outbound_event`
- `mcp:date`
- `mcp:location`
- `mcp:quantity`

### New Namespace (Flow Code v3.5)
```sparql
PREFIX hvdc: <http://samsung.com/project-logistics#>
```

**Properties**:
- Case URIs: `hvdc:Case_XXXXX` (not `case_id`)
- `hvdc:hasFlowCode`
- `hvdc:hasVendor`
- `hvdc:hasInboundEvent`
- `hvdc:hasOutboundEvent`
- `hvdc:hasEventDate`
- `hvdc:hasLocationAtEvent`
- `hvdc:hasQuantity`

**New v3.5 Properties**:
- `hvdc:hasFlowCodeOriginal` - Original Flow Code before override
- `hvdc:hasFlowOverrideReason` - Reason for override (e.g., "AGI/DAS requires MOSB leg")
- `hvdc:hasFlowDescription` - Human-readable description
- `hvdc:hasFinalLocation` - Automatically extracted final site

---

## Query Pattern Changes

### Old Pattern (mcp: namespace)
```sparql
PREFIX mcp: <http://example.com/mcp#>
SELECT ?case_id ?flow_code
WHERE {
    ?case mcp:case_id ?case_id ;
          mcp:flow_code ?flow_code .
}
```

### New Pattern (hvdc: namespace)
```sparql
PREFIX hvdc: <http://samsung.com/project-logistics#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?caseId ?flowCode
WHERE {
    ?case a hvdc:Case ;
          hvdc:hasFlowCode ?flowStr .
    BIND(xsd:integer(?flowStr) AS ?flowCode)
    BIND(STRAFTER(STR(?case), "Case_") AS ?caseId)
}
```

**Key Differences**:
1. Case URI extraction: `STRAFTER(STR(?case), "Case_")`
2. Flow Code is string, need `xsd:integer` casting for comparisons
3. Type checking: `?case a hvdc:Case`
4. Property naming: `has` prefix pattern

---

## Key Features

### 1. Flow Code v3.5 Queries

**Distribution Query** (Flow 0-5):
```sparql
PREFIX hvdc: <http://samsung.com/project-logistics#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?flowCode ?description (COUNT(?case) AS ?count)
WHERE {
    ?case a hvdc:Case ;
          hvdc:hasFlowCode ?flowStr ;
          hvdc:hasFlowDescription ?description .
    BIND(xsd:integer(?flowStr) AS ?flowCode)
}
GROUP BY ?flowCode ?description
ORDER BY ?flowCode
```

**AGI/DAS Compliance Validation**:
```sparql
PREFIX hvdc: <http://samsung.com/project-logistics#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT
    (COUNT(?case) AS ?totalAgiDas)
    (COUNT(?compliant) AS ?compliantCount)
WHERE {
    ?case hvdc:hasFinalLocation ?loc .
    FILTER(?loc IN ("AGI", "DAS"))
    OPTIONAL {
        ?case hvdc:hasFlowCode ?flow .
        FILTER(xsd:integer(?flow) >= 3)
        BIND(?case AS ?compliant)
    }
}
```

**Override Cases Tracking**:
```sparql
PREFIX hvdc: <http://samsung.com/project-logistics#>
SELECT ?caseId ?flowCode ?flowCodeOrig ?reason ?finalLoc
WHERE {
    ?case hvdc:hasFlowCodeOriginal ?flowCodeOrig ;
          hvdc:hasFlowOverrideReason ?reason ;
          hvdc:hasFlowCode ?flowCode ;
          hvdc:hasFinalLocation ?finalLoc .
    BIND(STRAFTER(STR(?case), "Case_") AS ?caseId)
}
```

### 2. API Endpoints

| Endpoint | Method | Description | Expected Result |
|----------|--------|-------------|-----------------|
| `/flow/distribution` | GET | Flow 0-5 stats | 6 entries (one per flow code) |
| `/flow/compliance` | GET | AGI/DAS validation | 100% compliance |
| `/flow/overrides` | GET | Override tracking | 31 records |
| `/case/{case_id}` | GET | Case details | Single case JSON |
| `/flow/5/analysis` | GET | Mixed cases | 81 Flow 5 cases |
| `/flow/0/status` | GET | Pre-arrival | 71 Flow 0 cases |
| `/mcp/query` | POST | Custom SPARQL | Variable results |

### 3. CLI Commands

```bash
# Distribution
python -m mcp_server.commands flow_code_distribution_v35
# Output:
# Flow 0: 71 cases - Flow 0: Pre Arrival
# Flow 1: 255 cases - Flow 1: Port → Site
# Flow 2: 152 cases - Flow 2: Port → WH → Site
# Flow 3: 131 cases - Flow 3: Port → MOSB → Site
# Flow 4: 65 cases - Flow 4: Port → WH → MOSB → Site
# Flow 5: 81 cases - Flow 5: Mixed / Waiting / Incomplete leg

# Compliance check
python -m mcp_server.commands agi_das_compliance
# Output:
# Total AGI/DAS: 31
# Compliant: 31
# Rate: 100.00%

# Override cases
python -m mcp_server.commands override_cases
# Output: 31 cases with original flow code, new flow code, reason, and location
```

---

## Performance Considerations

### In-Memory RDFLib (Current)
- **Dataset Size**: 755 cases, ~10K triples
- **Query Time**: 50-100ms per query
- **Memory**: ~150MB
- **Scalability**: Good for <10K cases

**Pros**:
- Simple setup (no external database)
- Fast for small datasets
- Suitable for development and testing

**Cons**:
- All data in memory
- Limited to single process
- No persistent query optimization

### Production Recommendations

For larger datasets or production use:

**Apache Fuseki**:
```bash
# Setup
fuseki-server --file=hvdc_status_v35.ttl /hvdc

# Update SPARQLEngine
from SPARQLWrapper import SPARQLWrapper
sparql = SPARQLWrapper("http://localhost:3030/hvdc/query")
```

**Virtuoso**:
- Better for >100K triples
- Native RDF storage
- Advanced indexing

**Performance Targets**:
- Query time: <500ms (current: ~100ms)
- Concurrent users: 10+
- Dataset growth: Support up to 10K cases

---

## Security

### CORS Configuration

For GPT Custom Actions, add CORS middleware:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chat.openai.com"],  # GPT origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Authentication (Optional)

For production deployment, add API key authentication:

```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

@app.get("/flow/distribution", dependencies=[Depends(verify_api_key)])
def flow_distribution():
    # ... existing code
```

### Data Privacy

- **PII Protection**: TTL data contains vendor names and HVDC codes (non-sensitive)
- **NDA Considerations**: No confidential financial data exposed
- **Access Control**: Deploy behind VPN or firewall for internal use

---

## Integration with GPT

### Custom Action Configuration

1. **Start Server**:
   ```bash
   uvicorn mcp_server.mcp_ttl_server:app --host 0.0.0.0 --port 8000
   ```

2. **Download OpenAPI Spec**:
   ```bash
   curl http://localhost:8000/openapi.json > hvdc_mcp_openapi.json
   ```

3. **Configure GPT Actions**:
   - Go to GPT → Configure → Actions
   - Import `hvdc_mcp_openapi.json`
   - Set server URL: `http://your-server:8000`

4. **Test Actions**:
   ```
   User: "Show me the Flow Code distribution"
   GPT: [Calls GET /flow/distribution]

   User: "Are all AGI/DAS cases compliant?"
   GPT: [Calls GET /flow/compliance]

   User: "How many cases were overridden?"
   GPT: [Calls GET /flow/overrides]
   ```

### Example GPT Prompts

- "What's the distribution of Flow Codes in the HVDC project?"
- "Check if AGI and DAS cases comply with MOSB requirements"
- "Show me all cases that had their Flow Code overridden"
- "Analyze the mixed/incomplete cases (Flow 5)"
- "List all pre-arrival cases"

---

## Deployment Options

### Local Development
```bash
pip install -r requirements.txt
uvicorn mcp_server.mcp_ttl_server:app --reload
```

### Docker
```bash
docker-compose up
```

### Production (Linux Server)
```bash
# Install dependencies
pip install -r requirements.txt

# Run with systemd
cat > /etc/systemd/system/mcp-server.service << EOF
[Unit]
Description=MCP TTL Server v3.5

[Service]
Type=simple
User=hvdc
WorkingDirectory=/opt/hvdc_mcp_server_v35
Environment="TTL_PATH=../output/hvdc_status_v35.ttl"
ExecStart=/usr/bin/uvicorn mcp_server.mcp_ttl_server:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
EOF

systemctl enable mcp-server
systemctl start mcp-server
```

---

## Troubleshooting

### Common Issues

**1. TTL File Not Found**
```
Error: FileNotFoundError: output/hvdc_status_v35.ttl
Solution: Set TTL_PATH environment variable or copy TTL to correct location
```

**2. SPARQL Query Fails**
```
Error: Variable 'flowCode' not found
Solution: Check namespace (hvdc:), property names (hasFlowCode), and BIND statements
```

**3. Zero Results**
```
Issue: Query returns empty list
Debug:
  - Check TTL has expected data: len(engine.graph) should be ~10000
  - Verify property exists: grep "hasFlowCode" hvdc_status_v35.ttl
  - Test simple query: SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10
```

**4. Performance Slow**
```
Issue: Queries take >1 second
Solution:
  - Check dataset size (should be ~755 cases)
  - Reduce result set with LIMIT
  - Consider Fuseki for production
```

---

## Testing

### Unit Tests
```bash
pytest tests/test_sparql_queries.py -v
```

Expected results:
- `test_flow_distribution`: Pass (6 flow codes, 755 total)
- `test_agi_das_compliance`: Pass (100% compliance)
- `test_override_cases`: Pass (31 overrides)

### Integration Tests
```bash
pytest tests/test_mcp_integration.py -v
```

Validates full pipeline from TTL load to query execution.

### API Tests
```bash
pytest tests/test_mcp_server.py -v
```

Tests FastAPI endpoints with TestClient.

---

## Next Steps

1. **Deploy to Production**
   - Set up Linux server or cloud instance
   - Configure systemd service
   - Add HTTPS with nginx reverse proxy

2. **Enhance Queries**
   - Add date range filters
   - Vendor-wise summaries
   - Time series analysis

3. **GPT Integration**
   - Configure Custom Actions
   - Test with real queries
   - Create GPT instructions for context

4. **Monitoring**
   - Add logging middleware
   - Track query performance
   - Set up alerts for errors

---

## References

- **Flow Code v3.5 Documentation**: `FLOW_CODE_V35_MASTER_DOCUMENTATION.md`
- **Algorithm Specification**: `FLOW_CODE_V35_ALGORITHM.md`
- **Implementation Report**: `FLOW_CODE_V35_IMPLEMENTATION_COMPLETE.md`
- **MCP Server README**: `hvdc_mcp_server_v35/README.md`
- **RDFLib Documentation**: https://rdflib.readthedocs.io/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/

---

**Version**: 1.0
**Last Updated**: 2025-01-25
**Status**: Production Ready

