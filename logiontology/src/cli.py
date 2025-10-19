from __future__ import annotations
import typer
from ..pipeline.main import run_pipeline_excel_to_ttl
from ..core.ids import deterministic_id

app = typer.Typer(help="Logiontology CLI: ingest/map/validate/reason/report")


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


if __name__ == "__main__":
    app()
