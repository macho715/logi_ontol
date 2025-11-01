"""Neo4j Cypher query endpoint."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

from src.graph.neo4j_store import Neo4jStore

logger = logging.getLogger(__name__)

router = APIRouter()


class CypherQuery(BaseModel):
    """Cypher query request model."""
    query: str
    parameters: dict = {}


class CypherResponse(BaseModel):
    """Cypher query response model."""
    results: list
    count: int


@router.post("/", response_model=CypherResponse)
async def execute_cypher(query: CypherQuery):
    """
    Execute Cypher query against Neo4j.

    Args:
        query: Cypher query object

    Returns:
        Query results
    """
    try:
        # Create Neo4j connection
        with Neo4jStore() as store:
            results = store.execute_cypher(query.query, query.parameters)

            return CypherResponse(
                results=results,
                count=len(results)
            )

    except Exception as e:
        logger.error(f"Cypher query error: {e}")
        raise HTTPException(status_code=400, detail=f"Query error: {str(e)}")


@router.get("/sample-queries")
async def get_sample_queries():
    """Get sample Cypher queries for HVDC graph."""
    return {
        "queries": [
            {
                "name": "Get all cargo nodes",
                "query": "MATCH (c:Cargo) RETURN c LIMIT 10"
            },
            {
                "name": "Get cargo with warehouse",
                "query": """
MATCH (c:Cargo)-[:STOREDAT]->(w:Warehouse)
RETURN c.hvdc_code AS cargo, w.name AS warehouse
LIMIT 10
"""
            },
            {
                "name": "Get flow path",
                "query": """
MATCH path = (p:Port)-[:FROMPORT]-(c:Cargo)-[:STOREDAT]->(w:Warehouse)-[:DESTINEDTO]->(s:Site)
RETURN path
LIMIT 5
"""
            },
            {
                "name": "Count by flow code",
                "query": """
MATCH (c:Cargo)-[:HASFLOWCODE]->(f:FlowCode)
RETURN f.flowCodeValue AS flowCode, COUNT(c) AS count
ORDER BY flowCode
"""
            }
        ]
    }


