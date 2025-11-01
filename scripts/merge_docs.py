#!/usr/bin/env python3
"""Merge 9 documentation files into a single master document."""

import os
from pathlib import Path

# Define the files in order
FILES = [
    'README_ontology_data_hub.md',
    'README_consolidated.md',
    'MASTER_INDEX.md',
    'ONTOLOGY_COVERAGE_MATRIX.md',
    'FLOW_CODE_LINEAGE.md',
    'DATA_FILES_GUIDE.md',
    'QUERY_TEMPLATES.md',
    'USAGE_GUIDE.md',
    'VALIDATION_REPORT.md',
]

# Part headers
PARTS = [
    '# Part 1: Overview and Introduction\n\n',
    '# Part 2: Master Index and Coverage\n\n',
    '# Part 3: Flow Code System\n\n',
    '# Part 4: Data Files Guide\n\n',
    '# Part 5: Query Templates and Usage\n\n',
    '# Part 6: Validation and Quality Assurance\n\n',
]

# Header template
HEADER = """# HVDC Logistics Ontology - Core Documentation Master

**Version**: 1.0
**Created**: 2025-11-01
**Purpose**: Complete unified reference for HVDC Ontology (5 CONSOLIDATED docs + 9 supporting docs)

This document consolidates the following source files:
- README_ontology_data_hub.md
- README_consolidated.md
- MASTER_INDEX.md
- ONTOLOGY_COVERAGE_MATRIX.md
- FLOW_CODE_LINEAGE.md
- DATA_FILES_GUIDE.md
- QUERY_TEMPLATES.md
- USAGE_GUIDE.md
- VALIDATION_REPORT.md

---

## Table of Contents

1. [Part 1: Overview and Introduction](#part-1-overview-and-introduction)
2. [Part 2: Master Index and Coverage](#part-2-master-index-and-coverage)
3. [Part 3: Flow Code System](#part-3-flow-code-system)
4. [Part 4: Data Files Guide](#part-4-data-files-guide)
5. [Part 5: Query Templates and Usage](#part-5-query-templates-and-usage)
6. [Part 6: Validation and Quality Assurance](#part-6-validation-and-quality-assurance)

---

"""


def main():
    # Change to the correct directory
    base_dir = Path(__file__).parent.parent / 'Logi ontol core doc'

    # Build the combined content
    combined = HEADER

    # Process each file
    for i, filename in enumerate(FILES):
        filepath = base_dir / filename

        if not filepath.exists():
            print(f"Warning: {filename} not found, skipping")
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Add part header
        if i < len(PARTS):
            combined += PARTS[i]

        # Add content
        combined += content

        # Add separator
        combined += '\n\n---\n\n'

    # Write the output
    output_file = base_dir / 'CORE_DOCUMENTATION_MASTER.md'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(combined)

    # Print stats
    line_count = combined.count('\n')
    size_kb = len(combined) / 1024
    print(f"Successfully created CORE_DOCUMENTATION_MASTER.md")
    print(f"Lines: {line_count}")
    print(f"Size: {size_kb:.1f} KB")


if __name__ == '__main__':
    main()

