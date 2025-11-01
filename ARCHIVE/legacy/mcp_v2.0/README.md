# HVDC MCP TTL Server

FastAPI-based server for querying `hvdc_data.ttl` via SPARQL. Supports 8 commands for real-time logistics data analysis and GPT Custom Action integration.

## Features

- **8 Commands**: case_lookup, monthly_warehouse, vendor_summary, flow_distribution, search_by_location, search_by_date_range, sparql_query, statistics
- **SPARQL Engine**: RDFLib-based query execution on hvdc_data.ttl (74,324 triples)
- **GPT Custom Action Ready**: CORS enabled, OpenAPI schema auto-generated
- **Docker Support**: Containerized deployment
- **Health Checks**: `/health` endpoint for monitoring
- **Auto Documentation**: FastAPI `/docs` and `/redoc` endpoints

## Quick Start

### Local Development

```bash
# Clone or navigate to project
cd hvdc_mcp_server

# Install dependencies
pip install -r requirements.txt

# Run server
python -m uvicorn src.server:app --reload --host 0.0.0.0 --port 8000
```

Server will start at: `http://localhost:8000`

### Docker Deployment

```bash
# Build and run with docker-compose
docker-compose up --build

# Or build and run manually
docker build -t hvdc-mcp-server .
docker run -p 8000:8000 hvdc-mcp-server
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

### GET /commands

List all available commands with descriptions.

### GET /docs

Interactive API documentation (Swagger UI).

## Supported Commands

1. **case_lookup** - Lookup case by ID
2. **monthly_warehouse** - Monthly warehouse inbound/outbound summary
3. **vendor_summary** - Vendor summary with case counts
4. **flow_distribution** - Distribution of cases by FLOW code
5. **search_by_location** - Search events by location
6. **search_by_date_range** - Search events by date range
7. **sparql_query** - Execute custom SPARQL SELECT query
8. **statistics** - Get overall TTL statistics

See detailed documentation in `docs/API.md` for all commands with examples.

## GPT Custom Action Integration

### Step 1: Download OpenAPI Schema

After starting the server:

```bash
curl http://localhost:8000/openapi.json > hvdc_mcp_openapi.json
```

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

See detailed guide in `docs/GPT_INTEGRATION.md`.

## Configuration

Environment variables (see `env.example`):

- `TTL_PATH`: Path to hvdc_data.ttl (default: `data/hvdc_data.ttl`)
- `SERVER_HOST`: Server host (default: `0.0.0.0`)
- `SERVER_PORT`: Server port (default: `8000`)
- `ALLOWED_ORIGINS`: CORS allowed origins (default: `*`)

## Development

See `docs/DEPLOYMENT.md` for detailed deployment guide.

## Documentation

- `docs/API.md` - Complete API documentation
- `docs/DEPLOYMENT.md` - Deployment guide
- `docs/GPT_INTEGRATION.md` - GPT Custom Action integration

## License

Internal Samsung Project - Confidential

---

**Version**: 1.0.0
**Status**: Production Ready
**Last Updated**: 2025-10-30


