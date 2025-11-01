"""FastAPI main application for HVDC Ontology System."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="HVDC Ontology API",
    description="HVDC Full Stack MVP: Ontology Schema + Excel→RDF→Neo4j + AI Insights",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "HVDC Ontology System API v2.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "flows": "/api/flows",
            "kpi": "/api/kpi",
            "sparql": "/api/sparql",
            "cypher": "/api/cypher"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/flows")
async def list_flows(limit: int = 100, offset: int = 0):
    """
    List all logistics flows.

    Args:
        limit: Maximum number of flows to return
        offset: Offset for pagination

    Returns:
        List of flow objects
    """
    # TODO: Query from Neo4j
    return {
        "total": 0,
        "limit": limit,
        "offset": offset,
        "flows": []
    }


@app.get("/api/flows/{flow_id}")
async def get_flow(flow_id: str):
    """
    Get specific flow by ID.

    Args:
        flow_id: Flow identifier

    Returns:
        Flow object with details
    """
    # TODO: Query from Neo4j
    return {
        "flow_id": flow_id,
        "flow_code": None,
        "hvdc_code": None,
        "details": "Not implemented yet"
    }


@app.get("/api/search")
async def search_flows(
    hvdc_code: str = None,
    site: str = None,
    warehouse: str = None,
    flow_code: int = None
):
    """
    Search flows by various criteria.

    Args:
        hvdc_code: HVDC code to search for
        site: Site name
        warehouse: Warehouse name
        flow_code: Flow code (0-4)

    Returns:
        List of matching flows
    """
    # TODO: Implement search with Neo4j Cypher
    return {
        "query": {
            "hvdc_code": hvdc_code,
            "site": site,
            "warehouse": warehouse,
            "flow_code": flow_code
        },
        "results": []
    }


# Import and include routers from endpoints
try:
    from src.api.endpoints import kpi, sparql, cypher

    app.include_router(kpi.router, prefix="/api/kpi", tags=["KPI"])
    app.include_router(sparql.router, prefix="/api/sparql", tags=["SPARQL"])
    app.include_router(cypher.router, prefix="/api/cypher", tags=["Cypher"])

    logger.info("API endpoints registered successfully")
except ImportError as e:
    logger.warning(f"Could not import all endpoints: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

