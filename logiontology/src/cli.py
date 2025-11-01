from __future__ import annotations
import typer
from pathlib import Path
from ..pipeline.main import run_pipeline_excel_to_ttl
from ..core.ids import deterministic_id

app = typer.Typer(help="Logiontology CLI: ingest/map/validate/reason/report + Full Stack MVP")


@app.command()
def run(xlsx: str, out: str = "out.ttl"):
    """Run end-to-end pipeline: Excel → TTL."""
    run_pipeline_excel_to_ttl(xlsx, out)
    typer.echo(f"✅ Wrote {out}")


@app.command()
def make_id(kind: str, parts: list[str] = typer.Argument(None)):
    """Generate deterministic ID from kind + parts."""
    parts = parts or []
    print(deterministic_id(kind, *parts))


@app.command()
def ingest_excel(
    file: str = typer.Argument(..., help="Excel file path"),
    out: str = typer.Option("output/flows.ttl", help="Output TTL file path")
):
    """Ingest Excel file and convert to RDF."""
    from src.ingest.excel_to_rdf import ExcelToRDFConverter

    converter = ExcelToRDFConverter()
    converter.convert(Path(file), Path(out))
    typer.echo(f"✓ Converted {file} → {out}")


@app.command()
def load_neo4j(
    ttl_file: str = typer.Argument(..., help="TTL file to load"),
    uri: str = typer.Option("bolt://localhost:7687", help="Neo4j URI")
):
    """Load RDF TTL file into Neo4j."""
    from src.graph.loader import Neo4jLoader
    from src.graph.neo4j_store import Neo4jStore

    store = Neo4jStore(uri=uri)
    loader = Neo4jLoader(neo4j_store=store)

    typer.echo(f"Loading {ttl_file} into Neo4j...")
    loader.load_ttl_file(Path(ttl_file))
    typer.echo(f"✓ Loaded {ttl_file} to Neo4j")


@app.command()
def setup_neo4j(uri: str = typer.Option("bolt://localhost:7687", help="Neo4j URI")):
    """Setup Neo4j database (create indexes and constraints)."""
    from src.graph.loader import Neo4jLoader
    from src.graph.neo4j_store import Neo4jStore

    store = Neo4jStore(uri=uri)
    loader = Neo4jLoader(neo4j_store=store)

    typer.echo("Setting up Neo4j database...")
    loader.setup_database()
    typer.echo("✓ Neo4j setup complete")


@app.command()
def serve_api(
    host: str = typer.Option("0.0.0.0", help="Host to bind"),
    port: int = typer.Option(8000, help="Port to bind"),
    reload: bool = typer.Option(False, help="Enable auto-reload")
):
    """Start FastAPI server."""
    import uvicorn

    typer.echo(f"Starting API server at http://{host}:{port}")
    uvicorn.run("src.api.main:app", host=host, port=port, reload=reload)


@app.command()
def batch_ingest(
    input_dir: str = typer.Argument(..., help="Directory with Excel files"),
    output_dir: str = typer.Option("output/", help="Output directory for TTL files"),
    pattern: str = typer.Option("*.xlsx", help="File pattern to match")
):
    """Batch process Excel files to RDF."""
    from src.ingest.batch_processor import BatchProcessor

    processor = BatchProcessor(validate=True)

    typer.echo(f"Processing Excel files in {input_dir}...")
    results = processor.process_directory(Path(input_dir), Path(output_dir), pattern)
    typer.echo(f"✓ Processed {len(results)} files")


if __name__ == "__main__":
    app()
