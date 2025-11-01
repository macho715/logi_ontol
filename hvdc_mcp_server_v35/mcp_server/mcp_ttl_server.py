from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .sparql_engine import SPARQLEngine

app = FastAPI(title="MCP TTL Server v3.5", version="3.5")

engine = SPARQLEngine()

class QueryRequest(BaseModel):
    query: str

@app.post("/mcp/query")
def generic_query(request: QueryRequest):
    results = engine.graph.query(request.query)
    return {"results": [dict(row) for row in results]}

@app.get("/flow/distribution")
def flow_distribution():
    return engine.get_flow_code_distribution_v35()

@app.get("/flow/compliance")
def flow_compliance():
    return engine.get_agi_das_compliance()

@app.get("/flow/overrides")
def flow_overrides():
    return engine.get_override_cases()

@app.get("/case/{case_id}")
def case_lookup(case_id: str):
    case = engine.get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@app.get("/flow/5/analysis")
def flow_5_analysis():
    return engine.get_flow_5_analysis()

@app.get("/flow/0/status")
def pre_arrival_status():
    return engine.get_pre_arrival_status()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

