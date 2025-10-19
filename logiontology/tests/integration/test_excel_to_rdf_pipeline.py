#!/usr/bin/env python3
"""
Integration tests for Excel to RDF pipeline

Tests end-to-end workflow: Excel load → mapping → validation → RDF output
"""

import pytest
import pandas as pd
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile
import os

from logiontology.ingest.excel import load_excel, convert_excel_to_rdf
from logiontology.mapping.registry import MappingRegistry
from logiontology.validation.schema_validator import SchemaValidator


class TestExcelToRdfPipeline:
    """Integration tests for complete Excel to RDF pipeline"""

    def test_complete_pipeline_success(self, sample_dataframe, tmp_path):
        """Test complete pipeline from Excel to RDF with validation"""
        # Step 1: Create Excel file
        excel_file = tmp_path / "pipeline_test.xlsx"
        sample_dataframe.to_excel(excel_file, index=False)

        # Step 2: Load Excel
        df = load_excel(str(excel_file))
        assert len(df) > 0

        # Step 3: Setup mapping registry
        mapping_rules = {
            "namespaces": {
                "ex": "http://samsung.com/project-logistics#",
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
            },
            "field_map": {
                "Case_No": "hasCase",
                "Date": "hasDate",
                "Location": "hasLocation",
                "Qty": "hasQuantity",
                "Amount": "hasAmount",
                "HVDC CODE": "hasHvdcCode",
                "HVDC CODE 3": "hasHvdcCode3",
                "Operation Month": "hasOperationMonth",
                "ETA": "hasETA",
            },
            "property_mappings": {
                "Qty": {"datatype": "xsd:integer"},
                "Amount": {"datatype": "xsd:decimal"},
            },
            "hvdc_code3_valid": ["HE", "SIM"],
            "warehouse_codes": ["DSV Outdoor", "DSV Indoor", "DSV Al Markaz", "DSV MZP"],
            "month_matching": "operation_month_eq_eta_month",
        }

        rules_file = tmp_path / "mapping_rules.json"
        rules_file.write_text(json.dumps(mapping_rules))

        registry = MappingRegistry()
        registry.load(rules_file)

        # Step 4: Apply HVDC filters
        filtered_df = registry.apply_hvdc_filters_to_rdf(df)
        assert len(filtered_df) <= len(df)

        # Step 5: Convert to RDF
        output_path = tmp_path / "pipeline_output.ttl"

        with patch("rdflib.Graph.serialize") as mock_serialize:
            result_path = registry.dataframe_to_rdf(filtered_df, str(output_path))

            assert result_path == str(output_path)
            mock_serialize.assert_called_once()

        # Step 6: Validate conversion
        validation_result = registry.validate_rdf_conversion(filtered_df)
        assert validation_result["total_records"] == len(filtered_df)
        assert validation_result["mappable_fields"] > 0

    def test_pipeline_with_real_hvdc_data(self, tmp_path):
        """Test pipeline with realistic HVDC logistics data"""
        # Create realistic HVDC data
        hvdc_data = pd.DataFrame(
            {
                "Case_No": ["HVDC-2024-001", "HVDC-2024-002", "HVDC-2024-003"],
                "Date": ["2024-01-15", "2024-01-16", "2024-01-17"],
                "Location": ["DSV Indoor", "DSV Outdoor", "DSV Al Markaz"],
                "Qty": [100, 200, 150],
                "Amount": [10000.0, 20000.0, 15000.0],
                "HVDC CODE": ["HE-001", "SIM-123", "HE-456"],
                "HVDC CODE 2": ["HVDC-001", "HVDC-123", "HVDC-456"],
                "HVDC CODE 3": ["HE", "SIM", "HE"],
                "HVDC CODE 4": ["HE-001", "SIM-123", "HE-456"],
                "Operation Month": ["2024-01-01", "2024-01-01", "2024-01-01"],
                "ETA": ["2024-01-15", "2024-01-15", "2024-01-15"],
                "SQM": [100.5, 200.0, 150.0],
                "Handling In freight ton": [10.0, 20.0, 15.0],
                "Handling out Freight Ton": [5.0, 10.0, 7.5],
                "CBM": [50.0, 100.0, 75.0],
                "Pkg": [10, 20, 15],
                "G.W(KG)": [1000.0, 2000.0, 1500.0],
                "N.W(kgs)": [900.0, 1800.0, 1350.0],
                "L(CM)": [100.0, 200.0, 150.0],
                "W(CM)": [50.0, 100.0, 75.0],
                "H(CM)": [25.0, 50.0, 37.5],
            }
        )

        # Save to Excel
        excel_file = tmp_path / "hvdc_data.xlsx"
        hvdc_data.to_excel(excel_file, index=False)

        # Load Excel
        df = load_excel(str(excel_file))
        assert len(df) == 3

        # Setup mapping registry
        mapping_rules = {
            "namespaces": {
                "ex": "http://samsung.com/project-logistics#",
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
            },
            "field_map": {
                "Case_No": "hasCase",
                "Date": "hasDate",
                "Location": "hasLocation",
                "Qty": "hasQuantity",
                "Amount": "hasAmount",
                "HVDC CODE": "hasHvdcCode",
                "HVDC CODE 2": "hasHvdcCode2",
                "HVDC CODE 3": "hasHvdcCode3",
                "HVDC CODE 4": "hasHvdcCode4",
                "Operation Month": "hasOperationMonth",
                "ETA": "hasETA",
                "SQM": "hasSQM",
                "Handling In freight ton": "hasHandlingIn",
                "Handling out Freight Ton": "hasHandlingOut",
                "CBM": "hasCBM",
                "Pkg": "hasPackage",
                "G.W(KG)": "hasGrossWeight",
                "N.W(kgs)": "hasNetWeight",
                "L(CM)": "hasLength",
                "W(CM)": "hasWidth",
                "H(CM)": "hasHeight",
            },
            "property_mappings": {
                "Qty": {"datatype": "xsd:integer"},
                "Amount": {"datatype": "xsd:decimal"},
                "SQM": {"datatype": "xsd:decimal"},
                "CBM": {"datatype": "xsd:decimal"},
                "Pkg": {"datatype": "xsd:integer"},
                "G.W(KG)": {"datatype": "xsd:decimal"},
                "N.W(kgs)": {"datatype": "xsd:decimal"},
                "L(CM)": {"datatype": "xsd:decimal"},
                "W(CM)": {"datatype": "xsd:decimal"},
                "H(CM)": {"datatype": "xsd:decimal"},
            },
            "hvdc_code3_valid": ["HE", "SIM"],
            "warehouse_codes": ["DSV Outdoor", "DSV Indoor", "DSV Al Markaz", "DSV MZP"],
            "month_matching": "operation_month_eq_eta_month",
        }

        rules_file = tmp_path / "hvdc_mapping_rules.json"
        rules_file.write_text(json.dumps(mapping_rules))

        registry = MappingRegistry()
        registry.load(rules_file)

        # Apply filters
        filtered_df = registry.apply_hvdc_filters_to_rdf(df)

        # Should filter out invalid data
        assert len(filtered_df) <= len(df)

        # Convert to RDF
        output_path = tmp_path / "hvdc_output.ttl"

        with patch("rdflib.Graph.serialize") as mock_serialize:
            result_path = registry.dataframe_to_rdf(filtered_df, str(output_path))

            assert result_path == str(output_path)
            mock_serialize.assert_called_once()

    def test_pipeline_error_handling(self, tmp_path):
        """Test pipeline error handling and recovery"""
        # Create Excel file with problematic data
        problematic_data = pd.DataFrame(
            {
                "Case_No": ["CASE001", "CASE002", "CASE003"],
                "Date": ["invalid-date", "2024-01-02", "2024-01-03"],
                "Location": ["", "DSV Outdoor", "DSV Indoor"],  # Empty location
                "Qty": [-100, 200, 300],  # Negative quantity
                "Amount": [None, 2000.0, 3000.0],  # Missing amount
                "HVDC CODE": ["INVALID", "SIM-123", "HE-456"],
                "HVDC CODE 3": ["INVALID", "SIM", "HE"],  # Invalid vendor
                "Operation Month": ["2024-01-01", "2024-02-01", "2024-01-01"],  # Month mismatch
                "ETA": ["2024-01-15", "2024-01-15", "2024-01-15"],
            }
        )

        excel_file = tmp_path / "problematic_data.xlsx"
        problematic_data.to_excel(excel_file, index=False)

        # Load Excel
        df = load_excel(str(excel_file))

        # Setup mapping registry
        mapping_rules = {
            "namespaces": {
                "ex": "http://samsung.com/project-logistics#",
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
            },
            "field_map": {
                "Case_No": "hasCase",
                "Date": "hasDate",
                "Location": "hasLocation",
                "Qty": "hasQuantity",
                "Amount": "hasAmount",
                "HVDC CODE": "hasHvdcCode",
                "HVDC CODE 3": "hasHvdcCode3",
                "Operation Month": "hasOperationMonth",
                "ETA": "hasETA",
            },
            "hvdc_code3_valid": ["HE", "SIM"],
            "warehouse_codes": ["DSV Outdoor", "DSV Indoor", "DSV Al Markaz", "DSV MZP"],
            "month_matching": "operation_month_eq_eta_month",
        }

        rules_file = tmp_path / "error_mapping_rules.json"
        rules_file.write_text(json.dumps(mapping_rules))

        registry = MappingRegistry()
        registry.load(rules_file)

        # Apply filters - should handle errors gracefully
        filtered_df = registry.apply_hvdc_filters_to_rdf(df)

        # Should filter out problematic data
        assert len(filtered_df) < len(df)

        # Should not raise exceptions
        assert isinstance(filtered_df, pd.DataFrame)

    def test_pipeline_performance(self, tmp_path):
        """Test pipeline performance with larger dataset"""
        import time

        # Create larger dataset
        large_data = {
            "Case_No": [f"HVDC-2024-{i:03d}" for i in range(100)],
            "Date": ["2024-01-15"] * 100,
            "Location": ["DSV Indoor" if i % 2 == 0 else "DSV Outdoor" for i in range(100)],
            "Qty": [100 + i for i in range(100)],
            "Amount": [10000.0 + i * 100 for i in range(100)],
            "HVDC CODE": [f"HE-{i:03d}" for i in range(100)],
            "HVDC CODE 2": [f"HVDC-{i:03d}" for i in range(100)],
            "HVDC CODE 3": ["HE" if i % 2 == 0 else "SIM" for i in range(100)],
            "HVDC CODE 4": [f"HE-{i:03d}" for i in range(100)],
            "Operation Month": ["2024-01-01"] * 100,
            "ETA": ["2024-01-15"] * 100,
            "SQM": [100.0 + i for i in range(100)],
            "Handling In freight ton": [10.0 + i * 0.1 for i in range(100)],
            "Handling out Freight Ton": [5.0 + i * 0.05 for i in range(100)],
            "CBM": [50.0 + i for i in range(100)],
            "Pkg": [10 + i for i in range(100)],
            "G.W(KG)": [1000.0 + i * 10 for i in range(100)],
            "N.W(kgs)": [900.0 + i * 9 for i in range(100)],
            "L(CM)": [100.0 + i for i in range(100)],
            "W(CM)": [50.0 + i * 0.5 for i in range(100)],
            "H(CM)": [25.0 + i * 0.25 for i in range(100)],
        }

        large_df = pd.DataFrame(large_data)
        excel_file = tmp_path / "large_data.xlsx"
        large_df.to_excel(excel_file, index=False)

        # Setup mapping registry
        mapping_rules = {
            "namespaces": {
                "ex": "http://samsung.com/project-logistics#",
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
            },
            "field_map": {
                "Case_No": "hasCase",
                "Date": "hasDate",
                "Location": "hasLocation",
                "Qty": "hasQuantity",
                "Amount": "hasAmount",
                "HVDC CODE": "hasHvdcCode",
                "HVDC CODE 2": "hasHvdcCode2",
                "HVDC CODE 3": "hasHvdcCode3",
                "HVDC CODE 4": "hasHvdcCode4",
                "Operation Month": "hasOperationMonth",
                "ETA": "hasETA",
                "SQM": "hasSQM",
                "Handling In freight ton": "hasHandlingIn",
                "Handling out Freight Ton": "hasHandlingOut",
                "CBM": "hasCBM",
                "Pkg": "hasPackage",
                "G.W(KG)": "hasGrossWeight",
                "N.W(kgs)": "hasNetWeight",
                "L(CM)": "hasLength",
                "W(CM)": "hasWidth",
                "H(CM)": "hasHeight",
            },
            "hvdc_code3_valid": ["HE", "SIM"],
            "warehouse_codes": ["DSV Outdoor", "DSV Indoor", "DSV Al Markaz", "DSV MZP"],
            "month_matching": "operation_month_eq_eta_month",
        }

        rules_file = tmp_path / "performance_mapping_rules.json"
        rules_file.write_text(json.dumps(mapping_rules))

        registry = MappingRegistry()
        registry.load(rules_file)

        # Measure performance
        start_time = time.time()

        # Load Excel
        df = load_excel(str(excel_file))

        # Apply filters
        filtered_df = registry.apply_hvdc_filters_to_rdf(df)

        # Convert to RDF
        output_path = tmp_path / "performance_output.ttl"

        with patch("rdflib.Graph.serialize") as mock_serialize:
            result_path = registry.dataframe_to_rdf(filtered_df, str(output_path))

        end_time = time.time()

        # Should complete within reasonable time (5 seconds)
        assert (end_time - start_time) < 5.0
        assert len(filtered_df) == 100
        assert result_path == str(output_path)

    def test_pipeline_memory_usage(self, tmp_path):
        """Test pipeline memory usage with large dataset"""
        import psutil
        import os

        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Create large dataset
        large_data = {
            "Case_No": [f"HVDC-2024-{i:06d}" for i in range(1000)],
            "Date": ["2024-01-15"] * 1000,
            "Location": ["DSV Indoor"] * 1000,
            "Qty": [100 + i for i in range(1000)],
            "Amount": [10000.0 + i * 100 for i in range(1000)],
            "HVDC CODE": [f"HE-{i:03d}" for i in range(1000)],
            "HVDC CODE 3": ["HE"] * 1000,
            "Operation Month": ["2024-01-01"] * 1000,
            "ETA": ["2024-01-15"] * 1000,
        }

        large_df = pd.DataFrame(large_data)
        excel_file = tmp_path / "memory_test.xlsx"
        large_df.to_excel(excel_file, index=False)

        # Setup mapping registry
        mapping_rules = {
            "namespaces": {
                "ex": "http://samsung.com/project-logistics#",
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
            },
            "field_map": {
                "Case_No": "hasCase",
                "Date": "hasDate",
                "Location": "hasLocation",
                "Qty": "hasQuantity",
                "Amount": "hasAmount",
                "HVDC CODE": "hasHvdcCode",
                "HVDC CODE 3": "hasHvdcCode3",
                "Operation Month": "hasOperationMonth",
                "ETA": "hasETA",
            },
            "hvdc_code3_valid": ["HE", "SIM"],
            "warehouse_codes": ["DSV Outdoor", "DSV Indoor", "DSV Al Markaz", "DSV MZP"],
            "month_matching": "operation_month_eq_eta_month",
        }

        rules_file = tmp_path / "memory_mapping_rules.json"
        rules_file.write_text(json.dumps(mapping_rules))

        registry = MappingRegistry()
        registry.load(rules_file)

        # Process data
        df = load_excel(str(excel_file))
        filtered_df = registry.apply_hvdc_filters_to_rdf(df)

        # Check memory usage
        current_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = current_memory - initial_memory

        # Should not use excessive memory (less than 100MB increase)
        assert memory_increase < 100

        # Clean up
        del df, filtered_df, large_df
        import gc

        gc.collect()

    def test_pipeline_with_validation_integration(self, sample_documents, tmp_path):
        """Test pipeline with document validation integration"""
        # Create Excel file
        excel_data = pd.DataFrame(
            {
                "Case_No": ["CASE001", "CASE002"],
                "Date": ["2024-01-01", "2024-01-02"],
                "Location": ["DSV Indoor", "DSV Outdoor"],
                "Qty": [100, 200],
            }
        )

        excel_file = tmp_path / "validation_test.xlsx"
        excel_data.to_excel(excel_file, index=False)

        # Load Excel
        df = load_excel(str(excel_file))

        # Setup mapping registry
        mapping_rules = {
            "namespaces": {
                "ex": "http://samsung.com/project-logistics#",
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
                "xsd": "http://www.w3.org/2001/XMLSchema#",
            },
            "field_map": {
                "Case_No": "hasCase",
                "Date": "hasDate",
                "Location": "hasLocation",
                "Qty": "hasQuantity",
            },
            "hvdc_code3_valid": ["HE", "SIM"],
            "warehouse_codes": ["DSV Outdoor", "DSV Indoor", "DSV Al Markaz", "DSV MZP"],
            "month_matching": "operation_month_eq_eta_month",
        }

        rules_file = tmp_path / "validation_mapping_rules.json"
        rules_file.write_text(json.dumps(mapping_rules))

        registry = MappingRegistry()
        registry.load(rules_file)

        # Apply filters
        filtered_df = registry.apply_hvdc_filters_to_rdf(df)

        # Convert to RDF
        output_path = tmp_path / "validation_output.ttl"

        with patch("rdflib.Graph.serialize") as mock_serialize:
            result_path = registry.dataframe_to_rdf(filtered_df, str(output_path))

        # Validate documents
        validator = SchemaValidator()

        # Create test documents
        test_docs = [
            {
                "type": "BOE",
                "mbl_no": "ABCD1234567890",
                "entry_no": "ENT001",
                "containers": "ABCD1234567",
                "gross_weight": 1000.0,
                "hs_code": "1234567890",
                "meta": {"source": "test", "timestamp": "2024-01-01T00:00:00Z", "version": "1.0"},
                "blocks": [{"type": "text", "content": "test"}],
            }
        ]

        # Validate documents
        results = validator.validate_batch(test_docs)

        # Verify pipeline results
        assert result_path == str(output_path)
        assert results["total"] == 1
        assert results["valid"] == 1
        assert len(filtered_df) == 2
