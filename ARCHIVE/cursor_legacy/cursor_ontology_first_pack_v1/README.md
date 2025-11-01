# Cursor Pack — Ontology First (v1)

## Quick Start
1) Unzip into your repo root.
2) Open a PowerShell in the repo and run:
   ```powershell
   ./scripts/setup.ps1 -OntologyPath "C:\logi_ontol\ontology_unified" -OpenTop 8
   ```
   or double-click `scripts/run_sync.bat`.

## What it does
- Ensures `.cursor/rules/015-ontology-first.mdc` is **AlwaysApply** so your ontology docs are read **first**.
- Mirrors source docs into `docs/ontology_unified/` and auto-opens the most important ones on start.
- Adds an optional pre-commit hook to keep docs and workspace in sync.
