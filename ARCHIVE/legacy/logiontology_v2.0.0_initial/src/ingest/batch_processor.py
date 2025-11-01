"""Batch processing for multiple Excel files."""

from pathlib import Path
from typing import List
import logging

from src.ingest.excel_to_rdf import ExcelToRDFConverter
from src.ontology.validator import OntologyValidator

logger = logging.getLogger(__name__)


class BatchProcessor:
    """Process multiple Excel files to RDF with validation."""

    def __init__(self, validate: bool = True):
        """Initialize batch processor."""
        self.converter = ExcelToRDFConverter()
        self.validator = OntologyValidator() if validate else None
        self.validate_flag = validate

    def process_directory(
        self,
        input_dir: Path,
        output_dir: Path,
        pattern: str = "*.xlsx"
    ) -> List[Path]:
        """
        Process all Excel files in directory.

        Args:
            input_dir: Directory containing Excel files
            output_dir: Directory for output TTL files
            pattern: Glob pattern for Excel files

        Returns:
            List of generated TTL file paths
        """
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        excel_files = list(input_dir.glob(pattern))
        logger.info(f"Found {len(excel_files)} Excel files matching pattern: {pattern}")

        results = []
        success_count = 0
        error_count = 0

        for file in excel_files:
            try:
                logger.info(f"Processing: {file.name}")

                # Convert to RDF
                output_file = output_dir / f"{file.stem}.ttl"
                graph = self.converter.convert(file, output_file)

                # Validate if enabled
                if self.validate_flag and self.validator:
                    logger.info(f"Validating: {file.name}")
                    conforms, report = self.validator.validate(graph)

                    if not conforms:
                        logger.warning(f"Validation failed for {file.name}:\n{report}")
                    else:
                        logger.info(f"✓ Validation passed for {file.name}")

                results.append(output_file)
                success_count += 1
                logger.info(f"✓ Successfully converted: {file.name}")

            except Exception as e:
                error_count += 1
                logger.error(f"✗ Failed to convert {file.name}: {e}")

        logger.info(
            f"Batch processing complete: {success_count} succeeded, {error_count} failed"
        )

        return results

    def process_files(
        self,
        excel_files: List[Path],
        output_dir: Path
    ) -> List[Path]:
        """
        Process specific Excel files.

        Args:
            excel_files: List of Excel file paths
            output_dir: Directory for output TTL files

        Returns:
            List of generated TTL file paths
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        results = []

        for file in excel_files:
            try:
                output_file = output_dir / f"{Path(file).stem}.ttl"
                graph = self.converter.convert(Path(file), output_file)

                if self.validate_flag and self.validator:
                    conforms, report = self.validator.validate(graph)
                    if not conforms:
                        logger.warning(f"Validation issues in {file}:\n{report}")

                results.append(output_file)
                logger.info(f"✓ Converted: {file}")

            except Exception as e:
                logger.error(f"✗ Failed: {file} - {e}")

        return results


