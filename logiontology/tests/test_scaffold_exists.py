def test_scaffold_exists():
    import importlib
    for mod in [
        "logiontology",
        "logiontology.core.models",
        "logiontology.core.contracts",
        "logiontology.core.ids",
        "logiontology.ingest.excel",
        "logiontology.mapping.registry",
        "logiontology.validation.schema_validator",
        "logiontology.rdfio.writer",
        "logiontology.pipeline.main",
    ]:
        importlib.import_module(mod)
