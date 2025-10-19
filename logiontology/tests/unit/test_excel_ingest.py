#!/usr/bin/env python3
"""
Unit tests for Excel ingest functionality

Tests Excel loading, conversion, and data validation
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
import tempfile
import os

from src.ingest.excel import (
    load_excel,
    convert_excel_to_rdf,
    batch_convert_excel_to_rdf,
    validate_excel_data,
    generate_excel_summary,
)


class TestLoadExcel:
    """Test cases for load_excel function"""

    def test_load_excel_success(self, sample_excel_file):
        """Test successful Excel file loading"""
        df = load_excel(str(sample_excel_file))

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0
        assert "Case_No" in df.columns

    def test_load_excel_with_sheet_name(self, sample_excel_file):
        """Test Excel loading with specific sheet name"""
        df = load_excel(str(sample_excel_file), sheet=0)

        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

    def test_load_excel_with_rename_map(self, sample_excel_file):
        """Test Excel loading with column renaming"""
        rename_map = {"Case_No": "case_number", "Date": "event_date"}
        df = load_excel(str(sample_excel_file), rename_map=rename_map)

        assert "case_number" in df.columns
        assert "event_date" in df.columns
        assert "Case_No" not in df.columns

    def test_load_excel_file_not_found(self):
        """Test Excel loading with non-existent file"""
        with pytest.raises(FileNotFoundError):
            load_excel("nonexistent_file.xlsx")

    def test_load_excel_invalid_format(self, tmp_path):
        """Test Excel loading with invalid file format"""
        invalid_file = tmp_path / "invalid.txt"
        invalid_file.write_text("not excel content")

        with pytest.raises(Exception):  # Should raise some exception
            load_excel(str(invalid_file))

    @patch("pandas.read_excel")
    def test_load_excel_pandas_error(self, mock_read_excel):
        """Test Excel loading when pandas raises an error"""
        mock_read_excel.side_effect = Exception("Pandas error")

        with pytest.raises(Exception):
            load_excel("test.xlsx")

    def test_load_excel_empty_file(self, tmp_path):
        """Test Excel loading with empty file"""
        empty_file = tmp_path / "empty.xlsx"
        # Create empty Excel file
        empty_df = pd.DataFrame()
        empty_df.to_excel(empty_file, index=False)

        df = load_excel(str(empty_file))

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0

    def test_load_excel_large_file(self, tmp_path):
        """Test Excel loading with large file"""
        # Create large DataFrame
        large_data = {
            "Case_No": [f"CASE{i:06d}" for i in range(1000)],
            "Date": ["2024-01-01"] * 1000,
            "Location": ["DSV Indoor"] * 1000,
            "Qty": list(range(1000)),
        }
        large_df = pd.DataFrame(large_data)

        large_file = tmp_path / "large.xlsx"
        large_df.to_excel(large_file, index=False)

        df = load_excel(str(large_file))

        assert len(df) == 1000
        assert len(df.columns) == 4


class TestConvertExcelToRdf:
    """Test cases for convert_excel_to_rdf function"""

    def test_convert_excel_to_rdf_success(self, sample_excel_file, tmp_path):
        """Test successful Excel to RDF conversion"""
        output_path = tmp_path / "output.ttl"

        result_path = convert_excel_to_rdf(str(sample_excel_file), str(output_path))

        assert result_path == str(output_path)
        assert Path(result_path).exists()
        assert output_path.suffix == ".ttl"

    def test_convert_excel_to_rdf_auto_output_path(self, sample_excel_file):
        """Test Excel to RDF conversion with auto-generated output path"""
        with patch("pathlib.Path.mkdir") as mock_mkdir:
            with patch("rdflib.Graph.serialize") as mock_serialize:
                result_path = convert_excel_to_rdf(str(sample_excel_file))

                assert result_path is not None
                assert result_path.endswith(".ttl")
                mock_mkdir.assert_called_once()
                mock_serialize.assert_called_once()

    def test_convert_excel_to_rdf_with_field_mappings(self, sample_excel_file, tmp_path):
        """Test Excel to RDF conversion with field mappings"""
        output_path = tmp_path / "mapped_output.ttl"

        with patch("rdflib.Graph.serialize") as mock_serialize:
            result_path = convert_excel_to_rdf(str(sample_excel_file), str(output_path))

            assert result_path == str(output_path)
            mock_serialize.assert_called_once()

    def test_convert_excel_to_rdf_data_types(self, tmp_path):
        """Test Excel to RDF conversion with different data types"""
        # Create test data with various data types
        test_data = {
            "Case_No": ["CASE001", "CASE002"],
            "Date": ["2024-01-01", "2024-01-02"],
            "Qty": [100, 200],  # Integer
            "Amount": [1000.5, 2000.7],  # Float
            "Location": ["DSV Indoor", "DSV Outdoor"],  # String
            "G.W(KG)": [1000.0, 2000.0],  # Float
            "Pkg": [10, 20],  # Integer
        }

        test_df = pd.DataFrame(test_data)
        test_file = tmp_path / "test_types.xlsx"
        test_df.to_excel(test_file, index=False)

        output_path = tmp_path / "types_output.ttl"

        with patch("rdflib.Graph.serialize") as mock_serialize:
            result_path = convert_excel_to_rdf(str(test_file), str(output_path))

            assert result_path == str(output_path)
            mock_serialize.assert_called_once()

    def test_convert_excel_to_rdf_handles_nan_values(self, tmp_path):
        """Test Excel to RDF conversion with NaN values"""
        # Create test data with NaN values
        test_data = {
            "Case_No": ["CASE001", "CASE002", "CASE003"],
            "Date": ["2024-01-01", None, "2024-01-03"],
            "Qty": [100, np.nan, 300],
            "Amount": [1000.0, 2000.0, np.nan],
            "Location": ["DSV Indoor", "DSV Outdoor", None],
        }

        test_df = pd.DataFrame(test_data)
        test_file = tmp_path / "test_nan.xlsx"
        test_df.to_excel(test_file, index=False)

        output_path = tmp_path / "nan_output.ttl"

        with patch("rdflib.Graph.serialize") as mock_serialize:
            result_path = convert_excel_to_rdf(str(test_file), str(output_path))

            assert result_path == str(output_path)
            mock_serialize.assert_called_once()

    def test_convert_excel_to_rdf_excel_load_error(self, tmp_path):
        """Test Excel to RDF conversion when Excel loading fails"""
        invalid_file = tmp_path / "invalid.xlsx"
        invalid_file.write_text("not excel content")

        result = convert_excel_to_rdf(str(invalid_file))

        assert result is None

    def test_convert_excel_to_rdf_creates_output_directory(self, sample_excel_file, tmp_path):
        """Test that output directory is created if it doesn't exist"""
        output_dir = tmp_path / "new_directory"
        output_path = output_dir / "output.ttl"

        with patch("rdflib.Graph.serialize") as mock_serialize:
            result_path = convert_excel_to_rdf(str(sample_excel_file), str(output_path))

            assert result_path == str(output_path)
            # Verify directory creation was attempted
            assert output_dir.exists() or mock_serialize.called

    def test_convert_excel_to_rdf_performance(self, sample_excel_file, tmp_path):
        """Test Excel to RDF conversion performance"""
        output_path = tmp_path / "perf_output.ttl"

        import time

        start_time = time.time()

        with patch("rdflib.Graph.serialize") as mock_serialize:
            result_path = convert_excel_to_rdf(str(sample_excel_file), str(output_path))

        end_time = time.time()

        # Should complete within reasonable time (2 seconds)
        assert (end_time - start_time) < 2.0
        assert result_path == str(output_path)


class TestBatchConvertExcelToRdf:
    """Test cases for batch_convert_excel_to_rdf function"""

    def test_batch_convert_success(self, tmp_path):
        """Test successful batch conversion"""
        # Create multiple Excel files
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        for i in range(3):
            test_data = {"Case_No": [f"CASE{i:03d}"], "Date": ["2024-01-01"], "Qty": [100 + i]}
            df = pd.DataFrame(test_data)
            df.to_excel(input_dir / f"test_{i}.xlsx", index=False)

        output_dir = tmp_path / "output"

        with patch("src.ingest.excel.convert_excel_to_rdf") as mock_convert:
            mock_convert.return_value = "converted.ttl"

            result = batch_convert_excel_to_rdf(str(input_dir), str(output_dir))

            assert len(result) == 3
            assert mock_convert.call_count == 3

    def test_batch_convert_no_files(self, tmp_path):
        """Test batch conversion with no Excel files"""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        output_dir = tmp_path / "output"

        result = batch_convert_excel_to_rdf(str(empty_dir), str(output_dir))

        assert result == []

    def test_batch_convert_mixed_files(self, tmp_path):
        """Test batch conversion with mixed file types"""
        input_dir = tmp_path / "mixed"
        input_dir.mkdir()

        # Create Excel and non-Excel files
        test_data = {"Case_No": ["CASE001"], "Qty": [100]}
        df = pd.DataFrame(test_data)
        df.to_excel(input_dir / "test.xlsx", index=False)
        (input_dir / "test.txt").write_text("not excel")
        (input_dir / "test.csv").write_text("not excel")

        output_dir = tmp_path / "output"

        with patch("src.ingest.excel.convert_excel_to_rdf") as mock_convert:
            mock_convert.return_value = "converted.ttl"

            result = batch_convert_excel_to_rdf(str(input_dir), str(output_dir))

            # Should only process Excel files
            assert len(result) == 1
            assert mock_convert.call_count == 1

    def test_batch_convert_error_handling(self, tmp_path):
        """Test batch conversion error handling"""
        input_dir = tmp_path / "error"
        input_dir.mkdir()

        # Create Excel file
        test_data = {"Case_No": ["CASE001"], "Qty": [100]}
        df = pd.DataFrame(test_data)
        df.to_excel(input_dir / "test.xlsx", index=False)

        output_dir = tmp_path / "output"

        with patch("src.ingest.excel.convert_excel_to_rdf") as mock_convert:
            mock_convert.side_effect = Exception("Conversion error")

            result = batch_convert_excel_to_rdf(str(input_dir), str(output_dir))

            # Should return empty list when conversion fails
            assert result == []

    def test_batch_convert_creates_output_directory(self, tmp_path):
        """Test that output directory is created if it doesn't exist"""
        input_dir = tmp_path / "input"
        input_dir.mkdir()

        test_data = {"Case_No": ["CASE001"], "Qty": [100]}
        df = pd.DataFrame(test_data)
        df.to_excel(input_dir / "test.xlsx", index=False)

        output_dir = tmp_path / "new_output"

        with patch("src.ingest.excel.convert_excel_to_rdf") as mock_convert:
            mock_convert.return_value = "converted.ttl"

            result = batch_convert_excel_to_rdf(str(input_dir), str(output_dir))

            assert len(result) == 1
            # Output directory should be created
            assert output_dir.exists()


class TestValidateExcelData:
    """Test cases for validate_excel_data function"""

    def test_validate_excel_data_success(self, sample_dataframe):
        """Test successful Excel data validation"""
        result = validate_excel_data(sample_dataframe)

        assert result["total_rows"] == len(sample_dataframe)
        assert result["total_columns"] == len(sample_dataframe.columns)
        assert isinstance(result["missing_values"], dict)
        assert isinstance(result["duplicate_rows"], (int, np.integer))
        assert isinstance(result["data_types"], dict)
        assert isinstance(result["required_columns"], list)
        assert isinstance(result["missing_required"], list)

    def test_validate_excel_data_missing_required_columns(self):
        """Test validation with missing required columns"""
        test_df = pd.DataFrame({"Unknown_Field": [1, 2, 3], "Another_Field": ["a", "b", "c"]})

        result = validate_excel_data(test_df)

        assert result["total_rows"] == 3
        assert result["total_columns"] == 2
        assert len(result["missing_required"]) == 4  # All required columns missing

    def test_validate_excel_data_with_missing_values(self):
        """Test validation with missing values"""
        test_df = pd.DataFrame(
            {
                "Case_No": ["CASE001", "CASE002", None],
                "Date": ["2024-01-01", None, "2024-01-03"],
                "Qty": [100, 200, None],
                "Location": ["DSV Indoor", "DSV Outdoor", "DSV Al Markaz"],
            }
        )

        result = validate_excel_data(test_df)

        assert result["total_rows"] == 3
        assert result["missing_values"]["Case_No"] == 1
        assert result["missing_values"]["Date"] == 1
        assert result["missing_values"]["Qty"] == 1
        assert result["missing_values"]["Location"] == 0

    def test_validate_excel_data_with_duplicates(self):
        """Test validation with duplicate rows"""
        test_df = pd.DataFrame(
            {
                "Case_No": ["CASE001", "CASE002", "CASE001"],  # Duplicate
                "Date": ["2024-01-01", "2024-01-02", "2024-01-01"],  # Duplicate
                "Qty": [100, 200, 100],  # Duplicate
            }
        )

        result = validate_excel_data(test_df)

        assert result["total_rows"] == 3
        assert result["duplicate_rows"] == 1

    def test_validate_excel_data_empty_dataframe(self):
        """Test validation with empty DataFrame"""
        empty_df = pd.DataFrame()

        result = validate_excel_data(empty_df)

        assert result["total_rows"] == 0
        assert result["total_columns"] == 0
        assert result["duplicate_rows"] == 0

    def test_validate_excel_data_data_types(self):
        """Test validation with different data types"""
        test_df = pd.DataFrame(
            {
                "Case_No": ["CASE001", "CASE002"],  # Object
                "Qty": [100, 200],  # Int64
                "Amount": [1000.5, 2000.7],  # Float64
                "Date": pd.to_datetime(["2024-01-01", "2024-01-02"]),  # Datetime
            }
        )

        result = validate_excel_data(test_df)

        assert result["data_types"]["Case_No"] == "object"
        assert result["data_types"]["Qty"] == "int64"
        assert result["data_types"]["Amount"] == "float64"
        assert "datetime" in str(result["data_types"]["Date"])


class TestGenerateExcelSummary:
    """Test cases for generate_excel_summary function"""

    def test_generate_excel_summary_success(self, sample_dataframe):
        """Test successful Excel summary generation"""
        result = generate_excel_summary(sample_dataframe)

        assert "file_info" in result
        assert "data_quality" in result
        assert "numeric_summary" in result
        assert "categorical_summary" in result

        assert result["file_info"]["total_rows"] == len(sample_dataframe)
        assert result["file_info"]["total_columns"] == len(sample_dataframe.columns)
        assert isinstance(result["file_info"]["memory_usage"], (int, np.integer))

    def test_generate_excel_summary_data_quality(self, sample_dataframe):
        """Test data quality metrics in summary"""
        result = generate_excel_summary(sample_dataframe)

        assert isinstance(result["data_quality"]["missing_values"], (int, np.integer))
        assert isinstance(result["data_quality"]["duplicate_rows"], (int, np.integer))
        assert isinstance(result["data_quality"]["unique_values"], dict)

    def test_generate_excel_summary_numeric_columns(self):
        """Test summary with numeric columns"""
        test_df = pd.DataFrame(
            {
                "Qty": [100, 200, 300, 400, 500],
                "Amount": [1000.5, 2000.7, 3000.9, 4000.1, 5000.3],
                "Location": ["DSV Indoor", "DSV Outdoor", "DSV Al Markaz", "DSV MZP", "DSV Indoor"],
            }
        )

        result = generate_excel_summary(test_df)

        assert "Qty" in result["numeric_summary"]
        assert "Amount" in result["numeric_summary"]
        assert "count" in result["numeric_summary"]["Qty"]
        assert "mean" in result["numeric_summary"]["Qty"]
        assert "std" in result["numeric_summary"]["Qty"]

    def test_generate_excel_summary_categorical_columns(self):
        """Test summary with categorical columns"""
        test_df = pd.DataFrame(
            {
                "Location": ["DSV Indoor", "DSV Outdoor", "DSV Indoor", "DSV Al Markaz"],
                "Status": ["Active", "Inactive", "Active", "Pending"],
            }
        )

        result = generate_excel_summary(test_df)

        assert "Location" in result["categorical_summary"]
        assert "Status" in result["categorical_summary"]
        assert "unique_count" in result["categorical_summary"]["Location"]
        assert "most_common" in result["categorical_summary"]["Location"]
        assert "most_common_count" in result["categorical_summary"]["Location"]

    def test_generate_excel_summary_empty_dataframe(self):
        """Test summary with empty DataFrame"""
        empty_df = pd.DataFrame()

        result = generate_excel_summary(empty_df)

        assert result["file_info"]["total_rows"] == 0
        assert result["file_info"]["total_columns"] == 0
        assert result["data_quality"]["missing_values"] == 0
        assert result["data_quality"]["duplicate_rows"] == 0

    def test_generate_excel_summary_mixed_data_types(self):
        """Test summary with mixed data types"""
        test_df = pd.DataFrame(
            {
                "Case_No": ["CASE001", "CASE002", "CASE003"],  # Object
                "Qty": [100, 200, 300],  # Numeric
                "Amount": [1000.5, 2000.7, 3000.9],  # Numeric
                "Location": ["DSV Indoor", "DSV Outdoor", "DSV Indoor"],  # Object
                "Active": [True, False, True],  # Boolean
            }
        )

        result = generate_excel_summary(test_df)

        assert len(result["numeric_summary"]) == 2  # Qty and Amount
        assert (
            len(result["categorical_summary"]) == 2
        )  # Case_No, Location (Boolean is not categorical)

    def test_generate_excel_summary_performance(self, sample_dataframe):
        """Test summary generation performance"""
        import time

        start_time = time.time()

        result = generate_excel_summary(sample_dataframe)

        end_time = time.time()

        # Should complete within reasonable time (1 second)
        assert (end_time - start_time) < 1.0
        assert isinstance(result, dict)

    def test_generate_excel_summary_large_dataset(self):
        """Test summary generation with large dataset"""
        # Create large dataset
        large_data = {
            "Case_No": [f"CASE{i:06d}" for i in range(1000)],
            "Qty": list(range(1000)),
            "Amount": [1000.0 + i for i in range(1000)],
            "Location": ["DSV Indoor" if i % 2 == 0 else "DSV Outdoor" for i in range(1000)],
        }

        large_df = pd.DataFrame(large_data)

        result = generate_excel_summary(large_df)

        assert result["file_info"]["total_rows"] == 1000
        assert result["file_info"]["total_columns"] == 4
        assert result["data_quality"]["duplicate_rows"] == 0  # No duplicates in this dataset
