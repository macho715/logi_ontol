# HVDC MCP TTL Server

FastAPI-based server for querying `hvdc_data.ttl` via SPARQL. Supports 8 commands for real-time logistics data analysis.

## Features

- **8 Commands**: case_lookup, monthly_warehouse, vendor_summary, flow_distribution, search_by_location, search_by_date_range, sparql_query, statistics
- **SPARQL Engine**: RDFLib-based query execution on hvdc_data.ttl
- **GPT Custom Action Ready**: CORS enabled, OpenAPI schema auto-generated
- **Docker Support**: Containerized deployment
- **Health Checks**: `/health` endpoint for monitoring
- **Auto Documentation**: FastAPI `/docs` and `/redoc` endpoints

## Quick Start

### Local Development

```bash
# Navigate to mcp_server directory
cd hvdc_final_package/mcp_server

# Install dependencies
pip install -r requirements.txt

# Run server (from parent directory)
cd ..
python -m uvicorn mcp_server.mcp_ttl_server:app --reload --host 0.0.0.0 --port 8000
```

Server will start at: `http://localhost:8000`

### Docker Deployment

```bash
# Build and run with docker-compose
cd hvdc_final_package/mcp_server
docker-compose up --build

# Or build and run manually
docker build -t hvdc-mcp-server -f Dockerfile ..
docker run -p 8000:8000 -v $(pwd)/../sample_outputs:/app/sample_outputs:ro hvdc-mcp-server
```

## API Endpoints

### POST /mcp/query

Execute MCP command.

**Request:**
```json
{
  "command": "case_lookup",
  "params": {
    "case_id": "Case_00045"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "case_id": "Case_00045",
    "flow_code": "3",
    "vendor": null,
    "cbm": 2.54736,
    "net_weight": null,
    "inbound_event": {
      "date": "2025-05-27",
      "location": "MOSB",
      "quantity": 1.0
    },
    "outbound_event": {
      "date": "2025-04-12",
      "location": "DAS",
      "quantity": 1.0
    }
  },
  "source": "hvdc_data.ttl",
  "timestamp": "2025-10-30T12:34:56.789Z"
}
```

### GET /health

Health check endpoint.

```json
{
  "status": "healthy",
  "ttl_path": "sample_outputs/hvdc_data.ttl",
  "ttl_loaded": true,
  "triple_count": 74324,
  "timestamp": "2025-10-30T12:34:56.789Z"
}
```

### GET /commands

List all available commands with descriptions and examples.

### GET /docs

Interactive API documentation (Swagger UI).

### GET /redoc

Alternative API documentation (ReDoc).

## Supported Commands

### 1. case_lookup

Lookup case by ID.

**Parameters:**
- `case_id` (string): Case ID (e.g., "Case_00045" or "00045")

**Example:**
```bash
curl -X POST http://localhost:8000/mcp/query \
  -H "Content-Type: application/json" \
  -d '{"command": "case_lookup", "params": {"case_id": "Case_00045"}}'
```

### 2. monthly_warehouse

Monthly warehouse inbound/outbound summary.

**Parameters:**
- `year_month` (string): YYYY-MM format (e.g., "2024-03")

**Example:**
```bash
curl -X POST http://localhost:8000/mcp/query \
  -H "Content-Type: application/json" \
  -d '{"command": "monthly_warehouse", "params": {"year_month": "2024-03"}}'
```

### 3. vendor_summary

Vendor summary with case counts.

**Parameters:**
- `vendor` (string, optional): Vendor name filter

**Example:**
```bash
curl -X POST http://localhost:8000/mcp/query \
  -H "Content-Type: application/json" \
  -d '{"command": "vendor_summary", "params": {}}'
```

### 4. flow_distribution

Distribution of cases by FLOW code.

**Parameters:** None

**Example:**
```bash
curl -X POST http://localhost:8000/mcp/query \
  -H "Content-Type: application/json" \
  -d '{"command": "flow_distribution", "params": {}}'
```

### 5. search_by_location

Search events by location.

**Parameters:**
- `location` (string): Location name (e.g., "MOSB", "DAS", "DSV Indoor")

**Example:**
```bash
curl -X POST http://localhost:8000/mcp/query \
  -H "Content-Type: application/json" \
  -d '{"command": "search_by_location", "params": {"location": "MOSB"}}'
```

### 6. search_by_date_range

Search events by date range.

**Parameters:**
- `start_date` (string): YYYY-MM-DD format
- `end_date` (string): YYYY-MM-DD format

**Example:**
```bash
curl -X POST http://localhost:8000/mcp/query \
  -H "Content-Type: application/json" \
  -d '{"command": "search_by_date_range", "params": {"start_date": "2024-01-01", "end_date": "2024-12-31"}}'
```

### 7. sparql_query

Execute custom SPARQL SELECT query.

**Parameters:**
- `query` (string): SPARQL SELECT query

**Example:**
```bash
curl -X POST http://localhost:8000/mcp/query \
  -H "Content-Type: application/json" \
  -d '{"command": "sparql_query", "params": {"query": "PREFIX hvdc: <http://samsung.com/project-logistics#> SELECT ?s WHERE { ?s a hvdc:Case } LIMIT 10"}}'
```

### 8. statistics

Get overall TTL statistics.

**Parameters:** None

**Example:**
```bash
curl -X POST http://localhost:8000/mcp/query \
  -H "Content-Type: application/json" \
  -d '{"command": "statistics", "params": {}}'
```

## GPT Custom Action Integration

### Step 1: Get OpenAPI Schema

After starting the server, download the OpenAPI schema:

```bash
curl http://localhost:8000/openapi.json > hvdc_mcp_openapi.json
```

Or access it directly in your browser: `http://localhost:8000/openapi.json`

### Step 2: Import to GPT Actions

1. Go to GPT Builder
2. Navigate to "Actions" tab
3. Click "Import from OpenAPI"
4. Upload `hvdc_mcp_openapi.json`
5. Configure authentication (if needed)
6. Save and test

### Step 3: Test Integration

In GPT, try:
```
"Lookup Case_00045 from HVDC TTL data"
"Show me monthly warehouse summary for March 2024"
"What's the FLOW distribution in the TTL?"
```

## Configuration

Environment variables (see `env.example`):

- `TTL_PATH`: Path to hvdc_data.ttl (default: `sample_outputs/hvdc_data.ttl`)
- `SERVER_HOST`: Server host (default: `0.0.0.0`)
- `SERVER_PORT`: Server port (default: `8000`)
- `ALLOWED_ORIGINS`: CORS allowed origins (default: `*`)

## Troubleshooting

### "SPARQL engine not initialized"

Check that `TTL_PATH` points to a valid hvdc_data.ttl file.

```bash
# Set correct path
export TTL_PATH=/path/to/hvdc_data.ttl
```

### "Case not found"

Ensure the case_id exists in the TTL. Use `statistics` command to check total cases.

### CORS Issues

If GPT Custom Action fails with CORS error, ensure `ALLOWED_ORIGINS=*` in environment.

## Development

### Run Tests

```bash
pytest tests/test_mcp_server.py -v
```

### Add New Command

1. Add method to `sparql_engine.py`
2. Add command handler to `commands.py`
3. Add description to `COMMAND_DESCRIPTIONS`
4. Test with `/mcp/query`

## Performance

- **TTL Load Time**: ~2-3 seconds for 74K triples
- **Query Time**: <100ms for most queries
- **Memory Usage**: ~200MB (TTL in memory)

## License

Internal Samsung Project - Confidential

---

**Version**: 1.0.0
**Status**: Production Ready
**Last Updated**: 2025-10-30


