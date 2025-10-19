#!/usr/bin/env python3
"""
Schema Validator for Unified IR Documents

Validates parsed documents against the Unified IR schema (unified_ir_schema_hvdc.yaml).
Enforces confidence thresholds and field completeness for HVDC requirements.
"""

from __future__ import annotations
from typing import Dict, List, Tuple, Any, Optional, Iterable
import logging
import re
from datetime import datetime
from pydantic import ValidationError
from logiontology.core.models import TransportEvent, StockSnapshot, DeadStock


class SchemaValidator:
    """
    Validate documents against Unified IR schema

    Key validations:
    - Required fields present
    - Field types correct
    - Confidence thresholds met (≥0.95 for HVDC safety-critical)
    - HVDC-specific field completeness
    - Document type-specific requirements
    """

    def __init__(self, min_confidence: float = 0.90, log_level: str = "INFO"):
        """
        Initialize validator

        Args:
            min_confidence: Minimum confidence threshold (default: 0.90 for HVDC)
            log_level: Logging level
        """
        self.min_confidence = min_confidence
        self.logger = self._setup_logger(log_level)

        # HVDC-specific confidence thresholds by field
        self.field_confidence_thresholds = {
            "BOE": {
                "mbl_no": 0.95,
                "entry_no": 0.95,
                "containers": 0.90,
                "gross_weight": 0.85,
                "hs_code": 0.95,
            },
            "DO": {"do_number": 0.95, "do_validity_date": 0.90, "container_no": 0.95},
            "DN": {
                "origin": 0.85,
                "destination": 0.85,
                "delivery_date": 0.90,
            },
            "CarrierInvoice": {
                "invoice_number": 0.95,
                "total_amount": 0.95,
                "currency": 0.90,
            },
            "WarehouseInvoice": {
                "warehouse_name": 0.90,
                "rental_period": 0.85,
                "sqm": 0.90,
            },
        }

        # Required fields by document type
        self.required_fields = {
            "BOE": ["mbl_no", "entry_no", "containers", "gross_weight", "hs_code"],
            "DO": ["do_number", "do_validity_date", "container_no"],
            "DN": ["origin", "destination", "delivery_date"],
            "CarrierInvoice": ["invoice_number", "total_amount", "currency"],
            "WarehouseInvoice": ["warehouse_name", "rental_period", "sqm"],
        }

        # HVDC-specific field patterns
        self.hvdc_patterns = {
            "mbl_no": r"^[A-Z]{4}\d{10}$",  # 4 letters + 10 digits
            "container_no": r"^[A-Z]{4}\d{7}$",  # 4 letters + 7 digits
            "hs_code": r"^\d{6,10}$",  # 6-10 digits
            "do_number": r"^DO\d{6,10}$",  # DO + 6-10 digits
        }

    def _setup_logger(self, log_level: str) -> logging.Logger:
        """Setup logger for validation"""
        logger = logging.getLogger(__name__)
        logger.setLevel(getattr(logging, log_level.upper()))

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def validate(self, document: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a single document against schema

        Args:
            document: Document to validate

        Returns:
            Tuple[bool, List[str]]: (is_valid, list_of_errors)
        """
        errors = []

        # Check document type
        doc_type = document.get("type")
        if not doc_type:
            errors.append("Missing document type")
            return False, errors

        if doc_type not in self.required_fields:
            errors.append(f"Unknown document type: {doc_type}")
            return False, errors

        # Check required fields
        required = self.required_fields[doc_type]
        for field in required:
            if field not in document:
                errors.append(f"Missing required field: {field}")
            elif not document[field]:
                errors.append(f"Empty required field: {field}")

        # Check confidence thresholds
        confidence_errors = self._validate_confidence(document, doc_type)
        errors.extend(confidence_errors)

        # Check HVDC-specific patterns
        pattern_errors = self._validate_hvdc_patterns(document, doc_type)
        errors.extend(pattern_errors)

        # Check meta section
        meta_errors = self._validate_meta_section(document)
        errors.extend(meta_errors)

        # Check blocks array
        blocks_errors = self._validate_blocks(document)
        errors.extend(blocks_errors)

        is_valid = len(errors) == 0
        if is_valid:
            self.logger.info(f"Document validation passed: {doc_type}")
        else:
            self.logger.warning(f"Document validation failed: {doc_type}, errors: {len(errors)}")

        return is_valid, errors

    def _validate_confidence(self, document: Dict[str, Any], doc_type: str) -> List[str]:
        """Validate confidence thresholds"""
        errors = []
        thresholds = self.field_confidence_thresholds.get(doc_type, {})

        for field, min_conf in thresholds.items():
            if field in document:
                field_data = document[field]
                if isinstance(field_data, dict) and "confidence" in field_data:
                    conf = field_data["confidence"]
                    if conf < min_conf:
                        errors.append(
                            f"Field '{field}' confidence {conf:.3f} below threshold {min_conf:.3f}"
                        )

        return errors

    def _validate_hvdc_patterns(self, document: Dict[str, Any], doc_type: str) -> List[str]:
        """Validate HVDC-specific field patterns"""
        errors = []

        for field, pattern in self.hvdc_patterns.items():
            if field in document:
                value = str(document[field])
                if not re.match(pattern, value):
                    errors.append(f"Field '{field}' value '{value}' does not match HVDC pattern")

        return errors

    def _validate_meta_section(self, document: Dict[str, Any]) -> List[str]:
        """Validate meta section"""
        errors = []

        if "meta" not in document:
            errors.append("Missing meta section")
            return errors

        meta = document["meta"]
        required_meta = ["source", "timestamp", "version"]

        for field in required_meta:
            if field not in meta:
                errors.append(f"Missing meta field: {field}")

        # Validate timestamp format
        if "timestamp" in meta:
            try:
                datetime.fromisoformat(meta["timestamp"].replace("Z", "+00:00"))
            except ValueError:
                errors.append("Invalid timestamp format in meta section")

        return errors

    def _validate_blocks(self, document: Dict[str, Any]) -> List[str]:
        """Validate blocks array"""
        errors = []

        if "blocks" not in document:
            errors.append("Missing blocks array")
            return errors

        blocks = document["blocks"]
        if not isinstance(blocks, list):
            errors.append("Blocks must be an array")
            return errors

        if len(blocks) == 0:
            errors.append("Blocks array cannot be empty")

        # Validate each block
        for i, block in enumerate(blocks):
            if not isinstance(block, dict):
                errors.append(f"Block {i} must be a dictionary")
                continue

            if "type" not in block:
                errors.append(f"Block {i} missing type field")

            if "content" not in block:
                errors.append(f"Block {i} missing content field")

        return errors

    def validate_batch(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate a batch of documents

        Args:
            documents: List of documents to validate

        Returns:
            Dict with validation summary
        """
        results = {
            "total": len(documents),
            "valid": 0,
            "invalid": 0,
            "errors_by_type": {},
            "confidence_failures": 0,
            "pattern_failures": 0,
        }

        for doc in documents:
            is_valid, errors = self.validate(doc)

            if is_valid:
                results["valid"] += 1
            else:
                results["invalid"] += 1

                # Categorize errors
                for error in errors:
                    if "confidence" in error.lower():
                        results["confidence_failures"] += 1
                    elif "pattern" in error.lower():
                        results["pattern_failures"] += 1

                    # Count by document type
                    doc_type = doc.get("type", "unknown")
                    if doc_type not in results["errors_by_type"]:
                        results["errors_by_type"][doc_type] = 0
                    results["errors_by_type"][doc_type] += 1

        return results


# Pydantic model validation functions
def validate_transport_events(records: Iterable[dict[str, Any]]) -> Tuple[bool, list[str]]:
    """Validate TransportEvent records using Pydantic models"""
    errors: list[str] = []
    for i, rec in enumerate(records):
        try:
            TransportEvent.model_validate(rec)
        except Exception as e:
            errors.append(f"row={i}: {e}")
    return (len(errors) == 0, errors)


def validate_stock_snapshots(records: Iterable[dict[str, Any]]) -> Tuple[bool, list[str]]:
    """Validate StockSnapshot records using Pydantic models"""
    errors: list[str] = []
    for i, rec in enumerate(records):
        try:
            StockSnapshot.model_validate(rec)
        except Exception as e:
            errors.append(f"row={i}: {e}")
    return (len(errors) == 0, errors)


def validate_dead_stock(records: Iterable[dict[str, Any]]) -> Tuple[bool, list[str]]:
    """Validate DeadStock records using Pydantic models"""
    errors: list[str] = []
    for i, rec in enumerate(records):
        try:
            DeadStock.model_validate(rec)
        except Exception as e:
            errors.append(f"row={i}: {e}")
    return (len(errors) == 0, errors)
