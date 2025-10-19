#!/usr/bin/env python3
"""
Unit tests for Pydantic models in logiontology.core.models
"""

import pytest
import json
from datetime import datetime
from typing import Dict, Any

from logiontology.core.models import TransportEvent, StockSnapshot, DeadStock


class TestTransportEvent:
    """Test cases for TransportEvent model"""

    def test_transport_event_valid_data(self):
        """Test TransportEvent with valid data"""
        valid_data = {
            "event_id": "EVT001",
            "shipment_id": "SHIP001",
            "event_type": "LOAD",
            "occurred_at": "2024-01-01T00:00:00Z",
            "location": "Dubai Port",
        }

        event = TransportEvent(**valid_data)
        assert event.event_id == "EVT001"
        assert event.shipment_id == "SHIP001"
        assert event.event_type == "LOAD"
        assert event.occurred_at.replace(tzinfo=None) == datetime(2024, 1, 1, 0, 0, 0)
        assert event.location == "Dubai Port"

    def test_transport_event_minimal_data(self):
        """Test TransportEvent with minimal required data"""
        minimal_data = {
            "event_id": "EVT001",
            "shipment_id": "SHIP001",
            "event_type": "LOAD",
            "occurred_at": "2024-01-01T00:00:00Z",
        }

        event = TransportEvent(**minimal_data)
        assert event.event_id == "EVT001"
        assert event.shipment_id == "SHIP001"
        assert event.event_type == "LOAD"
        assert event.occurred_at.replace(tzinfo=None) == datetime(2024, 1, 1, 0, 0, 0)
        assert event.location is None

    def test_transport_event_missing_required_fields(self):
        """Test TransportEvent with missing required fields"""
        with pytest.raises(ValueError):
            TransportEvent(event_id="EVT001")  # Missing required fields

    def test_transport_event_invalid_event_type(self):
        """Test TransportEvent with invalid event type"""
        with pytest.raises(ValueError):
            TransportEvent(
                event_id="EVT001",
                shipment_id="SHIP001",
                event_type="INVALID",
                occurred_at="2024-01-01T00:00:00Z",
            )

    def test_transport_event_invalid_timestamp_format(self):
        """Test TransportEvent with invalid timestamp format"""
        with pytest.raises(ValueError):
            TransportEvent(
                event_id="EVT001",
                shipment_id="SHIP001",
                event_type="LOAD",
                occurred_at="invalid-date",
            )

    def test_transport_event_empty_values(self):
        """Test TransportEvent with empty string values"""
        # Pydantic allows empty strings by default, so this should not raise an error
        event = TransportEvent(
            event_id="",
            shipment_id="SHIP001",
            event_type="LOAD",
            occurred_at="2024-01-01T00:00:00Z",
        )
        assert event.event_id == ""

    def test_transport_event_none_values(self):
        """Test TransportEvent with None values for required fields"""
        with pytest.raises(ValueError):
            TransportEvent(
                event_id=None,
                shipment_id="SHIP001",
                event_type="LOAD",
                occurred_at="2024-01-01T00:00:00Z",
            )

    def test_transport_event_optional_fields(self):
        """Test TransportEvent with optional fields"""
        data_with_optionals = {
            "event_id": "EVT001",
            "shipment_id": "SHIP001",
            "event_type": "LOAD",
            "occurred_at": "2024-01-01T00:00:00Z",
            "location": "Dubai Port",
            "attributes": {"vessel": "MV Test", "container": "ABCD1234567"},
        }

        event = TransportEvent(**data_with_optionals)
        assert event.location == "Dubai Port"
        assert event.attributes == {"vessel": "MV Test", "container": "ABCD1234567"}

    def test_transport_event_datetime_parsing(self):
        """Test TransportEvent datetime parsing with different formats"""
        # ISO format
        event1 = TransportEvent(
            event_id="EVT001",
            shipment_id="SHIP001",
            event_type="LOAD",
            occurred_at="2024-01-01T00:00:00Z",
        )
        assert event1.occurred_at.replace(tzinfo=None) == datetime(2024, 1, 1, 0, 0, 0)

        # ISO format without timezone
        event2 = TransportEvent(
            event_id="EVT002",
            shipment_id="SHIP002",
            event_type="UNLOAD",
            occurred_at="2024-01-01T00:00:00",
        )
        assert event2.occurred_at == datetime(2024, 1, 1, 0, 0, 0)

    def test_transport_event_serialization(self):
        """Test TransportEvent serialization to dict"""
        event = TransportEvent(
            event_id="EVT001",
            shipment_id="SHIP001",
            event_type="LOAD",
            occurred_at="2024-01-01T00:00:00Z",
            location="Dubai Port",
        )

        data = event.model_dump()
        assert data["event_id"] == "EVT001"
        assert data["shipment_id"] == "SHIP001"
        assert data["event_type"] == "LOAD"
        assert data["location"] == "Dubai Port"

    def test_transport_event_json_serialization(self):
        """Test TransportEvent JSON serialization"""
        event = TransportEvent(
            event_id="EVT001",
            shipment_id="SHIP001",
            event_type="LOAD",
            occurred_at="2024-01-01T00:00:00Z",
            location="Dubai Port",
        )

        json_str = event.model_dump_json()
        data = json.loads(json_str)
        assert data["event_id"] == "EVT001"
        assert data["event_type"] == "LOAD"


class TestStockSnapshot:
    """Test cases for StockSnapshot model"""

    def test_stock_snapshot_valid_data(self):
        """Test StockSnapshot with valid data"""
        valid_data = {
            "snapshot_id": "SNAP001",
            "sku_id": "SKU001",
            "location_id": "LOC001",
            "on_hand": 100,
            "allocated": 20,
            "available": 80,
            "at": "2024-01-01T00:00:00Z",
        }

        snapshot = StockSnapshot(**valid_data)
        assert snapshot.snapshot_id == "SNAP001"
        assert snapshot.sku_id == "SKU001"
        assert snapshot.location_id == "LOC001"
        assert snapshot.on_hand == 100
        assert snapshot.allocated == 20
        assert snapshot.available == 80
        assert snapshot.at.replace(tzinfo=None) == datetime(2024, 1, 1, 0, 0, 0)

    def test_stock_snapshot_minimal_data(self):
        """Test StockSnapshot with minimal required data"""
        minimal_data = {
            "snapshot_id": "SNAP001",
            "sku_id": "SKU001",
            "location_id": "LOC001",
            "at": "2024-01-01T00:00:00Z",
        }

        snapshot = StockSnapshot(**minimal_data)
        assert snapshot.snapshot_id == "SNAP001"
        assert snapshot.sku_id == "SKU001"
        assert snapshot.location_id == "LOC001"
        assert snapshot.on_hand == 0
        assert snapshot.allocated == 0
        assert snapshot.available == 0

    def test_stock_snapshot_zero_quantity(self):
        """Test StockSnapshot with zero quantity (should be valid)"""
        snapshot = StockSnapshot(
            snapshot_id="SNAP001",
            sku_id="SKU001",
            location_id="LOC001",
            on_hand=0,
            at="2024-01-01T00:00:00Z",
        )
        assert snapshot.on_hand == 0

    def test_stock_snapshot_negative_quantity(self):
        """Test StockSnapshot with negative quantity (should be valid)"""
        snapshot = StockSnapshot(
            snapshot_id="SNAP001",
            sku_id="SKU001",
            location_id="LOC001",
            on_hand=-10,
            at="2024-01-01T00:00:00Z",
        )
        assert snapshot.on_hand == -10

    def test_stock_snapshot_missing_required_fields(self):
        """Test StockSnapshot with missing required fields"""
        with pytest.raises(ValueError):
            StockSnapshot(snapshot_id="SNAP001")  # Missing required fields

    def test_stock_snapshot_invalid_timestamp_format(self):
        """Test StockSnapshot with invalid timestamp format"""
        with pytest.raises(ValueError):
            StockSnapshot(
                snapshot_id="SNAP001",
                sku_id="SKU001",
                location_id="LOC001",
                at="invalid-date",
            )

    def test_stock_snapshot_empty_values(self):
        """Test StockSnapshot with empty string values"""
        # Pydantic allows empty strings by default, so this should not raise an error
        snapshot = StockSnapshot(
            snapshot_id="",
            sku_id="SKU001",
            location_id="LOC001",
            at="2024-01-01T00:00:00Z",
        )
        assert snapshot.snapshot_id == ""

    def test_stock_snapshot_none_values(self):
        """Test StockSnapshot with None values for required fields"""
        with pytest.raises(ValueError):
            StockSnapshot(
                snapshot_id=None,
                sku_id="SKU001",
                location_id="LOC001",
                at="2024-01-01T00:00:00Z",
            )

    def test_stock_snapshot_serialization(self):
        """Test StockSnapshot serialization to dict"""
        snapshot = StockSnapshot(
            snapshot_id="SNAP001",
            sku_id="SKU001",
            location_id="LOC001",
            on_hand=100,
            at="2024-01-01T00:00:00Z",
        )

        data = snapshot.model_dump()
        assert data["snapshot_id"] == "SNAP001"
        assert data["sku_id"] == "SKU001"
        assert data["on_hand"] == 100


class TestDeadStock:
    """Test cases for DeadStock model"""

    def test_dead_stock_valid_data(self):
        """Test DeadStock with valid data"""
        valid_data = {
            "deadstock_id": "DS001",
            "sku_id": "SKU001",
            "location_id": "LOC001",
            "quantity": 50,
            "days_stagnant": 90,
            "reason": "no_demand",
        }

        dead_stock = DeadStock(**valid_data)
        assert dead_stock.deadstock_id == "DS001"
        assert dead_stock.sku_id == "SKU001"
        assert dead_stock.location_id == "LOC001"
        assert dead_stock.quantity == 50
        assert dead_stock.days_stagnant == 90
        assert dead_stock.reason == "no_demand"

    def test_dead_stock_minimal_data(self):
        """Test DeadStock with minimal required data"""
        minimal_data = {
            "deadstock_id": "DS001",
            "sku_id": "SKU001",
            "location_id": "LOC001",
            "quantity": 50,
            "days_stagnant": 90,
        }

        dead_stock = DeadStock(**minimal_data)
        assert dead_stock.deadstock_id == "DS001"
        assert dead_stock.sku_id == "SKU001"
        assert dead_stock.location_id == "LOC001"
        assert dead_stock.quantity == 50
        assert dead_stock.days_stagnant == 90
        assert dead_stock.reason is None

    def test_dead_stock_zero_quantity(self):
        """Test DeadStock with zero quantity (should be valid)"""
        dead_stock = DeadStock(
            deadstock_id="DS001",
            sku_id="SKU001",
            location_id="LOC001",
            quantity=0,
            days_stagnant=90,
        )
        assert dead_stock.quantity == 0

    def test_dead_stock_negative_quantity(self):
        """Test DeadStock with negative quantity (should be valid)"""
        dead_stock = DeadStock(
            deadstock_id="DS001",
            sku_id="SKU001",
            location_id="LOC001",
            quantity=-10,
            days_stagnant=90,
        )
        assert dead_stock.quantity == -10

    def test_dead_stock_missing_required_fields(self):
        """Test DeadStock with missing required fields"""
        with pytest.raises(ValueError):
            DeadStock(deadstock_id="DS001")  # Missing required fields

    def test_dead_stock_empty_values(self):
        """Test DeadStock with empty string values"""
        # Pydantic allows empty strings by default, so this should not raise an error
        dead_stock = DeadStock(
            deadstock_id="",
            sku_id="SKU001",
            location_id="LOC001",
            quantity=50,
            days_stagnant=90,
        )
        assert dead_stock.deadstock_id == ""

    def test_dead_stock_none_values(self):
        """Test DeadStock with None values for required fields"""
        with pytest.raises(ValueError):
            DeadStock(
                deadstock_id=None,
                sku_id="SKU001",
                location_id="LOC001",
                quantity=50,
                days_stagnant=90,
            )

    def test_dead_stock_serialization(self):
        """Test DeadStock serialization to dict"""
        dead_stock = DeadStock(
            deadstock_id="DS001",
            sku_id="SKU001",
            location_id="LOC001",
            quantity=50,
            days_stagnant=90,
            reason="no_demand",
        )

        data = dead_stock.model_dump()
        assert data["deadstock_id"] == "DS001"
        assert data["sku_id"] == "SKU001"
        assert data["quantity"] == 50
        assert data["reason"] == "no_demand"


class TestModelIntegration:
    """Integration tests for all models"""

    def test_models_with_realistic_data(self):
        """Test all models with realistic HVDC logistics data"""
        # TransportEvent
        transport_event = TransportEvent(
            event_id="EVT-2024-001",
            shipment_id="SHIP-2024-001",
            event_type="LOAD",
            occurred_at="2024-01-15T08:30:00Z",
            location="Dubai Port",
            attributes={"vessel": "MV HVDC Carrier", "container": "ABCD1234567"},
        )
        assert transport_event.event_id == "EVT-2024-001"
        assert transport_event.event_type == "LOAD"

        # StockSnapshot
        stock_snapshot = StockSnapshot(
            snapshot_id="SNAP-2024-001",
            sku_id="HVDC-HE-001",
            location_id="DSV-INDOOR-001",
            on_hand=100,
            allocated=20,
            available=80,
            at="2024-01-15T08:30:00Z",
        )
        assert stock_snapshot.sku_id == "HVDC-HE-001"
        assert stock_snapshot.on_hand == 100

        # DeadStock
        dead_stock = DeadStock(
            deadstock_id="DS-2024-001",
            sku_id="HVDC-HE-002",
            location_id="DSV-INDOOR-002",
            quantity=25,
            days_stagnant=120,
            reason="no_demand",
        )
        assert dead_stock.sku_id == "HVDC-HE-002"
        assert dead_stock.days_stagnant == 120

    def test_models_json_roundtrip(self):
        """Test JSON serialization and deserialization roundtrip"""
        # Create models
        transport_event = TransportEvent(
            event_id="EVT001",
            shipment_id="SHIP001",
            event_type="LOAD",
            occurred_at="2024-01-01T00:00:00Z",
        )

        # Serialize to JSON
        json_str = transport_event.model_dump_json()
        data = json.loads(json_str)

        # Deserialize from JSON
        restored_event = TransportEvent.model_validate(data)
        assert restored_event.event_id == transport_event.event_id
        assert restored_event.shipment_id == transport_event.shipment_id
        assert restored_event.event_type == transport_event.event_type

    def test_models_validation_performance(self):
        """Test model validation performance with large datasets"""
        import time

        # Test TransportEvent validation performance
        start_time = time.time()

        for i in range(100):
            TransportEvent(
                event_id=f"EVT{i:03d}",
                shipment_id=f"SHIP{i:03d}",
                event_type="LOAD",
                occurred_at="2024-01-01T00:00:00Z",
            )

        end_time = time.time()
        validation_time = end_time - start_time

        # Should complete 100 validations in less than 1 second
        assert validation_time < 1.0, f"Validation took too long: {validation_time:.2f}s"

    def test_models_with_numpy_types(self):
        """Test models with numpy types (common in pandas DataFrames)"""
        import numpy as np

        # Test with numpy int64
        snapshot = StockSnapshot(
            snapshot_id="SNAP001",
            sku_id="SKU001",
            location_id="LOC001",
            on_hand=np.int64(100),
            at="2024-01-01T00:00:00Z",
        )
        assert snapshot.on_hand == 100
        assert isinstance(snapshot.on_hand, int)

        # Test with numpy float64
        dead_stock = DeadStock(
            deadstock_id="DS001",
            sku_id="SKU001",
            location_id="LOC001",
            quantity=int(np.float64(50)),
            days_stagnant=90,
        )
        assert dead_stock.quantity == 50
        assert isinstance(dead_stock.quantity, int)
