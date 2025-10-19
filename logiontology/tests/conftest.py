#!/usr/bin/env python3
"""
Pytest configuration and shared fixtures for logiontology tests
"""

import pytest
import pandas as pd
import json
from pathlib import Path
from datetime import datetime, date
from typing import Dict, Any

from logiontology.mapping.registry import MappingRegistry
from logiontology.validation.schema_validator import SchemaValidator


@pytest.fixture
def sample_dataframe():
    """Sample DataFrame for testing HVDC data processing"""
    return pd.DataFrame(
        {
            "Case_No": ["CASE001", "CASE002", "CASE003"],
            "Date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "Location": ["DSV Indoor", "DSV Outdoor", "DSV Al Markaz"],
            "Qty": [100, 200, 150],
            "Amount": [1000.0, 2000.0, 1500.0],
            "Handling Fee": [50.0, 100.0, 75.0],
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


@pytest.fixture
def sample_mapping_rules():
    """Sample mapping rules for testing"""
    return {
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
            "Handling Fee": "hasHandlingFee",
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
            "Handling Fee": {"datatype": "xsd:decimal"},
            "SQM": {"datatype": "xsd:decimal"},
            "CBM": {"datatype": "xsd:decimal"},
            "Pkg": {"datatype": "xsd:integer"},
            "G.W(KG)": {"datatype": "xsd:decimal"},
            "N.W(kgs)": {"datatype": "xsd:decimal"},
            "L(CM)": {"datatype": "xsd:decimal"},
            "W(CM)": {"datatype": "xsd:decimal"},
            "H(CM)": {"datatype": "xsd:decimal"},
        },
        "class_mappings": {"TransportEvent": "TransportEvent", "Dataset": "Dataset"},
        "hvdc_code3_valid": ["HE", "SIM"],
        "warehouse_codes": ["DSV Outdoor", "DSV Indoor", "DSV Al Markaz", "DSV MZP"],
        "month_matching": "operation_month_eq_eta_month",
    }


@pytest.fixture
def mapping_registry(sample_mapping_rules, tmp_path):
    """MappingRegistry instance with test rules"""
    # Save rules to temporary file
    rules_file = tmp_path / "test_mapping_rules.json"
    rules_file.write_text(json.dumps(sample_mapping_rules, indent=2))

    registry = MappingRegistry()
    registry.load(rules_file)
    return registry


@pytest.fixture
def schema_validator():
    """SchemaValidator instance for testing"""
    return SchemaValidator(min_confidence=0.90)


@pytest.fixture
def sample_documents():
    """Sample documents for validation testing"""
    return [
        {
            "type": "BOE",
            "mbl_no": "ABCD1234567890",
            "entry_no": "ENT001",
            "containers": "ABCD1234567",
            "gross_weight": 1000.0,
            "hs_code": "1234567890",
            "meta": {"source": "test", "timestamp": "2024-01-01T00:00:00Z", "version": "1.0"},
            "blocks": [{"type": "text", "content": "Sample BOE content"}],
        },
        {
            "type": "DO",
            "do_number": "DO1234567890",
            "do_validity_date": "2024-12-31",
            "container_no": "ABCD1234567",
            "meta": {"source": "test", "timestamp": "2024-01-01T00:00:00Z", "version": "1.0"},
            "blocks": [{"type": "text", "content": "Sample DO content"}],
        },
        {
            "type": "DN",
            "origin": "Dubai",
            "destination": "Abu Dhabi",
            "delivery_date": "2024-01-15",
            "meta": {"source": "test", "timestamp": "2024-01-01T00:00:00Z", "version": "1.0"},
            "blocks": [{"type": "text", "content": "Sample DN content"}],
        },
        {
            "type": "CarrierInvoice",
            "invoice_number": "INV-2024-001",
            "total_amount": 5000.0,
            "currency": "USD",
            "meta": {"source": "test", "timestamp": "2024-01-01T00:00:00Z", "version": "1.0"},
            "blocks": [{"type": "text", "content": "Sample Carrier Invoice content"}],
        },
        {
            "type": "WarehouseInvoice",
            "warehouse_name": "DSV Indoor",
            "rental_period": "2024-01-01 to 2024-01-31",
            "sqm": 100.5,
            "meta": {"source": "test", "timestamp": "2024-01-01T00:00:00Z", "version": "1.0"},
            "blocks": [{"type": "text", "content": "Sample Warehouse Invoice content"}],
        },
    ]


@pytest.fixture
def sample_excel_file(tmp_path, sample_dataframe):
    """Sample Excel file for testing"""
    excel_file = tmp_path / "test_data.xlsx"
    sample_dataframe.to_excel(excel_file, index=False)
    return excel_file


@pytest.fixture
def sample_invalid_dataframe():
    """DataFrame with invalid data for testing validation"""
    return pd.DataFrame(
        {
            "Case_No": ["CASE001", "CASE002"],
            "Date": ["invalid-date", "2024-01-02"],
            "Location": ["", "DSV Outdoor"],  # Empty location
            "Qty": [-100, 200],  # Negative quantity
            "Amount": [None, 2000.0],  # Missing amount
            "HVDC CODE": ["INVALID", "SIM-123"],
            "HVDC CODE 3": ["INVALID", "SIM"],  # Invalid vendor
            "Operation Month": ["2024-01-01", "2024-02-01"],  # Month mismatch
            "ETA": ["2024-01-15", "2024-01-15"],
        }
    )


@pytest.fixture
def hvdc_test_cases():
    """Test cases for HVDC code normalization and validation"""
    return [
        # (input_code, expected_normalized, is_valid_vendor)
        ("HE-001", "001", True),
        ("SIM-123", "123", True),
        ("INVALID-456", "456", False),
        ("HE", "HE", True),
        ("SIM", "SIM", True),
        ("", "", False),
        (None, "", False),
        ("HE-ABC", "ABC", True),  # Non-numeric suffix
        ("123-HE", "123", False),  # Wrong format
    ]


@pytest.fixture
def warehouse_test_cases():
    """Test cases for warehouse code validation"""
    return [
        # (input_code, expected_result)
        ("DSV Outdoor", True),
        ("DSV Indoor", True),
        ("DSV Al Markaz", True),
        ("DSV MZP", True),
        ("INVALID Warehouse", False),
        ("", False),
        (None, False),
        ("DSV-Outdoor", False),  # Wrong format
    ]


@pytest.fixture
def confidence_test_cases():
    """Test cases for confidence threshold validation"""
    return [
        # (confidence, threshold, expected_result)
        (0.95, 0.95, True),
        (0.96, 0.95, True),
        (0.94, 0.95, False),
        (0.90, 0.90, True),
        (0.89, 0.90, False),
        (1.0, 0.95, True),
        (0.0, 0.95, False),
    ]


@pytest.fixture
def pattern_test_cases():
    """Test cases for HVDC pattern matching"""
    return [
        # (field, value, expected_result)
        ("mbl_no", "ABCD1234567890", True),
        ("mbl_no", "ABC123456789", False),  # Too short
        ("mbl_no", "abcd1234567890", False),  # Lowercase
        ("container_no", "ABCD1234567", True),
        ("container_no", "ABC123456", False),  # Too short
        ("hs_code", "1234567890", True),
        ("hs_code", "12345", False),  # Too short
        ("hs_code", "12345678901", True),  # 10 digits
        ("do_number", "DO1234567890", True),
        ("do_number", "do1234567890", False),  # Lowercase
        ("do_number", "DO12345", False),  # Too short
    ]


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "unit: mark test as unit test")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on file location"""
    for item in items:
        # Add markers based on file path
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Add slow marker for tests that might take longer
        if "performance" in item.name or "benchmark" in item.name:
            item.add_marker(pytest.mark.slow)
