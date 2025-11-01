"""
FastAPI MCP TTL Server
Real-time SPARQL query server for hvdc_data.ttl
"""
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import datetime
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

from .config import TTL_PATH, ALLOWED_ORIGINS, SERVER_HOST, SERVER_PORT
from .sparql_engine import SPARQLEngine
from .commands import execute_command, COMMAND_DESCRIPTIONS

# Initialize FastAPI app
app = FastAPI(
    title="HVDC MCP TTL Server",
    description="FastAPI server for querying hvdc_data.ttl via SPARQL. Supports 8 commands for logistics data analysis.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware (allow GPT Custom Action)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SPARQL engine
try:
    logger.info(f"Initializing SPARQL engine with TTL: {TTL_PATH}")
    engine = SPARQLEngine(TTL_PATH)
    logger.info(f"SPARQL engine initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize SPARQL engine: {e}")
    engine = None


class QueryRequest(BaseModel):
    """MCP query request model"""
    command: str = Field(..., description="Command name (e.g., 'case_lookup', 'monthly_warehouse')")
    params: Dict[str, Any] = Field(default_factory=dict, description="Command parameters")

    class Config:
        json_schema_extra = {
            "example": {
                "command": "case_lookup",
                "params": {"case_id": "Case_00045"}
            }
        }


class QueryResponse(BaseModel):
    """MCP query response model"""
    success: bool = Field(..., description="Whether the query succeeded")
    data: Any = Field(..., description="Query result data")
    source: str = Field(..., description="Data source (hvdc_data.ttl)")
    timestamp: str = Field(..., description="Response timestamp (ISO format)")
    error: Optional[str] = Field(None, description="Error message if failed")


@app.on_event("startup")
async def startup_event():
    """Server startup event"""
    logger.info(f"Starting HVDC MCP TTL Server v1.0.0")
    logger.info(f"TTL Path: {TTL_PATH}")
    logger.info(f"CORS Origins: {ALLOWED_ORIGINS}")
    if engine:
        stats = engine.get_statistics()
        logger.info(f"TTL Statistics: {stats}")


@app.post("/mcp/query", response_model=QueryResponse)
async def mcp_query(query: QueryRequest = Body(...)):
    """
    Execute MCP query command

    Supported commands:
    - case_lookup: Lookup case by ID
    - monthly_warehouse: Monthly warehouse summary
    - vendor_summary: Vendor aggregation
    - flow_distribution: FLOW code distribution
    - search_by_location: Search by location
    - search_by_date_range: Search by date range
    - sparql_query: Custom SPARQL query
    - statistics: Overall statistics
    """
    if not engine:
        raise HTTPException(
            status_code=503,
            detail="SPARQL engine not initialized. Check TTL file path."
        )

    try:
        logger.info(f"Executing command: {query.command} with params: {query.params}")
        data = execute_command(engine, query.command, query.params)

        return QueryResponse(
            success=True,
            data=data,
            source="hvdc_data.ttl",
            timestamp=datetime.datetime.now().isoformat()
        )

    except ValueError as e:
        # Client error (invalid params, case not found, etc.)
        logger.warning(f"ValueError in command {query.command}: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        # Server error (SPARQL failure, etc.)
        logger.error(f"Unexpected error in command {query.command}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/health")
async def health_check():
    """
    Health check endpoint

    Returns:
        Status and TTL load information
    """
    if not engine:
        return {
            "status": "unhealthy",
            "error": "SPARQL engine not initialized",
            "ttl_loaded": False
        }

    return {
        "status": "healthy",
        "ttl_path": TTL_PATH,
        "ttl_loaded": len(engine.graph) > 0,
        "triple_count": len(engine.graph),
        "timestamp": datetime.datetime.now().isoformat()
    }


@app.get("/commands")
async def get_commands():
    """
    List all available commands with descriptions

    Returns:
        Command list with usage examples
    """
    return {
        "commands": list(COMMAND_DESCRIPTIONS.keys()),
        "descriptions": COMMAND_DESCRIPTIONS,
        "total_commands": len(COMMAND_DESCRIPTIONS)
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "HVDC MCP TTL Server",
        "version": "1.0.0",
        "description": "FastAPI server for querying hvdc_data.ttl via SPARQL",
        "endpoints": {
            "query": "POST /mcp/query",
            "health": "GET /health",
            "commands": "GET /commands",
            "docs": "GET /docs",
            "redoc": "GET /redoc"
        },
        "timestamp": datetime.datetime.now().isoformat()
    }


def main():
    """Entry point for running the server"""
    import uvicorn
    logger.info(f"Starting server on {SERVER_HOST}:{SERVER_PORT}")
    uvicorn.run(
        "src.server:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()


