#!/usr/bin/env python3
"""
Test cases for MappingRegistry v2.6 system
"""

import pytest
import pandas as pd
from pathlib import Path
import tempfile
import yaml

from src.mapping.registry import MappingRegistry


class TestMappingRegistryV26:
    """Test cases for MappingRegistry v2.6 system"""

    def test_init_default_values(self):
        """Test MappingRegistry initialization with default values"""
        registry = MappingRegistry()

        assert registry.rules == {}
        assert registry.ns_map == {}
        assert registry.header_map == {}
        assert registry.business_rules == {}
        assert registry.identity_rules == {}
        assert registry.property_mappings == {}
        assert registry.class_mappings == {}

    def test_load_rules_yaml(self, tmp_path):
        """Test loading mapping rules from YAML file"""
        yaml_content = """
namespaces:
  hvdc: "https://hvdc.example.org/ns#"
  ops: "https://hvdc.example.org/ops#"
  org: "https://schema.org/"

header_map_kr2en:
  "Case_No": "Case No."
  "HVDC_Code": "HVDC_Code"

business_rules:
  vendor_whitelist: ["HE", "SIM"]
  pressure_max: 4.0
  warehouse_codes: ["MZP", "MOSB"]

property_mappings:
  "HVDC_Code":
    property: "hasHVDCCode"
    datatype: "xsd:string"
"""

        yaml_file = tmp_path / "test_rules.yaml"
        yaml_file.write_text(yaml_content)

        registry = MappingRegistry.load_rules(yaml_file)

        assert "hvdc" in registry.ns_map
        assert "ops" in registry.ns_map
        assert "org" in registry.ns_map
        assert registry.header_map["Case_No"] == "Case No."
        assert registry.business_rules["vendor_whitelist"] == ["HE", "SIM"]
        assert registry.business_rules["pressure_max"] == 4.0

    def test_normalize_columns(self):
        """Test column normalization"""
        registry = MappingRegistry()
        registry.header_map = {"케이스 번호": "Case No.", "HVDC 코드": "HVDC_Code"}

        df = pd.DataFrame({
            "케이스 번호": ["CASE001", "CASE002"],
            "HVDC 코드": ["HE-001", "SIM-002"],
            "기타": ["value1", "value2"]
        })

        result = registry.normalize_columns(df)

        assert "Case No." in result.columns
        assert "HVDC_Code" in result.columns
        assert "기타" in result.columns  # Unmapped columns remain

    def test_normalize_values(self):
        """Test value normalization"""
        registry = MappingRegistry()

        df = pd.DataFrame({
            "BL No.": ["BL-123-456", "BL 789 012"],
            "Container": ["ABCD1234567", "EFGH-8901234"],
            "ETA": ["2024-01-15", "2024-02-20"],
            "Operation Month": ["2024-01-01", "2024-02-01"]
        })

        result = registry.normalize_values(df)

        assert "ETA_iso" in result.columns
        assert result["BL No."].iloc[0] == "BL123456"
        assert result["Container"].iloc[0] == "ABCD1234567"
        assert result["Operation Month"].iloc[0] == "2024-01"

    def test_apply_business_filters(self):
        """Test business rule filtering"""
        registry = MappingRegistry()
        registry.business_rules = {
            "vendor_whitelist": ["HE", "SIM"],
            "pressure_max": 4.0,
            "warehouse_codes": ["MZP", "MOSB"]
        }

        df = pd.DataFrame({
            "Vendor": ["HE", "SIM", "INVALID"],
            "Pressure (t/m2)": [3.5, 3.8, 2.0],
            "Warehouse Code": ["MZP", "MOSB", "INVALID"],
            "ETA": ["2024-01-15", "2024-01-20", "2024-01-25"],
            "Operation Month": ["2024-01", "2024-01", "2024-01"]
        })

        result = registry.apply_business_filters(df)

        # Only HE and SIM should remain (vendor filter)
        assert len(result) == 2
        assert all(vendor in ["HE", "SIM"] for vendor in result["Vendor"])

    def test_dataframe_to_rdf_basic(self, tmp_path):
        """Test basic DataFrame to RDF conversion"""
        registry = MappingRegistry()
        registry.ns_map = {
            "hvdc": "https://hvdc.example.org/ns#",
            "hvdci": "https://hvdc.example.org/id/"
        }

        df = pd.DataFrame({
            "HVDC_Code": ["HE-001", "SIM-002"],
            "Case No.": ["CASE001", "CASE002"],
            "Vendor": ["HE", "SIM"],
            "BL No.": ["BL001", "BL002"],
            "ETA": ["2024-01-15", "2024-01-20"],
            "Pressure (t/m2)": [3.5, 4.0]
        })

        # Add ETA_iso for RDF generation
        df["ETA_iso"] = df["ETA"].apply(lambda x: f"{x}T00:00:00+04:00")

        output_path = tmp_path / "test_output.ttl"
        result_path = registry.dataframe_to_rdf(df, output_path)

        assert Path(result_path).exists()
        
        content = output_path.read_text()
        assert "Shipment" in content
        assert "LogisticsItem" in content
        assert "Organization" in content
        assert "ArrivalEvent" in content
        assert "TransportConstraint" in content

    def test_run_pipeline(self, tmp_path):
        """Test complete pipeline execution"""
        yaml_content = """
namespaces:
  hvdc: "https://hvdc.example.org/ns#"
  hvdci: "https://hvdc.example.org/id/"

header_map_kr2en:
  "Case_No": "Case No."
  "HVDC_Code": "HVDC_Code"

business_rules:
  vendor_whitelist: ["HE", "SIM"]
  pressure_max: 4.0
"""

        yaml_file = tmp_path / "test_rules.yaml"
        yaml_file.write_text(yaml_content)

        df = pd.DataFrame({
            "Case_No": ["CASE001", "CASE002"],
            "HVDC_Code": ["HE-001", "SIM-002"],
            "Vendor": ["HE", "SIM"],
            "BL No.": ["BL001", "BL002"],
            "ETA": ["2024-01-15", "2024-01-20"],
            "Pressure (t/m2)": [3.5, 4.0],
            "Operation Month": ["2024-01-01", "2024-01-01"]
        })

        registry = MappingRegistry.load_rules(yaml_file)
        output_path = tmp_path / "pipeline_output.ttl"
        result_path = registry.run(df, output_path)

        assert Path(result_path).exists()
        
        content = output_path.read_text()
        assert "Shipment" in content
        assert "HE-001" in content
        assert "SIM-002" in content

    def test_legacy_compatibility(self):
        """Test legacy method compatibility"""
        registry = MappingRegistry()
        
        # Test legacy load method
        assert hasattr(registry, 'load')
        
        # Test legacy apply_hvdc_filters_to_rdf method
        assert hasattr(registry, 'apply_hvdc_filters_to_rdf')
        
        # Test legacy validate_rdf_conversion method
        assert hasattr(registry, 'validate_rdf_conversion')

    def test_validate_rdf_conversion(self):
        """Test RDF conversion validation"""
        registry = MappingRegistry()
        registry.header_map = {"Case_No": "hasCaseNo", "Date": "hasDate"}

        df = pd.DataFrame({
            "Case_No": ["CASE001", "CASE002"],
            "Date": ["2024-01-01", "2024-01-02"],
            "Unmapped": ["value1", "value2"]
        })

        result = registry.validate_rdf_conversion(df)

        assert result["total_records"] == 2
        assert result["mappable_fields"] == 2
        assert "Unmapped" in result["unmappable_fields"]
        assert result["missing_mappings"] == []
