"""Ontology loader for HVDC ontology."""

from pathlib import Path
from typing import List, Dict, Any
from rdflib import Graph, Namespace, RDF, OWL, RDFS

HVDC = Namespace("https://hvdc-project.com/ontology#")


class OntologyLoader:
    """Load and parse OWL/TTL ontology files."""

    def __init__(self, ontology_path: Path):
        """Initialize with ontology file path."""
        self.ontology_path = ontology_path
        self.graph = Graph()
        self.graph.bind("hvdc", HVDC)

    def load(self) -> Graph:
        """Load ontology file into RDFLib Graph."""
        if not self.ontology_path.exists():
            raise FileNotFoundError(f"Ontology file not found: {self.ontology_path}")

        format_map = {
            ".ttl": "turtle",
            ".owl": "xml",
            ".rdf": "xml",
            ".n3": "n3",
        }

        file_format = format_map.get(self.ontology_path.suffix.lower(), "turtle")
        self.graph.parse(self.ontology_path, format=file_format)
        return self.graph

    def extract_classes(self) -> List[str]:
        """Extract all OWL classes from ontology."""
        classes = []
        for s in self.graph.subjects(predicate=RDF.type, object=OWL.Class):
            classes.append(str(s))
        return classes

    def extract_object_properties(self) -> List[str]:
        """Extract all object properties."""
        props = []
        for s in self.graph.subjects(predicate=RDF.type, object=OWL.ObjectProperty):
            props.append(str(s))
        return props

    def extract_datatype_properties(self) -> List[str]:
        """Extract all datatype properties."""
        props = []
        for s in self.graph.subjects(predicate=RDF.type, object=OWL.DatatypeProperty):
            props.append(str(s))
        return props

    def get_class_hierarchy(self) -> Dict[str, List[str]]:
        """Get class hierarchy (subclass relationships)."""
        hierarchy = {}
        for s, o in self.graph.subject_objects(predicate=RDFS.subClassOf):
            parent = str(o)
            child = str(s)
            if parent not in hierarchy:
                hierarchy[parent] = []
            hierarchy[parent].append(child)
        return hierarchy

    def get_property_domains(self, property_uri: str) -> List[str]:
        """Get domains for a property."""
        from rdflib import URIRef

        domains = []
        prop = URIRef(property_uri)
        for o in self.graph.objects(subject=prop, predicate=RDFS.domain):
            domains.append(str(o))
        return domains

    def get_property_ranges(self, property_uri: str) -> List[str]:
        """Get ranges for a property."""
        from rdflib import URIRef

        ranges = []
        prop = URIRef(property_uri)
        for o in self.graph.objects(subject=prop, predicate=RDFS.range):
            ranges.append(str(o))
        return ranges

    def get_ontology_info(self) -> Dict[str, Any]:
        """Get ontology metadata."""
        info = {
            "classes": len(self.extract_classes()),
            "object_properties": len(self.extract_object_properties()),
            "datatype_properties": len(self.extract_datatype_properties()),
            "triples": len(self.graph),
        }

        # Get version info if available
        for s, o in self.graph.subject_objects(predicate=OWL.versionInfo):
            info["version"] = str(o)
            break

        # Get ontology label
        for s in self.graph.subjects(predicate=RDF.type, object=OWL.Ontology):
            for o in self.graph.objects(subject=s, predicate=RDFS.label):
                info["label"] = str(o)
                break
            for o in self.graph.objects(subject=s, predicate=RDFS.comment):
                info["description"] = str(o)
                break

        return info


def load_hvdc_ontology(ontology_path: Path | str = None) -> Graph:
    """Convenience function to load HVDC ontology."""
    if ontology_path is None:
        # Default path
        ontology_path = Path(__file__).parent.parent.parent / "configs" / "ontology" / "hvdc_ontology.ttl"

    loader = OntologyLoader(Path(ontology_path))
    return loader.load()


