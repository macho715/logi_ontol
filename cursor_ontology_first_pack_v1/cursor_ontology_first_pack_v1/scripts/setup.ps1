Param(
  [string]$OntologyPath = "C:\logi_ontol\ontology_unified",
  [int]$OpenTop = 8
)
Write-Host "Setting ONTOLOGY_DOCS_DIR to $OntologyPath"
$Env:ONTOLOGY_DOCS_DIR = $OntologyPath

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  Write-Error "python not found in PATH"; exit 2
}

Write-Host "Running initial sync..."
python tools/sync_ontology_docs.py --open-top $OpenTop

Write-Host "Optional: installing pre-commit and enabling sync hook"
try {
  pip install pre-commit | Out-Null
  pre-commit install
  Write-Host "pre-commit hook installed."
} catch {
  Write-Warning "pre-commit not installed; continuing."
}
