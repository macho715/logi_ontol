"""Neo4j graph loader for RDF data."""

from pathlib import Path
from rdflib import Graph
import logging

from src.graph.neo4j_store import Neo4jStore

logger = logging.getLogger(__name__)


class Neo4jLoader:
    """Load RDF data into Neo4j graph database."""

    def __init__(self, neo4j_store: Neo4jStore = None):
        """
        Initialize loader with Neo4j store.

        Args:
            neo4j_store: Neo4jStore instance (creates new if None)
        """
        self.store = neo4j_store or Neo4jStore()

    def load_ttl_file(self, ttl_path: Path):
        """
        Load TTL file into Neo4j.

        Args:
            ttl_path: Path to Turtle RDF file
        """
        logger.info(f"Loading TTL file: {ttl_path}")

        # Parse TTL file
        g = Graph()
        g.parse(ttl_path, format="turtle")
        logger.info(f"Parsed {len(g)} triples from {ttl_path}")

        # Load into Neo4j
        self.store.load_rdf_graph(g)
        logger.info(f"✓ Loaded {ttl_path} into Neo4j")

    def load_directory(self, directory: Path, pattern: str = "*.ttl"):
        """
        Load all TTL files from directory.

        Args:
            directory: Directory containing TTL files
            pattern: Glob pattern for files
        """
        directory = Path(directory)
        ttl_files = list(directory.glob(pattern))
        logger.info(f"Found {len(ttl_files)} TTL files in {directory}")

        for ttl_file in ttl_files:
            try:
                self.load_ttl_file(ttl_file)
            except Exception as e:
                logger.error(f"Failed to load {ttl_file}: {e}")

    def setup_database(self):
        """Initialize database with indexes and constraints."""
        logger.info("Setting up Neo4j database...")

        # Create indexes
        self.store.create_indexes()

        # Create constraints
        self.store.create_constraints()

        logger.info("✓ Neo4j database setup complete")

    def close(self):
        """Close Neo4j connection."""
        self.store.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


