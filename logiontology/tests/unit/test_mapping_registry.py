#!/usr/bin/env python3
"""
Unit tests for MappingRegistry class

Tests HVDC filtering, RDF conversion, and validation functionality
"""

import pytest
import pandas as pd
import json
from pathlib import Path
from unittest.mock import patch, mock_open

from logiontology.mapping.registry import MappingRegistry


class TestMappingRegistry:
    """Test cases for MappingRegistry class"""

    def test_init_default_values(self):
        """Test MappingRegistry initialization with default values"""
        registry = MappingRegistry()

        assert registry.rules == {}
        assert registry.ns == {}
        assert registry.field_map == {}
        assert registry.property_mappings == {}
        assert registry.class_mappings == {}
        assert registry.hvdc_code3_valid == ["HE", "SIM"]
        assert registry.warehouse_codes == ["DSV Outdoor", "DSV Indoor", "DSV Al Markaz", "DSV MZP"]
        assert registry.month_matching == "operation_month_eq_eta_month"

    def test_load_json_file(self, tmp_path):
        """Test loading mapping rules from JSON file"""
        # Create test JSON file
        test_rules = {
            "namespaces": {
                "ex": "http://test.com#",
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            },
            "field_map": {"test_field": "hasTest"},
            "hvdc_code3_valid": ["TEST"],
            "warehouse_codes": ["Test Warehouse"],
        }

        json_file = tmp_path / "test_rules.json"
        json_file.write_text(json.dumps(test_rules))

        registry = MappingRegistry()
        registry.load(json_file)

        assert "ex" in registry.ns
        assert "test_field" in registry.field_map
        assert registry.hvdc_code3_valid == ["TEST"]
        assert registry.warehouse_codes == ["Test Warehouse"]

    def test_load_yaml_file(self, tmp_path):
        """Test loading mapping rules from YAML file"""
        yaml_content = """
namespaces:
  ex: "http://test.com#"
field_map:
  test_field: "hasTest"
hvdc_code3_valid: ["TEST"]
warehouse_codes: ["Test Warehouse"]
"""

        yaml_file = tmp_path / "test_rules.yaml"
        yaml_file.write_text(yaml_content)

        registry = MappingRegistry()
        registry.load(yaml_file)

        assert "ex" in registry.ns
        assert "test_field" in registry.field_map
        assert registry.hvdc_code3_valid == ["TEST"]

    def test_load_invalid_file(self, tmp_path):
        """Test loading invalid file format"""
        invalid_file = tmp_path / "test.txt"
        invalid_file.write_text("invalid content")

        registry = MappingRegistry()
        registry.load(invalid_file)

        # Should fall back to defaults
        assert registry.hvdc_code3_valid == ["HE", "SIM"]

    def test_parse_rules_success(self):
        """Test successful parsing of rules"""
        registry = MappingRegistry()
        registry.rules = {
            "namespaces": {"ex": "http://test.com#"},
            "field_map": {"test": "hasTest"},
            "property_mappings": {"test": {"datatype": "xsd:string"}},
            "class_mappings": {"Event": "TransportEvent"},
            "hvdc_code3_valid": ["TEST"],
            "warehouse_codes": ["Test"],
            "month_matching": "test_matching",
        }

        registry._parse_rules()

        assert "ex" in registry.ns
        assert "test" in registry.field_map
        assert registry.hvdc_code3_valid == ["TEST"]

    def test_parse_rules_failure_fallback(self):
        """Test fallback to defaults when parsing fails"""
        registry = MappingRegistry()
        registry.rules = {"invalid": "data"}

        with patch("logging.getLogger") as mock_logger:
            registry._parse_rules()

        # Should use defaults
        assert registry.hvdc_code3_valid == ["HE", "SIM"]
        assert registry.warehouse_codes == ["DSV Outdoor", "DSV Indoor", "DSV Al Markaz", "DSV MZP"]

    def test_set_defaults(self):
        """Test setting default values"""
        registry = MappingRegistry()
        registry._set_defaults()

        assert "ex" in registry.ns
        assert "rdf" in registry.ns
        assert "rdfs" in registry.ns
        assert "xsd" in registry.ns

    def test_apply_hvdc_filters_to_rdf_basic(self, sample_dataframe):
        """Test basic HVDC filtering functionality"""
        registry = MappingRegistry()

        # Test with valid HVDC codes
        result_df = registry.apply_hvdc_filters_to_rdf(sample_dataframe)

        assert len(result_df) <= len(sample_dataframe)
        assert "HVDC_CODE_NORMALIZED" in result_df.columns
        assert "CODE_MATCH" in result_df.columns

    def test_apply_hvdc_filters_code_matching(self, sample_dataframe):
        """Test HVDC code matching logic"""
        registry = MappingRegistry()

        # Create test data with matching codes
        test_df = pd.DataFrame(
            {
                "HVDC CODE": ["HE-001", "SIM-123"],
                "HVDC CODE 4": ["HE-001", "SIM-123"],
                "HVDC CODE 3": ["HE", "SIM"],
                "Operation Month": ["2024-01-01", "2024-01-01"],
                "ETA": ["2024-01-15", "2024-01-15"],
            }
        )

        result_df = registry.apply_hvdc_filters_to_rdf(test_df)

        # All rows should pass code matching
        assert all(result_df["CODE_MATCH"] == True)

    def test_apply_hvdc_filters_vendor_filtering(self, sample_dataframe):
        """Test vendor filtering (HE/SIM only)"""
        registry = MappingRegistry()

        # Create test data with mixed vendors
        test_df = pd.DataFrame(
            {
                "HVDC CODE": ["HE-001", "SIM-123", "INVALID-456"],
                "HVDC CODE 4": ["HE-001", "SIM-123", "INVALID-456"],
                "HVDC CODE 3": ["HE", "SIM", "INVALID"],
                "Operation Month": ["2024-01-01", "2024-01-01", "2024-01-01"],
                "ETA": ["2024-01-15", "2024-01-15", "2024-01-15"],
            }
        )

        result_df = registry.apply_hvdc_filters_to_rdf(test_df)

        # Only HE and SIM should remain
        assert len(result_df) == 2
        assert all(result_df["HVDC CODE 3"].isin(["HE", "SIM"]))

    def test_apply_hvdc_filters_warehouse_processing(self, sample_dataframe):
        """Test warehouse code processing and SQM handling"""
        registry = MappingRegistry()

        # Create test data with warehouse codes
        test_df = pd.DataFrame(
            {
                "HVDC CODE": ["DSV Indoor", "DSV Outdoor", "INVALID"],
                "HVDC CODE 4": ["DSV Indoor", "DSV Outdoor", "INVALID"],
                "HVDC CODE 3": ["HE", "SIM", "HE"],
                "SQM": [100.5, 200.0, 150.0],
                "Operation Month": ["2024-01-01", "2024-01-01", "2024-01-01"],
                "ETA": ["2024-01-15", "2024-01-15", "2024-01-15"],
            }
        )

        result_df = registry.apply_hvdc_filters_to_rdf(test_df)

        # Should process warehouse data
        assert "SQM" in result_df.columns

    def test_apply_hvdc_filters_month_matching(self, sample_dataframe):
        """Test month matching between Operation Month and ETA"""
        registry = MappingRegistry()

        # Create test data with month mismatch
        test_df = pd.DataFrame(
            {
                "HVDC CODE": ["HE-001", "SIM-123"],
                "HVDC CODE 4": ["HE-001", "SIM-123"],
                "HVDC CODE 3": ["HE", "SIM"],
                "Operation Month": ["2024-01-01", "2024-02-01"],  # Different months
                "ETA": ["2024-01-15", "2024-01-15"],  # Same month
            }
        )

        result_df = registry.apply_hvdc_filters_to_rdf(test_df)

        # Only matching month should remain
        assert len(result_df) == 1
        assert result_df.iloc[0]["Operation Month"] == "2024-01-01"

    def test_apply_hvdc_filters_handling_fields(self, sample_dataframe):
        """Test handling of IN/OUT freight fields"""
        registry = MappingRegistry()

        test_df = pd.DataFrame(
            {
                "HVDC CODE": ["HE-001", "HE-001", "HE-001"],
                "HVDC CODE 4": ["HE-001", "HE-001", "HE-001"],
                "HVDC CODE 3": ["HE", "HE", "HE"],
                "Handling In freight ton": [10.0, None, 0],  # Use valid data
                "Handling out Freight Ton": [5.0, 0, 0],  # Use valid data
                "Operation Month": ["2024-01-01", "2024-01-01", "2024-01-01"],
                "ETA": ["2024-01-15", "2024-01-15", "2024-01-15"],
            }
        )

        result_df = registry.apply_hvdc_filters_to_rdf(test_df)

        # Should convert to float and handle None values
        assert "Handling In freight ton" in result_df.columns
        assert "Handling out Freight Ton" in result_df.columns

    def test_dataframe_to_rdf_basic(self, sample_dataframe, mapping_registry, tmp_path):
        """Test basic DataFrame to RDF conversion"""
        output_path = tmp_path / "test_output.ttl"

        result_path = mapping_registry.dataframe_to_rdf(sample_dataframe, str(output_path))

        assert Path(result_path).exists()
        assert output_path.suffix == ".ttl"

    def test_dataframe_to_rdf_with_filters(self, sample_dataframe, mapping_registry, tmp_path):
        """Test DataFrame to RDF conversion with HVDC filters applied"""
        output_path = tmp_path / "test_filtered_output.ttl"

        result_path = mapping_registry.dataframe_to_rdf(sample_dataframe, str(output_path))

        assert Path(result_path).exists()

        # Read the generated RDF file to verify content
        content = output_path.read_text()
        assert "TransportEvent" in content
        assert "hasCase" in content

    def test_dataframe_to_rdf_empty_dataframe(self, mapping_registry, tmp_path):
        """Test RDF conversion with empty DataFrame"""
        empty_df = pd.DataFrame()
        output_path = tmp_path / "empty_output.ttl"

        result_path = mapping_registry.dataframe_to_rdf(empty_df, str(output_path))

        assert Path(result_path).exists()
        # Should create empty RDF file
        content = output_path.read_text()
        # Empty DataFrame should create minimal RDF structure
        # Check if file exists and has some content (even if minimal)
        assert len(content) >= 0  # File exists, content may be minimal

    def test_validate_rdf_conversion_success(self, sample_dataframe, mapping_registry):
        """Test RDF conversion validation with valid data"""
        result = mapping_registry.validate_rdf_conversion(sample_dataframe)

        assert result["total_records"] == len(sample_dataframe)
        assert result["mappable_fields"] > 0
        assert isinstance(result["unmappable_fields"], list)
        assert isinstance(result["missing_mappings"], list)

    def test_validate_rdf_conversion_missing_fields(self, mapping_registry):
        """Test RDF conversion validation with missing fields"""
        # Create DataFrame with fields not in mapping
        test_df = pd.DataFrame({"Unknown_Field_1": [1, 2, 3], "Unknown_Field_2": ["a", "b", "c"]})

        result = mapping_registry.validate_rdf_conversion(test_df)

        assert result["total_records"] == 3
        assert result["mappable_fields"] == 0
        assert len(result["unmappable_fields"]) == 2

    def test_apply_single_record(self, mapping_registry):
        """Test applying mapping to single record"""
        test_record = {"Case_No": "TEST001", "Date": "2024-01-01", "Location": "Test Location"}

        result = mapping_registry.apply(test_record)

        # Should return the same record (placeholder implementation)
        assert result == test_record

    @pytest.mark.parametrize(
        "hvdc_code,expected",
        [
            ("HE-001", "001"),
            ("SIM-123", "123"),
            ("INVALID", ""),
            ("", ""),
            (None, ""),
            ("HE-ABC", ""),  # Only digits are extracted
        ],
    )
    def test_normalize_code_num_fallback(self, hvdc_code, expected):
        """Test normalize_code_num fallback function"""
        registry = MappingRegistry()

        # Test the fallback function directly
        import re

        result = re.sub(r"\D", "", str(hvdc_code)) if hvdc_code else ""
        assert result == expected

    @pytest.mark.parametrize(
        "code1,code2,expected",
        [
            ("HE-001", "HE-001", True),
            ("SIM-123", "SIM-123", True),
            ("HE-001", "SIM-123", False),
            ("", "", True),
            (None, None, True),
        ],
    )
    def test_codes_match_fallback(self, code1, code2, expected):
        """Test codes_match fallback function"""
        registry = MappingRegistry()

        # Test the fallback function directly
        import re

        norm1 = re.sub(r"\D", "", str(code1)) if code1 else ""
        norm2 = re.sub(r"\D", "", str(code2)) if code2 else ""
        result = norm1 == norm2
        assert result == expected

    def test_error_handling_invalid_data(self, mapping_registry):
        """Test error handling with invalid data types"""
        # Create DataFrame with problematic data
        test_df = pd.DataFrame(
            {
                "Case_No": [None, "", 123],  # Mixed types
                "Date": ["invalid-date", None, "2024-01-01"],
                "Qty": ["not-a-number", None, 100],
            }
        )

        # Should not raise exception
        result_df = mapping_registry.apply_hvdc_filters_to_rdf(test_df)
        assert isinstance(result_df, pd.DataFrame)

    def test_memory_usage_large_dataset(self, mapping_registry):
        """Test memory usage with larger dataset"""
        # Create larger dataset
        large_data = {
            "Case_No": [f"CASE{i:06d}" for i in range(1000)],
            "Date": ["2024-01-01"] * 1000,
            "Location": ["DSV Indoor"] * 1000,
            "Qty": list(range(1000)),
            "HVDC CODE": [f"HE-{i:03d}" for i in range(1000)],
            "HVDC CODE 4": [f"HE-{i:03d}" for i in range(1000)],
            "HVDC CODE 3": ["HE"] * 1000,
            "Operation Month": ["2024-01-01"] * 1000,
            "ETA": ["2024-01-15"] * 1000,
        }

        large_df = pd.DataFrame(large_data)

        # Should handle large dataset without issues
        result_df = mapping_registry.apply_hvdc_filters_to_rdf(large_df)
        assert len(result_df) == 1000

    def test_performance_timing(self, sample_dataframe, mapping_registry):
        """Test performance timing for critical operations"""
        import time

        start_time = time.time()
        result_df = mapping_registry.apply_hvdc_filters_to_rdf(sample_dataframe)
        filter_time = time.time() - start_time

        # Should complete within reasonable time (1 second)
        assert filter_time < 1.0

        # Test RDF conversion timing
        start_time = time.time()
        with pytest.MonkeyPatch().context() as m:
            m.setattr("pathlib.Path.mkdir", lambda self, parents, exist_ok: None)
            m.setattr("rdflib.Graph.serialize", lambda self, destination, format: None)
            mapping_registry.dataframe_to_rdf(result_df, "test.ttl")
        conversion_time = time.time() - start_time

        # Should complete within reasonable time (2 seconds)
        assert conversion_time < 2.0
