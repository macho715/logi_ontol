# Protégé Plugin Installation Guide for HVDC Project

**Version**: 1.0
**Last Updated**: 2025-10-26
**Protégé Version**: 5.6.4+
**Target**: HVDC Logistics Ontology Project

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Overview](#installation-overview)
3. [Tier 1: Critical Plugins](#tier-1-critical-plugins)
4. [Tier 2: Built-in Features](#tier-2-built-in-features)
5. [Tier 3: Optional Plugins](#tier-3-optional-plugins)
6. [Configuration Files](#configuration-files)
7. [Quick Start Examples](#quick-start-examples)
8. [Installation Checklist](#installation-checklist)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### 1. Java Development Kit (JDK)

**Required Version**: Java 11 or higher

**Verify Installation**:
```bash
java -version
```

**Install if needed**:
- Download from: [Adoptium JDK 11 (LTS)](https://adoptium.net/)
- Windows: Download `.msi` installer and run
- macOS: `brew install --cask temurin`
- Linux: `sudo apt install openjdk-11-jdk`

### 2. Protégé Desktop

**Required Version**: 5.6.4 or higher

**Download Links**:
- Windows: [Protégé-5.6.4-win.exe](https://github.com/protegeproject/protege/releases/download/v5.6.4/Protégé-5.6.4-win.exe)
- macOS: [Protégé-5.6.4-mac.dmg](https://github.com/protegeproject/protege/releases/download/v5.6.4/Protégé-5.6.4-mac.dmg)
- Linux: [Protégé-5.6.4-linux.tar.gz](https://github.com/protegeproject/protege/releases/download/v5.6.4/Protégé-5.6.4-linux.tar.gz)

**Installation**:
1. Download appropriate version for your OS
2. Install/Extract to desired location
3. Launch Protégé
4. Verify: `Help` → `About` shows version 5.6.4+

### 3. GraphViz (for OWLViz plugin)

**Required for**: OWLViz class hierarchy visualization

**Download**: [graphviz.org/download](https://graphviz.org/download/)

**Installation**:
- Windows: Download MSI installer, run, note installation path
- macOS: `brew install graphviz`
- Linux: `sudo apt install graphviz`

**Verify**:
```bash
dot -V
```

---

## Installation Overview

### Plugin Tiers

**Tier 1 (Critical - Install First)**:
- Cellfie: Excel → Ontology import
- OWLViz: Class hierarchy visualization

**Tier 2 (Built-in - Activate)**:
- SHACL: Data validation
- OntoGraf: Network graphs
- Reasoner (HermiT): Inference
- SPARQL Query: Internal queries

**Tier 3 (Optional - Enhanced Features)**:
- VOWL: Web visualization
- Explanation: Reasoning details
- Git Plugin: Version control

### Basic Plugin Installation Method

1. Launch Protégé
2. `File` → `Check for plugins...`
3. Search for plugin name
4. Click `Install`
5. Restart Protégé
6. Verify: `Window` → `Tabs` → Check for new tab

---

## Tier 1: Critical Plugins

### 1. Cellfie - Excel to Ontology Import

**Purpose**: Import Excel data directly into HVDC ontology

**Installation**:
1. `File` → `Check for plugins...`
2. Search: `Cellfie`
3. Click `Install`
4. Restart Protégé

**Configuration**:
1. Open HVDC ontology: `File` → `Open` → `hvdc_ontology.ttl`
2. `Window` → `Tabs` → `Cellfie`
3. Load mapping file: `configs/protege/cellfie_hvdc_mapping.transform`

**HVDC Usage Example**:

**Excel Format** (`sample_warehouse.xlsx`):
```
| HVDC_CODE         | WEIGHT | WAREHOUSE    | SITE | PORT    |
|-------------------|--------|--------------|------|---------|
| HVDC-ADOPT-SCT-001| 25.5   | DSV Indoor   | MIR  | ZAYED   |
| HVDC-ADOPT-SCT-002| 18.3   | MOSB         | DAS  | KHALIFA |
```

**Import Process**:
1. Cellfie tab → `Load Excel`
2. Select mapping: `cellfie_hvdc_mapping.transform`
3. Click `Transform`
4. Result: 2 `Cargo` instances created with all properties

**Verification**:
- `Individuals` tab → Check for `cargo-001`, `cargo-002`
- Properties should show: `hasHVDCCode`, `weight`, `storedAt`, `destinedTo`

---

### 2. OWLViz - Class Hierarchy Visualization

**Purpose**: Visualize HVDC ontology class structure

**Installation**:
1. **First**: Install GraphViz (see Prerequisites)
2. `File` → `Check for plugins...`
3. Search: `OWLViz`
4. Click `Install`
5. Restart Protégé

**Configuration**:
1. `Window` → `Tabs` → `OWLViz`
2. `OWLViz` → `Preferences`
3. Set GraphViz path:
   - Windows: `C:\Program Files\Graphviz\bin\dot.exe`
   - macOS: `/usr/local/bin/dot`
   - Linux: `/usr/bin/dot`

**HVDC Usage Example**:
1. Select class: `Cargo`
2. OWLViz tab will show:
   - `Cargo` at center
   - Subclasses (if any)
   - Superclass: `Project`
   - Related classes: `Site`, `Warehouse`, `FlowCode`

**Export**:
- Right-click graph → `Export as PNG`
- Save to: `docs/diagrams/cargo_hierarchy.png`

---

## Tier 2: Built-in Features

### 3. SHACL - Data Validation

**Status**: Built-in, activate via `Window` → `SHACL Shapes`

**Configuration**:
1. `Window` → `Tabs` → `SHACL Shapes`
2. Load constraints: `configs/protege/hvdc_shacl_constraints.ttl`

**HVDC Validation Rules**:

**FlowCode Range (0-4)**:
```turtle
hvdc:FlowCodeShape a sh:NodeShape ;
    sh:targetClass hvdc:FlowCode ;
    sh:property [
        sh:path hvdc:flowCodeValue ;
        sh:minInclusive 0 ;
        sh:maxInclusive 4 ;
        sh:message "FlowCode must be between 0 and 4"
    ] .
```

**Weight Positive**:
```turtle
hvdc:CargoShape a sh:NodeShape ;
    sh:targetClass hvdc:Cargo ;
    sh:property [
        sh:path hvdc:weight ;
        sh:minExclusive 0 ;
        sh:message "Weight must be positive"
    ] .
```

**Usage**:
1. Add/modify instances
2. Click `Validate` button
3. Errors shown in red
4. Fix violations before exporting

---

### 4. OntoGraf - Network Visualization

**Status**: Built-in

**Activation**:
1. `Window` → `Tabs` → `OntoGraf`

**HVDC Usage**:
1. Drag `Cargo` to canvas
2. Right-click → `Add children`
3. Right-click → `Add related individuals`
4. Result: Full network showing:
   - Cargo instances
   - Connected warehouses
   - Destination sites
   - Related B/L documents

**Export**:
- `File` → `Export graph` → PNG/PDF
- Save to: `docs/diagrams/hvdc_network.png`

---

### 5. Reasoner (HermiT) - Inference

**Status**: Built-in

**Activation**:
1. `Reasoner` menu → `HermiT`
2. Click `Start reasoner`

**HVDC Inference Example**:

**Rule**: Automatically classify high-risk flows
```turtle
hvdc:HighRiskFlow a owl:Class ;
    owl:equivalentTo [
        a owl:Restriction ;
        owl:onProperty hvdc:hasFlowCode ;
        owl:someValuesFrom [
            a owl:Restriction ;
            owl:onProperty hvdc:flowCodeValue ;
            owl:hasValue 4
        ]
    ] .
```

**Result**:
- All cargo with FlowCode=4 automatically classified as `HighRiskFlow`
- View: `Classes` tab → `Inferred hierarchy`

---

### 6. SPARQL Query - Internal Queries

**Status**: Built-in

**Activation**:
1. `Window` → `Tabs` → `SPARQL Query`

**HVDC Query Examples**:

**1. Find Cargo by HVDC Code**:
```sparql
SELECT ?cargo ?code ?weight ?warehouse
WHERE {
    ?cargo hvdc:hasHVDCCode ?code ;
           hvdc:weight ?weight ;
           hvdc:storedAt ?warehouse .
    FILTER(?code = "HVDC-ADOPT-SCT-001")
}
```

**2. List All Cargo for Site MIR**:
```sparql
SELECT ?cargo ?code ?site
WHERE {
    ?cargo hvdc:hasHVDCCode ?code ;
           hvdc:destinedTo ?site .
    ?site hvdc:siteName "MIR" .
}
```

**3. FlowCode Distribution**:
```sparql
SELECT ?flowCodeValue (COUNT(?cargo) as ?count)
WHERE {
    ?cargo hvdc:hasFlowCode ?flowCode .
    ?flowCode hvdc:flowCodeValue ?flowCodeValue .
}
GROUP BY ?flowCodeValue
ORDER BY ?flowCodeValue
```

---

## Tier 3: Optional Plugins

### 7. VOWL - Web-Based Visualization

**Installation**:
1. `File` → `Check for plugins...`
2. Search: `VOWL`
3. Click `Install`
4. Restart Protégé

**Usage**:
1. `File` → `Export` → `VOWL`
2. Generates HTML file
3. Open in browser
4. Interactive visualization with zoom/pan

**HVDC Benefit**: Share ontology structure with team via web

---

### 8. Explanation Plugin

**Installation**:
1. `File` → `Check for plugins...`
2. Search: `Explanation`
3. Click `Install`
4. Restart Protégé

**Usage**:
- After running reasoner
- Select inferred axiom
- Click `?` (Explain) button
- Shows reasoning chain

**HVDC Example**:
- Question: "Why is cargo-001 classified as HighRiskFlow?"
- Answer: Shows: `cargo-001` → `hasFlowCode` → `flowCode-4` → `flowCodeValue=4`

---

### 9. Git Plugin

**Installation**:
1. `File` → `Check for plugins...`
2. Search: `Git`
3. Click `Install`
4. Restart Protégé

**Configuration**:
1. `File` → `Git` → `Settings`
2. Set repository: `https://github.com/macho715/logi_ontol.git`
3. Set credentials

**Usage**:
- `File` → `Git` → `Commit` (save changes)
- `File` → `Git` → `Push` (upload to GitHub)
- `File` → `Git` → `Pull` (sync from team)

---

## Configuration Files

### Location: `logiontology/configs/protege/`

**1. cellfie_hvdc_mapping.transform**
- Excel column mappings for HVDC data
- Ready to import warehouse data

**2. hvdc_shacl_constraints.ttl**
- SHACL validation rules
- FlowCode: 0-4 range
- Weight: positive values
- Required properties

**3. owlviz_config.properties**
- GraphViz executable path
- Platform-specific settings

**4. README.md**
- Config file documentation
- Usage instructions

---

## Automated Launch Script

### Windows Quick Start

**File**: `scripts/launch_protege_hvdc.bat`

**Usage**:
```cmd
cd c:\logi_ontol
scripts\launch_protege_hvdc.bat
```

**Features**:
- Auto-detects Protégé installation (multiple possible paths)
- Launches Protégé with HVDC ontology pre-loaded
- Validates ontology file existence
- Displays helpful next steps

**Supported Installation Paths**:
1. `C:\Program Files\Protege-5.6.4\`
2. `C:\Program Files (x86)\Protege-5.6.4\`
3. `%USERPROFILE%\Protege-5.6.4\`
4. `c:\logi_ontol\tools\Protege-5.6.4\`

**Customization**:
- Edit `PROTEGE_PATH1` through `PROTEGE_PATH4` variables
- Set `PROTEGE_EXE` environment variable for custom location

---

## Quick Start Examples

### Example 1: Import 10 Cargo Items from Excel

**Step 1**: Prepare Excel file (`data/hvdc_cargo_batch.xlsx`)
```
HVDC_CODE | WEIGHT | WAREHOUSE | SITE | PORT
...10 rows...
```

**Step 2**: Import
1. Cellfie tab → `Load Excel`
2. Select file
3. Use mapping: `cellfie_hvdc_mapping.transform`
4. Click `Transform`

**Step 3**: Validate
1. SHACL tab → `Validate`
2. Fix any errors
3. Save: `File` → `Save as` → `hvdc_batch_001.ttl`

---

### Example 2: Visualize and Export Class Hierarchy

**Step 1**: Open ontology
- `File` → `Open` → `hvdc_ontology.ttl`

**Step 2**: Generate visualization
1. OWLViz tab
2. Select `Cargo` class
3. View hierarchy

**Step 3**: Export
- Right-click → `Export as PNG`
- Save to: `docs/diagrams/`

---

### Example 3: Run SPARQL Query for KPI

**Query**: Count cargo by FlowCode
```sparql
SELECT ?flowCodeValue (COUNT(?cargo) as ?cargoCount)
WHERE {
    ?cargo hvdc:hasFlowCode ?flowCode .
    ?flowCode hvdc:flowCodeValue ?flowCodeValue .
}
GROUP BY ?flowCodeValue
ORDER BY ?flowCodeValue
```

**Result**:
```
flowCodeValue | cargoCount
0             | 5
1             | 12
2             | 25
3             | 8
4             | 3
```

---

## Installation Checklist

### Prerequisites
- [ ] Java 11+ installed and verified
- [ ] Protégé 5.6.4+ downloaded and launched
- [ ] GraphViz installed (for OWLViz)

### Tier 1 (Critical)
- [ ] Cellfie plugin installed
- [ ] Cellfie mapping file loaded
- [ ] OWLViz plugin installed
- [ ] OWLViz GraphViz path configured
- [ ] Test Excel import successful

### Tier 2 (Built-in)
- [ ] SHACL tab activated
- [ ] SHACL constraints loaded
- [ ] OntoGraf tab activated
- [ ] Reasoner (HermiT) configured
- [ ] SPARQL Query tab activated
- [ ] Test SPARQL query executed

### Tier 3 (Optional)
- [ ] VOWL plugin installed (if needed)
- [ ] Explanation plugin installed (if needed)
- [ ] Git plugin installed (if version control needed)

### Configuration
- [ ] All config files present in `configs/protege/`
- [ ] HVDC ontology loads without errors
- [ ] Sample data imports successfully

### Verification
- [ ] Create test cargo instance manually
- [ ] Import test Excel file (5 rows)
- [ ] Run SHACL validation
- [ ] Execute SPARQL query
- [ ] Export class diagram
- [ ] Export network visualization

---

## Troubleshooting

### Issue 1: Protégé Won't Start

**Symptoms**: Application crashes or won't launch

**Solutions**:
1. Verify Java version: `java -version` (must be 11+)
2. Increase memory:
   - Edit `Protege.l4j.ini` (Windows)
   - Add: `-Xmx4G` (4GB RAM)
3. Check logs: `Protégé/logs/protege.log`

---

### Issue 2: Plugin Not Installing

**Symptoms**: Plugin install fails or doesn't appear after restart

**Solutions**:
1. Check internet connection
2. Manually install:
   - Download `.jar` file
   - Place in `Protégé/plugins/`
   - Restart
3. Check plugin compatibility with Protégé version

---

### Issue 3: OWLViz Not Showing Graph

**Symptoms**: OWLViz tab is blank or shows error

**Solutions**:
1. Verify GraphViz installed: `dot -V`
2. Check GraphViz path in OWLViz settings
3. Windows: Use full path with `.exe`
   - Correct: `C:\Program Files\Graphviz\bin\dot.exe`
   - Wrong: `C:\Program Files\Graphviz\bin\dot`

---

### Issue 4: Cellfie Import Fails

**Symptoms**: Excel file won't import or creates empty instances

**Solutions**:
1. Verify Excel format:
   - First row must be headers
   - No empty rows
   - Column names match mapping file
2. Check mapping file syntax
3. Ensure ontology classes exist before import

---

### Issue 5: SHACL Validation Errors

**Symptoms**: Many validation errors after import

**Common Errors**:
1. **FlowCode out of range**: Change values to 0-4
2. **Negative weight**: Check Excel for negative/zero values
3. **Missing required property**: Add missing columns to Excel

**Fix Process**:
1. Note all errors
2. Fix in Excel source file
3. Re-import
4. Re-validate

---

### Issue 6: Reasoner Takes Too Long

**Symptoms**: HermiT reasoner runs for minutes without completing

**Solutions**:
1. Start with small ontology (< 1000 instances)
2. Simplify complex class expressions
3. Use FaCT++ reasoner instead (faster for some ontologies)
4. Increase Protégé memory allocation

---

### Issue 7: SPARQL Query Returns Empty

**Symptoms**: Query executes but returns no results

**Solutions**:
1. Check namespace prefixes in query
2. Verify property names match ontology
3. Use `SELECT * WHERE { ?s ?p ?o } LIMIT 10` to test
4. Check if instances exist: `Individuals` tab

---

## Getting Help

### Resources

**Protégé Documentation**:
- Official Guide: [protege.stanford.edu/support.php](https://protege.stanford.edu/support.php)
- Tutorial: [protege.stanford.edu/tutorials](https://protege.stanford.edu/tutorials/)

**HVDC Project Documentation**:
- Main README: `logiontology/README.md`
- Full Stack Guide: `logiontology/README_FULL_STACK.md`
- Plugin System Guide: `logiontology/Protégé는 플러그인 시스템.md`

**Community Support**:
- Protégé Users List: [groups.google.com/g/protege-user](https://groups.google.com/g/protege-user)
- Stack Overflow: Tag `protege`
- GitHub Issues: HVDC project repository

---

## Next Steps

After completing installation:

1. **Import Real Data**: Use actual HVDC Excel files
2. **Customize Ontology**: Add project-specific classes/properties
3. **Create Views**: Build custom visualization dashboards
4. **Integrate with Python**: Use `rdflib` to query from code
5. **Load to Neo4j**: Export TTL and import to graph database
6. **Build FastAPI**: Create REST API endpoints for ontology queries

---

**Installation Guide Version**: 1.0
**Last Updated**: 2025-10-26
**Maintained By**: HVDC Project Team
**License**: Internal Use - Samsung C&T / ADNOC·DSV Partnership
