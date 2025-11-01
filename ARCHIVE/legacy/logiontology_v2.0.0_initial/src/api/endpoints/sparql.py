"""SPARQL query endpoint."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from rdflib import Graph
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class SPARQLQuery(BaseModel):
    """SPARQL query request model."""
    query: str


class SPARQLResponse(BaseModel):
    """SPARQL query response model."""
    results: list
    count: int


@router.post("/", response_model=SPARQLResponse)
async def execute_sparql(query: SPARQLQuery):
    """
    Execute SPARQL query against RDF graph.

    Args:
        query: SPARQL query object

    Returns:
        Query results
    """
    try:
        # TODO: Load RDF graph from persistent store
        g = Graph()
        # g.parse("path/to/data.ttl", format="turtle")

        # Execute query
        results = g.query(query.query)

        # Convert results to list of dicts
        result_list = []
        for row in results:
            result_dict = {}
            for var in results.vars:
                result_dict[str(var)] = str(row[var]) if row[var] else None
            result_list.append(result_dict)

        return SPARQLResponse(
            results=result_list,
            count=len(result_list)
        )

    except Exception as e:
        logger.error(f"SPARQL query error: {e}")
        raise HTTPException(status_code=400, detail=f"Query error: {str(e)}")


@router.get("/sample-queries")
async def get_sample_queries():
    """Get sample SPARQL queries for HVDC ontology."""
    return {
        "queries": [
            {
                "name": "Get all cargo",
                "query": """
PREFIX hvdc: <https://hvdc-project.com/ontology#>
SELECT ?cargo ?hvdcCode ?weight
WHERE {
    ?cargo a hvdc:Cargo ;
           hvdc:hasHVDCCode ?hvdcCode .
    OPTIONAL { ?cargo hvdc:weight ?weight }
}
LIMIT 10
"""
            },
            {
                "name": "Get cargo by site",
                "query": """
PREFIX hvdc: <https://hvdc-project.com/ontology#>
SELECT ?cargo ?hvdcCode ?site
WHERE {
    ?cargo a hvdc:Cargo ;
           hvdc:hasHVDCCode ?hvdcCode ;
           hvdc:destinedTo ?site .
}
"""
            },
            {
                "name": "Get flow code distribution",
                "query": """
PREFIX hvdc: <https://hvdc-project.com/ontology#>
SELECT ?flowCode (COUNT(?cargo) AS ?count)
WHERE {
    ?cargo a hvdc:Cargo ;
           hvdc:hasFlowCode ?flowCode .
}
GROUP BY ?flowCode
ORDER BY ?flowCode
"""
            }
        ]
    }


