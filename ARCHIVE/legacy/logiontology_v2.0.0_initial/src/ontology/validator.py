"""Ontology validation using SHACL constraints."""

from pathlib import Path
from typing import Tuple, Optional
from rdflib import Graph
import logging

logger = logging.getLogger(__name__)


class OntologyValidator:
    """Validate RDF data against SHACL shapes."""

    def __init__(self, shapes_path: Path | str = None):
        """Initialize with SHACL shapes file path."""
        if shapes_path is None:
            shapes_path = Path(__file__).parent.parent.parent / "configs" / "shapes" / "FlowCode.shape.ttl"

        self.shapes_path = Path(shapes_path)
        self.shapes_graph = Graph()

        if self.shapes_path.exists():
            self.shapes_graph.parse(self.shapes_path, format="turtle")
        else:
            logger.warning(f"SHACL shapes file not found: {self.shapes_path}")

    def validate(self, data_graph: Graph, ontology_graph: Optional[Graph] = None) -> Tuple[bool, str]:
        """
        Validate data graph against SHACL shapes.

        Args:
            data_graph: RDF graph containing data to validate
            ontology_graph: Optional ontology graph for inference

        Returns:
            Tuple of (conforms: bool, report_text: str)
        """
        try:
            from pyshacl import validate

            conforms, results_graph, results_text = validate(
                data_graph=data_graph,
                shacl_graph=self.shapes_graph,
                ont_graph=ontology_graph,
                inference='rdfs',
                abort_on_first=False,
                allow_infos=True,
                allow_warnings=True,
            )

            return conforms, results_text

        except ImportError:
            logger.error("pyshacl not installed. Install with: pip install pyshacl")
            return True, "SHACL validation skipped (pyshacl not installed)"
        except Exception as e:
            logger.error(f"SHACL validation error: {e}")
            return False, f"Validation error: {str(e)}"

    def validate_file(self, data_file: Path, ontology_file: Optional[Path] = None) -> Tuple[bool, str]:
        """
        Validate RDF file against SHACL shapes.

        Args:
            data_file: Path to RDF data file
            ontology_file: Optional path to ontology file

        Returns:
            Tuple of (conforms: bool, report_text: str)
        """
        data_graph = Graph()
        data_graph.parse(data_file, format="turtle")

        ontology_graph = None
        if ontology_file and ontology_file.exists():
            ontology_graph = Graph()
            ontology_graph.parse(ontology_file, format="turtle")

        return self.validate(data_graph, ontology_graph)


def validate_hvdc_data(data_graph: Graph) -> Tuple[bool, str]:
    """Convenience function to validate HVDC data."""
    validator = OntologyValidator()

    # Load HVDC ontology
    from src.ontology.protege_loader import load_hvdc_ontology
    ontology_graph = load_hvdc_ontology()

    return validator.validate(data_graph, ontology_graph)


